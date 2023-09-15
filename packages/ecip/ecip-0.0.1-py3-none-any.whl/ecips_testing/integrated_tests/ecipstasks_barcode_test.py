"""
import pickle
import time
from ecips_utils import ecips_config
from ecips_tasks.tasks_barcode import (UserData, completion_callback,
                                       prime_barcode, prime_digits)
from tensorrtserver.api import ProtocolType, InferContext
import os

VERBOSE = ecips_config.ECIPS_INFERENCE_VERBOSE
STREAMING = ecips_config.ECIPS_INFERENCE_STREAMING
BAR_MODEL_VERSION = ecips_config.ECIPS_INFERENCE_BARCODE_VERSION
DIG_MODEL_VERSION = ecips_config.ECIPS_INFERENCE_DIGIT_VERSION
BATCH_SIZE = ecips_config.ECIPS_INFERENCE_BATCH_SIZE
URL = ecips_config.ECIPS_INFERENCE_SERVER_URL
PROTOCOL = ProtocolType.from_str(ecips_config.ECIPS_INFERENCE_SERVER_PROTOCOL)
SLEEP = 5

# callbacks
bar_data = UserData()
digit_data = UserData()

# infer modeling context
ctx_barcode = InferContext(URL, PROTOCOL, "barcode", BAR_MODEL_VERSION, VERBOSE, 0, STREAMING)
ctx_digits = InferContext(URL, PROTOCOL, "digits", DIG_MODEL_VERSION, VERBOSE, 0, STREAMING)


def test_prime_barcode():
    path = os.environ['WORKSPACE'] + '/ecips_testing/ecips_test_files/bar_inference_files/image_data.dat'
    with open(path, "rb") as f:
        image_data = pickle.load(f)

    input_batch = [image_data[0][0]]
    qsize = bar_data._completed_requests.qsize()
    prime_barcode(completion_callback, bar_data, input_batch, BATCH_SIZE, ctx_barcode)

    time.sleep(SLEEP)
    qsize = bar_data._completed_requests.qsize()
    prime_barcode(completion_callback, bar_data, input_batch, BATCH_SIZE, ctx_barcode)
    time.sleep(SLEEP)
    assert bar_data._completed_requests.qsize() != qsize, "no image was added to the queue. Queuing function failed"


def test_prime_digits():
    qsize = digit_data._completed_requests.qsize()

    path = os.environ['WORKSPACE'] + "/ecips_testing/ecips_test_files/bar_inference_files/cropped_batch.dat"
    with open(path, "rb") as f:
        cropped_batch = pickle.load(f)

    prime_digits(completion_callback, digit_data, cropped_batch, BATCH_SIZE, ctx_digits)
    time.sleep(SLEEP)
    assert digit_data._completed_requests.qsize() != qsize, "no image was added to the queue. Queuing function failed"
"""
