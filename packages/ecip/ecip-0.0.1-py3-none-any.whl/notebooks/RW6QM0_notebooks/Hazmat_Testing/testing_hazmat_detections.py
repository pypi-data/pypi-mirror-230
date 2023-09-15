import glob
import math

import cv2
# path_to_yolo_odb = "/home/garveyer/ecip-yolov5_obb"
from tqdm import tqdm
# sys.path.append(path_to_yolo_odb)
# from utils.general import (non_max_suppression_obb, scale_polys)
# from utils.rboxs_utils import rbox2poly
import matplotlib.pyplot as plt
# import sys
import shutil
import numpy as np
# import torch

from ecips_tasks.tasks_triton import run_ensemble_grpc_filename, \
    extract_shipping_label_metrics, extract_hazmat_yolo_metrics, extract_OG_hazmat_metrics
# from tritoncient.utils import InferenceServerException
# from ecips_triton_ensemble import ECIPsApplicationTritonModels
# from ecips_tasks.tasks_comms import send_hazmat_to_webapat
from ecips_utils.ecips_config import ECIPS_INFERENCE_HAZMAT_SCORE_THRES as hazmat_minconf
from ecips_utils import ecips_config

# names = ['Lithium_UN_Label',
#          'Lithium__Class_9',
#          'Lithium_Battery_Label',
#          'Biohazard',
#          'No_Fly',
#          'Finger_Small',
#          'Finger_Large',
#          'Cargo_Air_Only',
#          'Suspected_Label',
#          'Hazmat_Surface_Only',
#          'address-block',
#          'address-block-handwritten',
#          'first-class',
#          'ibi',
#          'imb',
#          'impb',
#          'priority',
#          'permit-imprint',
#          'pvi',
#          's10',
#          'Cremated_Remains']
retina_hazmat_ids = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 20]
retina_class_map_dict = {0: 'Lithium_UN_Label',
                  1: 'Lithium__Class_9',
                  2: 'Lithium_Battery_Label',
                  3: 'Biohazard',
                  4: 'No_Fly',
                  5: 'Finger_Small',
                  6: 'Finger_Large',
                  7: 'Cargo_Air_Only',
                  8: 'Suspected_Label',
                  9: 'Hazmat_Surface_Only',
                  10: 'address-block',
                  11: 'address-block-handwritten',
                  12: 'first-class',
                  13: 'ibi',
                  14: 'imb',
                  15: 'impb',
                  16: 'priority',
                  17: 'permit-imprint',
                  18: 'pvi',
                  19: 's10',
                  20: 'Cremated_Remains'}
yolo_hazmat_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 16, 27]
yolo_class_map_dict = {0: None,
                      1: 'Lithium_UN_Label',
                      2: 'Lithium__Class_9',
                      3: 'Lithium_Battery_Label',
                      4: 'Biohazard',
                      5: 'No_Fly',
                      6: 'Finger_Small',
                      7: 'Finger_Large',
                      8: 'Cargo_Air_Only',
                      9: 'Suspected_Label',
                      10: '',
                      11: None,
                      12: None,
                      13: None,
                      14: None,
                      15: None,
                      16: 'Hazmat_Surface_Only',
                      17: None,
                      18: None,
                      19: None,
                      20: None,
                      21: None,
                      22: None,
                      23: None,
                      24: None,
                      25: None,
                      26: None,
                      27: 'Cremated_Remains'}

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
def plot_yolo_detections(img, boxes, classes, scores, fig_name="default", save=False, img_filepath=None):
    # plt.clf()

    for box, cls, score in zip(boxes, classes, scores):

        box = np.int0(box)

        try:
            if score > 0.4:
                box = np.array(box).reshape(4,2)
                # img = cv2.drawContours(img, [box], 0, category_id_2[int(cls)], 7)
                for coord_pt in box:
                    cv2.circle(img, coord_pt, 5, (255, 0, 0), 2)
                display_nm = yolo_class_map_dict[int(cls)] + ": " + str(score)
                img = cv2.putText(img, display_nm, box[0], cv2.FONT_HERSHEY_SIMPLEX, 2, 255)
        except AttributeError:
            if float(score.flatten())*-1 > 0.2:
                img = cv2.drawContours(img, [box], 0, category_id_2[int(cls.flatten())], 7)
                display_nm = yolo_class_map_dict[int(cls.flatten())] + ": " + str(float(score.flatten()))
                img = cv2.putText(img, display_nm, org=tuple(box[0]), fontFace=cv2.FONT_HERSHEY_TRIPLEX,
                                  fontScale=3,
                                  color=category_id_2[int(cls.flatten())], thickness=3)

    if not save:
        plt.figure(fig_name)
        plt.imshow(img)
        plt.show()
        print()
    else:
        plt.figure(fig_name)
        plt.imshow(img)
        out_dir = "/data/Hazmat_yolo_analysis/result_analysis/false_positives_labeled/"
        out_path = out_dir + img_filepath.split("/")[-1].split(".")[0]+".png"
        plt.savefig(out_path)


def check_fp_tp_results(tp_filepaths, fp_filepaths):
    # start_time = time.time()
    # problem_filenames = []
    tp_scores = np.zeros((len(tp_filepaths)))
    fp_classes = []
    fp_scores = np.zeros((len(fp_filepaths)))
    # compare_preprocessed = False
    plt.clf()

    for i, filename in enumerate(fp_filepaths):

        try:
            response = run_ensemble_grpc_filename(filename, url='localhost:8001')
        except AssertionError as e_msg:
            print(f"Encountered an image too small to be a package. File {filename}"
                  f"raises an Assertion Error, due to small image dimensions. {e_msg}")
            raise ValueError(f"On file,  {filename}, Assertion Error Raised: {e_msg}")
        # except InferenceServerException as e:
        #     print(f"Triton Inference Server encountered an exception {e.message()}")
        #     raise Exception("Triton Inference Server Exception", e.message())

        # bar_metrics = extract_barcode_metrics(response)
        # package_metrics = extract_package_metrics(response)
        # pvi_metrics = extract_pvi_metrics(response)
        # stamp_metrics = extract_stamp_metrics(response)
        results_dict = {}
        pvi_metrics, package_metrics, \
            hazmat_metrics, barcode_metrics, \
            raw_yolo_results \
            = extract_shipping_label_metrics(response)

        for key in hazmat_metrics.keys():
            results_dict.update({key: hazmat_metrics[key]})

        hazmat_score = float(str(results_dict["hazmat_scores"][0]))
        hazmat_class = results_dict['hazmat_classes'].tolist()
        if hazmat_score > hazmat_minconf:
            fp_scores[i] = hazmat_score
            # scores = response["YOLO_SCORES_OUT"][0].squeeze()
            # boxes = response["YOLO_BOXES_OUT"][0].squeeze()
            # classes = response["YOLO_CLASSES_OUT"][0].squeeze()
            # plot_yolo_detections(cv2.imread(filename), boxes, classes, scores, save=False, img_filepath=filename)
            for cls_id in hazmat_class:
                fp_classes.append(int(cls_id))
        else:
            print()
            # scores = response["YOLO_SCORES_OUT"][0].squeeze()
            # boxes = response["YOLO_BOXES_OUT"][0].squeeze()
            # classes = response["YOLO_CLASSES_OUT"][0].squeeze()
            # plot_yolo_detections(cv2.imread(filename), boxes, classes, scores)

    for i, filename in enumerate(tp_filepaths):

        try:
            response = run_ensemble_grpc_filename(filename, url='localhost:8001')
        except AssertionError as e_msg:
            print(f"Encountered an image too small to be a package. File {filename}"
                  f"raises an Assertion Error, due to small image dimensions. {e_msg}")
            raise ValueError(f"On file,  {filename}, Assertion Error Raised: {e_msg}")
        # except InferenceServerException as e:
        #     print(f"Triton Inference Server encountered an exception {e.message()}")
        #     raise Exception("Triton Inference Server Exception", e.message())

        # bar_metrics = extract_barcode_metrics(response)
        # package_metrics = extract_package_metrics(response)
        # pvi_metrics = extract_pvi_metrics(response)
        # stamp_metrics = extract_stamp_metrics(response)
        results_dict = {}
        # pvi_metrics, package_metrics, \
        #     hazmat_metrics, barcode_metrics, \
        #     raw_yolo_results \
        #     = extract_shipping_label_metrics(response)
        # self.hazmat_metrics, self.raw_yolov7_results = extract_hazmat_metrics(self.triton_response)

        for key in hazmat_metrics.keys():
            results_dict.update({key: hazmat_metrics[key]})

        hazmat_score = float(str(results_dict["hazmat_scores"][0]))
        # hazmat_class = results_dict['hazmat_classes'].tolist()
        if hazmat_score > hazmat_minconf:
            tp_scores[i] = hazmat_score

        else:
            print()
            # scores = response["YOLO_SCORES_OUT"][0].squeeze()
            # boxes = response["YOLO_BOXES_OUT"][0].squeeze()
            # classes = response["YOLO_CLASSES_OUT"][0].squeeze()
            # plot_yolo_detections(cv2.imread(filename), scores, boxes, classes)
    #
    plt.figure("fp vs tp")
    plt.plot(np.linspace(0, len(fp_scores), num=len(tp_scores)), tp_scores, 'o', label='True Positives')
    plt.plot(np.linspace(0, len(fp_scores), num=len(fp_scores)), fp_scores, 'x', label='False Positives')
    plt.legend()
    plt.show()
    plt.savefig("/data/Hazmat_yolo_analysis/result_analysis/false_positives_labeled/confidence_scores.png")
    print(f"Images that were FPs but were actually TN: {np.count_nonzero(fp_scores == 0)}")
    print(f"Images that were TPs but removed with increase of threshold: {np.count_nonzero(tp_scores == 0)}")
    histo = np.histogram(fp_classes, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 20])
    print(histo)


def compare_hazmat_models(filepaths):
    positive_count = 0
    true_positive = 0
    for i, filename in enumerate(filepaths):

        try:
            response = run_ensemble_grpc_filename(filename, url='localhost:8001')
        except AssertionError as e_msg:
            print(f"Encountered an image too small to be a package. File {filename}"
                  f"raises an Assertion Error, due to small image dimensions. {e_msg}")
            pass
            # raise ValueError(f"On file,  {filename}, Assertion Error Raised: {e_msg}")
        # except InferenceServerException as e:
        #     print(f"Triton Inference Server encountered an exception {e.message()}")
        #     raise Exception("Triton Inference Server Exception", e.message())

        # only care about the hazmat metrics for now
        yolo_hazmat_metrics = extract_hazmat_yolo_metrics(response)
        retina_hazmat_metrics = extract_OG_hazmat_metrics(response)
        # hazmat_metrics_OG = extract_OG_hazmat_metrics(response)
        # print(f"YOLO Results: \n {hazmat_metrics_yolo}")
        # print(f"Retinanet Results: \n {hazmat_metrics_OG}")

        if yolo_hazmat_metrics["num_hazmat_labels"] > 0 and retina_hazmat_metrics["num_hazmat_labels"] > 0:
            true_positive += 1
            # positive_count += 1
            boxes = np.expand_dims(yolo_hazmat_metrics["detected_hazmat"], 0)
            classes = yolo_hazmat_metrics["hazmat_classes"]
            scores = yolo_hazmat_metrics["hazmat_scores"]
            plot_yolo_detections(cv2.imread(filename), boxes, classes, scores)

        print(f"Total Hazmat detections: {positive_count}/{len(filepaths)}")
        if retina_hazmat_metrics["num_hazmat_labels"] > 0:
            boxes = retina_hazmat_metrics["detected_hazmat"]
            classes = retina_hazmat_metrics["hazmat_classes"]
            scores = retina_hazmat_metrics["hazmat_scores"]
            # plot_yolo_detections(cv2.imread(filename), boxes, classes, scores)


def sort_data_for_labeling(data_to_sort, sorted_data_output):
    data_to_sort = glob.glob(data_to_sort+"*.tif*")
    ecips_config.ECIPS_INFERENCE_HAZMAT_SCORE_THRES = 0.3
    ecips_config.ECIPS_INFERENCE_SCORE_THRES = 0.3

    for img in tqdm(data_to_sort):
        try:
            response = run_ensemble_grpc_filename(img, url='localhost:8001')
        except AssertionError as e_msg:
            print(f"Encountered an image too small to be a package. File {img}"
                  f"raises an Assertion Error, due to small image dimensions. {e_msg}")
            pass
            # raise ValueError(f"On file,  {filename}, Assertion Error Raised: {e_msg}")
        except Exception as e:
            print(f"Triton Inference Server encountered an exception {e}")
            pass

        # only care about the hazmat metrics for now
        try:
            _, _, hazmat_metrics_yolo, _, raw_yolo_results = extract_shipping_label_metrics(response)
            hazmat_metrics_retina = extract_OG_hazmat_metrics(response)
            # print("Conf Score: ", ecips_config.ECIPS_INFERENCE_HAZMAT_SCORE_THRES)

            if hazmat_metrics_yolo["num_hazmat_labels"] > 0:
                yolo_scores = hazmat_metrics_yolo["hazmat_scores"]

                if hazmat_metrics_retina["num_hazmat_labels"] > 0:
                    retina_scores = hazmat_metrics_retina["hazmat_scores"]
                    if yolo_scores.any() < 0.5 or retina_scores.any() < 0.5:
                        # Low conf detection
                        shutil.copy(img, sorted_data_output+"FN_TP/conf_lt_pt5/")
                    elif yolo_scores.any() < 0.6 or retina_scores.any() < 0.6:
                        # Low conf detection
                        shutil.copy(img, sorted_data_output+"FN_TP/conf_lt_pt6/")
                    elif yolo_scores.any() < 0.7 or retina_scores.any() < 0.7:
                        # Low conf detection
                        shutil.copy(img, sorted_data_output+"FN_TP/conf_lt_pt7/")
                    elif yolo_scores.any() < 0.8 or retina_scores.any() < 0.8:
                        # Low conf detection
                        shutil.copy(img, sorted_data_output+"FN_TP/conf_lt_pt8/")
                    elif yolo_scores.any() < 0.9 or retina_scores.any() < 0.9:
                        # Low conf detection
                        shutil.copy(img, sorted_data_output+"FN_TP/conf_lt_pt9/")

                else:
                    # Yolo Detected but Retina didnt
                    # False Negative or False Positive
                    # Copy to folder
                    if yolo_scores.any() < 0.5:
                        # Low conf detection
                        shutil.copy(img, sorted_data_output + "FP_TN/yolo/conf_lt_pt5/")
                    elif yolo_scores.any() < 0.6:
                        # Low conf detection
                        shutil.copy(img, sorted_data_output + "FP_TN/yolo/conf_lt_pt6/")
                    elif yolo_scores.any() < 0.7:
                        # Low conf detection
                        shutil.copy(img, sorted_data_output + "FP_TN/yolo/conf_lt_pt7/")
                    elif yolo_scores.any() < 0.8:
                        # Low conf detection
                        shutil.copy(img, sorted_data_output + "FP_TN/yolo/conf_lt_pt8/")
                    elif yolo_scores.any() < 0.9:
                        # Low conf detection
                        shutil.copy(img, sorted_data_output + "FP_TN/yolo/conf_lt_pt9/")


            elif hazmat_metrics_retina["num_hazmat_labels"] > 0:
                retina_scores = hazmat_metrics_retina["hazmat_scores"]

                if hazmat_metrics_yolo["num_hazmat_labels"] > 0:
                    yolo_scores = hazmat_metrics_yolo["hazmat_scores"]
                    if yolo_scores.any() < 0.5 or retina_scores.any() < 0.5:
                        # Low conf detection
                        shutil.copy(img, sorted_data_output + "FN_TP/conf_lt_pt5/")
                    elif yolo_scores.any() < 0.6 or retina_scores.any() < 0.6:
                        # Low conf detection
                        shutil.copy(img, sorted_data_output + "FN_TP/conf_lt_pt6/")
                    elif yolo_scores.any() < 0.7 or retina_scores.any() < 0.7:
                        # Low conf detection
                        shutil.copy(img, sorted_data_output + "FN_TP/conf_lt_pt7/")
                    elif yolo_scores.any() < 0.8 or retina_scores.any() < 0.8:
                        # Low conf detection
                        shutil.copy(img, sorted_data_output + "FN_TP/conf_lt_pt8/")
                    elif yolo_scores.any() < 0.9 or retina_scores.any() < 0.9:
                        # Low conf detection
                        shutil.copy(img, sorted_data_output + "FN_TP/conf_lt_pt9/")

                else:
                    # Retina Detected but Yolo didnt
                    # False Negative or False Positive
                    # Copy to folder
                    if retina_scores.any() < 0.5:
                        # Low conf detection
                        shutil.copy(img, sorted_data_output + "FP_TN/retina/conf_lt_pt5/")
                    elif retina_scores.any() < 0.6:
                        # Low conf detection
                        shutil.copy(img, sorted_data_output + "FP_TN/retina/conf_lt_pt6/")
                    elif retina_scores.any() < 0.7:
                        # Low conf detection
                        shutil.copy(img, sorted_data_output + "FP_TN/retina/conf_lt_pt7/")
                    elif retina_scores.any() < 0.8:
                        # Low conf detection
                        shutil.copy(img, sorted_data_output + "FP_TN/retina/conf_lt_pt8/")
                    elif retina_scores.any() < 0.9:
                        # Low conf detection
                        shutil.copy(img, sorted_data_output + "FP_TN/retina/conf_lt_pt9/")
        except:
            pass

if __name__ == "__main__":
    # pkl_file = "/home/garveyer/ECIP-Application_feature_nvidia_dali_enhancements/notebooks/cv2_warp_results.pickle"
    # cv2_results = load_cv2_warp_results(pkl_file)
    # print("num cv2 results: ", len(cv2_results))

    fp_glob = "/data/Hazmat_yolo_analysis/result_analysis/false_positives/*.tif"
    fp_filepaths = glob.glob(fp_glob)
    tp_glob = "/data/package-detection/hazmat_datasets/hazmat-yolov5-4.1/test_decks/test-data-rp-2022-12-10/positive_retina_detections_0p5/*.tif*"
    tp_filepaths = glob.glob(tp_glob)[:110]


    # Look at the tp and fp results and plot the confidence thresholds for each
    # check_fp_tp_results(tp_filepaths, fp_filepaths)

    # for now, this just loads both of the hazmat models (OG is retina net, and the new one is yolo)
    compare_hazmat_models(tp_filepaths)

    # Extract Data for retraining
    # Input Data Path
    # data_to_sort = "/data/MPE_images/PSM Images/unsorted_PSM_data/"
    # sorted_data_output = "/data/CVAT_data/not_uploaded_to_CVAT/"
    # sort_data_for_labeling(data_to_sort, sorted_data_output)
