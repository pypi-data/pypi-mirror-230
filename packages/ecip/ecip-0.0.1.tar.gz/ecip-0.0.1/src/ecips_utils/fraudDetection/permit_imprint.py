from Levenshtein import distance
import numpy as np
import re
from fuzzywuzzy import process
from ecips_utils.fraudDetection.fraud_config import MAX_EPOS_DIST, MAX_EVS_DIST, MAX_PERMIT_DIST, MAX_PAID_DIST, \
    get_invalid_permits, DETECT_MISSING_EPOSTAGE_COMPANYNAME, DETECT_MISSING_EVS_VALIDATION, DETECT_INVALID_EVS_PERMIT,\
    MIN_PERMIT_CONF, FUZZY_MATCH_PERMIT, MAX_SHIPPO_DIST, get_valid_shippo_mids, DETECT_SHIPPO_EPOSTAGE_FRAUD
from ecips_utils.anomalyDetection.anomaly_config import MAX_GA_DIST, MAX_PRIORITY_DIST, MAX_FC_DIST

invalid_permit_numbers = get_invalid_permits()
valid_shippo_mids = get_valid_shippo_mids()


def classify_mc_helper(type_text):
    if len(type_text) > 1:
        ga_dist = min(distance(type_text.lower().strip(), "groundadvantage"),
                      distance(type_text.lower().strip(), "uspsgroundadvantage"),
                      distance(type_text.lower().strip(), "uspsground"))

        priority_dist = distance(type_text.lower(), "prioritymail")

        first_class_dist = distance(type_text.lower(), "first-classpkg")

        if ga_dist < priority_dist and ga_dist < first_class_dist:
            return "ground-advantage", ga_dist

        elif priority_dist < first_class_dist:
            return "priority", priority_dist
        else:
            return "first-class", first_class_dist
    else:
        return "priority", 100


def permit_mailclass_extraction(ocr_results):
    rotation = 0
    # TODO: Mary, why are we getting an index error here?
    try:
        (_, type_text_last, conf_last) = ocr_results[-1]
        (_, type_text_first, conf_first) = ocr_results[0]
    except IndexError:
        return "neither", -1, "", 0.0, rotation

    type_text_last = "".join(type_text_last.lower().split())
    type_text_first = "".join(type_text_first.lower().split())

    mc_last, dist_last = classify_mc_helper(type_text_last)
    mc_first, dist_first = classify_mc_helper(type_text_first)

    mc, dist, type_text, conf, rotation = (mc_last, dist_last, type_text_last, conf_last, 180) \
        if dist_last < dist_first else \
        (mc_first, dist_first, type_text_first, conf_first, 0)

    if (mc == "ground-advantage" and dist > MAX_GA_DIST) or (mc == "priority" and dist > MAX_PRIORITY_DIST) or (
            mc == "first-class" and dist > MAX_FC_DIST):
        mc = "neither"
        dist = -1

    return mc, dist, type_text, conf, rotation


def classify_helper(type_text):
    if len(type_text) > 1:
        evs_dist = min(distance(type_text.lower().strip(), "evs"),
                       distance(type_text.lower().strip(), "e-vs"))
        epos_dist = min(distance(type_text.lower(), "epostage"), distance(type_text.lower(), "e-postage"))
        pi_type, dist = ("evs", evs_dist) if evs_dist < epos_dist else ("epostage", epos_dist)

    else:
        pi_type, dist = ("evs", 100)

    return pi_type, dist


def classify_permit_imprint(ocr_results):
    """Classify permit_imprint as either epostage, evs, or neither

        Parameters:
            ocr_results (array): The bounding box, text, and confidence returned by EasyOCR for each detected line
        Returns:
            pi_type (string), dist (int): pi_type is the type of permit-imprint either "evs", "epostage", or "neither".
                dist is the distance between the expected type text on the permit-imprint and what was detected in ocr.
    """

    rotation = 0
    # TODO: Mary, why are we getting an index error here?
    try:
        (_, type_text_last, conf_last) = ocr_results[-1]
        (_, type_text_first, conf_first) = ocr_results[0]
    except IndexError:
        return "neither", -1, "", 0.0, rotation

    type_text_last = "".join(type_text_last.lower().split())
    type_text_first = "".join(type_text_first.lower().split())

    pi_type_last, dist_last = classify_helper(type_text_last)
    pi_type_first, dist_first = classify_helper(type_text_first)

    pi_type, dist, type_text, conf, rotation = (pi_type_last, dist_last, type_text_last, conf_last, 0) \
        if dist_last < dist_first else \
        (pi_type_first, dist_first, type_text_first, conf_first, 180)

    if (pi_type == "epostage" and dist > MAX_EPOS_DIST) or (pi_type == "evs" and dist > MAX_EVS_DIST):
        pi_type = "neither"
        dist = -1

    return pi_type, dist, type_text, conf, rotation


def check_permit_number(one_line_above_evs, one_line_above_evs_conf, two_lines_above_evs, two_lines_above_evs_conf):
    """Determine if a permit number is invalid.
    Parameters: one_line_above_evs (string): The text returned by EasyOCR for line above eVS line,
     one_line_above_evs_conf(float): The confidence of the detected text for one line above eVS line,
     two_lines_above_evs (string): The text returned by EasyOCR for line above the line above the eVS line
     two_lines_above_evs_conf(float): The confidence of the detected text for two lines above eVS line
    Returns: is_valid (bool), detected_permit_number (string),
    detected_permit_number_confidence (int), detected_permit_invalid (bool) detected_business (string),
    detected_business_confidence (int): Returns True if evs is suspected to be fraudulent Returns False if invalid
    evs is found to be valid. Includes detection results for metrics and debugging purposes
    """
    # grab permit number w/o conditioning on presence of "permit"
    permit_no1 = "".join(re.findall(r"\d{2}\d*", one_line_above_evs))
    permit_no2 = "".join(re.findall(r"\d{2}\d*", two_lines_above_evs))

    if permit_no1 in invalid_permit_numbers:

        return True, permit_no1, one_line_above_evs, one_line_above_evs_conf, True, None, None, None, None
    if permit_no2 in invalid_permit_numbers:

        return True, permit_no2, two_lines_above_evs, two_lines_above_evs_conf, True, None, None, None, None

    if FUZZY_MATCH_PERMIT:
        if one_line_above_evs_conf < MIN_PERMIT_CONF:
            invalid_perm1, score1 = process.extractOne(permit_no1, invalid_permit_numbers)
            distance1 = distance(invalid_perm1, permit_no1)
        else:
            invalid_perm1 = None
            distance1 = 100
        if two_lines_above_evs_conf < MIN_PERMIT_CONF:
            invalid_perm2, score2 = process.extractOne(permit_no2, invalid_permit_numbers)
            distance2 = distance(invalid_perm2, permit_no2)
        else:
            invalid_perm2 = None
            distance2 = 100

        if distance1 <= MAX_PERMIT_DIST and distance1 < distance2:

            return True, invalid_perm1, one_line_above_evs, one_line_above_evs_conf, True, None, None, None, None
        if distance2 <= MAX_PERMIT_DIST and distance2 < distance1:

            return True, invalid_perm2, two_lines_above_evs, two_lines_above_evs_conf, True, None, None, None, None

    return None


def is_fraud_evs(ocr_results, rotation_info):
    """Determine validity of evs by checking if a permit no or business name is present. Parameters: ocr_results (
    array): The bounding box, text, and confidence returned by EasyOCR for each detected line rotation_info (int):
    How many degrees the image was rotated during OCR Returns: is_valid (bool), detected_permit_number (string),
    detected_permit_number_confidence (int), detected_permit_invalid (bool) detected_business (string),
    detected_business_confidence (int): Returns True if evs is suspected to be fraudulent Returns False if invalid
    evs is found to be valid. Includes detection results for metrics and debugging purposes
    """
    number_of_lines = len(ocr_results)
    lines_check = number_of_lines > 1
    if not lines_check:
        return False, None, None, None, None, None, None

    if rotation_info == 0:
        one_line_above_evs, one_line_above_evs_conf = ocr_results[-2][1], ocr_results[-2][2]
        two_lines_above_evs, two_lines_above_evs_conf = ocr_results[-3][1], ocr_results[-3][2]
    else:
        one_line_above_evs, one_line_above_evs_conf = ocr_results[1][1], ocr_results[1][2]
        two_lines_above_evs, two_lines_above_evs_conf = ocr_results[2][1], ocr_results[2][2]

    if DETECT_INVALID_EVS_PERMIT:
        permit_results = check_permit_number(one_line_above_evs, one_line_above_evs_conf, two_lines_above_evs,
                                             two_lines_above_evs_conf)
        if permit_results is not None:
            return permit_results

    # Check that "Permit" keyword is the first word in the line above or the line two above
    permit_one_check = distance(one_line_above_evs.split()[0], "permit") <= MAX_PERMIT_DIST
    if permit_one_check:
        # There is a permit, if we checked that it was invalid, we found that it was not invalid, return no fraud
        # found, permit number as detected by the numbers in the permit line
        return False, "".join(re.findall(r"\d{2}\d*", one_line_above_evs)), one_line_above_evs, \
            one_line_above_evs_conf, False, None, None, None, None

    permit_two_check = distance(two_lines_above_evs.split()[0], "permit") <= MAX_PERMIT_DIST

    if permit_two_check:
        # There is a permit, if we checked that it was invalid, we found that it was not invalid, return no fraud
        # found, permit number as detected by the numbers in the permit line
        return False, "".join(re.findall(r"\d{2}\d*", two_lines_above_evs)), two_lines_above_evs, \
            two_lines_above_evs_conf, False, None, None, None, None

    # if "Perimt" is not present, check the line above is a valid business, not the "Postage Paid" line
    biz_check = distance(one_line_above_evs.split()[-1], "paid") > MAX_PAID_DIST
    if lines_check and biz_check:
        # line above is a business name presumably, return no fraud found, no permit number
        return False, None, None, None, None, one_line_above_evs, one_line_above_evs_conf, None, None

    return True, None, None, None, None, None, None, None, None


def is_fraud_epostage(ocr_results, rotation_info, barcode):
    """Determine validity of epostage by checking if a business name is present. Parameters: ocr_results (array): The
    bounding box, text, and confidence returned by EasyOCR for each detected line rotation_info (int): How many
    degrees the image was rotated during OCR Returns: is_valid (bool), detected_permit_number (string),
    detected_permit_number_confidence (int), detected_permit_invalid (bool),detected_business (string),
    detected_business_confidence (int): Returns True if epostage is suspected to be fraudulent. Returns False if
    invalid evs is found to be valid. Also returns detection results for metrics and debugging purposes.
    """
    number_of_lines = len(ocr_results)

    if rotation_info == 0:
        one_line_above_epos, one_line_above_epos_conf = ocr_results[-2][1], ocr_results[-2][2]
    else:
        one_line_above_epos, one_line_above_epos_conf = ocr_results[1][1], ocr_results[1][2]

    # Check  number or lines meets ePostage requirement, at least 3
    lines_check = number_of_lines > 2

    # Check the line above is a valid business, not the "Postage Paid" line
    biz_check = distance(one_line_above_epos.split()[-1], "paid") > MAX_PAID_DIST

    # Check the line above is not a permit number
    permit_check = distance(one_line_above_epos.split()[0], "permit") > MAX_PERMIT_DIST

    if DETECT_SHIPPO_EPOSTAGE_FRAUD:
        # check if business is "shippo"
        shippo_check = distance(one_line_above_epos, "shippo") <= MAX_SHIPPO_DIST

        if shippo_check:
            if barcode is not None:
                mid = barcode.mid

                if mid is not None and mid not in valid_shippo_mids:
                    return True, None, None, None, None, one_line_above_epos, one_line_above_epos_conf, True, mid
                else:
                    return False, None, None, None, None, one_line_above_epos, one_line_above_epos_conf, True, mid
            else:
                return False, None, None, None, None, one_line_above_epos, one_line_above_epos_conf, True, None
    if DETECT_MISSING_EPOSTAGE_COMPANYNAME:
        if lines_check and biz_check and permit_check:
            return False, None, None, None, None, one_line_above_epos, one_line_above_epos_conf, False, None

        # If permit number is detected, return the detected permit number which is always an invalid permit number
        if not permit_check:
            return True, one_line_above_epos, None, one_line_above_epos_conf, True, None, None, False, None

        # If no permit number and no business, return fraud and no detections
        return True, None, None, None, None, None, None, False, None

    # if not shippo fraud and not checking missing company name return not fraud
    return False, None, None, None, None, one_line_above_epos, one_line_above_epos_conf, False, None


def is_fraud_permit_imprint(ocr_results, barcode):
    """Determine validity of permit-imprint by checking if a permit no or business name is present on evs and epostage
    labels.
            Parameters:
                ocr_results (array): The bounding box, text, and confidence returned by EasyOCR for each detected line
                barcode (string): The impb barcode. May be None if impb was not decoded
            Returns:
                is_fraud_results (dict):
                returns True if permit imprint is valid.
                Returns False if invalid label is found. Returns null if the permit_imprint label is neither evs or
                epostage. Returns type of permit-imprint, and the edit_distance from "evs" or "epostage" used in
                classification. Also return detection details for each label class to for metrics and debugging purposes
    """
    fraud_results = {
        "is_fraud": None,
        "all_detected_text": None,
        "classification_results": {
            "permit_imprint_class": None,  # evs, epostage, none
            "edit_dist_to_class": None,  # how close the text was to clss
            "detected_class_text": None,  # raw ocr text
            "detected_class_text_confidence": None,  # ocr confidence
            "rotation_info": None  # rotation of label
        },
        "validation_results": {
            "detected_permit_number": None,  # permit number picked up in evs label
            "detected_permit_number_line": None,  # raw ocr text from line where permit was detected
            "detected_permit_number_confidence": None,  # ocr confidence
            "detected_permit_invalid": None,  # Boolean: permit detected on invalid list
            "detected_business": None,  # raw ocr text picked up as business
            "detected_business_confidence": None,  # ocr confidence
            "shippo_epostage": None,  # boolean: label identified as shippo_epostage, None for evs packages
            "mid": None  # mailer id for shippo_epostage packages and invaild permit. None for all others
        }

    }
    classification_results_keys = np.array(list(fraud_results['classification_results'].keys()))
    validation_results_keys = np.array(list(fraud_results['validation_results'].keys()))
    try:
        fraud_results['all_detected_text'] = [[text, prob] for bbox, text, prob in ocr_results]
    except IndexError:
        fraud_results['all_detected_text'] = np.array(ocr_results)
    fraud_results['classification_results'].update(
        zip(classification_results_keys, classify_permit_imprint(ocr_results)))

    if fraud_results['classification_results']['permit_imprint_class'] == "evs" and DETECT_MISSING_EVS_VALIDATION:
        is_fraud = is_fraud_evs(ocr_results, fraud_results['classification_results']['rotation_info'])
        fraud_results['is_fraud'] = is_fraud[0]
        fraud_results['validation_results'].update(zip(validation_results_keys, is_fraud[1:]))

    elif fraud_results['classification_results']['permit_imprint_class'] \
            == "epostage" and (DETECT_MISSING_EPOSTAGE_COMPANYNAME or DETECT_SHIPPO_EPOSTAGE_FRAUD):
        is_fraud = is_fraud_epostage(ocr_results, fraud_results['classification_results']['rotation_info'], barcode)
        fraud_results['is_fraud'] = is_fraud[0]
        fraud_results['validation_results'].update(zip(validation_results_keys, is_fraud[1:]))

    return fraud_results
