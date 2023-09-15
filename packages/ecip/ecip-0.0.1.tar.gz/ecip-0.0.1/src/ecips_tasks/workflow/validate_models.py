from tensorrtserver.api import ServerStatusContext
import tensorrtserver.api.model_config_pb2 as model_config
import numpy as np


def model_dtype_to_np(model_dtype):
    if model_dtype == model_config.TYPE_BOOL:
        return np.bool
    elif model_dtype == model_config.TYPE_INT8:
        return np.int8
    elif model_dtype == model_config.TYPE_INT16:
        return np.int16
    elif model_dtype == model_config.TYPE_INT32:
        return np.int32
    elif model_dtype == model_config.TYPE_INT64:
        return np.int64
    elif model_dtype == model_config.TYPE_UINT8:
        return np.uint8
    elif model_dtype == model_config.TYPE_UINT16:
        return np.uint16
    elif model_dtype == model_config.TYPE_FP16:
        return np.float16
    elif model_dtype == model_config.TYPE_FP32:
        return np.float32
    elif model_dtype == model_config.TYPE_FP64:
        return np.float64
    elif model_dtype == model_config.TYPE_STRING:
        return np.dtype(object)
    return None


def parse_model(url, protocol, model_name, batch_size, verbose=False):
    """
    Check the configuration of a model to make sure it meets the
    requirements for an image classification network (as expected by
    this client)
    """
    ctx = ServerStatusContext(url, protocol, model_name, verbose)
    server_status = ctx.get_server_status()

    if model_name not in server_status.model_status:
        raise Exception("unable to get status for '" + model_name + "'")

    status = server_status.model_status[model_name]
    config = status.config

    input = config.input[0]

    max_batch_size = config.max_batch_size

    if max_batch_size == 0:
        if batch_size != 1:
            raise Exception("batching not supported for model '" + model_name + "'")
    else:  # max_batch_size > 0
        if batch_size > max_batch_size:
            raise Exception("expecting batch size <= {} for model {}".format(max_batch_size, model_name))

    # Variable-size dimensions are not currently supported.
    for dim in input.dims:
        if dim == -1:
            raise Exception("variable-size dimension in model input not supported")

    # TODO look into why the stamp model returns dimensions of length 3
    if len(input.dims) == 4:
        c = input.dims[1]
        h = input.dims[2]
        w = input.dims[3]

    else:
        c = input.dims[0]
        h = input.dims[1]
        w = input.dims[2]

    return (input.name, c, h, w, input.format, model_dtype_to_np(input.data_type))
