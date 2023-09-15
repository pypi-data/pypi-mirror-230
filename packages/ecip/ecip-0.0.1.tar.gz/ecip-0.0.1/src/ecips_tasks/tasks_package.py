from tensorrtserver.api import InferContext, ProtocolType
import logging
from celery import Celery
import numpy as np
from ecips_utils import ecips_config
from ecips_tasks.workflow.validate_models import parse_model
from ecips_tasks.workflow.prepare_data import preprocess
from ecips_tasks.workflow.inference import (UserData,
                                            completion_callback)
from functools import partial


# Create Celery App configs
class CeleryConfig:
    task_serializer = 'pickle'
    result_serializer = 'pickle'
    event_serializer = 'pickle'
    accept_content = ['pickle']


# Create Celery `App` for Tasking
app = Celery('tasks_package', broker=ecips_config.CELERY_BROKER, backend=ecips_config.CELERY_BACKEND)
app.conf.result_expires = 3*60*60
app.config_from_object(CeleryConfig)

# set logs
logging.getLogger(__name__)

# Modeling constants
SCORE_THRES = ecips_config.ECIPS_INFERENCE_PACKAGE_SCORE_THRES
VERBOSE = ecips_config.ECIPS_INFERENCE_VERBOSE
STREAMING = ecips_config.ECIPS_INFERENCE_STREAMING
PACKAGE_MODEL_VERSION = ecips_config.ECIPS_INFERENCE_PACKAGE_VERSION
BATCH_SIZE = ecips_config.ECIPS_INFERENCE_BATCH_SIZE
URL = ecips_config.ECIPS_INFERENCE_SERVER_URL
PROTOCOL = ProtocolType.from_str(ecips_config.ECIPS_INFERENCE_SERVER_PROTOCOL)
PACKAGE_MDL_NAME = ecips_config.ECIPS_INFERENCE_PACKAGE_MODEL_NAME
PACKAGE_MAPPINGS = ecips_config.ECIPS_PACKAGE_MAPPINGS

# Initialize callback
package_data = UserData()

# extract model info.
package_input_name, package_c, package_h, package_w, package_format, package_dtype = parse_model(
    URL, PROTOCOL, PACKAGE_MDL_NAME,
    BATCH_SIZE, VERBOSE)

# infer modeling context
ctx_package = InferContext(URL, PROTOCOL, PACKAGE_MDL_NAME, PACKAGE_MODEL_VERSION, VERBOSE, 0, STREAMING)


@app.task
def detect_package(img):
    """
    This function utilizes the UDF's defined in workflow to detect packages contained in a given image (if any).

    Input:
        img - image to process
    Output:
        inference_metrics - results from detecting packages in the image
    """

    logging.debug(f"Starting package detection for {img}")
    try:
        logging.debug(f"Attempting image preprocessing for {img}")
        image_data = [preprocess(img, package_dtype, package_w, package_h)]
    except Exception:
        logging.error(f"Image preprocessing for {img} failed. Image file may be corrupt")
        raise Exception("Image preprocessing failed and image was not None type")

    logging.debug(f"Preparing inference parameters for {img}")
    input_batch = [image_data[0][0]]

    logging.debug(f"Priming package queue for {img}")
    ctx_package.async_run(partial(completion_callback, package_data),
                          {package_input_name: [input_batch[0][0]]},
                          {
                            'output': (InferContext.ResultFormat.RAW)
                          },
                          BATCH_SIZE)

    logging.debug(f"Getting package detection results gpt {img}")
    (request_id_package) = package_data._completed_requests.get()
    result_package = ctx_package.get_async_run_results(request_id_package)

    index = np.argmax(result_package['output'][0])
    package = PACKAGE_MAPPINGS[index]
    scores = result_package['output'][0]
    scores = max(np.exp(scores) / sum(np.exp(scores)))

    logging.debug(f"Compiling and returning inference metrics fpr {img}")
    inference_metrics = {
      "package": package,
      "package_score": scores,
      "Package_model_version": str(PACKAGE_MODEL_VERSION)
    }
    logging.info(f"Inference metrics for {img}:"
                 f"package: {package}"
                 f"package_score: {scores}"
                 f"package_model_version: {str(PACKAGE_MODEL_VERSION)}"
                 )
    return inference_metrics
