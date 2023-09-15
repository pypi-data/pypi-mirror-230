import logging
import json
from celery import Celery, chord, subtask

from ecips_utils import (ecips_config, ecips_logging)
from ecips_utils.lokiLogging import (loki_config, loki_utils)
from ecips_utils.webAPAT_IDD.webapat_utils import post_webapat_message
from ecips_utils.prlmProcessing.read_PRLM import PRLMFile
from ecips_utils.fraudDetection.fraud_config import FRAUD_TYPES
from ecips_utils.anomalyDetection.anomaly_config import ANOMALY_TYPES

if ecips_config.ECIPS_WEBAPAT_IDD_VERSION == 10:
    from ecips_utils.webAPAT_IDD.create_webapat_idd10 import generate_webapat_hazmat_message
else:
    # Always default to previous version
    from ecips_utils.webAPAT_IDD.create_webapat_idd9 import generate_webapat_hazmat_message

IP = ecips_config.ECIPS_DEVICE_MAPPING["ip"]

# Load Celery App
app = Celery(
    "tasks_comms",
    broker=ecips_config.CELERY_BROKER,
    backend=ecips_config.CELERY_BACKEND,
)

HAZMAT_CLASS_LIST = [
    {"id": 1, "name": "Lithium_UN_Label", "supercategory": ""},
    {"id": 2, "name": "Lithium__Class_9", "supercategory": ""},
    {"id": 3, "name": "Lithium_Battery_Label", "supercategory": ""},
    {"id": 4, "name": "Biohazard", "supercategory": ""},
    {"id": 5, "name": "No_Fly", "supercategory": ""},
    {"id": 6, "name": "Finger_Small", "supercategory": ""},
    {"id": 7, "name": "Finger_Large", "supercategory": ""},
    {"id": 8, "name": "Cargo_Air_Only", "supercategory": ""},
    {"id": 9, "name": "Suspected_Label", "supercategory": ""},
    {"id": 10, "name": "Hazmat_Surface_Only", "supercategory": ""},
    {"id": 21, "name": "Cremated_Remains", "supercategory": ""},
]

min_timeout = 60 * 60  # 60 seconds in minute X 60 minutes in an hour  = 1 hour min timeout


@app.task
def send_hazmat_to_webapat(
        img_filepath,
        hazmat_scores_first,
        hazmat_class_first,
):
    if ecips_config.ECIPS_INFERENCE_SERVER_USE_HAZMAT_YOLO:
        # If we are using the yolo model
        hazmat_minconf = ecips_config.ECIPS_INFERENCE_HAZMAT_YOLO_SCORE_THRES[hazmat_class_first]
        if hazmat_minconf != "":
            hazmat_minconf = float(hazmat_minconf)
        else:
            hazmat_minconf = 0.0
    else:
        # If we are using the retina net model
        hazmat_minconf = ecips_config.ECIPS_INFERENCE_HAZMAT_SCORE_THRES

    if float(hazmat_scores_first) > hazmat_minconf:

        results_json, device_map_error = generate_webapat_hazmat_message(img_filepath)

        logging.info(f"JSON results for {img_filepath}: {results_json}")

        for hazmat_result in results_json["images"][0]["hazmat_labels"]:
            # increment hazmat detection counter
            # increment counter for individual hazmat types. redis key is the hazmat class name
            ecips_logging.inc_redis_counter(hazmat_result["description"])

        send_comms(results_json["images"], results_json["action"], "ecip_webapat_msg")

        if device_map_error:
            raise AssertionError(f"The MPE device key does not map to the mpe mappings value for image {img_filepath}\n"
                                 f"with MPE Mapping {ecips_config.get_mpe_mappings()} so it was set to 0.0.0.0 \n"
                                 f"This Error was raised AFTER sending hazmat results to WebAPAT")
        return results_json
    else:
        logging.info(
            f"Hazmat Score of  {hazmat_scores_first} does not meet {hazmat_minconf} threshold"
        )

        return {}


@app.task
def process_prlm_start(
        prlm_file,
):
    logging.debug(f"Process PRLM Task started for {prlm_file}")
    prlm_obj = PRLMFile(prlm_file)
    logging.debug("PRLM file object created")
    images_to_bcr = prlm_obj.get_images_to_bcr()
    logging.debug("List of images to BCR was returned")
    ibi_barcode_dict = prlm_obj.get_ibi_barcodes()
    logging.debug("List of images and IBI barcodes was returned")
    volume_dict = prlm_obj.get_package_volume()
    double_scan_dict = prlm_obj.get_double_scans()
    impb_barcode_dict = prlm_obj.get_impb_barcodes()
    logging.debug("List of images and IMPB barcodes was returned")
    images_in_prlm = prlm_obj.get_image_filepaths()
    logging.debug("List of all image filepaths present in the PRLM as returned")
    # timeout = 10 * len(images_to_bcr)

    prlm_info = {"filepath": prlm_file,
                 "total_packages_wout_barcode": prlm_obj.total_packages_wout_barcode,
                 "total_packages": prlm_obj.total_packages,
                 "images_to_bcr": len(images_to_bcr),
                 "device_key": prlm_obj.device_key}

    if ecips_config.ECIPS_PERFORM_BCR or ecips_config.ECIPS_DETECT_FRAUD:
        logging.debug(f"Preparing to send images to compute OCR from filepath \n"
                      f"ECIPS Perform BCR: {ecips_config.ECIPS_PERFORM_BCR} \n"
                      f"ECIPS DETECT FRAUD: {ecips_config.ECIPS_DETECT_FRAUD}")
        subtasklistOCR = [subtask("ecips_tasks.tasks.compute_OCR_from_filepath",
                                  kwargs={"filepath": img_file,
                                          "ibi": ibi_barcode_dict[img_file],
                                          "volume": volume_dict[img_file],
                                          "double_scan": double_scan_dict[img_file],
                                          "impb": impb_barcode_dict[img_file]},
                                  queue="livemail",
                                  expires=24*60*60,
                                  rate_limit=ecips_config.OCR_RATELIMIT,
                                  time_limit=ecips_config.OCR_TIMELIMIT,
                                  soft_time_limit=ecips_config.OCR_TIMELIMIT, app=app) for img_file in images_in_prlm]
        subtaskSummmary = subtask("ecips_tasks.tasks_comms.process_ocr_results",
                                  kwargs={"prlm_info": prlm_info},
                                  queue="communication-prlm",
                                  time_limit=2*24*60*60,
                                  soft_time_limit=2*24*60*60,
                                  expires=2*24*60*60, app=app
                                  )
        logging.debug("Subtasks sent to livemail queue")
        task_chord = chord(subtasklistOCR)(subtaskSummmary)
        logging.debug(f"subtasks converted to a group of subtasks {task_chord}")


@app.task
def process_ocr_results(ocr_results,
                        prlm_info
                        ):
    root_prlm_dir = prlm_info["filepath"].split(prlm_info["filepath"].split("/")[-1])[0]
    logging.debug(f"Length of OCR Results {len(ocr_results)}")
    logging.debug("Results were successfully joined")

    # A List the track the errors that occur during the run.
    # Celery chords will NOT propagate errors correctly so we need to track these ourselves
    error_list = ''

    # Initialize results
    bcr_request = {}
    fraud_request = {}
    anomaly_request = {}

    images_w_barcode_ct = 0
    images_w_fraud_ct = 0
    images_w_anomaly_ct = 0
    fraud_type_count = {fraud_type: 0 for fraud_type in FRAUD_TYPES}
    anomaly_type_count = {f"anomaly_{anomaly_type.anomaly_id}": 0 for anomaly_type in ANOMALY_TYPES}

    if ecips_config.ECIPS_PERFORM_BCR:
        # Count how many images were successfully reconstructed
        img_base_out = []
        for result in ocr_results:
            logging.debug(f"On result: {result}")
            try:
                bcr_result = result["bcr_results"]
            except TypeError:
                # If an error occurred on the task, then we cannot grab results as a dict
                logging.debug(f"An error occured on result: {result}")
                continue
            if type(bcr_result) != dict and type(bcr_result) == str:
                # An Error occurred that we want to log
                # These errors are identical for Fraud, BCR and Anomalies so we will only add once
                error_list += f"{bcr_result} \n"
            elif bcr_result != {} and type(bcr_result) == dict:
                # Adds 0 if false, 1 if True to count the number of successfully reconstructed barcodes
                images_w_barcode_ct += 1
                img_base_out.append(bcr_result)

        if images_w_barcode_ct > 0:
            # If we have reconstructed barcodes:

            # Send the message to webapat and loki
            bcr_action = "rbc_orig_list_from_ecip"
            send_comms(img_base_out, bcr_action, "ecip_webapat_msg")

            if ecips_config.WRITE_BCR_RESULTS:
                ecips_logging.write_results(root_prlm_dir, img_base_out, result_type="BCR_WebAPAT_message")

        else:
            logging.info(f"No barcodes in the PRLM file {prlm_info['filepath']} were able to be reconstructed")

        # Increment the BCR Performance Trackers
        ecips_logging.increment_bcr_counters(images_w_barcode_ct, prlm_info)

    if ecips_config.ECIPS_DETECT_FRAUD:
        # Count how many images were successfully reconstructed
        logging.debug("Processing fraudulent results")
        img_base_out = []
        for result in ocr_results:
            try:
                fraud_results = result["fraud_results"]
            except TypeError:
                # If an error occurred on the task, then we cannot grab results as a dict
                logging.debug(f"An error occurred on result: {result}")
                continue
            if fraud_results != {} and type(fraud_results) == dict:
                images_w_fraud_ct += 1
                fraud_type_detected = fraud_results["fraud_type"].split(',')[:-1]
                for fraud in fraud_type_detected:
                    fraud_type_count[fraud] += 1
                ecips_logging.inc_redis_counter("total_fraud_package_volume", fraud_results.pop('volume'))
                img_base_out.append(fraud_results)

        if images_w_fraud_ct > 0:
            # If we have fraudulent items:

            # Count how many of each fraud type
            for key, value in fraud_type_count.items():
                ecips_logging.inc_redis_counter(key, value)
            # Send the message to webapat and loki
            fraud_action = "fr_orig_list_from_ecip"
            send_comms(img_base_out, fraud_action, "ecip_webapat_msg")

            if ecips_config.WRITE_FRAUD_RESULTS:
                ecips_logging.write_results(root_prlm_dir, img_base_out, result_type="Fraud_WebAPAT_message")
        else:
            logging.info(f"No fraud was found in the PRLM file: {prlm_info['filepath']}")

    if ecips_config.ECIPS_DETECT_ANOMALY:
        # Count how many images were successfully reconstructed
        logging.debug("Processing anomalous results")
        img_base_out = []
        for result in ocr_results:
            try:
                anomaly_results = result["anomaly_results"]
            except TypeError:
                # If an error occurred on the task, then we cannot grab results as a dict
                logging.debug(f"An error occurred on result: {result}")
                continue
            if anomaly_results != {} and type(anomaly_results) == dict:
                images_w_anomaly_ct += 1
                anomaly_type_detected = anomaly_results["anomaly_type"].split(',')[:-1]
                for anomaly in anomaly_type_detected:
                    anomaly_type_count[f"anomaly_{anomaly}"] += 1
                img_base_out.append(anomaly_results)

        if images_w_anomaly_ct > 0:
            # If we have anomalous results:

            # Send the message to webapat and loki
            anomaly_action = "mail_anomaly_list_from_ecip"
            send_comms(img_base_out, anomaly_action, "ecip_webapat_msg")

            if ecips_config.WRITE_ANOMALY_RESULTS:
                ecips_logging.write_results(root_prlm_dir, img_base_out, result_type="Anomaly_WebAPAT_message")

        else:
            logging.info(f"No anomalies were found in the PRLM file: {prlm_info['filepath']}")

    ecips_logging.prlm_logging(prlm_info,
                               images_w_barcode_ct,
                               images_w_fraud_ct,
                               images_w_anomaly_ct,
                               fraud_type_count,
                               anomaly_type_count)

    if ecips_config.WRITE_OCR_RESULTS:
        json_out = {}
        loki_list = []
        # write the OCR results to a json file
        for result in ocr_results:
            raw_ocr_results = result["image_results"]
            if raw_ocr_results != {} and type(raw_ocr_results) == dict:
                json_out.update({raw_ocr_results['absolute_image_path']: raw_ocr_results})
                # A flag to decide if we send this to loki, only send results where bcr,
                # fraud, anomaly or hazmat are present
                send_to_loki = json.loads((json.loads(raw_ocr_results.pop('send_to_loki').lower())))
                if send_to_loki:
                    loki_list.append(raw_ocr_results)

        ecips_logging.write_results(root_prlm_dir, json_out, result_type="raw_image_results")
        loki_utils.post_loki_message(loki_list, job_name="image_results_from_ecip", source_name="ecip_db")

    if error_list == '':
        # No errors occurred while processing the PRLM file
        return {"bcr_request_results": bcr_request,
                "fraud_request_results": fraud_request,
                "anomaly_results": anomaly_request}
    else:
        # Errors occurred.  Propagate the Error message to the process_ocr_results task
        raise AssertionError(f"Errors occurred while processing the PRLM file {prlm_info['filepath']}.  The "
                             f"error(s) were as follows: \n {error_list}")


def send_comms(img_message, action, message_type):
    """
    A function to send comms to both webapat AND loki

    Args:
        img_message (dict): the message that will be send to both loki and webapat
        action (str): the message action according to the WebAPAT IDD
        message_type (str): the type of message (loki only)
    """
    logging.info(f"The flag to send message for {action} for communications to WebAPAT is"
                 f"set to {ecips_config.POST_WEBAPAT_MSG_TYPE[action]}")
    if ecips_config.POST_WEBAPAT_MSG_TYPE[action]:
        # If we have the flag turned on to send this particular message type to webapat
        post_webapat_message(img_message, action=action)

    logging.info(f"The flag to send message for {action} for communications to LOKI is"
                 f"set to {loki_config.POST_LOKI_MSG_TYPE[action]}")
    if loki_config.POST_LOKI_MSG_TYPE[action]:
        # If we have the flag turned on to send this particular message type to loki
        loki_utils.post_loki_message(img_message,
                                     source_name=message_type,
                                     job_name=action)
