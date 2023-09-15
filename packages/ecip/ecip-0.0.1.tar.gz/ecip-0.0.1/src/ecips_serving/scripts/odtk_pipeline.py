import nvidia.dali as dali
import nvidia.dali.types as types


def createIngestPipeline_Dali(
    file_name="/home/lindenbaumde/ecip_informed_address_application/ia_serving/models/preprocessdali/3/model.dali",
    export=True,
):
    pipe = dali.pipeline.Pipeline(batch_size=1, num_threads=2, device_id=0)
    # export = False
    with pipe:
        # def pipe(eii=ExternalInputIterator(batch_size=16, fileList=fileList),
        resize_crop = [1920, 1920]
        resize_mean = [255.0 * x for x in [0.485, 0.456, 0.406]]
        resize_std = [255.0 * x for x in [0.229, 0.224, 0.225]]
        max_size = 1920
        images = dali.fn.external_source(device="cpu", name="DALI_INPUT_0")
        images = dali.fn.image_decoder(images, device="mixed", output_type=types.RGB)
        images, attrs_resize = dali.fn.resize(
            images,
            # mode="not_larger",
            # size=self.max_size,
            # max_size=self.max_size,
            interp_type=types.DALIInterpType.INTERP_CUBIC,
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
            crop_pos_x=0.0,
            crop_pos_y=0.0,
            fill_values=0.0,
            out_of_bounds_policy="pad",
        )

        pipe.set_outputs(images, attrs_resize)
        pipe.serialize(filename=file_name)


if __name__ == "__main__":
    createIngestPipeline_Dali(
        file_name="/home/lindenbaumde/ecip_informed_address_application/ia_serving/models/preprocessdali/3/model.dali",
        export=True,
    )
