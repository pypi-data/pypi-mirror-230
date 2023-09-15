import argparse
import math
import os.path

import numpy as np
import json
import csv
from PIL import Image
import time
from tqdm import tqdm
import tritonclient.grpc as grpcclient
import tritonclient.http as httpclient

# The human-readable class names for hazmat detections
HAZMAT_CLASS_MAP = {1: 'Lithium_UN_Label',
                    2: 'Lithium__Class_9',
                    4: 'Biohazard',
                    5: 'No_Fly',
                    7: 'Finger_Large',
                    8: 'Cargo_Air_Only',
                    8: 'Suspected_Label',
                    16: 'Hazmat_Surface_Only',
                    27: 'Cremated_Remains'}


def ensemble_model_hazmat_grpc(image_filepath, url="localhost:8001"):
    """ The ensemble_model_hazmat function returns the results from the hazmat model. Including detected scores,
        hazmat class ids and locations of detected hazmats.
        Args:
            image_filepath (str): The filepath to the test image
            url (str): the url where the grpc inference service is present. By default it is set to port 8001
        Returns:
            scores (np.array): The confidence scores of the detected hazmat label.  Only scores greater
                                than the threshold of 0.9 are returned. Of shape (x, 1), where x is the
                                number of hazmat detections.
            boxes (np.array): The location of the bounding boxes for a detected hazmat label. Of shape (x, 4),
                                where x is the number of hazmat detections.  The 4 item array is of form x1, y1, x2, y2
            classes (np.array): The class ID of the detected hazmat label.  Of shape (x, 1), where x is the number
                                of hazmat detections.
            """
    # Reading in the image buffer to a np array
    with open(image_filepath, 'rb') as f:
        file_bytestring = np.frombuffer(f.read(), dtype=np.uint8)
        file_bytestring = np.expand_dims(file_bytestring, axis=0)

    with grpcclient.InferenceServerClient(url) as client:
        # Defining the input tensor name, shape and type
        input_name = "IMAGE_BYTESTRING"
        dtype = "UINT8"
        input0 = grpcclient.InferInput(input_name, file_bytestring.shape, dtype)

        # Set the input value
        input0.set_data_from_numpy(file_bytestring)

        # Define the expected output tenosr names
        output0 = grpcclient.InferRequestedOutput("processed_hazmat_scores")
        output1 = grpcclient.InferRequestedOutput("processed_hazmat_boxes")
        output2 = grpcclient.InferRequestedOutput("processed_hazmat_classes")

        input_list = [input0]
        output_list = [output0, output1, output2]

        response = client.infer(
            "ensemble_model_hazmat", input_list, outputs=output_list, client_timeout=5.0
        )

        # Extracting the scores, boxes and classes from the hazmat detection.
        scores = response.as_numpy("processed_hazmat_scores")[0]
        boxes = response.as_numpy("processed_hazmat_boxes")[0]
        classes = response.as_numpy("processed_hazmat_classes")[0]

        return scores, boxes, classes


def ensemble_model_hazmat_http(image_filepath, url="localhost:8000"):
    """ The ensemble_model_hazmat function returns the results from the hazmat model. Including detected scores,
        hazmat class ids and locations of detected hazmats.
        Args:
            image_filepath (str): The filepath to the test image
            url (str): the url where the grpc inference service is present. By default it is set to port 8001
        Returns:
            scores (np.array): The confidence scores of the detected hazmat label.  Only scores greater
                                than the threshold of 0.9 are returned. Of shape (x, 1), where x is the
                                number of hazmat detections.
            boxes (np.array): The location of the bounding boxes for a detected hazmat label. Of shape (x, 4),
                                where x is the number of hazmat detections.  The 4 item array is of form x1, y1, x2, y2
            classes (np.array): The class ID of the detected hazmat label.  Of shape (x, 1), where x is the number
                                of hazmat detections.
            """
    # Reading in the image buffer to a np array
    with open(image_filepath, 'rb') as f:
        file_bytestring = np.frombuffer(f.read(), dtype=np.uint8)
        file_bytestring = np.expand_dims(file_bytestring, axis=0)

    with httpclient.InferenceServerClient(url) as client:
        # Defining the input tensor name, shape and type
        input_name = "IMAGE_BYTESTRING"
        dtype = "UINT8"
        input0 = httpclient.InferInput(input_name, file_bytestring.shape, dtype)

        # Set the input value
        input0.set_data_from_numpy(file_bytestring)

        # Define the expected output tenosr names
        output0 = httpclient.InferRequestedOutput("processed_hazmat_scores")
        output1 = httpclient.InferRequestedOutput("processed_hazmat_boxes")
        output2 = httpclient.InferRequestedOutput("processed_hazmat_classes")

        input_list = [input0]
        output_list = [output0, output1, output2]

        response = client.infer(
            "ensemble_model_hazmat", input_list, outputs=output_list
        )

        # Extracting the scores, boxes and classes from the hazmat detection.
        scores = response.as_numpy("processed_hazmat_scores")[0]
        boxes = response.as_numpy("processed_hazmat_boxes")[0]
        classes = response.as_numpy("processed_hazmat_classes")[0]

        return scores, boxes, classes


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filepath", help="Path to the image file containing a hazmat image")
    parser.add_argument("-o", "--output", help="Path to json file that will be written out", default=None)
    parser.add_argument("-csv", "--csv_output", help="Path to output CSV", default=None)
    parser.add_argument("-t", "--testing", help="Bool, test the same image 500 times and print size/time metrics",
                        default=False)
    parser.add_argument("-u", "--url", help="The url where the GRPCInferenceService is present",
                        default="56.72.40.42:8002")
    parser.add_argument("-p", "--protocol", help="The protocol to use (http or grpc)",
                        default="grpc")

    args = parser.parse_args()
    filepath = args.filepath
    output_json = args.output
    url = args.url
    protocol = args.protocol
    time_test = args.testing

    # Grab the results from the ensemble
    if time_test:
        test_num = 50
    else:
        test_num = 1

    img = Image.open(filepath)
    print(f"Testing the following image, {filepath} with dimensions {img.size} {test_num} times")
    proc_time = np.zeros((test_num))
    for i in tqdm(range(test_num)):
        start_time = time.time()
        if protocol == "grpc":
            scores, boxes, classes = ensemble_model_hazmat_grpc(filepath, url)
        elif protocol == "http":
            scores, boxes, classes = ensemble_model_hazmat_http(filepath, url)
        else:
            raise ValueError("Protocol (-p) must be either 'gprc' or 'http'")
        proc_time[i] = time.time() - start_time
    print(f"Testing took an average of {np.mean(proc_time)} per image")

    if -1 not in scores:
        # If a positive hazmat detection is made
        class_names = [HAZMAT_CLASS_MAP[int(class_id)] for class_id in classes]

        hazmat_results_dict = {"scores": scores.tolist(),
                               "class_names": class_names,
                               "class_ids": classes.tolist(),
                               "boxes": boxes.tolist()}
        print(f"Hazmat Results for image {filepath}: \n"
              f"{hazmat_results_dict}")

        # Write the dict to .json
        if output_json is not None:
            with open(output_json, "w") as json_out:
                json.dump(hazmat_results_dict, json_out)

    else:
        # -1 present in the results.  When no hazmat detections are present,
        # All results are -1.
        print(f"No Hazmat Results for image {filepath}: \n")

    csv_output = args.csv_output
    if csv_output:
        # Does the file exist?
        num_hazmats = 0 if -1 in scores else len(scores)
        data = [filepath, np.mean(proc_time), np.std(proc_time), img.size[0], img.size[1], img.size[0] * img.size[1],
                math.sqrt(img.size[0] * img.size[1]), num_hazmats]

        if not os.path.exists(csv_output):
            # write the entry
            header = ["filename", "avg_proc (ms)", "stdev proc (ms)", "width (pixels)", "height (pixels)",
                      "total pixels (pix2)", "sq pixels", "num_hazmats"]

            with open(csv_output, 'w') as file:
                writer = csv.writer(file)
                writer.writerow(header)

                writer.writerow(data)
        else:
            # write the header and 1st entry
            with open(csv_output, 'a') as file:
                writer = csv.writer(file)
                writer.writerow(data)
