from tensorrtserver.api import InferContext
from functools import partial
import sys
if sys.version_info >= (3, 0):
    import queue
else:
    import Queue as queue


class UserData:
    def __init__(self):
        self._completed_requests = queue.Queue()


# Callback function used for async_run()
def completion_callback(user_data, infer_ctx, request_id):
    user_data._completed_requests.put((request_id))


def prime_model_queue(completion_callback, model_queue, model_data,
                      batch_size, ctx_model, model_input_name):
    """
    This function primes a specific models' queue with images to run inference on.
    """
    ctx_model.async_run(partial(completion_callback, model_queue),
                        {model_input_name: model_data},
                        {
                            'scores': (InferContext.ResultFormat.RAW),
                            'boxes': (InferContext.ResultFormat.RAW),
                            'classes': (InferContext.ResultFormat.RAW)
                        },
                        batch_size)
