import nvidia.dali as dali
from nvidia.dali.plugin.triton import autoserialize
import nvidia.dali.types as types

MODEL_OD_YOLO_1280 = 1280  # pixels
MODEL_OD_YOLO_896 = 896  # pixels
RESIZE_MEAN_YOLO = [0.0, 0.0, 0.0]
RESIZE_STD_YOLO = [255. * x for x in [1.0, 1.0, 1.0]]
DTYPE_YOLO = types.FLOAT16
STRIDE_YOLO = 32  # pixels

BATCH_SIZE = 1


def resize_pipeline(images, max_size):
    images, attrs_resize = dali.fn.resize(
        images,
        interp_type=types.INTERP_LINEAR,
        resize_longer=max_size,
        save_attrs=True,
        device="gpu"
    )
    return images, attrs_resize


def pad_paste_pipeline(images, resize_crop,
                       resize_mean, resize_std, output_type,
                       min_canvas_size, ratio=1.1,
                       start_x=0, start_y=0, fill_value=0
                       ):

    images = dali.fn.paste(images, fill_value=fill_value,
                           ratio=ratio, min_canvas_size=min_canvas_size,
                           paste_x=start_x, paste_y=start_y)/255
    images = dali.fn.cast(images, dtype=output_type)
    images = dali.fn.transpose(images, perm=[2, 0, 1])
    # images = dali.fn.crop_mirror_normalize(images,
    #                                        mean=resize_mean,
    #                                        std=resize_std,
    #                                        crop=resize_crop,
    #                                        crop_pos_x=0,
    #                                        crop_pos_y=0,
    #                                        fill_values=0,
    #                                        out_of_bounds_policy='pad',
    #                                        dtype=output_type)

    return images


# Combines the dali_resize_gpu and dali_preprocessing_yolo models
@autoserialize
@dali.pipeline_def(batch_size=BATCH_SIZE, num_threads=1, device_id=0)
def pipe():
    # 1280x1280 Model (Shipping label)
    max_size_yolo_1280 = MODEL_OD_YOLO_1280
    resize_crop_yolo_1280 = [MODEL_OD_YOLO_1280, MODEL_OD_YOLO_1280]
    # 896x896 Model (hazmat)
    max_size_yolo_896 = MODEL_OD_YOLO_896
    resize_crop_yolo_896 = [MODEL_OD_YOLO_896, MODEL_OD_YOLO_896]

    # Read in the file bytestring and decode
    # images = dali.fn.external_source(device="cpu", name="DALI_INPUT_0")
    # images = dali.fn.image_decoder(images, device="cpu", output_type=types.RGB)
    images = dali.fn.external_source(device="gpu", name="DALI_INPUT_0")
    images = dali.fn.color_space_conversion(images, image_type=types.GRAY, output_type=types.RGB)

    # Resize both the retina and yolo images to different sizes
    images_yolo_1280, attrs_resize = resize_pipeline(images, max_size_yolo_1280)
    images_yolo_896, _ = resize_pipeline(images, max_size_yolo_896)

    # Pad and Paste both retina and yolo models
    start_x = 0.5
    start_y = 0.5
    fill = (114, 114, 114)
    images_yolo_1280 = pad_paste_pipeline(images_yolo_1280, resize_crop=resize_crop_yolo_1280,
                                          resize_mean=RESIZE_MEAN_YOLO, resize_std=RESIZE_STD_YOLO,
                                          min_canvas_size=max_size_yolo_1280, fill_value=fill, ratio=1,
                                          output_type=DTYPE_YOLO, start_x=start_x, start_y=start_y)

    images_yolo_896 = pad_paste_pipeline(images_yolo_896, resize_crop=resize_crop_yolo_896,
                                         resize_mean=RESIZE_MEAN_YOLO, resize_std=RESIZE_STD_YOLO,
                                         min_canvas_size=max_size_yolo_896, fill_value=fill, ratio=1,
                                         output_type=DTYPE_YOLO, start_x=start_x, start_y=start_y)

    return images_yolo_1280, images_yolo_896, attrs_resize
