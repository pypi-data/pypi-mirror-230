import glob
import math
import logging
import os
import time
import json

import cv2
import matplotlib.pyplot as plt
import numpy as np
# import sys
import orjson
import requests
# import torch

PROJECT_ROOT_DIR = "/"+os.path.join(*os.path.split(os.getcwd())[0].split("/")[:4])
os.environ['INVALID_PERMIT_FILE'] = PROJECT_ROOT_DIR + "/Docker/Invalid_eVS_Permit_List.xlsx"
os.environ['STC_DB_FILE'] = PROJECT_ROOT_DIR + "/Docker/stc_db.json"
os.environ['SHIPPO_MIDS_FILE'] = PROJECT_ROOT_DIR + "/Docker/SHIPPO_POPOUT_MIDS.xlsx"

from ecips_tasks.tasks import compute_OCR_from_filepath
from ecips_tasks.tasks_comms import send_hazmat_to_webapat
# from ecips_triton_ensemble import ECIPsApplicationTritonModels
from ecips_utils.packageObject.packageclass import ImageObject
from ecips_utils import (ecips_config, ecips_logging)
from ecips_utils.lokiLogging import (loki_config, loki_utils)
from ecips_utils.prlmProcessing.read_PRLM import PRLMFile
from ecips_utils.fraudDetection.fraud_config import FRAUD_TYPES
from ecips_utils.anomalyDetection.anomaly_config import ANOMALY_TYPES

TESTING = False
names = ['Lithium_UN_Label',
         'Lithium__Class_9',
         'Lithium_Battery_Label',
         'Biohazard',
         'No_Fly',
         'Finger_Small',
         'Finger_Large',
         'Cargo_Air_Only',
         'Suspected_Label',
         'Hazmat_Surface_Only',
         'address-block',
         'address-block-handwritten',
         'first-class',
         'ibi',
         'imb',
         'impb',
         'priority',
         'permit-imprint',
         'pvi',
         's10',
         'Cremated_Remains']
class_map_dict = {1: 'Lithium_UN_Label',
                  2: 'Lithium__Class_9',
                  3: 'Lithium_Battery_Label',
                  4: 'Biohazard',
                  5: 'No_Fly',
                  6: 'Finger_Small',
                  7: 'Finger_Large',
                  8: 'Cargo_Air_Only',
                  9: 'Suspected_Label',
                  10: 'Hazmat_Surface_Only',
                  11: 'address-block',
                  12: 'address-block-handwritten',
                  13: 'first-class',
                  14: 'ibi',
                  15: 'imb',
                  16: 'impb',
                  17: 'priority',
                  18: 'permit-imprint',
                  19: 'pvi',
                  20: 's10',
                  21: 'Cremated_Remains'}
category_id_2 = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (255, 255, 0), (255, 0, 255), (0, 255, 255), (50, 200, 255),
                 (255, 30, 30), (30, 30, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255), (25, 255, 63),
                 (255, 30, 30), (30, 30, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255), (85, 69, 255),
                 (255, 30, 30), (30, 30, 255)]
max_det = 1000
iou_thres = 0.2
conf_thres = 0.25


def letterbox(im, new_shape=(640, 640), color=(114, 114, 114), auto=True, scaleFill=False, scaleup=True, stride=32):
    """
    Resize and pad image while meeting stride-multiple constraints
    Returns:
        im (array): (height, width, 3)
        ratio (array): [w_ratio, h_ratio]
        (dw, dh) (array): [w_padding h_padding]
    """
    shape = im.shape[:2]  # current shape [height, width]
    if isinstance(new_shape, int):  # [h_rect, w_rect]
        new_shape = (new_shape, new_shape)

    # Scale ratio (new / old)
    r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])
    if not scaleup:  # only scale down, do not scale up (for better val mAP)
        r = min(r, 1.0)

    # Compute padding
    ratio = r, r  # wh ratios
    new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))  # w h
    dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1]  # wh padding
    if auto:  # minimum rectangle
        dw, dh = np.mod(dw, stride), np.mod(dh, stride)  # wh padding
    elif scaleFill:  # stretch
        dw, dh = 0.0, 0.0
        new_unpad = (new_shape[1], new_shape[0])  # [w h]
        ratio = new_shape[1] / shape[1], new_shape[0] / shape[0]  # [w_ratio, h_ratio]

    dw /= 2  # divide padding into 2 sides
    dh /= 2

    if shape[::-1] != new_unpad:  # resize
        im = cv2.resize(im, new_unpad, interpolation=cv2.INTER_LINEAR)
    top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
    left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
    im = cv2.copyMakeBorder(im, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)  # add border
    return im, ratio, (dw, dh)


def check_img_size(imgsz, s=32, floor=0):
    # Verify image size is a multiple of stride s in each dimension
    if isinstance(imgsz, int):  # integer i.e. img_size=640
        new_size = max(make_divisible(imgsz, int(s)), floor)
    else:  # list i.e. img_size=[640, 480]
        new_size = [max(make_divisible(x, int(s)), floor) for x in imgsz]
    # if new_size != imgsz:
    #     print(f'WARNING: --img-size {imgsz} must be multiple of max stride {s}, updating to {new_size}')
    return new_size


def make_divisible(x, divisor):
    # Returns nearest x divisible by divisor
    divisor = int(divisor.max())  # to int

    return math.ceil(x / divisor) * divisor


# def post_process_yolo_results(img, yolo_output, fig_name='default'):
#     detections = non_max_suppression_obb(torch.tensor(yolo_output[0]), conf_thres, iou_thres,
#                                          classes=None, multi_label=True, max_det=max_det)
#     scores = np.zeros((len(detections), 100, 1, 1))
#     classes = np.zeros((len(detections), 100, 1, 1))
#     boxes = np.zeros((len(detections), 400, 4, 2))
#     for batch, img_detections in enumerate(detections):  # parses through images
#         # bbox = pred[:, :5]
#         # print(bbox)
#         # print("converting to radian", item[:,5]*180/np.pi)
#         pred_poly = rbox2poly(img_detections[:, :5])
#         # print("polygon predictions", pred_poly)
#         # print("processed shape: ", preprocessed_yolo_img.shape[2:])
#         # print("og shape: ", og_dims[:-1])
#         pred_poly_resize = scale_polys(preprocessed_yolo_img.shape[2:], pred_poly, og_dims[:-1])
#         img_detections = torch.cat((pred_poly_resize, img_detections[:, -2:]), dim=1)  # (n, [poly conf cls])
#         for det_i, (*poly, conf, cls) in enumerate(reversed(img_detections)):
#             if conf.numpy() > 0.4:
#                 # poly = poly.tolist()
#                 box = poly
#                 # print(box)
#                 line = (cls, *poly, conf) if True else (cls, *poly)  # label format
#                 print((('%g ' * len(line)).rstrip() % line + '\n'))
#
#                 # cropped_img = cv2_affine_crop(cv2.imread(filepath), box)
#                 minRect = cv2.minAreaRect(
#                     np.asarray([(box[0], box[1]), (box[2], box[3]), (box[4], box[5]), (box[6], box[7])]))
#                 # print("Result from min area rect: ", minRect)
#
#                 box = cv2.boxPoints(minRect)  # of form (TR, BR, BL, TL) shape is (4,2)
#
#                 scores[batch, det_i] = conf.numpy()
#                 classes[batch, det_i] = cls.numpy()
#                 boxes[batch, det_i] = box
#                 # print(int(cls.numpy()))
#                 # class_name = names[int(cls.numpy())]
#                 # img_root_name = filepath.split("/")[-1].split(".")[0]
#                 # print(class_name)
#                 # print(img_root_name)
#                 # box = np.int0(box)
#                 # img = cv2.drawContours(img, [box], 0, category_id_2[cls.numpy().astype(int)], 7)
#         # plt.figure(fig_name)
#         # plt.imshow(img)
#         # plt.show()
#
#     return scores, boxes, classes


def load_fraud_image(image_filepath, imgsz=(896, 896)):
    img = cv2.imread(image_filepath)
    og_dims = img.shape
    stride = 32
    img_size = check_img_size(imgsz, stride)
    auto = False
    img, ratio, (_, _) = letterbox(img, img_size, stride=stride, auto=auto)
    img = img.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
    img = np.ascontiguousarray(img)
    img = img.astype('float16')
    img /= 255  # 0 - 255 to 0.0 - 1.0
    if len(img.shape) == 3:  # expand for batch dim
        img = img[None]

    # # Convert
    # img = img.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
    # img = np.ascontiguousarray(img)

    return img, og_dims


def load_cv2_warp_results(filepath):
    import pickle
    with open(filepath, 'rb') as file:
        data = pickle.load(file)

    return data


# def compare_results(results_file, triton_detections):
#     with open(results_file, 'r') as text_file:
#         results = text_file.read()


# def compare_yolo_retinanet_models(filepath):
def plot_yolo_detections(img, boxes, classes, scores, fig_name="default"):
    plt.clf()
    for box, cls, score in zip(boxes[0], classes[0], scores[0]):

        box = np.int0(box)

        try:
            if score.numpy() > 0.4:
                img = cv2.drawContours(img, [box], 0, category_id_2[cls.numpy().astype(int)], 7)
                display_nm = names[cls.numpy().astype(int)] + ": " + str(score)
                img = cv2.putText(img, display_nm, org=(box[0], box[1]))
        except AttributeError:
            if float(score.flatten()) > 0.4:
                try:
                    img = cv2.drawContours(img, [box], 0, category_id_2[int(cls.flatten())], 7)
                    display_nm = names[int(cls.flatten())] + ": " + str(float(score.flatten()))
                    img = cv2.putText(img, display_nm, org=tuple(box[0]), fontFace=cv2.FONT_HERSHEY_TRIPLEX,
                                      fontScale=3,
                                      color=category_id_2[int(cls.flatten())], thickness=3)
                except cv2.error:
                    out = img.shape
                    return out

    plt.figure(fig_name)
    plt.imshow(img)
    plt.show()


def test_run(filename):
    ecip_models = ECIPsApplicationTritonModels(hostname='localhost:8001')

    # loaded_img = ecip_models.dali_load_img(filename)
    # stamp_score, attr_resize, hazmat_score, small_img = ecip_models.ensemble_model_dali(loaded_img)
    # scores, boxes, classes = ecip_models.ensemble_model_shipping_label(loaded_img)

    og_dims, yolo_scores, \
        yolo_boxes, yolo_classes, \
        hazmat_scores, stamp_scores = ecip_models.ensemble_model_ecips(filename)

    # scores, boxes, classes = ecip_models.ensemble_model_shipping_label(filename)

    # img_batch, matrix_out, dims_out, cropped_label_classes =
    # ecip_models.extract_crop_args(filename, scores, boxes, classes)
    # cropped_labels = ecip_models.dali_crop_gpu(img_batch, matrix_out, dims_out)
    # plot_yolo_detections(cv2.imread(filename), boxes, classes=classes, scores=scores,
    #                      fig_name="end-to-end-triton")
    # cropped_labels, classes_out = ecip_models.ensemble_model_crop_label(filename, scores, boxes, classes)
    shipping_label_OCR = ecip_models.shipping_label_ocr(filename, yolo_scores[0], yolo_boxes[0], yolo_classes[0])
    print(shipping_label_OCR)


def compute_feature_from_filepath(filename, output_path=None):
    # Compute feature_from filepath
    image = ImageObject(filename)

    # Load imagery & confirm it is valid
    image.check_img_valid()

    if image.is_valid_img():
        # because we are testing locally
        image.update_grpc_url('localhost:8001')
        # Call the triton inference server
        image.get_triton_response()
        # Extract the ECIP's attributes from the response
        image.extract_from_response()
        # Generate the json file with all results
        # results_dict, results_json = image.generate_results_json()
        # Write the json file to the disk
        # print(results_dict)
        # if write_tofile:

        results_dict = {}
        for key in image.hazmat_metrics.keys():
            results_dict.update({key: image.hazmat_metrics[key]})

        # if float(str(results_dict["hazmat_scores"][0])) > 0.4:
        image.descriptors = np.ones((125, 265))
        results_dict, results_json = image.generate_results_json()

        if output_path is not None:
            filepath_json = output_path + filename.split("/")[-1].split(".")[0] + ".json"
            with open(filepath_json, "wb") as fp:
                fp.write(orjson.dumps(results_dict, option=orjson.OPT_SERIALIZE_NUMPY))

        try:
            image.write_to_json(results_dict)
        except Exception as e:
            # Redis exception because its not running, ok for testing
            pass

            # logging.debug(f"Results for {img_filepath}: {results_dict}. Writing complete.")
        # Send hazmat to webapat
        if send_hazmat_to_webapat:
            if results_dict["num_hazmat_labels"] > 0:
                send_hazmat_to_webapat(filename, str(results_dict["hazmat_scores"][0]),
                                       str(int(results_dict["hazmat_classes"][0])))


def process_prlm(
    prlm_file,
    output_path=None,
    webapat_url=ecips_config.ECIPS_WEBAPAT_URL,
    webapat_secret_key=ecips_config.ECIPS_WEBAPAT_SECRET_KEY,
):
    prlm_obj = PRLMFile(prlm_file)
    images_to_bcr = prlm_obj.get_images_to_bcr()
    ibi_barcode_dict = prlm_obj.get_ibi_barcodes()
    impb_barcode_dict = prlm_obj.get_impb_barcodes()
    images_in_prlm = prlm_obj.get_image_filepaths()
    volume = prlm_obj.get_package_volume()
    root_prlm_dir = prlm_obj.device_key + "_" + prlm_file.split("/")[-1].split(".")[0]

    prlm_info = {"filepath": prlm_file,
                 "total_packages_wout_barcode": prlm_obj.total_packages_wout_barcode,
                 "total_packages": prlm_obj.total_packages,
                 "images_to_bcr": len(images_to_bcr),
                 "device_key": prlm_obj.device_key}

    if TESTING:
        # only test on first 100 images
        images_in_prlm = images_in_prlm[:100]
    ocr_results = []

    if ecips_config.ECIPS_PERFORM_BCR or ecips_config.ECIPS_DETECT_FRAUD:
        for img_file in images_in_prlm:
            # Adding in for testing only!
            # img_file_correct = img_file.split("/01-439")[0] + "/01-439" + img_file.split("/01-439")[-1]
            # img_file_correct = img_file.split("/01-439")[0] + "/01-439" + img_file.split("/01-439")[-1]
            if "20221004112944_040415268.tif" in img_file:
                print("")
            try:
                ocr_results.append(compute_OCR_from_filepath(img_file,
                                                             ibi_barcode_dict[img_file],
                                                             volume[img_file],
                                                             impb_barcode_dict[img_file],
                                                             ecips_serving_url='localhost:8001'))
            except OSError:
                continue

    error_list = ''

    # Initialize results
    bcr_request = {}
    fraud_request = {}
    anomaly_request = {}

    images_w_barcode_ct = 0
    images_w_fraud_ct = 0
    images_w_anomaly_ct = 0
    fraud_type_count = {fraud_type: 0 for fraud_type in FRAUD_TYPES}
    anomaly_type_count = {f"anomaly_{anomaly_type.anomaly_id}": 0 for anomaly_type in ANOMALY_TYPES}

    if ecips_config.ECIPS_PERFORM_BCR:
        # Count how many images were successfully reconstructed
        img_base_out = []
        for result in ocr_results:
            logging.debug(f"On result: {result}")
            try:
                bcr_result = result["bcr_results"]
            except TypeError:
                # If an error occurred on the task, then we cannot grab results as a dict
                logging.debug(f"An error occured on result: {result}")
                continue
            if type(bcr_result) != dict and type(bcr_result) == str:
                # An Error occurred that we want to log
                # These errors are identical for Fraud, BCR and Anomalies so we will only add once
                error_list += f"{bcr_result} \n"
            elif bcr_result != {} and type(bcr_result) == dict:
                # Adds 0 if false, 1 if True to count the number of successfully reconstructed barcodes
                images_w_barcode_ct += 1
                img_base_out.append(bcr_result)

        if images_w_barcode_ct > 0:
            # If we have reconstructed barcodes:

            # Send the message to webapat and loki
            bcr_action = "rbc_orig_list_from_ecip"
            send_comms(img_base_out, bcr_action, "ecip_webapat_msg")

            if ecips_config.WRITE_BCR_RESULTS:
                ecips_logging.write_results(root_prlm_dir, img_base_out, result_type="BCR_WebAPAT_message")

        else:
            logging.info(f"No barcodes in the PRLM file {prlm_info['filepath']} were able to be reconstructed")

        # Increment the BCR Performance Trackers
        ecips_logging.increment_bcr_counters(images_w_barcode_ct, prlm_info)

    if ecips_config.ECIPS_DETECT_FRAUD:
        # Count how many images were successfully reconstructed
        logging.debug("Processing fraudulent results")
        img_base_out = []
        for result in ocr_results:
            try:
                fraud_results = result["fraud_results"]
            except TypeError:
                # If an error occurred on the task, then we cannot grab results as a dict
                logging.debug(f"An error occurred on result: {result}")
                continue
            if fraud_results != {} and type(fraud_results) == dict:
                images_w_fraud_ct += 1
                fraud_type_detected = fraud_results["fraud_type"].split(',')[:-1]
                for fraud in fraud_type_detected:
                    fraud_type_count[fraud] += 1
                ecips_logging.inc_redis_counter("total_fraud_package_volume", fraud_results.pop('volume'))
                img_base_out.append(fraud_results)

        if images_w_fraud_ct > 0:
            # If we have fraudulent items:

            # Count how many of each fraud type
            for key, value in fraud_type_count.items():
                ecips_logging.inc_redis_counter(key, value)
            # Send the message to webapat and loki
            fraud_action = "fr_orig_list_from_ecip"
            send_comms(img_base_out, fraud_action, "ecip_webapat_msg")

            if ecips_config.WRITE_FRAUD_RESULTS:
                ecips_logging.write_results(root_prlm_dir, img_base_out, result_type="Fraud_WebAPAT_message")
        else:
            logging.info(f"No fraud was found in the PRLM file: {prlm_info['filepath']}")

    if ecips_config.ECIPS_DETECT_ANOMALY:
        # Count how many images were successfully reconstructed
        logging.debug("Processing anomalous results")
        img_base_out = []
        for result in ocr_results:
            try:
                anomaly_results = result["anomaly_results"]
            except TypeError:
                # If an error occurred on the task, then we cannot grab results as a dict
                logging.debug(f"An error occurred on result: {result}")
                continue
            if anomaly_results != {} and type(anomaly_results) == dict:
                images_w_anomaly_ct += 1
                anomaly_type_detected = anomaly_results["anomaly_type"].split(',')[:-1]
                for anomaly in anomaly_type_detected:
                    anomaly_type_count[f"anomaly_{anomaly}"] += 1
                img_base_out.append(anomaly_results)

        if images_w_anomaly_ct > 0:
            # If we have anomalous results:

            # Send the message to webapat and loki
            anomaly_action = "mail_anomaly_list_from_ecip"
            send_comms(img_base_out, anomaly_action, "ecip_webapat_msg")

            if ecips_config.WRITE_ANOMALY_RESULTS:
                ecips_logging.write_results(root_prlm_dir, img_base_out, result_type="Anomaly_WebAPAT_message")

        else:
            logging.info(f"No anomalies were found in the PRLM file: {prlm_info['filepath']}")

    ecips_logging.prlm_logging(prlm_info,
                               images_w_barcode_ct,
                               images_w_fraud_ct,
                               images_w_anomaly_ct,
                               fraud_type_count,
                               anomaly_type_count)

    if ecips_config.WRITE_OCR_RESULTS:
        json_out = {}
        loki_list = []
        # write the OCR results to a json file
        for result in ocr_results:
            raw_ocr_results = result["image_results"]
            if raw_ocr_results != {} and type(raw_ocr_results) == dict:
                json_out.update({raw_ocr_results['absolute_image_path']: raw_ocr_results})
                send_to_loki = json.loads((json.loads(raw_ocr_results.pop('send_to_loki').lower())))
                if send_to_loki:
                    loki_list.append(raw_ocr_results)

        ecips_logging.write_results(root_prlm_dir, json_out, result_type="raw_image_results")
        loki_utils.post_loki_message(loki_list, job_name="image_results_from_ecip", source_name="ecip_db")

    if error_list == '':
        # No errors occurred while processing the PRLM file
        return {"bcr_request_results": bcr_request,
                "fraud_request_results": fraud_request,
                "anomaly_results": anomaly_request}
    else:
        # Errors occurred.  Propagate the Error message to the process_ocr_results task
        raise AssertionError(f"Errors occurred while processing the PRLM file {prlm_info['filepath']}.  The "
                             f"error(s) were as follows: \n {error_list}")

def send_comms(img_message, action, message_type):
    """
    A function to send comms to both webapat AND loki

    Args:
        img_message (dict): the message that will be send to both loki and webapat
        action (str): the message action according to the WebAPAT IDD
        message_type (str): the type of message (loki only)
    """
    # logging.info(f"The flag to send message for {action} for communications to WebAPAT is"
    #              f"set to {ecips_config.POST_WEBAPAT_MSG_TYPE[action]}")
    # if ecips_config.POST_WEBAPAT_MSG_TYPE[action]:
    #     # If we have the flag turned on to send this particular message type to webapat
    #     post_webapat_message(img_message, action=action)

    logging.info(f"The flag to send message for {action} for communications to LOKI is"
                 f"set to {loki_config.POST_LOKI_MSG_TYPE[action]}")
    if loki_config.POST_LOKI_MSG_TYPE[action]:
        # If we have the flag turned on to send this particular message type to loki
        loki_utils.post_loki_message(img_message,
                                     source_name=message_type,
                                     job_name=action)



if __name__ == "__main__":
    GT_TESTING = False

    if GT_TESTING:
        prlm_files = glob.glob("/data/Fraud/datasets/validation_set/v1.0.0/ALL_IMAGES/**/**/**/*.zip")
        prlm_filepaths = glob.glob("/data/Fraud/datasets/validation_set/v1.0.0/ALL_IMAGES/**/**/**/**/*.tif")
        output_path = "/data/Fraud/test_results/validation_results/v1.6.1_rc1_results/raw_output/"
    else:
        # /data/Fraud/datasets/validation_set/v1.0.2/ALL_IMAGES/APBS-4/2022-10-04/04-438/11/20221004112944_040415268.tif
        prlm_files = ["/home/garveyer/data/royal_palms_test_data/APBS/2023-07-11/04-750/Run_0004.PRLM.zip"]
        prlm_filepaths = glob.glob(
            "/home/garveyer/data/royal_palms_test_data/APBS/2023-07-11/04-750/**/*.tif")
        output_path = None

    start_time = time.time()
    # prlm_filepaths = glob.glob("/home/garveyer/images/SPSS-1/2022-05-25/08-438/PSOC-1/*/*.tif")

    hazmat_filepath = '/home/garveyer/images/APPS/1_00090642P.tiff'

    #
    # for i, filename in enumerate(prlm_filepaths):
    #     try:
    #         start_time = time.time()
    #         compute_feature_from_filepath(filename, output_path)
    #         end_time = time.time()
    #         print(f"File {i}/{len(prlm_filepaths)}, {filename} processing time: {end_time - start_time}")
    #     except Exception as e:
    #         print(e)
    #         pass
    if GT_TESTING:
        for file in prlm_files:
            process_prlm(file, output_path)
    else:
        process_prlm(prlm_files[0])
    #     # print(filename)
    #     # compare_yolo_retinanet_models(filename)
    #     # prod_run(filename)
    #     test_run(filename)
    #
    #
