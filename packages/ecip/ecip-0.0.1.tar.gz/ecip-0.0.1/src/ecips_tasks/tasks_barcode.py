from tensorrtserver.api import InferContext, ProtocolType
import logging
import json
from celery import Celery
from ecips_utils import ecips_config
import numpy as np
from ecips_tasks.workflow.validate_models import parse_model
from ecips_tasks.workflow.prepare_data import preprocess, cropbarcode, prep_nms, nms
from ecips_tasks.workflow.inference import (
    UserData,
    completion_callback,
    prime_model_queue,
)
from ecips_tasks.workflow.validate_results import validate_barcode

# set logs
logging.getLogger(__name__)

# Modeling parameters
VERBOSE = ecips_config.ECIPS_INFERENCE_VERBOSE
STREAMING = ecips_config.ECIPS_INFERENCE_STREAMING
BAR_MODEL_VERSION = ecips_config.ECIPS_INFERENCE_BARCODE_VERSION
DIG_MODEL_VERSION = ecips_config.ECIPS_INFERENCE_DIGIT_VERSION
BATCH_SIZE = ecips_config.ECIPS_INFERENCE_BATCH_SIZE
URL = ecips_config.ECIPS_INFERENCE_SERVER_URL
PROTOCOL = ProtocolType.from_str(ecips_config.ECIPS_INFERENCE_SERVER_PROTOCOL)
BAR_MDL_NAME = ecips_config.ECIPS_INFERENCE_BARCODE_MODEL_NAME
DIGIT_MDL_NAME = ecips_config.ECIPS_INFERENCE_DIGIT_MODEL_NAME
IOU_THRES = ecips_config.ECIPS_INFERENCE_IOU_THRES
SCORE_THRES = ecips_config.ECIPS_INFERENCE_SCORE_THRES

# Create Celery `App` for Tasking
app = Celery(
    "tasks_barcode",
    broker=ecips_config.CELERY_BROKER,
    backend=ecips_config.CELERY_BACKEND,
)
app.conf.result_expires = 3 * 60 * 60


# callbacks
bar_data = UserData()
digit_data = UserData()

# extract model info.
bar_input_name, bar_c, bar_h, bar_w, bar_format, bar_dtype = parse_model(
    URL, PROTOCOL, BAR_MDL_NAME, BATCH_SIZE, VERBOSE
)

dig_input_name, dig_c, dig_h, dig_w, dig_format, dig_dtype = parse_model(
    URL, PROTOCOL, DIGIT_MDL_NAME, BATCH_SIZE, VERBOSE
)

# infer modeling context
ctx_barcode = InferContext(
    URL, PROTOCOL, BAR_MDL_NAME, BAR_MODEL_VERSION, VERBOSE, 0, STREAMING
)
ctx_digits = InferContext(
    URL, PROTOCOL, DIGIT_MDL_NAME, DIG_MODEL_VERSION, VERBOSE, 0, STREAMING
)


def update_statistics(inference_metrics):
    logging.debug("Writing Inference Metrics into JSON.")
    with open('/mnt/database/barcode_reconstruction_stats', 'a') as f:
        f.write(json.dumps(inference_metrics))
        f.write("\n")


@app.task
def decode_barcode_from_image(img):
    """
    This function utilizes the UDF's defined in workflow to extract the
    barcode from a package.

    Input:
        img - image to decode
    Output:
        inference_metrics - results from decoding barcode
    """
    logging.debug(f"Starting barcode extraction for {img}")

    # initializations
    barcodes = []
    batch_size = 1

    try:
        logging.debug(f"Attempting image preprocessing for {img}")
        image_data = [preprocess(img, bar_dtype, bar_w, bar_h)]
    except Exception:
        logging.error(f"Image preprocessing failed for {img}. Image file may be corrupt")
        raise Exception("Image preprocessing failed and image was not None type")

    logging.debug(f"Preparing inference parameters for {img}")
    input_batch = [image_data[0][0]]
    input_batch_raw = [image_data[0][1]]

    logging.debug(f"Priming barcode queue fpr {img}")
    prime_model_queue(
        completion_callback,
        bar_data,
        [input_batch[0]],
        batch_size,
        ctx_barcode,
        bar_input_name,
    )

    logging.debug(f"Getting barcode results for {img}")
    (request_id_bar) = bar_data._completed_requests.get()
    result_barcode = ctx_barcode.get_async_run_results(request_id_bar)

    logging.debug(f"Beginning barcode post processing procedure for {img}")
    logging.debug(f"Preparing barcode data for non-maximum suppression for {img}")
    barcode_array = prep_nms(result_barcode, SCORE_THRES)

    if barcode_array is not None:
        logging.debug(f"Candidate barcodes for {img} detected performing non-maximum suppression")
        barcode_detections = nms(barcode_array, IOU_THRES)

        logging.debug(f"Beginning cropping procedure for {img}")
        cropped_batch = cropbarcode(
            [input_batch_raw[0]],
            barcode_detections,
            dig_dtype,
            bar_w,
            bar_h,
            dig_w,
            dig_h,
        )

        logging.debug(f"Priming digit queue for {img}")
        prime_model_queue(
            completion_callback,
            digit_data,
            cropped_batch,
            batch_size,
            ctx_digits,
            dig_input_name,
        )

        logging.debug(f"Getting digit results for {img}")
        request_id_dig = digit_data._completed_requests.get()
        result_digits = ctx_digits.get_async_run_results(request_id_dig)

        logging.debug(f"Preparing digit data for non-maximum suppression for {img}")
        digit_array = prep_nms(result_digits, SCORE_THRES, rotated=False)
        if digit_array is not None:
            logging.debug(f"Performing non-maximum suppression for {img}")
            selected_boxes, classes, scores = nms(
                digit_array, IOU_THRES, rotated=False, out_dict=False, sort_bar=True
            )

            logging.debug(f"Validating OCR results with check digit calculation for {img}")
            valid = validate_barcode(classes)
            if valid:
                logging.debug(f"Extracted code passed check digit calculation for {img}")
                barcodes.append(classes)
            else:
                logging.debug(f"Extracted code failed check digit calculation for {img}")

            logging.debug(f"Compiling and returning inference metrics for {img}")
            logging.debug(f"Barcode scores for {img}: ")
            inference_metrics = {
                "barcode": np.squeeze(classes).reshape(-1),
                "detected_barcode": np.squeeze(np.round(
                    barcode_detections["box"].astype(np.single), decimals=3
                )).reshape(-1),
                "barcode_scores": np.squeeze(np.round(
                    barcode_detections["score"].astype(np.single), decimals=5
                )).reshape(-1),
                "detected_digits": np.squeeze(selected_boxes).reshape(-1),
                "digit_scores": np.squeeze(scores).reshape(-1),
                "barcode_valid": str(valid),
                "Barcode_model_version": str(BAR_MODEL_VERSION),
                "Digit_model_version": str(DIG_MODEL_VERSION),
            }
        else:
            inference_metrics = {
                "barcode": np.asarray([-1]),
                "detected_barcode": np.squeeze(np.round(
                    barcode_detections["box"].astype(np.single), decimals=3
                )).reshape(-1),
                "barcode_scores": np.squeeze(np.round(
                    barcode_detections["score"].astype(np.single), decimals=5
                )).reshape(-1),
                "detected_digits": np.asarray([-1]),
                "digit_scores": np.asarray([-1]),
                "barcode_valid": 'False',
                "Barcode_model_version": str(BAR_MODEL_VERSION),
                "Digit_model_version": str(DIG_MODEL_VERSION),
            }
    else:
        logging.debug(
            f"No candidate barcodes detected for {img}. Variable SCORE_THRES may need to be reduced"
        )
        inference_metrics = {
            "barcode": np.asarray([-1]),
            "detected_barcode": np.asarray([-1]),
            "barcode_scores": np.asarray([-1]),
            "detected_digits": np.asarray([-1]),
            "digit_scores": np.asarray([-1]),
            "barcode_valid": 'False',
            "Barcode_model_version": str(BAR_MODEL_VERSION),
            "Digit_model_version": str(DIG_MODEL_VERSION),
        }
    logging.info(f"Inference metrics for {img}: {inference_metrics}")
    update_statistics(inference_metrics)
    return inference_metrics
