"""
# Test tasks Command
# import json
from ecips_tasks import tasks
# import os
# import cv2
# import pandas as pd
# import pickle


def test_compute_feature_from_filepath():
    file_path = os.environ['WORKSPACE'] + '/ecips_testing/ecips_test_files/raw_images/003668.png'
    ground_truth_path = os.environ['WORKSPACE'] + '/ecips_testing/ecips_test_files/results/003668.json'

    with open(ground_truth_path) as json_file:
        ground_truth = json.load(json_file)

    result = tasks.compute_feature_from_filepath(file_path, False)

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


def test_compute_feature_orb():
    path = '/ecips_testing/ecips_test_files/results/orb_output.dat'
    impath = '/ecips_testing/ecips_test_files/raw_images/003506.png'
    path = os.environ['WORKSPACE'] + path
    impath = os.environ['WORKSPACE'] + impath

    img = cv2.imread(impath)
    with open(path, "rb") as f:
        true_kp, true_desc = pickle.load(f)
        true_pts = cv2.KeyPoint_convert(true_kp)

    kp, desc = tasks.compute_feature_orb(img)
    pts = cv2.KeyPoint_convert(kp)
    true_pts = pd.DataFrame(true_pts)
    pts = pd.DataFrame(pts)
    true_desc = pd.DataFrame(true_desc)
    desc = pd.DataFrame(desc)

    assert (true_pts == pts).all().all(), "extracted points are not equal"
    assert (true_desc == desc).all().all(), "descriptors not equal"


def test_convert_days_results_toparquet():
    status = tasks.convert_days_results_toparquet()
    assert status == 0, "conversion failed"
"""
