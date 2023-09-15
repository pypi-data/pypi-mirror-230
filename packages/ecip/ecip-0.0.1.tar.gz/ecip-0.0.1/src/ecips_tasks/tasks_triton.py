import logging
import time

import numpy as np
import tritonclient.grpc as grpcclient
import tritonclient.http as httpclient
from PIL import Image
import ast
from celery import Celery

from ecips_tasks.workflow.prepare_data import process_odtk_results
# from ecips_tasks.workflow.validate_results import validate_barcode
from ecips_utils import ecips_config

# set logs
logging.getLogger(__name__)

BAR_MODEL_VERSION = ecips_config.ECIPS_INFERENCE_BARCODE_VERSION
DIG_MODEL_VERSION = ecips_config.ECIPS_INFERENCE_DIGIT_VERSION
PACKAGE_MODEL_VERSION = ecips_config.ECIPS_INFERENCE_PACKAGE_VERSION
STAMP_MODEL_VERSION = ecips_config.ECIPS_INFERENCE_STAMP_MODEL_NAME
HAZMAT_MODEL_VERSION = ecips_config.ECIPS_INFERENCE_HAZMAT_VERSION  # we added this to utils
YOLO_MODEL_VERSION = ecips_config.ECIPS_INFERENCE_YOLO_VERSION
URL = ecips_config.ECIPS_INFERENCE_SERVER_URL
SCORE_THRES = ecips_config.ECIPS_INFERENCE_SCORE_THRES
IOU_THRES = ecips_config.ECIPS_INFERENCE_IOU_THRES
PVI_MODEL_VERSION = ecips_config.ECIPS_INFERENCE_PVI_VERSION
PACKAGE_MAPPINGS = ecips_config.ECIPS_PACKAGE_MAPPINGS
ECIPS_HAZMAT_MAPPINGS = ecips_config.ECIPS_HAZMAT_MAPPINGS
ECIPS_YOLO_HAZMAT_MAPPINGS = ecips_config.ECIPS_YOLO_HAZMAT_MAPPINGS
ECIPS_HAZMAT_INVALID_ID_DICT = ecips_config.ECIPS_HAZMAT_INVALID_ID_DICT
ECIPS_HAZMAT_YOLO_INVALID_ID_DICT = ecips_config.ECIPS_HAZMAT_YOLO_INVALID_ID_DICT
MIN_WIDTH = ecips_config.MIN_IMG_WIDTH
MIN_HEIGHT = ecips_config.MIN_IMG_HEIGHT
PVI_MAPPINGS = ecips_config.ECIPS_PVI_MAPPINGS
BARCODE_MAPPINGS = ecips_config.ECIPS_BARCODE_MAPPINGS


# Create Celery tasking config
class CeleryConfig:
    task_serializer = "pickle"
    result_serializer = "pickle"
    event_serializer = "pickle"
    accept_content = ["pickle"]
    result_accept_content = ["pickle"]


# Create Celery `App` for Tasking
app = Celery(
    "tasks_triton",
    broker=ecips_config.CELERY_BROKER,
    backend=ecips_config.CELERY_BACKEND,
)
app.conf.result_expires = 3 * 60 * 60
app.config_from_object(CeleryConfig)

TRITON_CLIENT = httpclient.InferenceServerClient(url=URL)


@app.task
def run_ensemble(img_filepath, triton_client=TRITON_CLIENT):
    """
    Parameters:
    img_filepath: an img created by OpenCV imread Function

    """
    logging.debug(f"Running ensemble model on {img_filepath} for {triton_client}. Starting inference.")
    MODEL_NAME = "ensemble_model"

    inputs = []
    outputs = []

    # Reading the data
    input1 = np.frombuffer(open(img_filepath, "rb").read(), dtype=np.uint8)
    inputarray = np.stack([input1], axis=0)

    inputs.append(httpclient.InferInput("IMAGE", inputarray.shape, "UINT8"))

    inputs[0].set_data_from_numpy(inputarray)

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
    start = time.time()
    results = triton_client.infer(MODEL_NAME, inputs, outputs=outputs)
    end = time.time()
    logging.info(f"Inference took {end - start} seconds")
    return results


def run_ensemble_grpc_filename(
    model_input, model_name="ensemble_model_ecip", url="ecips_serving:8001"
):
    if model_name == 'ensemble_model_ecip':
        img_filepath = model_input
        # We do not want to process images that are too small to be packages
        w, h = Image.open(img_filepath).size
        assert (w > MIN_WIDTH) and (h > MIN_HEIGHT), f"Image is too small. Actual dimensions: ({w}, {h}), " \
                                                     f"Min required dimensions ({MIN_WIDTH}, {MIN_HEIGHT})"

        with open(img_filepath, 'rb') as f:
            triton_input = np.frombuffer(f.read(), dtype=np.uint8)

    if model_name == 'shipping_label_ocr':
        # We do not want to process images that are too small to be packages
        img_filepath, scores, boxes, classes = model_input

        with open(img_filepath, 'rb') as f:
            img_filepath = np.frombuffer(f.read(), dtype=np.uint8)

        triton_input = [img_filepath, scores, boxes, classes]

    return run_ensemble_grpc(triton_input, model_name=model_name, url=url)


def run_ensemble_grpc(
    input1, model_name="ensemble_model_ecip", url="ecips_serving:8001"
):
    """
    Parameters:
    img_filepath: an img created by OpenCV imread Function

    """
    logging.debug(f"Starting Inference for {str(input1)} with {model_name}")

    if model_name == 'ensemble_model_ecip':
        # Resize for batch dimension
        input1 = np.expand_dims(input1, axis=0)

        with grpcclient.InferenceServerClient(url=url) as triton_client:
            input0 = grpcclient.InferInput("IMAGE_BYTESTRING", input1.shape, "UINT8")
            input0.set_data_from_numpy(input1)
            input_list = [input0]

            # output0 = grpcclient.InferRequestedOutput("ATTRS_RESIZE")
            # output1 = grpcclient.InferRequestedOutput("HAZMAT_SCORES")
            output2 = grpcclient.InferRequestedOutput("YOLO_SCORES")
            output3 = grpcclient.InferRequestedOutput("YOLO_BOXES")
            output4 = grpcclient.InferRequestedOutput("YOLO_CLASSES")
            # output5 = grpcclient.InferRequestedOutput("STAMP_SCORES")
            # output6 = grpcclient.InferRequestedOutput("STAMP_BOXES")
            # output7 = grpcclient.InferRequestedOutput("STAMP_CLASSES")
            # output8 = grpcclient.InferRequestedOutput("HAZMAT_BOXES")
            # output9 = grpcclient.InferRequestedOutput("HAZMAT_CLASSES")
            output10 = grpcclient.InferRequestedOutput("HAZMAT_YOLO_SCORES")
            output11 = grpcclient.InferRequestedOutput("HAZMAT_YOLO_BOXES")
            output12 = grpcclient.InferRequestedOutput("HAZMAT_YOLO_CLASSES")
            output13 = grpcclient.InferRequestedOutput("CUDA_SIFT_DESCRIPTORS")

            output_list = [output2, output3, output4,
                           output10, output11, output12, output13]

            start = time.time()
            response = triton_client.infer(
                model_name, input_list, request_id=str("1"), outputs=output_list,
                client_timeout=ecips_config.ECIPS_INFERENCE_TIMEOUT
            )
            end = time.time()
            response_dict = {"YOLO_SCORES_OUT": response.as_numpy("YOLO_SCORES"),
                             "YOLO_BOXES_OUT": response.as_numpy("YOLO_BOXES"),
                             "YOLO_CLASSES_OUT": response.as_numpy("YOLO_CLASSES"),
                             "ATTRS_RESIZE": np.zeros(2),  # response.as_numpy("ATTRS_RESIZE"),
                             "HAZMAT_SCORES": np.zeros((100, 1, 1)),
                             "HAZMAT_BOXES": np.zeros((400, 1, 1)),
                             "HAZMAT_CLASSES": np.zeros((100, 1, 1)),
                             "STAMP_SCORES": np.zeros((100, 1, 1)),
                             "STAMP_BOXES": np.zeros((600, 1, 1)),
                             "STAMP_CLASSES": np.zeros((100, 1, 1)),
                             "HAZMAT_YOLO_SCORES": response.as_numpy("HAZMAT_YOLO_SCORES"),
                             "HAZMAT_YOLO_BOXES": response.as_numpy("HAZMAT_YOLO_BOXES"),
                             "HAZMAT_YOLO_CLASSES": response.as_numpy("HAZMAT_YOLO_CLASSES"),
                             "CUDA_SIFT_DESCRIPTORS": response.as_numpy("CUDA_SIFT_DESCRIPTORS"),
                             }

    if model_name == 'shipping_label_ocr':
        # Resize for batch dimension
        file_bytestring, scores, boxes, classes = input1
        file_bytestring = np.expand_dims(file_bytestring, axis=0)

        with grpcclient.InferenceServerClient(url=url) as triton_client:
            input0 = grpcclient.InferInput("img_bytestring", file_bytestring.shape, "UINT8")
            input0.set_data_from_numpy(file_bytestring)
            input1 = grpcclient.InferInput("scores", scores.shape, "FP32")
            input1.set_data_from_numpy(scores)
            input2 = grpcclient.InferInput("boxes", boxes.shape, "FP32")
            input2.set_data_from_numpy(boxes)
            input3 = grpcclient.InferInput("classes", classes.shape, "FP32")
            input3.set_data_from_numpy(classes)

            output0 = grpcclient.InferRequestedOutput("shipping_label_OCR")

            input_list = [input0, input1, input2, input3]
            output_list = [output0]

            start = time.time()
            response = triton_client.infer(
                model_name, input_list, request_id=str("1"), outputs=output_list,
                client_timeout=ecips_config.ECIPS_INFERENCE_TIMEOUT
            )
            end = time.time()
            response_dict = {"shipping_label_OCR": response.as_numpy("shipping_label_OCR"),
                             }

    logging.info(f"Inference took {end - start} seconds")
    return response_dict


def extract_shipping_label_metrics(yolo_response):
    scores = yolo_response["YOLO_SCORES_OUT"][0].squeeze()
    boxes = yolo_response["YOLO_BOXES_OUT"][0].squeeze()
    classes = yolo_response["YOLO_CLASSES_OUT"][0].squeeze()

    # PVI initialization
    pvi_found = False

    # Package Class initialization
    package_class_found = False

    # Barcode Class initialization
    barcode_found = False

    for class_id, box, score in zip(classes, boxes, scores):
        # Check for PVI
        if int(class_id) in PVI_MAPPINGS.keys() and score > ecips_config.ECIPS_INFERENCE_PACKAGE_SCORE_THRES:
            if not pvi_found:
                pvi_metrics = extract_pvi_metrics(box, score)
                pvi_found = True

        # Check for Package class
        if int(class_id) in PACKAGE_MAPPINGS.keys() and score > ecips_config.ECIPS_INFERENCE_PACKAGE_SCORE_THRES:
            if not package_class_found:
                package_metrics = extract_package_metrics(class_id, score)
                package_class_found = True
        # Check for Barcode class
        if int(class_id) in BARCODE_MAPPINGS.keys() and score > ecips_config.ECIPS_INFERENCE_BARCODE_SCORE_THRES:
            if not barcode_found:
                barcode_metrics = extract_barcode_metrics(score, box)
                barcode_found = True

    if not pvi_found:
        pvi_metrics = extract_pvi_metrics(box, score, found=False)
    if not package_class_found:
        package_metrics = extract_package_metrics(class_id, score, found=False)
    if not barcode_found:
        barcode_metrics = extract_barcode_metrics(score, box, found=False)

    raw_yolo_metrics = extract_yolo_metrics(scores, boxes, classes)

    return pvi_metrics, package_metrics, barcode_metrics, raw_yolo_metrics


def extract_hazmat_yolo_metrics(yolo_response):
    scores = yolo_response["HAZMAT_YOLO_SCORES"][0].squeeze()
    boxes = yolo_response["HAZMAT_YOLO_BOXES"][0].squeeze()
    classes = yolo_response["HAZMAT_YOLO_CLASSES"][0].squeeze()

    # Hazmat initialization
    hazmat_classes = np.zeros((20, 1))
    hazmat_boxes = np.zeros((20, 4, 2))
    hazmat_scores = np.zeros((20, 1))
    num_hazmat_detections = 0

    for class_id, box, score in zip(classes, boxes, scores):

        # Check for Hazmat
        if int(class_id) in ECIPS_YOLO_HAZMAT_MAPPINGS.keys():
            class_id_key = str(int(class_id))
            class_id_conf = ecips_config.ECIPS_INFERENCE_HAZMAT_YOLO_SCORE_THRES[class_id_key]
            if class_id_conf != "":
                is_conf_detection = score > float(class_id_conf)
            else:
                is_conf_detection = False
            is_valid_hazmat_class = class_id_key not in ECIPS_HAZMAT_YOLO_INVALID_ID_DICT.keys()

            if not is_valid_hazmat_class:
                logging.info(
                    f"Hazmat Class={class_id} is in the list of invalid hazmat_ids={ECIPS_HAZMAT_YOLO_INVALID_ID_DICT}"
                )

            valid_hazmat_detection = is_conf_detection and is_valid_hazmat_class

            if valid_hazmat_detection:
                logging.info(
                    f"Hazmat Classes={class_id} is in the list of in valid hazmat_ids={ECIPS_HAZMAT_MAPPINGS}"
                )
                hazmat_classes[num_hazmat_detections] = class_id
                hazmat_boxes[num_hazmat_detections] = box
                hazmat_scores[num_hazmat_detections] = score
                num_hazmat_detections += 1

    hazmat_metrics = extract_hazmat_metrics(hazmat_classes, hazmat_boxes, hazmat_scores, num_hazmat_detections)

    return hazmat_metrics


def extract_yolo_metrics(scores, boxes, classes):

    inference_metrics = {
        "yolo": "",
        "yolo_scores": np.squeeze(
            np.round(scores.astype(np.single), decimals=5)
        ).reshape(-1),
        "yolo_boxes": np.squeeze(
            np.round(boxes.astype(np.single), decimals=5)
        ).reshape(-1),
        "yolo_classes": np.squeeze(
            np.round(classes.astype(np.single), decimals=5)
        ).reshape(-1),
        "YOLO_model_version": str(YOLO_MODEL_VERSION),
    }
    logging.debug(f"YOLO Inference results: {inference_metrics}")

    return inference_metrics


def extract_barcode_metrics(score, box, found=True):
    """
    Extract some barcode metrics from response
    """

    if found:
        digits_array = np.array([-1], dtype='int8')
        barcode_valid = True
        inference_metrics = {
            "barcode": digits_array,
            "detected_barcode": np.squeeze(
                np.round(box.astype(np.single), decimals=3)
            ).reshape(-1),
            "barcode_scores": np.squeeze(
                np.round(score.astype(np.single), decimals=5)
            ).reshape(-1),
            "detected_digits": np.asarray([-1], dtype='int8'),
            "digit_scores": np.asarray([-1], dtype='int8'),
            "barcode_valid": str(barcode_valid),
            "Barcode_model_version": str(BAR_MODEL_VERSION),
            "Digit_model_version": str(DIG_MODEL_VERSION),
        }

    else:

        logging.debug(
            "No candidate barcode detected. Variable SCORE_THRES may need to be reduced"
        )

        inference_metrics = {
            "barcode": np.asarray([-1], dtype='int8'),
            "detected_barcode": np.asarray([-1], dtype='int8'),
            "barcode_scores": np.asarray([-1], dtype='int8'),
            "detected_digits": np.asarray([-1], dtype='int8'),
            "digit_scores": np.asarray([-1], dtype='int8'),
            "barcode_valid": str(False),
            "Barcode_model_version": str(BAR_MODEL_VERSION),
            "Digit_model_version": str(DIG_MODEL_VERSION),
        }

    logging.debug(f"Barcode inference metrics: {inference_metrics}")
    return inference_metrics


def extract_package_metrics(class_id, score, found=True):
    """
    Extract some package metrics from response
    """

    if found:
        package = PACKAGE_MAPPINGS[class_id]
    else:
        # No label was detected, return "other" class and low score
        package = PACKAGE_MAPPINGS['no-package-label']
        score = 0.0

    inference_metrics = {
        "package": package,
        "package_score": str(score),
        "Package_model_version": str(PACKAGE_MODEL_VERSION),
    }
    logging.debug(f"Package Inference metrics: {inference_metrics}")
    return inference_metrics


def extract_descriptors(response):
    """
    Extract the cudasift descriptors from the ensemble model
    """
    cuda_sift_descriptors = response["CUDA_SIFT_DESCRIPTORS"]

    return cuda_sift_descriptors


def extract_stamp_metrics(response):
    """
    Extract some stamp metrics from response
    """
    # results = {
    #     "scores": response["STAMP_SCORES"],
    #     "classes": response["STAMP_CLASSES"],
    #     "boxes": response["STAMP_BOXES"],
    #     "attr_resize": response["ATTRS_RESIZE"],
    # }
    stamp_array = None  # process_odtk_results(results, SCORE_THRES, rotated=False)

    if stamp_array is not None:
        logging.debug(f"Candidate stamps detected performing non-maximum suppression for {str(response)}")
        inference_metrics = {
            "num_stamps": stamp_array.shape[0],
            "stamp_scores": np.squeeze(
                np.round(stamp_array[:, 4].astype(np.single), decimals=3)
            ).reshape(-1),
            "detected_stamp": np.squeeze(
                np.round(stamp_array[:, 0:4].astype(np.single), decimals=3)
            ).reshape(-1),
            "Stamp_model_version": str(STAMP_MODEL_VERSION),
        }

    else:
        logging.debug(
            f"No candidate stamps detected from {str(response)}. Variable SCORE_THRES may need to be reduced"
            f"Compiling and returning inference metrics"
        )
        inference_metrics = {
            "num_stamps": 0,
            "stamp_scores": np.asarray([-1], dtype='int8'),
            "detected_stamp": np.asarray([-1], dtype='int8'),
            "Stamp_model_version": str(STAMP_MODEL_VERSION),
        }
        logging.debug(f"Stamp Inference metrics: {inference_metrics}")
    return inference_metrics


def extract_pvi_metrics(box, score, found=True):
    """
    Extract some pvi metrics from response
    """

    if found:
        score_out = score
        box_out = box
    else:
        # No label was detected, return boxes as zeros and 0.0 score
        score_out = 0.0
        box_out = np.zeros((4, 2))

    result_pvi = {
        "score_5": np.array(score_out),
        "box_5": np.array(box_out)
    }

    inference_metrics = {
        "pvi": "",
        "pvi_scores": np.squeeze(
            np.round(result_pvi["score_5"].astype(np.single), decimals=5)
        ).reshape(-1),
        "detected_pvi": np.squeeze(
            np.round(result_pvi["box_5"].astype(np.single), decimals=5)
        ).reshape(-1),
        "PVI_model_version": str(PVI_MODEL_VERSION),
    }
    logging.debug(f"PVI Inference metrics: {inference_metrics}")
    return inference_metrics


def extract_OG_hazmat_metrics(response):
    """
    Extract some hazmat metrics from original retina net hazmat model
    """
    results = {
        "scores": response["HAZMAT_SCORES"],
        "classes": response["HAZMAT_CLASSES"],
        "boxes": response["HAZMAT_BOXES"],
        "attr_resize": response["ATTRS_RESIZE"],
    }

    hazmat_array = process_odtk_results(results, SCORE_THRES, rotated=False)

    if hazmat_array is not None:
        logging.debug("Candidate hazmat labels detected; performing non-maximum suppression")
        inference_metrics = {
            "num_hazmat_labels": hazmat_array.shape[0],
            "hazmat_scores": np.squeeze(
                np.round(hazmat_array[:, 4].astype(np.single), decimals=3)
            ).reshape(-1),
            "hazmat_classes": np.squeeze(
                np.round(hazmat_array[:, 5].astype(np.single), decimals=3)
            ).reshape(-1),
            "detected_hazmat": np.squeeze(
                np.round(hazmat_array[:, 0:4].astype(np.single), decimals=3)
            ).reshape(-1),
            "Hazmat_model_version": str(HAZMAT_MODEL_VERSION),
        }

    else:
        logging.debug(
            "No hazmat labels detected at current detection threshold."
        )
        logging.debug("Compiling and returning inference metrics")

        inference_metrics = {
            "num_hazmat_labels": 0,
            "hazmat_scores": np.asarray([-1], dtype='int8'),
            "hazmat_classes": np.asarray([-1], dtype='int8'),
            "detected_hazmat": np.asarray([-1], dtype='int8'),
            "Hazmat_model_version": str(HAZMAT_MODEL_VERSION),
        }
    logging.debug(f"Hazmat Inference metrics: {inference_metrics}")
    return inference_metrics


def extract_hazmat_metrics(hazmat_classes, hazmat_boxes, hazmat_scores, num_hazmat_detections):
    """
    Extract some hazmat metrics from response.
    """
    if num_hazmat_detections > 0:
        logging.debug("Candidate hazmat labels detected")
        inference_metrics = {
            "num_hazmat_labels": num_hazmat_detections,
            "hazmat_scores": np.squeeze(
                np.round(hazmat_scores[:num_hazmat_detections].astype(np.single), decimals=3)
            ).reshape(-1),
            "hazmat_classes": np.squeeze(
                np.round(hazmat_classes[:num_hazmat_detections].astype(np.single), decimals=3)
            ).reshape(-1),
            "detected_hazmat": np.squeeze(
                np.round(hazmat_boxes[:num_hazmat_detections].astype(np.single), decimals=3)
            ).reshape(-1),
            "Hazmat_model_version": str(HAZMAT_MODEL_VERSION),
        }

    else:
        logging.debug(
            "No hazmat labels detected at current detection threshold."
        )
        logging.debug("Compiling and returning inference metrics")

        inference_metrics = {
            "num_hazmat_labels": 0,
            "hazmat_scores": np.asarray([-1], dtype='int8'),
            "hazmat_classes": np.asarray([-1], dtype='int8'),
            "detected_hazmat": np.asarray([-1], dtype='int8'),
            "Hazmat_model_version": str(HAZMAT_MODEL_VERSION),
        }
    logging.debug(f"Hazmat Inference metrics: {inference_metrics}")
    return inference_metrics


def extract_bcr_metrics(response):
    """
    Extract barcode information metrics from response.
    """
    raw_results = response["shipping_label_OCR"]
    processed_response = convert_OCR_results(raw_results)
    # results_barcode = {
    #     "barcode_ocr": processed_response["barcode_ocr"],
    #     "barcode_decode": processed_response["barcode_decode"]
    # }
    results_barcode = processed_response["barcodes"]

    # Grab pyzbar and ocr model results.  Add preference for pyzbar result if available
    inference_metrics = []
    for pyzbar_result, ocr_result in results_barcode:

        # Grabbing the preferred barcode result
        preferred_result = pyzbar_result if pyzbar_result not in [None, 'None'] else ocr_result
        barcode_present = False if preferred_result is None or preferred_result == 'None' else True
        # TODO: return barcode classification
        barcode_type = "UCC/EAN 128" if barcode_present else None

        inference_metrics.append({
            "barcode_risk_score": 0.0,  # TODO: how do we derive risk score
            "barcode_present": str(barcode_present).upper(),
            "barcode_reconstructed": str(barcode_present).upper(),
            "barcode": preferred_result,
            "barcode_ocr": ocr_result,
            "barcode_decode": pyzbar_result,
            "barcode_class": str(barcode_type)
        })

    logging.debug(f"Barcode Inference metrics: {inference_metrics}")
    return inference_metrics


def extract_ocr_result(response):
    """
       Extract barcode information metrics from response.
       """
    raw_results = response["shipping_label_OCR"]
    ocr_results = convert_OCR_results(raw_results)

    return ocr_results


def convert_OCR_results(raw_ocr_results):
    results_as_string = raw_ocr_results.flatten()[0].decode().replace("'", '"')

    results_as_dict = ast.literal_eval(results_as_string)

    return results_as_dict
