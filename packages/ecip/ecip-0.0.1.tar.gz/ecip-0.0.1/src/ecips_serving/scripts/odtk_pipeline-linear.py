import nvidia.dali as dali
import nvidia.dali.types as types


@dali.pipeline_def(batch_size=16, num_threads=1, device_id=0)
def pipe(
    max_size=1280,
    resize_crop=[1280, 1280],
    resize_mean=[255.0 * x for x in [0.485, 0.456, 0.406]],
    resize_std=[255.0 * x for x in [0.229, 0.224, 0.225]],
):
    org_images = dali.fn.external_source(device="cpu", name="DALI_INPUT_0")
    # org_images = dali.fn.decoders.image(org_images, device="mixed", output_type=types.RGB)
    images, attrs_resize = dali.fn.resize(
        org_images,
        # mode="not_larger",
        # size=self.max_size,
        # max_size=self.max_size,
        interp_type=types.DALIInterpType.INTERP_LANCZOS3,
        resize_longer=max_size,
        save_attrs=True,
    )
    stride = 1
    padded_size = max_size + ((stride - max_size % stride) % stride)

    images = dali.fn.paste(
        images,
        fill_value=0,
        ratio=1.1,
        min_canvas_size=padded_size,
        paste_x=0,
        paste_y=0,
    )

    images = dali.fn.crop_mirror_normalize(
        images,
        mean=resize_mean,
        std=resize_std,
        crop=resize_crop,
        crop_pos_x=0,
        crop_pos_y=0,
        fill_values=0,
        out_of_bounds_policy="pad",
        dtype=types.FLOAT,
    )
    max_size = 224
    resize_crop = [224, 224]
    smaller_images, smaller_attrs_resize = dali.fn.resize(
        org_images,
        # mode="not_larger",
        # size=self.max_size,
        # max_size=self.max_size,
        interp_type=types.DALIInterpType.INTERP_LINEAR,
        resize_longer=max_size,
        save_attrs=True,
    )
    stride = 1
    padded_size = max_size + ((stride - max_size % stride) % stride)

    smaller_images = dali.fn.paste(
        smaller_images,
        fill_value=0,
        ratio=1.1,
        min_canvas_size=padded_size,
        paste_x=0,
        paste_y=0,
    )

    smaller_images = dali.fn.crop_mirror_normalize(
        smaller_images,
        mean=resize_mean,
        std=resize_std,
        crop=resize_crop,
        crop_pos_x=0,
        crop_pos_y=0,
        fill_values=0,
        out_of_bounds_policy="pad",
        dtype=types.FLOAT,
    )

    return images, smaller_images, attrs_resize

    # pipe.set_outputs(images, attrs_resize, labels)


# def main(filename):
filename = "./model.dali"
pipe().serialize(filename=filename)


# if __name__ == '__main__':
#    args = parse_args()
#    main(args.file_path)
