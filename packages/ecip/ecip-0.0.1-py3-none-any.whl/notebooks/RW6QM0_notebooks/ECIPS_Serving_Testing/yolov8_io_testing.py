import glob
import time

import numpy as np
import cv2
import sys
sys.path.append("/home/garveyer/ECIP-Application_release/ecips_serving/models/postprocessing_yolov8/2/")
from model import postprocess_yolov8_results, scale_image, scale_boxes, SHIPPING_LABEL_IMG_DIMS
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
        preprocessed_img, og_dims = ecips_serving_models.dali_preprocessing_yolov8(loaded_img)
        out1, out2 = ecips_serving_models.shipping_label_yolov8(preprocessed_img)
        predictions = [out1, out2]

        ecip_boxes, ecip_masks = postprocess_yolov8_results(predictions, og_dims[0])
        dimensions = SHIPPING_LABEL_IMG_DIMS
        # ecip_masks = scale_segments([640, 640], ecip_masks, og_dims[0])
        # ecip_masks = ecip_masks.reshape((ecip_masks.shape[1], ecip_masks.shape[2], ecip_masks.shape[0]))
        # if ecip_masks.shape[0] > 0:
        #     ecip_masks = scale_image([640, 640], ecip_masks, og_dims[0])

        for box, mask in zip(ecip_boxes, ecip_masks):
            time_4 = time.time()
            xy, y1, x2, y2, conf, class_id = box
            mask_bool = mask.astype(np.uint8) * 255
            contours, _ = cv2.findContours(mask_bool, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            time_5 = time.time()

            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                time_6 = time.time()
                rectangle = cv2.minAreaRect(largest_contour)
                time_7 = time.time()
                box_pts = cv2.boxPoints(rectangle)
                time_8 = time.time()
                # Scale the boxes up accordingly
                # boxes = np.array([box_pts[0][0], box_pts[0][1], box_pts[2][0], box_pts[2][1]])
                box_pts_scaled = scale_boxes(dimensions, box_pts, og_dims[0])

                # scores[i] = conf
                # classes[i] = class_id
                # boxes[i] = box_pts
                time_9 = time.time()

            else:  # No contours were found
                print("No Contours were found: ", flush=True)
                # scores[i] = 0.0
                # classes[i] = 0.0
                # boxes[i] = np.zeros((4, 2))
                time_6 = time.time()
                time_7 = time_6
                time_8 = time_6
                time_9 = time_6

            print(f"Time to find contours: {1000 * (time_5 - time_4)} ms", flush=True)
            print(f"Time to get max contours: {1000 * (time_6 - time_5)} ms", flush=True)
            print(f"Time to get min area rect: {1000 * (time_7 - time_6)} ms ", flush=True)
            print(f"Time to get box points: {1000 * (time_8 - time_7)} ms", flush=True)
            print(f"Time to convert to .numpy(): {1000 * (time_9 - time_8)} ms", flush=True)

        # cv2.imwrite("/home/garveyer/data/images/test/test_filepath_contours.jpeg", og_img)
        # results = onnx_model(filename)

        # plt.figure(0)
        # plt.imshow(results[0].plot(), cmap='gray')
        # plt.show()
