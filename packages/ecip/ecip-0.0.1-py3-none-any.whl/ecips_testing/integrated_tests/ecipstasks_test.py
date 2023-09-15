# Test tasks Command
"""
from ecips_tasks import tasks
import json
import time
import os
import pickle
import cv2
import pandas as pd
from ecips_utils import ecips_config


def test_compute_feature_fromcv2():
    path = '/ecips_testing/ecips_test_files/results/ecip_features.dat'
    impath = '/ecips_testing/ecips_test_files/raw_images/003506.png'
    algorithm = ecips_config.ECIPS_REVERSE_IMAGE_ALGORITHM
    path = os.environ['WORKSPACE'] + path
    impath = os.environ['WORKSPACE'] + impath

    img = cv2.imread(impath)
    if algorithm != 'pysift':
        with open(path, "rb") as f:
            true_kp, true_desc = pickle.load(f)
            true_pts = cv2.KeyPoint_convert(true_kp)
        kp, desc = tasks.compute_feature_fromcv2(img)
        pts = cv2.KeyPoint_convert(kp)
        true_pts = pd.DataFrame(true_pts)
        pts = pd.DataFrame(pts)
        true_desc = pd.DataFrame(true_desc)
        desc = pd.DataFrame(desc)
    else:
        with open(path, "rb") as f:
            true_pts, true_desc = pickle.load(f)
        pts, desc = tasks.compute_feature_fromcv2(img)

    assert (true_pts.sum() == pts.sum()).all(), "extracted points are not equal"
    # assert (true_desc == desc).all().all(), "descriptors not equal"


def test_compute_feature_from_filepath_celery():
    ground_truth_path = os.environ['WORKSPACE'] + "/ecips_testing/ecips_test_files/results/003506.json"
    file_path = "/ECIPs/ecips_testing/ecips_test_files/raw_images/003506.png"

    with open(ground_truth_path) as json_file:
        ground_truth = json.load(json_file)

    result_delay = tasks.compute_feature_from_filepath.delay(file_path, False)
    time.sleep(5)
    result = result_delay.get(timeout=5)

    result.pop('img_filepath', None)
    result.pop('dateProcessed', None)
    result.pop('year', None)
    result.pop('month', None)
    result.pop('day', None)
    result.pop('mpe_device', None)
    ground_truth.pop('img_filepath', None)
    ground_truth.pop('dateProcessed', None)
    ground_truth.pop('year', None)
    ground_truth.pop('month', None)
    ground_truth.pop('day', None)
    ground_truth.pop('mpe_device', None)

    assert result == ground_truth


def test_convert_results_toparquet():
    status = tasks.convert_results_toparquet()
    assert status == 0, "conversion failed"
"""
