import numpy as np

from ecips_utils import ecips_logging
from ecips_utils.anomalyDetection.anomaly_config import HAZMAT_SYMBOL_STC_ANOMALY, \
    HAZMAT_LETTER_INDICATOR_STC_ANOMALY, MIN_CONF_HAZMAT_H_INDICATOR, GROUND_ADVANTAGE_BANNER_STC_ANOMALY, \
    MIN_CONF_GA_BANNER_TEXT, GROUND_ADVANTAGE_PERMIT_IMPRINT_INDICIA_STC_ANOMALY, \
    NON_GROUND_ADVANTAGE_INDICATOR_STC_ANOMALY, GROUND_ADVANTAGE_INDICATOR_STC_ANOMALY, \
    MIN_CONF_PRIORITY_P_INDICATOR, MIN_CONF_FIRST_CLASS_F_INDICATOR, MIN_CONF_GROUND_G_INDICATOR
from ecips_utils.fraudDetection.permit_imprint import permit_mailclass_extraction


def is_anomaly_01(mail_class_from_stc,
                  anomaly_metrics,
                  contains_hazmat_markings,
                  anomaly_id=HAZMAT_SYMBOL_STC_ANOMALY.anomaly_id):
    """
    The is_anomaly_01 function looks for anomaly ID 01, the case where a hazmat symbol
    was confidently detected on the package but the STC code is not a Hazmat STC code

    Args:
        mail_class_from_stc (str): the string that describes the mail class.  Must be one of ['hazmat',
            'first-class', 'priority', 'ground-advantage', 'express']
        anomaly_metrics (dict): a dictionary that describes various anomaly metrics including the stc code,
            anomalies present and if anomaly logic was executed.
        contains_hazmat_markings (bool):  flag that describes if the package contains any hazmat markings
        anomaly_id (str): the two digit string that identifies the anomaly type

    Returns:
        is_anomaly (bool): T/F if the anomaly in question was detected
        anomaly_metrics (dict): the updated anomaly metrics that include if the anomaly was detected
            or logic was executed
    """

    anomaly_key = f'anomaly_{anomaly_id}'
    is_anomaly = False

    if mail_class_from_stc is None and not anomaly_metrics['barcode_attributes']['is_stc_code_valid']:
        anomaly_metrics[anomaly_key]['anomaly_logic_executed'] = False
    else:
        # The Hazmat Symbol could be on any side of the package, so we have to check all sides
        anomaly_metrics[anomaly_key]['anomaly_logic_executed'] = True
        # Requesting the positive hazmat designation ONLY if we meet the high conf standards
        if contains_hazmat_markings and mail_class_from_stc != "hazmat":
            is_anomaly = True
            ecips_logging.inc_redis_counter(anomaly_key)
            anomaly_metrics[anomaly_key]['anomaly_confidence'] = \
                anomaly_metrics["yolo_conf"]
            anomaly_metrics[anomaly_key]['anomaly_detected'] = True

    return is_anomaly, anomaly_metrics


def is_anomaly_02(mail_class_from_stc,
                  mail_class_from_img,
                  anomaly_metrics,
                  anomaly_id=HAZMAT_LETTER_INDICATOR_STC_ANOMALY.anomaly_id):
    """
    The is_anomaly_02 function looks for anomaly ID 02, the case where a hazmat letter indicator, "H"
    was confidently detected on the package but the STC code is not a Hazmat STC code

    Args:
        mail_class_from_stc (str): the string that describes the mail class as extracted from the STC code.
            Must be one of ['hazmat', 'first-class', 'priority', 'ground-advantage', 'express']
        mail_class_from_img (str): the string that describes the mail class as extracted from the letter indicator
            in the top left corner.  Must be one of ['hazmat', 'first-class', 'priority', 'ground-advantage', 'express']
        anomaly_metrics (dict): a dictionary that describes various anomaly metrics including the stc code,
            anomalies present and if anomaly logic was executed.
        anomaly_id (str): the two digit string that identifies the anomaly type

    Returns:
        is_anomaly (bool): T/F if the anomaly in question was detected
        anomaly_metrics (dict): the updated anomaly metrics that include if the anomaly was detected
            or logic was executed
    """

    anomaly_key = f'anomaly_{anomaly_id}'
    is_anomaly = False

    if mail_class_from_img is None:
        anomaly_metrics[anomaly_key]['anomaly_logic_executed'] = False
    elif mail_class_from_stc is None and not anomaly_metrics['barcode_attributes']['is_stc_code_valid']:
        anomaly_metrics[anomaly_key]['anomaly_logic_executed'] = False
    else:
        anomaly_metrics[anomaly_key]['anomaly_logic_executed'] = True
        # the mail class is hazmat and our confidence is above the threshold
        conf_hazmat_package = \
            (mail_class_from_img == "hazmat") and (float(anomaly_metrics["yolo_conf"]) > MIN_CONF_HAZMAT_H_INDICATOR)
        if conf_hazmat_package and mail_class_from_img != mail_class_from_stc:
            is_anomaly = True
            ecips_logging.inc_redis_counter(anomaly_key)
            anomaly_metrics[anomaly_key]['anomaly_confidence'] = \
                anomaly_metrics["yolo_conf"]
            anomaly_metrics[anomaly_key]['anomaly_detected'] = True

    return is_anomaly, anomaly_metrics


def is_anomaly_03(mail_class_from_stc,
                  mail_class_from_img,
                  anomaly_metrics,
                  anomaly_id=GROUND_ADVANTAGE_INDICATOR_STC_ANOMALY.anomaly_id):
    """
    The is_anomaly_03 function looks for anomaly ID 03, the case where a ground-advantage letter indicator, "G"
    was confidently detected on the package but the STC code is not a ground-advantage STC code

    Args:
        mail_class_from_stc (str): the string that describes the mail class as extracted from the STC code.
            Must be one of ['hazmat', 'first-class', 'priority', 'ground-advantage', 'express']
        mail_class_from_img (str): the string that describes the mail class as extracted from the letter indicator
            in the top left corner.  Must be one of ['hazmat', 'first-class', 'priority', 'ground-advantage', 'express']
        anomaly_metrics (dict): a dictionary that describes various anomaly metrics including the stc code,
            anomalies present and if anomaly logic was executed.
        anomaly_id (str): the two digit string that identifies the anomaly type

    Returns:
        is_anomaly (bool): T/F if the anomaly in question was detected
        anomaly_metrics (dict): the updated anomaly metrics that include if the anomaly was detected
            or logic was executed
    """

    anomaly_key = f'anomaly_{anomaly_id}'
    is_anomaly = False

    if mail_class_from_img is None:
        anomaly_metrics[anomaly_key]['anomaly_logic_executed'] = False
    elif mail_class_from_stc is None and not anomaly_metrics['barcode_attributes']['is_stc_code_valid']:
        anomaly_metrics[anomaly_key]['anomaly_logic_executed'] = False
    else:
        anomaly_metrics[anomaly_key]['anomaly_logic_executed'] = True
        # the mail class is ground advantage and our confidence is above the threshold
        ga_package = (mail_class_from_img == "ground-advantage")
        above_yolo_threshold = (float(anomaly_metrics["yolo_conf"]) > MIN_CONF_GROUND_G_INDICATOR)
        if ga_package and mail_class_from_img != mail_class_from_stc and above_yolo_threshold:
            is_anomaly = True
            ecips_logging.inc_redis_counter(anomaly_key)
            anomaly_metrics[anomaly_key]['anomaly_confidence'] = \
                anomaly_metrics["yolo_conf"]
            anomaly_metrics[anomaly_key]['anomaly_detected'] = True

    return is_anomaly, anomaly_metrics


def is_anomaly_04(mail_class_from_stc,
                  mail_class_from_img,
                  anomaly_metrics,
                  anomaly_id=NON_GROUND_ADVANTAGE_INDICATOR_STC_ANOMALY.anomaly_id):
    """
    The is_anomaly_04 function looks for anomaly ID 04, the case where a non-ground advantage letter indicator, "H/P/F"
    was confidently detected on the package but the STC code is a Ground-Advantage STC code

    Args:
        mail_class_from_stc (str): the string that describes the mail class as extracted from the STC code.
            Must be one of ['hazmat', 'first-class', 'priority', 'ground-advantage', 'express']
        mail_class_from_img (str): the string that describes the mail class as extracted from the letter indicator
            in the top left corner.  Must be one of ['hazmat', 'first-class', 'priority', 'ground-advantage', 'express']
        anomaly_metrics (dict): a dictionary that describes various anomaly metrics including the stc code,
            anomalies present and if anomaly logic was executed.
        anomaly_id (str): the two digit string that identifies the anomaly type

    Returns:
        is_anomaly (bool): T/F if the anomaly in question was detected
        anomaly_metrics (dict): the updated anomaly metrics that include if the anomaly was detected
            or logic was executed
    """

    anomaly_key = f'anomaly_{anomaly_id}'
    is_anomaly = False

    if mail_class_from_img is None:
        anomaly_metrics[anomaly_key]['anomaly_logic_executed'] = False
    elif mail_class_from_stc is None and not anomaly_metrics['barcode_attributes']['is_stc_code_valid']:
        anomaly_metrics[anomaly_key]['anomaly_logic_executed'] = False
    else:
        anomaly_metrics[anomaly_key]['anomaly_logic_executed'] = True
        # the mail class is ground advantage and our confidence is above the threshold
        ga_stc = (mail_class_from_stc == "ground-advantage")
        above_yolo_threshold = \
            ((mail_class_from_img == "priority") and
             (float(anomaly_metrics["yolo_conf"]) > MIN_CONF_PRIORITY_P_INDICATOR)) or \
            ((mail_class_from_img == "first-class") and
             (float(anomaly_metrics["yolo_conf"]) > MIN_CONF_FIRST_CLASS_F_INDICATOR)) or \
            ((mail_class_from_img == "hazmat") and
             (float(anomaly_metrics["yolo_conf"]) > MIN_CONF_HAZMAT_H_INDICATOR))
        if ga_stc and mail_class_from_img != mail_class_from_stc and above_yolo_threshold:
            is_anomaly = True
            ecips_logging.inc_redis_counter(anomaly_key)
            anomaly_metrics[anomaly_key]['anomaly_confidence'] = \
                anomaly_metrics["yolo_conf"]
            anomaly_metrics[anomaly_key]['anomaly_detected'] = True

    return is_anomaly, anomaly_metrics


def is_anomaly_05(mail_class_from_stc,
                  mail_class_from_banner,
                  anomaly_metrics,
                  anomaly_id=GROUND_ADVANTAGE_BANNER_STC_ANOMALY.anomaly_id):
    """
    The is_anomaly_02 function looks for anomaly ID 02, the case where a hazmat letter indicator, "H"
    was confidently detected on the package but the STC code is not a Hazmat STC code

    Args:
        mail_class_from_stc (str): the string that describes the mail class as extracted from the STC code.
            Must be one of ['hazmat', 'first-class', 'priority', 'ground-advantage', 'express']
        mail_class_from_banner (str): the string that describes the mail class as extracted from the banner below the
             letter indicator.  Must be one of ['hazmat', 'first-class', 'priority', 'ground-advantage', 'express']
        anomaly_metrics (dict): a dictionary that describes various anomaly metrics including the stc code,
            anomalies present and if anomaly logic was executed.
        anomaly_id (str): the two digit string that identifies the anomaly type

    Returns:
        is_anomaly (bool): T/F if the anomaly in question was detected
        anomaly_metrics (dict): the updated anomaly metrics that include if the anomaly was detected
            or logic was executed
    """

    anomaly_key = f'anomaly_{anomaly_id}'
    is_anomaly = False

    if mail_class_from_banner is None:
        anomaly_metrics[anomaly_key]['anomaly_logic_executed'] = False
    elif mail_class_from_stc is None and not anomaly_metrics['barcode_attributes']['is_stc_code_valid']:
        anomaly_metrics[anomaly_key]['anomaly_logic_executed'] = False
    else:
        anomaly_metrics[anomaly_key]['anomaly_logic_executed'] = True
        # the mail class is hazmat and our confidence is above the threshold
        conf_ga_banner_text = \
            (mail_class_from_banner == "ground-advantage") and \
            ((float(anomaly_metrics["mailclass_lettercode"]["confidence"]) > MIN_CONF_GA_BANNER_TEXT)
             or (anomaly_metrics["mailclass_lettercode"]["exact_text_to_keyword_match"]))
        # check if the stc code is hazmat because hazmat stcs CAN have GA language in the banner
        hazmat_stc = mail_class_from_stc == "hazmat"
        # In order to be considered anomalous, the package must have a confident GA banner, not be a hazmat sTC
        # and have the class of the banner != the class of the stc
        if conf_ga_banner_text and not hazmat_stc and mail_class_from_banner != mail_class_from_stc:
            is_anomaly = True
            ecips_logging.inc_redis_counter(anomaly_key)
            anomaly_metrics[anomaly_key]['anomaly_confidence'] = \
                anomaly_metrics["yolo_conf"]
            anomaly_metrics[anomaly_key]['anomaly_detected'] = True

    return is_anomaly, anomaly_metrics


def is_anomaly_06(permit_imprint_ocr,
                  mail_class_from_stc,
                  anomaly_id=GROUND_ADVANTAGE_PERMIT_IMPRINT_INDICIA_STC_ANOMALY.anomaly_id):
    """
       The is_anomaly_06 function looks for anomaly ID 06, the case where the permit imprint indicia contains ground
       advantage language, but the STC code does not  correspond to a ground advantage STC

       Args:
           permit_imprint_ocr (array): The bounding box, text, and confidence returned by EasyOCR for each detected line
           mail_class_from_stc (str): the string that describes the mail class as extracted from the STC code.
            Must be one of ['hazmat', 'first-class', 'priority', 'ground-advantage', 'express']
           anomaly_id (str): the two digit string that identifies the anomaly type

       Returns:
           Two values, is_anomaly and anomaly metrics.
           is_anomaly (bool): T/F if the anomaly in question was detected
           anomaly_metrics (dict): {"anomaly_logic_executed (bool) Only false if anomaly 06 is turned off,
           "mail_class_detected" (str) Class detected on Permit Imprint,
           "mail_class_raw_text" (str) EasyOCR text used to determine class,
           "mail_class_dist" (int) Levenstein distance between class detected and raw text,
           "mail_class_conf" (float) EasyOCR conf for text used to determine class}
       """
    anomaly_key = f'anomaly_{anomaly_id}'
    is_anomaly = False
    anomaly_metrics = {"anomaly_logic_executed": True,
                       "mail_class_detected": "",
                       "mail_class_raw_text": "",
                       "mail_class_dist": "",
                       "mail_class_conf": None,
                       }
    anomaly_metrics_keys = np.array(list(anomaly_metrics.keys()))

    if not GROUND_ADVANTAGE_PERMIT_IMPRINT_INDICIA_STC_ANOMALY.is_active:
        anomaly_metrics['anomaly_logic_executed'] = False
        return is_anomaly, anomaly_key, anomaly_metrics

    permit_imprint_class, dist, type_text, conf, rotation = permit_mailclass_extraction(permit_imprint_ocr)

    if permit_imprint_class == 'ground-advantage':
        anomaly_metrics.update(zip(anomaly_metrics_keys[1:], (permit_imprint_class, type_text, dist, conf, rotation)))
        if mail_class_from_stc != 'ground-advantage' and mail_class_from_stc != 'hazmat':
            is_anomaly = True
            ecips_logging.inc_redis_counter(anomaly_key)

    return is_anomaly, anomaly_key, anomaly_metrics
