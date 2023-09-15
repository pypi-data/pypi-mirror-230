import json
# import math
# import time
# from pathlib import Path

import numpy as np
import torch
# import torch.nn as nn
# import torchvision
# import triton_python_backend_utils as pb_utils
from models.experimental import attempt_load
from utils.general import check_img_size, non_max_suppression, scale_coords
from utils.torch_utils import TracedModel
from ecips_triton_ensemble import ECIPsApplicationTritonModels

MODEL_PT = "/home/garveyer/ECIP-Application/ecips_serving/yolov7_models/best.pt"
IMGSZ = 896


if __name__ == "__main__":
    if torch.cuda.is_available():
        # need to run only once to load model into memory
        device = torch.device('cuda:0')  # to be configured? defaulting to 0
        half = device.type != 'cpu'
        model = attempt_load(MODEL_PT, map_location=device)

        # Running as a Trace Model
        # try:
        model = TracedModel(model, device, IMGSZ)
        # except:
        #     pass

        if half:
            model.half()
        stride = int(model.stride.max())  # model stride
        imgsz = check_img_size(IMGSZ, s=stride)  # check img_size
    else:
        raise AssertionError(f"Cuda is not available, unable to run the hazmat torch model \n"
                             f"Status of torch.cuda.is_available(): {torch.cuda.is_available()}")

    # Define model variables
    augment = False
    conf_thresh = 0.25
    iou_thresh = 0.45
    classes = range(22)

    if device.type != 'cpu':
        model(torch.zeros(1, 3, IMGSZ, IMGSZ).to(device).type_as(next(model.parameters())))

    # Warmup the gpu during initialization
    warmup_img = np.random.rand(3, 896, 896)
    # warmup_img.astype("float32")
    warmup_img = torch.from_numpy(warmup_img).to(device)
    warmup_img = warmup_img.half() if half else warmup_img.float()
    warmup_img /= 255.0
    if warmup_img.ndimension() == 3:
        warmup_img = warmup_img.unsqueeze(0)
    for i in range(3):
        model(warmup_img, augment=augment)[0]

    positive_hazmat_img = "/data/Hazmat/datasets/hazmat-v1.4.8_rc1-model/data/raw_data/all_real_images/1_00037365T.tiff"
    ecips_models = ECIPsApplicationTritonModels()
    loaded_img = ecips_models.dali_load_img(positive_hazmat_img)
    img, img_size = ecips_models.dali_preprocessing(loaded_img)

    img = torch.from_numpy(img[0]).to(device)
    img = img.half() if half else img.float()  # uint8 to fp16/32
    img_size = img_size[0]
    # img /= 255.0  # 0 - 255 to 0.0 - 1.0
    if img.ndimension() == 3:
        img = img.unsqueeze(0)

    # Inference without gradients (can cause memory leak)
    with torch.no_grad():
        pred = model(img, augment)[0]

    # Apply NMS
    pred_nms = non_max_suppression(pred, conf_thresh, iou_thresh)

    boxes = np.zeros((100, 4))
    classes = np.zeros(100)
    scores = np.zeros(100)
    dets = np.zeros(1)

    for i, det in enumerate(pred_nms):  # detections per image
        # If we have detections that were made, rescale based on the original image size
        if len(det):
            # Rescale boxes from img_size to im0 size
            det[:, :4] = scale_coords(img.shape[2:], det[:, :4], img_size).round()
            # Write results
            det_index = 0
            for *xyxy, conf, cls in reversed(det):
                boxes[det_index] = [coord_val.cpu() for coord_val in xyxy]
                classes[det_index] = cls.cpu()
                scores[det_index] = conf.cpu()
                dets[0] += 1
                det_index += 1

    print(scores)
    print(boxes)
    print(classes)
