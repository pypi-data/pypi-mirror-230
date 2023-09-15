import nvidia.dali as dali
from nvidia.dali.plugin.triton import autoserialize
import nvidia.dali.types as types

BATCH_SIZE = 1


# Combines the dali_resize_gpu and dali_preprocessing_yolo models
@autoserialize
@dali.pipeline_def(batch_size=BATCH_SIZE, num_threads=1, device_id=0)
def pipe():

    # Read in the file bytestring and decode
    images = dali.fn.external_source(device="cpu", name="DALI_INPUT_0")
    images = dali.fn.image_decoder(images, device="mixed", output_type=types.GRAY)

    images = dali.fn.expand_dims(images, axes=2)

    return images
