import nvidia.dali as dali
import nvidia.dali.types as types
from nvidia.dali.plugin.triton import autoserialize

batch_size = 16
max_label_size = 800


@autoserialize
@dali.pipeline_def(batch_size=batch_size, num_threads=1, device_id=0)
def pipe_crop(max_size=max_label_size):
    # Read in the file bytestring and decode
    images = dali.fn.external_source(device="cpu", name="DALI_INPUT_0")
    images = dali.fn.image_decoder(images, device="mixed", output_type=types.RGB)

    M = dali.fn.external_source(device="cpu",
                                name="DALI_INPUT_1")
    dims = dali.fn.external_source(device="cpu",
                                   name="DALI_INPUT_2")

    rotation = dali.fn.external_source(device="cpu",
                                       name="DALI_INPUT_3")

    # if dali.math.floor(image) == 0.0 and dali.math.ceil(image) == 0:
    #     return image, image

    cropped_img = dali.fn.warp_affine(images, matrix=M, size=dims, device='gpu',
                                      interp_type=types.DALIInterpType.INTERP_LINEAR,
                                      fill_value=42, inverse_map=False)

    # rotation = dali.fn.reinterpret(rotation, dtype=dali.types.DALIDataType.FLOAT)
    img = dali.fn.rotate(cropped_img, angle=rotation, device='gpu')

    start_x = 0.5
    start_y = 0.5
    fill = (255, 255, 255)
    img = dali.fn.resize(
                                img,
                                interp_type=types.DALIInterpType.INTERP_LANCZOS3,
                                resize_longer=max_size,
                                device="gpu"
                            )

    img = dali.fn.paste(img, fill_value=fill,
                        ratio=1, min_canvas_size=max_size,
                        paste_x=start_x, paste_y=start_y)

    img = dali.fn.expand_dims(img, axes=0)

    return img
