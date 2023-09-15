import copyreg
import logging

import cv2
import numpy as np
import redis
from celery import Celery

from ecips_utils import (ecips_config, ecips_logging, ecips_path)
from ecips_utils.packageObject.packageclass import ImageObject

if ecips_config.ECIPS_WEBAPAT_IDD_VERSION == 10:
    from ecips_utils.webAPAT_IDD.create_webapat_idd10 import generate_webapat_bcr_message, \
        generate_webapat_fraud_message, generate_webapat_anomaly_message
else:
    # Always default to previous version
    from ecips_utils.webAPAT_IDD.create_webapat_idd9 import generate_webapat_bcr_message, \
        generate_webapat_fraud_message, generate_webapat_anomaly_message

# Globals
DEL_ARRAY = np.array([0.08838835] * 128)
R = redis.Redis(host=ecips_config.CELERY_BACKEND.split(":")[1].replace("//", ""))

# Load Celery App
app = Celery(
    "tasks", broker=ecips_config.CELERY_BROKER, backend=ecips_config.CELERY_BACKEND
)
app.conf.result_expires = 3 * 60 * 60
app.conf.broker_transport_options = {
    "queue_order_strategy": "priority",
}

ia_app = ecips_config.get_ia_celery_connection()


def _pickle_keypoints(point):
    """
    This Function enables pickling of a CV2.Keypoint

    """
    return (
        cv2.KeyPoint,
        (
            *point.pt,
            point.size,
            point.angle,
            point.response,
            point.octave,
            point.class_id,
        ),
    )


# registers custom pickle function
copyreg.pickle(cv2.KeyPoint().__class__, _pickle_keypoints)


@app.task
def compute_feature_from_filepath(
    img_filepath,
    write_tofile=True,
    algorithm=ecips_config.ECIPS_REVERSE_IMAGE_ALGORITHM,
    send_hazmat_to_webapat=True,
):
    """
    This Function calculates keypoints and descriptors based on the algorithms selected
    Supported Algorithms are orb, sift and pysift from a filepath.  It then writes the resulting json to file


    Parameters:
    img_filepath: an img created by OpenCV imread Function


    Returns:
    keypoints: Keypoint Values
    descriptors: [nxm] array

    """

    logging.debug(f"Start computing features from {img_filepath}".format(img_filepath=img_filepath))
    logging.debug(f"Load {algorithm} for {img_filepath}".format(algorithm=algorithm, img_filepath=img_filepath))

    # increment the mail processed counter based on the MPE type
    device_key = ecips_path.get_mpe_name(img_filepath)
    ecips_logging.inc_redis_counter(f"{device_key}_mail_processed_count")

    # Instantiate Image Object:
    image = ImageObject(img_filepath)

    # Load imagery & confirm it is valid
    image.check_img_valid()

    if image.is_valid_img():
        # Call the triton inference server
        try:
            image.get_triton_response()
        except Exception as e:
            raise Exception(f"Error occurred during call to Triton Inference Server: {e}")
        # Extract the ECIP's attributes from the response
        # If the triton response did not return a too small image
        if image.is_valid_img():
            image.extract_from_response()

            # Generate the json file with all results
            results_dict, results_json = image.generate_results_json()

            # Write the json file to the disk
            if write_tofile:
                image.write_to_json(results_dict)

                logging.debug(f"Results for {img_filepath}: {results_dict}. Writing complete.")

            if send_hazmat_to_webapat:
                if results_dict["num_hazmat_labels"] > 0:
                    app.send_task(
                        "ecips_tasks.tasks_comms.send_hazmat_to_webapat",
                        kwargs={
                            "img_filepath": img_filepath,
                            "hazmat_scores_first": str(results_dict["hazmat_scores"][0]),
                            "hazmat_class_first": str(int(results_dict["hazmat_classes"][0])),
                        },
                        ignore_result=True,
                        queue="communication",
                    )

            return results_json


@app.task(time_limit=ecips_config.OCR_TIMELIMIT, soft_time_limit=ecips_config.OCR_TIMELIMIT, ignore_result=False)
def compute_OCR_from_filepath(
    filepath,
    ibi,
    volume,
    double_scan,
    impb,
    ecips_serving_url=ecips_config.ECIPS_INFERENCE_SERVER_URL,
    perform_bcr=ecips_config.ECIPS_PERFORM_BCR,
    detect_fraud=ecips_config.ECIPS_DETECT_FRAUD,
    detect_anomaly=ecips_config.ECIPS_DETECT_ANOMALY
):
    try:
        image = ImageObject(filepath, load_from_json=True)

        if not image.json_written:
            logging.info(f"BCR and Fraud detection cannot be performed on image: {filepath}, because the json was not"
                         f"written to the disk")
            return {"bcr_results": {}, "fraud_results": {}, "anomaly_results": {}, "image_results": {}}

        if ecips_serving_url != ecips_config.ECIPS_INFERENCE_SERVER_URL:
            image.update_grpc_url(ecips_serving_url)

        image.get_triton_response(model_name='shipping_label_ocr')

        image.extract_from_response(model_name='shipping_label_ocr')

        barcode_metrics = image.bcr_metrics

        # initialize to empty string
        fraud_json = {}
        bcr_json = {}
        anomaly_json = {}

        # initialize to False:
        send_bcr_result = False

        if perform_bcr and (impb is None or impb == ''):
            bcr_json, send_bcr_result = generate_webapat_bcr_message(image)

            if send_bcr_result:
                # Grab the address block information & send address block info to IA
                logging.info(f"Results will be sent to WebAPAT for file {filepath}, barcodes able to be reconstructed "
                             f"to {barcode_metrics}")

            else:
                logging.info(f"No BCR Results sent to WebAPAT for file {filepath}, barcode unable to be reconstructed")
        else:
            logging.debug(f"No BCR not required for {filepath}, because the barcode {impb} was scanned by the MPE")

        if detect_fraud and not double_scan:
            if ibi:
                image.add_ibi_label(ibi)
            if volume:
                image.add_volume(volume)
            if impb:
                image.add_impb_label(impb_decoded=impb)
            elif send_bcr_result:
                # The impb barcode was able to be reconstructed
                # TODO: do we want to compare to >1 barcode?
                image.add_impb_label(impb_reconstructed=barcode_metrics[0]['barcode'])

            image.scan_package_for_fraud()
            if image.fraud_results.fraud_found():
                fraud_json = generate_webapat_fraud_message(image)
                logging.info(f"Fraudulent package detected. Results will be sent to WebAPAT for file {filepath}")
            else:
                fraud_json = {}
                logging.info(f"No Fraud detected on file {filepath} ")

        if detect_anomaly and not double_scan:

            if impb:
                image.add_impb_label(impb_decoded=impb)
            elif send_bcr_result:
                # The impb barcode was able to be reconstructed
                image.add_impb_label(impb_reconstructed=barcode_metrics[0]['barcode'])

            image.scan_package_for_anomaly()
            if image.anomaly_results.anomaly_found():
                anomaly_json = generate_webapat_anomaly_message(image)
                logging.info(f"Anomalous package detected. Results will be sent to WebAPAT for file {filepath}")
            else:
                anomaly_json = {}
                logging.info(f"No Anomalies detected on file {filepath} ")

        results_json = {"bcr_results": bcr_json,
                        "fraud_results": fraud_json,
                        "anomaly_results": anomaly_json,
                        "image_results": image.get_image_data()}

    except Exception as e:
        error_msg = f"Error occurred on file {filepath} with error message: {e}"
        logging.warning(error_msg)
        results_json = {"bcr_results": error_msg,
                        "fraud_results": error_msg,
                        "anomaly_results": error_msg,
                        "image_results": error_msg}

    return results_json
