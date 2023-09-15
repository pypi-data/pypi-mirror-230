# Set PATH
import sys
import os
sys.path.append(os.getcwd())
import argparse
import copy
import glob
import json
import os
import pickle
from pathlib import Path

import pandas as pd

# Need to update the environment variables when we run this locally so that we open the
# invalid permit and stc db files
PROJECT_ROOT_DIR = "/"+os.path.join(*os.path.split(os.getcwd())[0].split("/")[:-1])
os.environ['INVALID_PERMIT_FILE'] = PROJECT_ROOT_DIR + "/Docker/Invalid_eVS_Permit_List.xlsx"
os.environ['STC_DB_FILE'] = PROJECT_ROOT_DIR + "/Docker/stc_db.json"


def get_mail_id_APPS(fname):
    idx_start = fname.rfind('_') + 1
    idx_end = fname.find('.', idx_start) - 1
    return fname[idx_start:idx_end]


def get_mail_id_SPSS(fname):
    return fname.split('_')[2]


from ecips_utils.prlmProcessing.read_PRLM import PRLMFile
from ecips_utils.fraudDetection import fraud_config
from ecips_utils.packageObject.packageclass import ImageObject, IBIClass, IMPBBarcodeClass, MailMarkingsClass, PermitImprintClass


def extract_bcr_metrics(ocr_results):
    """
    Extract barcode information metrics from response.
    """
    processed_response = ocr_results
    # results_barcode = {
    #     "barcode_ocr": processed_response["barcode_ocr"],
    #     "barcode_decode": processed_response["barcode_decode"]
    # }
    results_barcode = processed_response["barcodes"]

    # Grab pyzbar and ocr model results.  Add preference for pyzbar result if available
    inference_metrics = []
    for pyzbar_result, ocr_result in results_barcode:

        # Grabbing the preferred barcode result
        preferred_result = pyzbar_result if pyzbar_result not in [None, 'None'] else ocr_result
        barcode_present = False if preferred_result is None or preferred_result == 'None' else True
        # TODO: return barcode classification
        barcode_type = "UCC/EAN 128" if barcode_present else None

        inference_metrics.append({
            "barcode_risk_score": 0.0,  # TODO: how do we derive risk score
            "barcode_present": str(barcode_present).upper(),
            "barcode_reconstructed": str(barcode_present).upper(),
            "barcode": preferred_result,
            "barcode_ocr": ocr_result,
            "barcode_decode": pyzbar_result,
            "barcode_class": str(barcode_type)
        })

    return inference_metrics

def get_barcodes_from_prlm(prlm_filepath_given):
    prlm = PRLMFile(filepath=prlm_filepath_given)

    impb_barcodes_extracted = prlm.get_impb_barcodes()
    ibi_barcodes_extracted = prlm.get_ibi_barcodes()

    for filepath in impb_barcodes_extracted:
        if impb_barcodes_extracted[filepath] == '':
            impb_barcodes_extracted[filepath] = None

    return impb_barcodes_extracted, ibi_barcodes_extracted


def update_mailclass_metrics(filename, mail_class_fraud_metrics, n_mailclass_metrics,
                             fraud_performance_metrics, mail_class_fraud_types_detected):
    # Mail Class Letter detected by YOLO
    n_mailclass_metrics['n_yolo_mailclass_letter'] += 1

    # IMPB initialized?
    if 'impb_barcode' in mail_class_fraud_metrics['service_code'] and mail_class_fraud_metrics['service_code']['impb_barcode'] is not None:
        n_mailclass_metrics['n_impb_barcodes'] += 1

    # STC extracted from IMPB
    if mail_class_fraud_metrics['service_code'].get('is_stc_code_valid'):
        n_mailclass_metrics['n_stc_extracted_from_impb'] += 1

    # Mail class banner cropped
    if 'ocr_results' in mail_class_fraud_metrics['mailclass_lettercode']:
        if mail_class_fraud_metrics['mailclass_lettercode']['ocr_results'] is None:
            n_mailclass_metrics['n_mailclass_banner_not_cropped'] += 1
    else:
        n_mailclass_metrics['n_mailclass_banner_cropped'] += 1

    # Mail class banner decoded by OCR
    if 'is_mailclass_detected_ocr' in mail_class_fraud_metrics['mailclass_lettercode']:
        if mail_class_fraud_metrics['mailclass_lettercode']['is_mailclass_detected_ocr']:
            n_mailclass_metrics['n_valid_banner_ocr'] += 1

    # Update classification metrics of `mismatch_mailclass_servicetype`
    if 'fraud_logic_executed' in mail_class_fraud_metrics['service_code'] and mail_class_fraud_metrics['service_code']['fraud_logic_executed']:
        fraud_performance_metrics['mismatch_mailclass_servicetype']['fraud_logic_executed'] += 1

        if 'mismatch_mailclass_servicetype' in mail_class_fraud_types_detected:
            fraud_performance_metrics['mismatch_mailclass_servicetype']['fraud'] += 1
            fraud_performance_metrics['mismatch_mailclass_servicetype']['fraud_filenames'].append(filename)
        else:
            fraud_performance_metrics['mismatch_mailclass_servicetype']['not_fraud'] += 1

    else:
        fraud_performance_metrics['mismatch_mailclass_servicetype']['fraud_logic_not_executed'] += 1
        fraud_performance_metrics['mismatch_mailclass_servicetype']['filenames_fraud_logic_not_executed'].append(
            filename)

    # Update classification metrics of `mismatch_mailclass_lettercode`
    if 'fraud_logic_executed' in mail_class_fraud_metrics['mailclass_lettercode'] and mail_class_fraud_metrics['mailclass_lettercode']['fraud_logic_executed']:
        fraud_performance_metrics['mismatch_mailclass_lettercode']['fraud_logic_executed'] += 1

        if 'mismatch_mailclass_lettercode' in mail_class_fraud_types_detected:
            fraud_performance_metrics['mismatch_mailclass_lettercode']['fraud'] += 1
            fraud_performance_metrics['mismatch_mailclass_lettercode']['fraud_filenames'].append(filename)
        else:
            fraud_performance_metrics['mismatch_mailclass_lettercode']['not_fraud'] += 1

    else:
        fraud_performance_metrics['mismatch_mailclass_lettercode']['fraud_logic_not_executed'] += 1
        fraud_performance_metrics['mismatch_mailclass_lettercode']['filenames_fraud_logic_not_executed'].append(
            filename)


def update_ibi_metrics(filename, ibi_barcodes_dict, ibi_class_fraud_metrics, n_ibi_metrics,
                       fraud_performance_metrics, ibi_fraud_types_detected, mail_id=None):
    # IBI labels detected by the YOLO model
    n_ibi_metrics['n_yolo_ibi'] += 1

    # IBI barcodes decoded in PRLM file
    if mail_id is None:
        if ibi_barcodes_dict[filename] is not None:
            n_ibi_metrics['n_prlm_ibi'] += 1
    else:
        if ibi_barcodes_dict[mail_id] is not None:
            n_ibi_metrics['n_prlm_ibi'] += 1

    # Date decoded by OCR
    if ibi_class_fraud_metrics['dates_ibi']['ocr_valid']:
        n_ibi_metrics['n_ocr_date_detected_ibi'] += 1

    # Date decoded by PRLM extraction logic
    if ibi_class_fraud_metrics['dates_ibi']['barcode_valid']:
        n_ibi_metrics['n_prlm_date_decoded_ibi'] += 1

    # Serial Number decoded by OCR
    if ibi_class_fraud_metrics['serial_number_ibi']['ocr_valid']:
        n_ibi_metrics['n_ocr_serial_number_detected_ibi'] += 1

    # Serial Number decoded by PRLM extraction logic
    if ibi_class_fraud_metrics['serial_number_ibi']['barcode_valid']:
        n_ibi_metrics['n_prlm_serial_number_decoded_ibi'] += 1

    # Date
    # OCR worked but IBI in PRLM not found
    if ibi_class_fraud_metrics['dates_ibi']['ocr_valid'] and not ibi_class_fraud_metrics['dates_ibi']['barcode_valid']:
        n_ibi_metrics['n_date_valid_ocr_no_prlm_ibi'] += 1

    # Barcode in PRLM but no OCR
    elif not ibi_class_fraud_metrics['dates_ibi']['ocr_valid'] and \
            ibi_class_fraud_metrics['dates_ibi']['barcode_valid']:
        n_ibi_metrics['n_date_valid_prlm_ibi_no_ocr'] += 1
        if ibi_class_fraud_metrics['ocr_results']['date']['ocr_date_found']:
            n_ibi_metrics['n_date_valid_ocr_wrong_parse'] += 1

    # Serial Number
    # OCR worked but IBI in PRLM not found
    if ibi_class_fraud_metrics['serial_number_ibi']['ocr_valid'] and \
            not ibi_class_fraud_metrics['serial_number_ibi']['barcode_valid']:
        n_ibi_metrics['n_serial_number_valid_ocr_no_prlm_ibi'] += 1

    # Barcode in PRLM but no OCR
    elif not ibi_class_fraud_metrics['serial_number_ibi']['ocr_valid'] and \
            ibi_class_fraud_metrics['serial_number_ibi']['barcode_valid']:
        n_ibi_metrics['n_serial_number_valid_prlm_ibi_no_ocr'] += 1

    # Update classification metrics of `mismatch_humanReadableDate_decodedIBIDate`
    if ibi_class_fraud_metrics['dates_ibi']['fraud_logic_executed']:
        fraud_performance_metrics['mismatch_humanReadableDate_decodedIBIDate']['fraud_logic_executed'] += 1

        if 'mismatch_humanReadableDate_decodedIBIDate' in ibi_fraud_types_detected:
            fraud_performance_metrics['mismatch_humanReadableDate_decodedIBIDate']['fraud'] += 1
            fraud_performance_metrics['mismatch_humanReadableDate_decodedIBIDate']['fraud_filenames'].append(filename)
        else:
            fraud_performance_metrics['mismatch_humanReadableDate_decodedIBIDate']['not_fraud'] += 1

    else:
        fraud_performance_metrics['mismatch_humanReadableDate_decodedIBIDate']['fraud_logic_not_executed'] += 1
        fraud_performance_metrics['mismatch_humanReadableDate_decodedIBIDate'][
            'filenames_fraud_logic_not_executed'].append(filename)

    # Update classification metrics of `mismatch_humanReadableSN_decodedIBISN`
    if ibi_class_fraud_metrics['serial_number_ibi']['fraud_logic_executed']:
        fraud_performance_metrics['mismatch_humanReadableSN_decodedIBISN']['fraud_logic_executed'] += 1

        if 'mismatch_humanReadableSN_decodedIBISN' in ibi_fraud_types_detected:
            fraud_performance_metrics['mismatch_humanReadableSN_decodedIBISN']['fraud'] += 1
            fraud_performance_metrics['mismatch_humanReadableSN_decodedIBISN']['fraud_filenames'].append(filename)

        else:
            fraud_performance_metrics['mismatch_humanReadableSN_decodedIBISN']['not_fraud'] += 1

    else:
        fraud_performance_metrics['mismatch_humanReadableSN_decodedIBISN']['fraud_logic_not_executed'] += 1
        fraud_performance_metrics['mismatch_humanReadableSN_decodedIBISN']['filenames_fraud_logic_not_executed'].append(
            filename)

    # Update classification metrics of `mismatch_humanReadableSN_decodedIBISN`
    if ibi_class_fraud_metrics['serial_number_construct_ibi']['fraud_logic_executed']:
        fraud_performance_metrics['invalid_IBI_SN']['fraud_logic_executed'] += 1

        if 'invalid_IBI_SN' in ibi_fraud_types_detected:
            fraud_performance_metrics['invalid_IBI_SN']['fraud'] += 1
            fraud_performance_metrics['invalid_IBI_SN']['fraud_filenames'].append(filename)

        else:
            fraud_performance_metrics['invalid_IBI_SN']['not_fraud'] += 1

    else:
        fraud_performance_metrics['invalid_IBI_SN']['fraud_logic_not_executed'] += 1
        fraud_performance_metrics['invalid_IBI_SN']['filenames_fraud_logic_not_executed'].append(
            filename)


def update_permit_imprint_metrics(filename, n_permit_imprint_metrics, fraud_performance_metrics,
                                  permit_imprint_fraud_metrics,
                                  permit_imprint_fraud_types_detected):
    # Permit-Imprint labels detected by the YOLO model
    n_permit_imprint_metrics['n_yolo_pi'] += 1

    # EVS or EPostage detected
    if permit_imprint_fraud_metrics['classification_results']['permit_imprint_class'] == "evs":
        n_permit_imprint_metrics['n_evs_detected'] += 1
        fraud_performance_metrics['invalid_eVS_permit']['fraud_logic_executed'] += 1
        fraud_performance_metrics['missing_eVS_validation']['fraud_logic_executed'] += 1

        if 'invalid_eVS_permit' in permit_imprint_fraud_types_detected:
            fraud_performance_metrics['invalid_eVS_permit']['fraud'] += 1
            fraud_performance_metrics['invalid_eVS_permit']['fraud_filenames'].append(filename)

        else:
            fraud_performance_metrics['invalid_eVS_permit']['not_fraud'] += 1

        if 'missing_eVS_validation' in permit_imprint_fraud_types_detected:
            fraud_performance_metrics['missing_eVS_validation']['fraud'] += 1
            fraud_performance_metrics['missing_eVS_validation']['fraud_filenames'].append(filename)
        else:
            fraud_performance_metrics['missing_eVS_validation']['not_fraud'] += 1

    if permit_imprint_fraud_metrics['classification_results']['permit_imprint_class'] == "epostage":
        n_permit_imprint_metrics['n_epos_detected'] += 1
        fraud_performance_metrics['invalid_ePostage']['fraud_logic_executed'] += 1

        if 'invalid_ePostage' in permit_imprint_fraud_types_detected:
            fraud_performance_metrics['invalid_ePostage']['fraud'] += 1
            fraud_performance_metrics['invalid_ePostage']['fraud_filenames'].append(filename)
        else:
            fraud_performance_metrics['invalid_ePostage']['not_fraud'] += 1

def update_impb_metrics(filename, n_impb_metrics, fraud_performance_metrics,
                                  impb_fraud_metrics,
                                  impb_fraud_types_detected):
    # IMPB labels detected by the YOLO model
    n_impb_metrics['n_yolo_impb'] += 1

    # EVS or EPostage detected
    fraud_performance_metrics['mismatch_hr_impb']['fraud_logic_executed'] += 1

    if 'mismatch_hr_impb' in impb_fraud_types_detected:
        fraud_performance_metrics['mismatch_hr_impb']['fraud'] += 1
        fraud_performance_metrics['mismatch_hr_impb']['fraud_filenames'].append(filename)
    else:
        fraud_performance_metrics['mismatch_hr_impb']['not_fraud'] += 1


def define_metrics():
    # Define fraud metrics
    n_ibi_metrics = {'n_yolo_ibi': 0,
                     'n_prlm_ibi': 0,
                     'n_prlm_date_decoded_ibi': 0,
                     'n_ocr_date_detected_ibi': 0,
                     'n_prlm_serial_number_decoded_ibi': 0,
                     'n_ocr_serial_number_detected_ibi': 0,
                     'n_ocr_date_regex_captured': 0,
                     'n_date_valid_prlm_ibi_no_ocr': 0,
                     'n_date_valid_ocr_no_prlm_ibi': 0,
                     'n_serial_number_valid_prlm_ibi_no_ocr': 0,
                     'n_serial_number_valid_ocr_no_prlm_ibi': 0,
                     'n_date_valid_ocr_wrong_parse': 0
                     }

    n_mailclass_metrics = {'n_yolo_mailclass_letter': 0,
                           'n_impb_barcodes': 0,
                           'n_stc_extracted_from_impb': 0,
                           'n_mailclass_banner_cropped': 0,
                           'n_mailclass_banner_not_cropped': 0,
                           'n_valid_banner_ocr': 0
                           }

    n_impb_metrics = {'n_yolo_impb': 0 }

    n_permit_imprint_metrics = {'n_yolo_pi': 0,
                                'n_evs_detected': 0,
                                'n_epos_detected': 0,
                                }

    # Define Fraud indicators and classification metrics
    fraud_indicators = fraud_config.FRAUD_TYPES

    classification_metrics = {'fraud_logic_executed': 0,
                              'fraud': 0,
                              'not_fraud': 0,
                              'fraud_logic_not_executed': 0,
                              'fraud_filenames': [],
                              'filenames_fraud_logic_not_executed': []
                              }

    fraud_performance_metrics = {}
    for indicator in fraud_indicators:
        fraud_performance_metrics[indicator] = copy.deepcopy(classification_metrics)

    return n_ibi_metrics, n_mailclass_metrics, n_permit_imprint_metrics, n_impb_metrics, fraud_performance_metrics


def gather_metrics(filepath, all_fraud_metrics,
                   ibi_class_fraud_metrics=None, ibi_fraud_types_detected=None,
                   mail_class_fraud_metrics=None, mail_class_fraud_types_detected=None,
                   permit_imprint_fraud_metrics=None, permit_imprint_fraud_types_detected=None,
                   impb_fraud_metrics=None, impb_fraud_types_detected=None
                   ):
    if ibi_class_fraud_metrics is not None:
        all_fraud_metrics['Date_metrics'].append(
            {
                "yolo_conf": ibi_class_fraud_metrics['yolo_conf'],
                **ibi_class_fraud_metrics['dates_ibi'],
                **ibi_class_fraud_metrics['ocr_results']['date'],
                **ibi_class_fraud_metrics['barcode_results']['date'],
                **{'is_fraud': True if 'mismatch_humanReadableDate_decodedIBIDate'
                                       in ibi_fraud_types_detected else False,
                   'filepath': filepath,
                   'matched_date': ibi_class_fraud_metrics['matched_date'] if 'matched_date'
                                                                              in ibi_class_fraud_metrics else None
                   }
            }
        )

        all_fraud_metrics['SN_metrics'].append(
            {
                "yolo_conf": ibi_class_fraud_metrics['yolo_conf'],
                **ibi_class_fraud_metrics['serial_number_ibi'],
                **ibi_class_fraud_metrics['ocr_results']['serial_number'],
                **ibi_class_fraud_metrics['barcode_results']['serial_number'],
                **{'is_fraud': True if 'mismatch_humanReadableSN_decodedIBISN'
                                       in ibi_fraud_types_detected else False,
                   'filepath': filepath}
            }
        )
        all_fraud_metrics['invalid_SN_metrics'].append(
            {
                **ibi_class_fraud_metrics['serial_number_construct_ibi'],
                **ibi_class_fraud_metrics['ocr_results']['serial_number'],
                **ibi_class_fraud_metrics['barcode_results']['serial_number'],
                **{'is_fraud': True if 'invalid_IBI_SN'
                                       in ibi_fraud_types_detected else False,
                   'filepath': filepath}
            }
        )

    elif mail_class_fraud_metrics is not None:
        all_fraud_metrics['STC_metrics'].append(
            {
                "yolo_conf": mail_class_fraud_metrics['yolo_conf'],
                **mail_class_fraud_metrics['service_code'],
                **{'is_fraud': True if 'mismatch_mailclass_servicetype'
                                       in mail_class_fraud_types_detected else False,
                   'filepath': filepath}
            }
        )

        all_fraud_metrics['MCB_metrics'].append(
            {
                "yolo_conf": mail_class_fraud_metrics['yolo_conf'],
                **mail_class_fraud_metrics['mailclass_lettercode'],
                **{'is_fraud': True if 'mismatch_mailclass_lettercode'
                                       in mail_class_fraud_types_detected else False,
                   'filepath': filepath}
            }
        )

    elif impb_fraud_metrics is not None:
        all_fraud_metrics['IMPB_metrics'].append(
            {
                "yolo_conf": impb_fraud_metrics['yolo_conf'],
                **impb_fraud_metrics['impb_barcode'],
                **{'is_fraud': True if 'mismatch_hr_impb'
                                       in impb_fraud_types_detected else False,
                   'filepath': filepath}
            }
        )


    else:
        all_fraud_metrics['PI_metrics'].append(
            {
                "yolo_conf": (permit_imprint_fraud_metrics['yolo_conf'] if 'yolo_conf' in permit_imprint_fraud_metrics
                              else None),
                **permit_imprint_fraud_metrics['classification_results'],
                **permit_imprint_fraud_metrics['validation_results'],
                **{'all_detected_text': permit_imprint_fraud_metrics['all_detected_text'],
                   'filepath': filepath,
                   'fraud_type': permit_imprint_fraud_types_detected[0] if len(permit_imprint_fraud_types_detected) == 1
                   else None
                   }
            }
        )


def run(images_ocr_results, impb_barcodes_dict, ibi_barcodes_dict,
        n_ibi_metrics, n_mailclass_metrics, n_permit_imprint_metrics, n_impb_metrics,
        all_fraud_metrics, fraud_performance_metrics):

    # Iterate through the images and generate fraud metrics
    for filepath, ocr_results in images_ocr_results.items():
        # Initialize ImageObject
        # try:
        mail_id = None
        # TODO: load the json here as well
        image_obj = ImageObject(OCR_FILEPATH + "/" + filepath[8:], load_from_json=True, check_fraud=True)
        image_obj.ocr_results = ocr_results
        image_obj.bcr_metrics = extract_bcr_metrics(ocr_results)
        try:
            image_obj.add_impb_label(impb_barcodes_dict[filepath])
            image_obj.add_ibi_label(ibi_barcodes_dict[filepath])
        except KeyError:
            try:
                filepath = OCR_FILEPATH + "/" + filepath[8:]
                image_obj.add_impb_label(impb_barcodes_dict[filepath])
                image_obj.add_ibi_label(ibi_barcodes_dict[filepath])
            except KeyError:

                try:
                    if "SPSS" in filepath:
                        mail_id = get_mail_id_SPSS(filepath)
                    elif "APPS" in filepath:
                        mail_id = get_mail_id_APPS(filepath)

                except:
                    continue
                image_obj.add_impb_label(impb_barcodes_dict[mail_id])
                image_obj.add_ibi_label(ibi_barcodes_dict[mail_id])
        # except Exception as e:
        #     print(f"Unable to process file {filepath} due to Error {e}")
        #     continue
        # Initialize IBIObject and get Fraud Metrics
        if ocr_results['IBI_date'] is not None:
            ibi_obj = IBIClass(image_obj)
            ibi_class_fraud_metrics = ibi_obj.describe_fraud_metrics()
            ibi_fraud_types_detected = ibi_obj.fraud_type

            gather_metrics(filepath, all_fraud_metrics,
                           ibi_class_fraud_metrics=ibi_class_fraud_metrics,
                           ibi_fraud_types_detected=ibi_fraud_types_detected,
                           )

            # IBI PERFORMANCE METRICS
            update_ibi_metrics(filepath, ibi_barcodes_dict, ibi_class_fraud_metrics, n_ibi_metrics,
                               fraud_performance_metrics, ibi_fraud_types_detected, mail_id=mail_id)

        # Initialize MailMarkingsObject and get Fraud Metrics
        if ocr_results['mail_class_letter'] is not None:
            mail_marking_obj = MailMarkingsClass(image_obj)
            mail_class_fraud_metrics = mail_marking_obj.describe_fraud_metrics()
            mail_class_fraud_types_detected = mail_marking_obj.fraud_type

            gather_metrics(filepath, all_fraud_metrics,
                           mail_class_fraud_metrics=mail_class_fraud_metrics,
                           mail_class_fraud_types_detected=mail_class_fraud_types_detected)

            # MailMarkingsClass PERFORMANCE METRICS
            update_mailclass_metrics(filepath, mail_class_fraud_metrics, n_mailclass_metrics,
                                     fraud_performance_metrics, mail_class_fraud_types_detected)

        # Initialize IMPB Barcode mismatch and get Fraud Metrics
        if ocr_results['barcode_ocr'] is not None:
            impb_obj = IMPBBarcodeClass(image_obj)
            impb_fraud_metrics = impb_obj.describe_fraud_metrics()
            impb_fraud_types_detected = impb_obj.fraud_type

            gather_metrics(filepath, all_fraud_metrics,
                           impb_fraud_metrics=impb_fraud_metrics,
                           impb_fraud_types_detected=impb_fraud_types_detected)

            # # MailMarkingsClass PERFORMANCE METRICS
            update_impb_metrics(filepath, n_impb_metrics, fraud_performance_metrics,
                                impb_fraud_metrics, impb_fraud_types_detected)

        #  Initialize PermitImprintObject and get fraud Metrics
        if ocr_results['permit_imprint'] is not None:
            permit_imprint_obj = PermitImprintClass(image_obj)
            permit_imprint_fraud_metrics = permit_imprint_obj.describe_fraud_metrics()
            permit_imprint_fraud_types_detected = permit_imprint_obj.fraud_type

            gather_metrics(filepath, all_fraud_metrics,
                           permit_imprint_fraud_metrics=permit_imprint_fraud_metrics,
                           permit_imprint_fraud_types_detected=permit_imprint_fraud_types_detected)

            # PERMIT-IMPRINT PERFORMANCE METRICS
            update_permit_imprint_metrics(filepath, n_permit_imprint_metrics,
                                          fraud_performance_metrics, permit_imprint_fraud_metrics,
                                          permit_imprint_fraud_types_detected)


def main():
    n_ibi_metrics, n_mailclass_metrics, n_permit_imprint_metrics, n_impb_metrics, fraud_performance_metrics = define_metrics()
    n_images = 0

    all_fraud_metrics = {
        'Date_metrics': [],
        'SN_metrics': [],
        'invalid_SN_metrics': [],
        'STC_metrics': [],
        'MCB_metrics': [],
        'PI_metrics': [],
        'IMPB_metrics': []
    }

    impb_barcodes_dict = {}
    ibi_barcodes_dict = {}

    # Load all PRLM results
    for root, dirs, files in os.walk(PRLM_FILEPATH):
        for walk_filename in files:
            if walk_filename.endswith(".zip") and 'zip' in walk_filename.lower():
                prlm = f"{root}/{walk_filename}"
                print(prlm)
                impb_bcr, ibi_bcr = get_barcodes_from_prlm(prlm)
                impb_barcodes_dict = {**impb_barcodes_dict, **impb_bcr}
                ibi_barcodes_dict = {**ibi_barcodes_dict, **ibi_bcr}

    # Load iterate through the raw_OCR_results.json and gather metrics for each image

    all_ocr_filepaths = glob.glob(f"{OCR_FILEPATH}/**/**/**/raw_OCR_results.json")
    for ocr_filepath_i in all_ocr_filepaths:
        with open(ocr_filepath_i, "r") as fp:
            ocr_results_loaded = json.load(fp)
            n_images += len(ocr_results_loaded)

        run(ocr_results_loaded, impb_barcodes_dict, ibi_barcodes_dict,
            n_ibi_metrics, n_mailclass_metrics, n_permit_imprint_metrics, n_impb_metrics,
            all_fraud_metrics, fraud_performance_metrics)

    # Save metrics
    for key in all_fraud_metrics:
        all_fraud_metrics[key] = pd.DataFrame(all_fraud_metrics[key])
        all_fraud_metrics[key].to_csv(f"{OUTPUT_PATH}/{key}.csv", index=False)

    fraud_metrics = {'n_ibi_metrics': n_ibi_metrics,
                     'n_mailclass_metrics': n_mailclass_metrics,
                     'n_permit_imprint_metrics': n_permit_imprint_metrics,
                     'n_impb_metrics': n_impb_metrics,
                     'fraud_performance_metrics': fraud_performance_metrics
                     }

    for fraud_key_type in fraud_metrics['fraud_performance_metrics']:
        print(f"Fraud Type: {fraud_key_type}")
        for key, value in fraud_metrics['fraud_performance_metrics'][fraud_key_type].items():
            if key not in ['fraud_filenames', 'filenames_fraud_logic_not_executed']:
                print(f"{key}: {value}")

        print("-" * 100)

    print("IBI metrics")
    print(fraud_metrics['n_ibi_metrics'])
    print("-" * 100)

    print("Mail Class Markings metrics")
    print(fraud_metrics['n_mailclass_metrics'])
    print("-" * 100)

    print("Permit Imprint metrics")
    print(fraud_metrics['n_permit_imprint_metrics'])
    print("-" * 100)

    with open(f"{OUTPUT_PATH}/fraud_performance.pkl", "wb") as f:
        pickle.dump(fraud_metrics, f)

    for fraud_key_type in fraud_metrics['fraud_performance_metrics']:
        del fraud_metrics['fraud_performance_metrics'][fraud_key_type]['fraud_filenames']
        del fraud_metrics['fraud_performance_metrics'][fraud_key_type]['filenames_fraud_logic_not_executed']

    with open(f"{OUTPUT_PATH}/fraud_performance.json", "w", encoding="utf-8") as f:
        json.dump(fraud_metrics, f)

    print("N IMAGES", n_images)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--raw_output_path",
                        help="""
                                Directory path to sift through the ocr results, contains `raw_output` directory.
                                Example: /data/Fraud/test_results/validation_results/test_v1.6.1_rc1_results
                             """,
                        default="/data/Fraud/test_results/validation_results/validation_set_v1.0.2_results/v1.6.8_rc2/"
                        )

    parser.add_argument("-p", "--prlm_path",
                        help="""
                                Directory path to sift through the PRLM results, contains files like Run_0004.PRLM.zip
                                Example: /data/Fraud/datasets/validation_set/v1.0.0/ALL_IMAGES
                            """,
                        default="/data/Fraud/datasets/validation_set/v1.0.2/ALL_IMAGES"
                        )


    args = parser.parse_args()

    OCR_FILEPATH = args.prlm_path
    PRLM_FILEPATH = args.prlm_path

    OUTPUT_PATH = args.raw_output_path + "/analysis"
    print("OUTPUT_PATH", OUTPUT_PATH, OCR_FILEPATH)
    Path(OUTPUT_PATH).mkdir(parents=True, exist_ok=True)

    main()
