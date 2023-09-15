import glob
import time

import numpy as np
import cv2
import sys
sys.path.append("/home/garveyer/ECIP-Application_release/ecips_serving/models/postprocessing_yolo/2/")
from model import non_max_suppression, scale_boxes, tlbrbltl_from_xyxy, HAZMAT_IMG_DIMS, MAX_DET, IOU_THRESH, CONF_THRESH
import torch
import torchvision
import tkinter
from scipy import ndimage as ndi
# from ._ccomp import label_cython as clabel
import torch.nn.functional as F
import matplotlib
matplotlib.use('tkagg')
from matplotlib import pyplot as plt

from ecips_triton_ensemble import ECIPsApplicationTritonModels
# from ultralytics import YOLO

shipping_label_names = {0: 'background',
                        1: 's10',
                        2: 'impb',
                        3: 'address-block',
                        4: 'pvi',
                        5: 'first-class',
                        6: 'priority',
                        7: 'ibi',
                        8: 'imb',
                        9: 'address-block-handwritten',
                        10: 'permit-imprint',
                        11: 'Lithium_UN_Label',
                        12: 'No_Fly',
                        13: 'Finger_Large',
                        14: 'Finger_Small',
                        15: 'Cargo_Air_Only',
                        16: 'hazmat',
                        17: 'express',
                        18: 'fcm',
                        19: 'Cremated_Remains'}
detection_conf = 0.25
iou = 0.75
agnostic_nms = False
max_det = 300
nc = len(shipping_label_names)
classes = None

if __name__ == "__main__":
    pkl_file = "/home/garveyer/ECIP-Application_feature_nvidia_dali_enhancements/notebooks/cv2_warp_results.pickle"

    filepath_glob = "/data/BCR/test_deck/*.tif*"
    filepaths = glob.glob(
            "/data/Fraud/datasets/validation_set/v1.0.2/ALL_IMAGES/APBS-4/2022-10-04/04-438/11/*.tif")

    start_time = time.time()
    ecips_serving_models = ECIPsApplicationTritonModels(hostname="localhost:8004")
    onnx_model_path = "/data/package-detection/yolov8/train15/weights/best.pt"
    # onnx_model = YOLO(onnx_model_path)

    for filename in filepaths:
        # filename = '/home/garveyer/data/images/test/20230510_00_263707833019701_T.tif'
        og_img = cv2.imread(filename)
        # loaded_img = cv2.resize(og_img, (640, 640))
        # loaded_img = loaded_img.astype(np.float32)
        # loaded_img /= 255.
        # loaded_img = loaded_img.reshape((3, 640, 640))
        # loaded_img = np.expand_dims(loaded_img, axis=0)

        loaded_img = ecips_serving_models.dali_load_img(filename)
        preprocessed_img, og_dims, rot = ecips_serving_models.dali_preprocessing_hazmat(loaded_img)
        predictions = ecips_serving_models.hazmat_yolov5(preprocessed_img)
        # predictions = [out1, out2]/

        detections = non_max_suppression(predictions, CONF_THRESH, IOU_THRESH,
                                              classes=None, multi_label=True, max_det=MAX_DET)
        dimensions = HAZMAT_IMG_DIMS

        scores = np.zeros((len(detections), 100, 1, 1))
        classes = np.zeros((len(detections), 100, 1, 1))
        boxes = np.zeros((len(detections), 400, 4, 2))

        for batch, img_detections in enumerate(detections):  # parses through images
            if not img_detections.any():
                scores, boxes, classes = ecips_serving_models.postprocessing_yolo(predictions, og_dims, rot)
                if (scores[0] > 0.25).any():
                    print("Error:")
                else:
                    continue
            img_detections[:, :4] = scale_boxes(dimensions, img_detections[:, :4], og_dims[0]).round()

            for det_i, (*xyxy, conf, cls) in enumerate(reversed(img_detections)):
                xyxy = np.array(xyxy).reshape(2, 2).tolist()
                box_out = tlbrbltl_from_xyxy(xyxy[0], xyxy[1])  # of form (TR, BR, BL, TL) shape is (4,2)

                scores[batch, det_i] = conf
                classes[batch, det_i] = cls
                boxes[batch, det_i] = box_out


        # cv2.imwrite("/home/garveyer/data/images/test/test_filepath_contours.jpeg", og_img)
        # results = onnx_model(filename)

        # plt.figure(0)
        # plt.imshow(results[0].plot(), cmap='gray')
        # plt.show()
