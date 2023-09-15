import nvidia.dali as dali
from nvidia.dali.plugin.triton import autoserialize
import nvidia.dali.types as types

MODEL_OD_YOLO_640 = 640  # pixels
MODEL_OD_YOLO_896 = 896  # pixels
RESIZE_MEAN_YOLO = [0.0, 0.0, 0.0]
RESIZE_STD_YOLO = [255. * x for x in [1.0, 1.0, 1.0]]
DTYPE_YOLO = types.FLOAT16
STRIDE_YOLO = 32  # pixels

BATCH_SIZE = 1


@autoserialize
@dali.pipeline_def(batch_size=BATCH_SIZE, num_threads=1, device_id=0)
def pipe():
    # 896x896 Model (hazmat)
    max_size_yolo_896 = MODEL_OD_YOLO_896

    # Read in the file bytestring and decode
    images = dali.fn.external_source(device="gpu", name="DALI_INPUT_0")
    images = dali.fn.color_space_conversion(images, image_type=types.GRAY, output_type=types.RGB)

    # Resize yolo images to different size
    images_yolo_896, attrs_resize = resize_pipeline(images, max_size_yolo_896)

    # Pad and Paste yolo model
    start_x = 0.5
    start_y = 0.5
    fill = (114, 114, 114)

    images_yolo_896 = pad_paste_pipeline(images_yolo_896, min_canvas_size=max_size_yolo_896, fill_value=fill, ratio=1,
                                         output_type=DTYPE_YOLO, start_x=start_x, start_y=start_y)

    return images_yolo_896, attrs_resize


def resize_pipeline(images, max_size):
    images, attrs_resize = dali.fn.resize(
        images,
        interp_type=types.INTERP_LINEAR,
        resize_longer=max_size,
        save_attrs=True,
        device="gpu"
    )
    return images, attrs_resize


def pad_paste_pipeline(images, output_type,
                       min_canvas_size, ratio=1.1,
                       start_x=0, start_y=0, fill_value=0
                       ):

    images = dali.fn.paste(images, fill_value=fill_value,
                           ratio=ratio, min_canvas_size=min_canvas_size,
                           paste_x=start_x, paste_y=start_y)/255
    images = dali.fn.cast(images, dtype=output_type)
    images = dali.fn.transpose(images, perm=[2, 0, 1])

    return images
