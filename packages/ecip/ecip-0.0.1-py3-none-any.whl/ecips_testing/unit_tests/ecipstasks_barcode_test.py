# from ecips_tasks.tasks_barcode import (prep_nms, nms,
#                                        adjust_detections)
# from ecips_tasks.concate_digits import validate_barcode
# import numpy as np
# from ecips_utils import ecips_config
# import pickle
# import os

# MAX_SIZE = ecips_config.ECIPS_INFERENCE_MAX_SIZE


# def test_validate_barcode():
#     barcode = "9400110200883923734923"
#     valid = validate_barcode(barcode)
#     assert isinstance(valid, bool), "validaton function failed to return the appropriate type"
#     return valid


# """
# def test_preprocess():
#     impath = '/images/APBS-1/2020-06-02/01-004/01-000/03/20200602034504_010219011.tif'
#     img = cv2.imread(os.environ['WORKSPACE'] + impath)
#     image_data = [tasks_barcode.preprocess(img, np.float32)]
#     assert np.equal(image_data[0][2], img).all(), "returned oimg is different from img"
#     assert image_data[0][0].shape[1:] == (3, MAX_SIZE, MAX_SIZE), "returned wrong shape for image"
#     return image_data
# """


# def test_prep_nms_bar():
#     path = os.environ['WORKSPACE'] + "/ecips_testing/ecips_test_files/bar_inference_files/result_barcode.dat"
#     with open(path, "rb") as f:
#         result_barcode = pickle.load(f)

#     # post process detected barcode
#     barcode_array = prep_nms(result_barcode, model='bar')

#     assert (isinstance(barcode_array, type(np.array([1])))) or isinstance(barcode_array, None), """
#     preparation function failed"""


# def test_nms_bar():
#     path = os.environ['WORKSPACE'] + "/ecips_testing/ecips_test_files/bar_inference_files/barcode_array.dat"
#     with open(path, "rb") as f:
#         barcode_array = pickle.load(f)

#     if barcode_array is not None:
#         selected_boxes, scores, classes, idx = nms(barcode_array)
#         assert len(idx) >= 1, "no candidate boxes detected nms failed"


# def test_adjust_detections():
#     path = os.environ['WORKSPACE'] + "/ecips_testing/ecips_test_files/bar_inference_files/adjust_detections_data.dat"
#     with open(path, "rb") as f:
#         selected_boxes, scores, classes, idx = pickle.load(f)

#     path = os.environ['WORKSPACE'] + "/ecips_testing/ecips_test_files/bar_inference_files/image_data.dat"
#     with open(path, "rb") as f:
#         image_data = pickle.load(f)

#     ratios = image_data[0][1]
#     barcode_detections = adjust_detections(selected_boxes, scores, classes, idx, ratios)
#     keys = list(barcode_detections.keys())
#     assert ('box' in keys) or (isinstance(barcode_detections, None)), """
#     barcode_detections does not have a box key or was not returned as a none object.
#     barcode_array is likely None type"""
#     return barcode_detections


# """
# def test_cropbarcode():
#     path = os.environ['WORKSPACE'] + "/ecips_testing/ecips_test_files/bar_inference_files/barcode_detections.dat"
#     with open(path, "rb") as f:
#         barcode_detections = pickle.load(f)

#     path = os.environ['WORKSPACE'] + "/ecips_testing/ecips_test_files/bar_inference_files/image_data.dat"
#     with open(path, "rb") as f:
#         image_data = pickle.load(f)

#     input_batch_raw = [image_data[0][2]]

#     cropped_batch = tasks_barcode.cropbarcode([input_batch_raw[0]], barcode_detections, np.float32)
#     assert cropped_batch[0].shape[1:] == (3, MAX_SIZE, MAX_SIZE), "wrong dimensions returned"
#     return cropped_batch
# """


# def test_prep_nms_dig():
#     path = os.environ['WORKSPACE'] + "/ecips_testing/ecips_test_files/bar_inference_files/result_digits.dat"
#     with open(path, "rb") as f:
#         result_digits = pickle.load(f)

#     digit_array = prep_nms(result_digits, model='digits')
#     assert (isinstance(digit_array, type(np.array([1])))) or isinstance(digit_array, None), "prep function failed"


# def test_nms_dig():
#     path = os.environ['WORKSPACE'] + "/ecips_testing/ecips_test_files/bar_inference_files/digit_array.dat"
#     with open(path, "rb") as f:
#         digit_array = pickle.load(f)

#     selected_boxes, scores, classes, idx = nms(digit_array, model='digits')
#     if digit_array is not None:
#         selected_boxes, scores, classes, idx = nms(digit_array)

#         assert len(idx) >= 1, "no candidate boxes detected nms failed"

#         return selected_boxes, scores, classes, idx
