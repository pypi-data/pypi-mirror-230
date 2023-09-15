from tensorrtserver.api import InferContext, ProtocolType
import logging
from celery import Celery
import numpy as np
from ecips_utils import ecips_config
from ecips_tasks.workflow.validate_models import parse_model
from ecips_tasks.workflow.prepare_data import (preprocess,
                                               prep_nms,
                                               nms)
from ecips_tasks.workflow.inference import (UserData,
                                            completion_callback,
                                            prime_model_queue)


# Create Celery tasking config
class CeleryConfig:
    task_serializer = 'pickle'
    result_serializer = 'pickle'
    event_serializer = 'pickle'
    accept_content = ['pickle']
    result_accept_content = ['pickle']


# Create Celery `App` for Tasking
app = Celery('tasks_stamp', broker=ecips_config.CELERY_BROKER, backend=ecips_config.CELERY_BACKEND)
app.conf.result_expires = 3*60*60
app.config_from_object(CeleryConfig)

# set logs
logging.getLogger(__name__)

# Modeling constants
IOU_THRES = ecips_config.ECIPS_INFERENCE_STAMP_IOU_THRES
SCORE_THRES = ecips_config.ECIPS_INFERENCE_STAMP_SCORE_THRES
VERBOSE = ecips_config.ECIPS_INFERENCE_VERBOSE
STREAMING = ecips_config.ECIPS_INFERENCE_STREAMING
STAMP_MODEL_VERSION = ecips_config.ECIPS_INFERENCE_STAMP_VERSION
BATCH_SIZE = ecips_config.ECIPS_INFERENCE_BATCH_SIZE
URL = ecips_config.ECIPS_INFERENCE_SERVER_URL
PROTOCOL = ProtocolType.from_str(ecips_config.ECIPS_INFERENCE_SERVER_PROTOCOL)
STAMP_MDL_NAME = ecips_config.ECIPS_INFERENCE_STAMP_MODEL_NAME
BATCH_SIZE = 1

# Initialize callback
stamp_data = UserData()

# extract model info.
stamp_input_name, stamp_c, stamp_h, stamp_w, stamp_format, stamp_dtype = parse_model(
    URL, PROTOCOL, STAMP_MDL_NAME,
    BATCH_SIZE, VERBOSE)

# infer modeling context
ctx_stamp = InferContext(URL, PROTOCOL, STAMP_MDL_NAME, STAMP_MODEL_VERSION, VERBOSE, 0, STREAMING)


@app.task
def find_stamps_on_image(img):
    """
    This function utilizes the UDF's defined in workflow to detect stamps on a given image.

    Input:
        img - image to process
    Output:
        inference_metrics - results from detecting stamps
    """

    logging.debug(f"Starting stamp detection on {str(img)}")
    try:
        logging.debug(f"Attempting image preprocessing on {str(img)}")
        image_data = [preprocess(img, stamp_dtype, stamp_w, stamp_h)]
    except Exception:
        logging.error(f"Image preprocessing failed  on {str(img)}. Image file may be corrupt")
        raise Exception("Image preprocessing failed and image was not None type")

    logging.debug(f"Preparing inference parameters for {str(img)}")
    input_batch = [image_data[0][0]]

    logging.debug(f"Priming stamp queue for {str(img)}")
    prime_model_queue(completion_callback, stamp_data, [input_batch[0]],
                      BATCH_SIZE, ctx_stamp, stamp_input_name)

    logging.debug(f"Getting stamp detection results on {str(img)}")
    (request_id_stamp) = stamp_data._completed_requests.get()
    result_stamp = ctx_stamp.get_async_run_results(request_id_stamp)

    # review below portion when testing code
    logging.debug(f"Beginning stamp post processing procedure on {str(img)}."
                  f"Preparing stamp data for non-maximum suppression")
    stamp_array = prep_nms(result_stamp, SCORE_THRES)

    if stamp_array is not None:
        logging.debug(f"Candidate stamps detected for {str(img)}. Performing non-maximum suppression")
        candidate_boxes, classes, scores = nms(stamp_array, IOU_THRES, rotated=True, out_dict=False)

        inference_metrics = {
            "num_stamps": len(classes),
            "stamp_scores": np.squeeze(np.round(scores.astype(np.single), decimals=5)).reshape(-1),
            "detected_stamp": np.squeeze(np.round(candidate_boxes.astype(np.single), decimals=3)).reshape(-1),
            "Stamp_model_version": str(STAMP_MODEL_VERSION),
        }

    else:
        logging.debug(f"No candidate stamps detected for {str(img)}. Variable SCORE_THRES may need to be reduced")
        logging.debug(f"Compiling and returning inference metrics for {str(img)}")

        inference_metrics = {
            "num_stamps": 0,
            "stamp_scores": np.asarray([-1]),
            "detected_stamp": np.asarray([-1]),
            "Stamp_model_version": str(STAMP_MODEL_VERSION),
        }
        logging.info(f"Inference metrics: {inference_metrics}")
    return inference_metrics
