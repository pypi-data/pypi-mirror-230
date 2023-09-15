from datetime import datetime
from ecips_utils import ecips_config
import logging
import redis
import orjson
import json
import os

from ecips_utils.fraudDetection.fraud_config import DETECT_MISSING_EPOSTAGE_COMPANYNAME, \
                                                    DETECT_INVALID_EVS_PERMIT, DETECT_MISSING_EVS_VALIDATION, \
                                                    DETECT_IBI_DATE_MISMATCH, DETECT_IBI_SN_MISMATCH, \
                                                    DETECT_SERVICETYPE_MISMATCH, DETECT_MAILCLASS_LETTERCODE_MISMATCH
from ecips_utils.lokiLogging import loki_utils


def logging_config(logging_path=ecips_config.LOGGING_PATH, logging_level=ecips_config.LOGGING_LEVEL):
    # Set logging configurations
    now = datetime.now()  # current date and time
    date_time = now.strftime("%Y%m%d%H%M%S")
    os.makedirs(ecips_config.LOGGING_PATH, exist_ok=True)
    logging_filename = logging_path + date_time + '_controller.log'
    logging.basicConfig(filename=logging_filename,  # NOSONAR
                        filemode='w',
                        level=logging_level,
                        format='%(asctime)s- %(levelname)s -: %(message)s')
    # - Logs going to local Docker container and require server access with access to
    # said Docker container files to access.
    logging.info("Controller Started. Filename = {}".format(logging_filename))

    return logging


def inc_redis_counter(key, amt=1):
    """
        increment the counter in redis for the supplied key. If the key doesn't exist it will be created.
        Unless the amt is specified, the counter is incremented by 1
    """
    # Set up redis connection
    # increment the counter
    red = ecips_config.get_redis_connection()
    try:
        red.incrby(key, amt)
    except redis.exceptions.ConnectionError:
        # During unit tests, the redis db is not running and results in a
        # Connection refused error
        pass


def increment_bcr_counters(images_w_barcode_ct, prlm_info):
    """
    The increment_bcr_counters function increments all of the necessary BCR stat collections
    including total and per MPE bcr_counts (actual barcodes reconstructed) and
    req_bcr_count (number of packages that did not have an associated barcode)

    Args:
        images_w_barcode_ct(int): the number of barcodes that were successfully reconstructed
        prlm_info(dict): dictionary with intrinsic info held in the prlm file. includes count of
            images that require bcr, the MPE device
    """

    # PER MPE COUNTS
    # The BCR count for a specific machine type
    device_key = prlm_info['device_key']
    inc_redis_counter(f"{device_key}_bcr_count", images_w_barcode_ct)
    # The count of images that required BCR for a specific machine type
    inc_redis_counter(f"{device_key}_req_bcr_count", prlm_info['images_to_bcr'])
    # The count of images that were in the PRLM file
    inc_redis_counter(f"{device_key}_total_packages_in_PRLM", prlm_info['total_packages'])


def write_results(outdir, result_contents, result_type):
    filepath_json = outdir + f"{result_type}.json"

    with open(filepath_json, "wb") as fp:
        fp.write(orjson.dumps(result_contents, option=orjson.OPT_SERIALIZE_NUMPY))
    logging.info(f"Results from the {result_type} Post Written to: {filepath_json}")


def prlm_logging(prlm_info,
                 images_w_barcode_ct,
                 images_w_fraud_ct,
                 images_w_anomaly_ct,
                 fraud_type_count,
                 anomaly_type_count):

    # BCR Logging summary
    logging.info(f"BCR summary for PRLM file: {prlm_info['filepath']}: \n"
                 f"\t\t\t\t {prlm_info['total_packages_wout_barcode']} packages out "
                 f"of {prlm_info['total_packages']} total packages required BCR \n"
                 f"\t\t\t\t In total, BCR was performed on {prlm_info['images_to_bcr']} images \n"
                 f"\t\t\t\t After reconstruction, {images_w_barcode_ct} images returned a valid barcode "
                 f"and were sent to WebAPAT")

    # Fraud Logging Summary
    logging.info(f"Fraud summary for PRLM file: {prlm_info['filepath']} \n"
                 f"{images_w_fraud_ct} images with fraud were detected out of {prlm_info['total_packages']} "
                 f"total images in the PRLM. \n"
                 f"The Fraud types were as follows \n {fraud_type_count}")

    logging.info(f"\n The following fraud types are being detected: \n"
                 f"Permit Imprint missing epostage company:{DETECT_MISSING_EPOSTAGE_COMPANYNAME} \n"
                 f"Permit Imprint invalid permit number:{DETECT_INVALID_EVS_PERMIT} \n"
                 f"Permit Imprint missing eVS validation: {DETECT_MISSING_EVS_VALIDATION} \n"
                 f"IBI Date mismatch: {DETECT_IBI_DATE_MISMATCH} \n"
                 f"IBI Serial Number mismatch: {DETECT_IBI_SN_MISMATCH} \n"
                 f"STC Code mismatch: {DETECT_SERVICETYPE_MISMATCH} \n"
                 f"Mail class lettercode/banner mismatch: {DETECT_MAILCLASS_LETTERCODE_MISMATCH}")

    # Anomaly Logging Summary
    logging.info(f"Anomaly summary for PRLM file: {prlm_info['filepath']} \n"
                 f"{images_w_anomaly_ct} images with an anomaly were detected "
                 f"out of {prlm_info['total_packages']} "
                 f"total images in the PRLM. \n"
                 f"The Anomaly types were as follows \n {anomaly_type_count}")

    # Collect the PRLM attributes into a single dictionary
    prlm_summary_attributes = prlm_info
    # Update total counts
    prlm_summary_attributes.update({
        "reconstructed_barcodes": images_w_barcode_ct,
        "fraudulent_packages": images_w_fraud_ct,
        "anomalous_packages": images_w_anomaly_ct
    })
    # Update Fraud summary
    prlm_summary_attributes.update(fraud_type_count)
    # Update Anomaly Summary
    prlm_summary_attributes.update(anomaly_type_count)

    for item in prlm_summary_attributes:
        prlm_summary_attributes[item] = json.dumps(prlm_summary_attributes[item])

    prlm_summary_attributes = [prlm_summary_attributes]
    loki_utils.post_loki_message(prlm_summary_attributes, job_name="prlm_performance_from_ecip", source_name="ecip_db")
