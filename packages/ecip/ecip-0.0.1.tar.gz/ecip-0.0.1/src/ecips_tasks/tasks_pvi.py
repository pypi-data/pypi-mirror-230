from tensorrtserver.api import InferContext, ProtocolType
import logging
from celery import Celery
import numpy as np
from functools import partial
from ecips_utils import ecips_config
from ecips_tasks.workflow.validate_models import parse_model
from ecips_tasks.workflow.prepare_data import preprocess
from ecips_tasks.workflow.inference import (UserData,
                                            completion_callback)


# Create Celery tasking config
class CeleryConfig:
    task_serializer = 'pickle'
    result_serializer = 'pickle'
    event_serializer = 'pickle'
    accept_content = ['pickle']
    result_accept_content = ['pickle']


# Create Celery `App` for Tasking
# Create Celery `App` for Tasking
app = Celery('tasks_pvi', broker=ecips_config.CELERY_BROKER, backend=ecips_config.CELERY_BACKEND)
app.conf.result_expires = 3*60*60
app.config_from_object(CeleryConfig)

# Modeling constants
VERBOSE = ecips_config.ECIPS_INFERENCE_VERBOSE
STREAMING = ecips_config.ECIPS_INFERENCE_STREAMING
PVI_MODEL_VERSION = ecips_config.ECIPS_INFERENCE_PVI_VERSION
BATCH_SIZE = ecips_config.ECIPS_INFERENCE_BATCH_SIZE
URL = ecips_config.ECIPS_INFERENCE_SERVER_URL
PROTOCOL = ProtocolType.from_str(ecips_config.ECIPS_INFERENCE_SERVER_PROTOCOL)
PVI_MDL_NAME = ecips_config.ECIPS_INFERENCE_PVI_MODEL_NAME
BATCH_SIZE = 1
IOU_THRES = ecips_config.ECIPS_INFERENCE_IOU_THRES
SCORE_THRES = ecips_config.ECIPS_INFERENCE_SCORE_THRES

# Initialize callback
pvi_data = UserData()

# extract model info.
pvi_input_name, pvi_c, pvi_h, pvi_w, pvi_format, pvi_dtype = parse_model(
    URL, PROTOCOL, PVI_MDL_NAME,
    BATCH_SIZE, VERBOSE)

# infer modeling context
ctx_pvi = InferContext(URL, PROTOCOL, PVI_MDL_NAME, PVI_MODEL_VERSION, VERBOSE, 0, STREAMING)


@app.task
def detect_pvi(img):
    """
    This function utilizes the UDF's defined in workflow to detect pvi on a given image.

    Input:
        img - image to process
    Output:
        inference_metrics - results from detecting pvi
    """

    logging.debug(f"Starting pvi detection for {str(img)}")
    try:
        logging.debug(f"Attempting image preprocessing for {str(img)}")
        image_data = [preprocess(img, pvi_dtype, pvi_w, pvi_h)]
    except Exception:
        logging.error(f"Image preprocessing for {str(img)} has failed. Image file may be corrupt")
        raise Exception("Image preprocessing failed and image was not None type")

    logging.debug(f"Preparing inference parameters for {str(img)}")
    input_batch = [image_data[0][0]]

    logging.debug(f"Priming pvi queue for {str(img)}")
    ctx_pvi.async_run(partial(completion_callback, pvi_data),
                      {pvi_input_name: [input_batch[0][0]]},
                      {
                        'score_5': (InferContext.ResultFormat.RAW),
                        'box_5': (InferContext.ResultFormat.RAW)
                      },
                      BATCH_SIZE)

    logging.debug(f"Getting pvi detection results for {str(img)}")
    (request_id_pvi) = pvi_data._completed_requests.get()
    result_pvi = ctx_pvi.get_async_run_results(request_id_pvi)
    '''
    # review below portion when testing code
    logging.debug("Beginning pvi post processing procedure")
    logging.debug("Preparing pvi data for non-maxmum suppression")
    pvi_array = prep_nms(result_pvi, SCORE_THRES)

    if pvi_array is not None:
        logging.debug("Candidate pvi detected performing non-maximum suppression")
        candidate_boxes, classes, scores = nms(pvi_array, IOU_THRES, rotated=True, out_dict=False)

        inference_metrics = {
            "pvi": classes.tolist(),
            "pvi_scores": scores.tolist(),
            "detected_pvi": candidate_boxes.tobytes().hex(),
            "PVI_model_version": str(PVI_MODEL_VERSION),
        }

    else:
        logging.debug("No pvi detected")
        logging.debug("Compiling and returning inference metrics")

        inference_metrics = {
            "pvi": '',
            "pvi_scores": '',
            "detected_pvi": '',
            "PVI_model_version": str(PVI_MODEL_VERSION),
        }
    '''
    inference_metrics = {
            "pvi": '',
            "pvi_scores": np.round(result_pvi['score_5'][0].astype(np.single), decimals=5),
            "detected_pvi": np.round(result_pvi['box_5'][0].astype(np.single), decimals=3),
            "PVI_model_version": str(PVI_MODEL_VERSION)
    }
    return inference_metrics
