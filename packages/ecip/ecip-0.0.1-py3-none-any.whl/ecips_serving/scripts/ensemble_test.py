import argparse
import glob
import os
import random
import sys
import time

import numpy as np
import tritonclient.http as httpclient


def load_image(img_path: str):
    """
    Loads an encoded image as an array of bytes.
    This is a typical approach you'd like to use in DALI backend.
    DALI performs image decoding, therefore this way the processing
    can be fully offloaded to the GPU.
    """
    input1 = np.frombuffer(open(img_path, "rb").read(), dtype=np.uint8)
    # filenameList.append(fileName)
    inputarray = np.stack([input1], axis=0)
    return inputarray


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        required=False,
        default=False,
        help="Enable verbose output",
    )
    parser.add_argument(
        "-u",
        "--url",
        type=str,
        required=False,
        default="localhost:8000",
        help="Inference server URL. Default is localhost:8000.",
    )
    parser.add_argument(
        "-f", "--folder", type=str, required=True, help="Folder with Inference Pictures"
    )
    parser.add_argument(
        "-n",
        "--number",
        type=int,
        required=False,
        default=10,
        help="Number of Inference Requests to Send",
    )

    FLAGS = parser.parse_args()

    request_count = int(FLAGS.number)
    try:
        # Need to specify large enough concurrency to issue all the
        # inference requests to the server in parallel.
        triton_client = httpclient.InferenceServerClient(
            url=FLAGS.url, verbose=FLAGS.verbose
        )
    except Exception as e:
        print("context creation failed: " + str(e))
        sys.exit()

    model_name = "ensemble_model"
    inference_files = list(glob.glob(os.path.join(FLAGS.folder, "*.tif")))

    start = time.time()
    for _ in range(request_count):
        inputs = []
        outputs = []
        file_selection = random.choice(inference_files)
        image_data = load_image(file_selection)
        inputs.append(httpclient.InferInput("IMAGE", image_data.shape, "UINT8"))
        # Initialize the data
        inputs[0].set_data_from_numpy(image_data)
        # outputs.append(httpclient.InferRequestedOutput('boxes'))
        # outputs.append(httpclient.InferRequestedOutput('scores'))
        # outputs.append(httpclient.InferRequestedOutput('classes'))

        outputs.append(httpclient.InferRequestedOutput("STAMP_SCORES"))
        outputs.append(httpclient.InferRequestedOutput("STAMP_BOXES"))
        outputs.append(httpclient.InferRequestedOutput("STAMP_CLASSES"))
        outputs.append(httpclient.InferRequestedOutput("BARCODE_SCORES"))
        outputs.append(httpclient.InferRequestedOutput("BARCODE_BOXES"))
        outputs.append(httpclient.InferRequestedOutput("BARCODE_CLASSES"))
        outputs.append(httpclient.InferRequestedOutput("DIGIT_SCORES"))
        outputs.append(httpclient.InferRequestedOutput("DIGIT_BOXES"))
        outputs.append(httpclient.InferRequestedOutput("DIGIT_CLASSES"))
        outputs.append(httpclient.InferRequestedOutput("PVI_SCORE"))
        outputs.append(httpclient.InferRequestedOutput("PVI_BOX"))
        outputs.append(httpclient.InferRequestedOutput("PACKAGES_OUTPUT"))
        # outputs.append(httpclient.InferRequestedOutput('DALI_OUTPUT_0'))
        # outputs.append(httpclient.InferRequestedOutput('DALI_OUTPUT_1'))
        # outputs.append(httpclient.InferRequestedOutput('DALI_OUTPUT_2'))
        # outputs.append(httpclient.InferRequestedOutput('DALI_OUTPUT_3'))
        results = triton_client.infer(model_name, inputs, outputs=outputs)
        # im = Image.fromarray(results.as_numpy("DALI_OUTPUT_0")[0][0])
        # im.save("your_file.tiff")
    end = time.time()
    print(f"{request_count} infrences took {end - start} seconds")
