'''test the utils functions'''

# from ecips_utils import ecips_logging
from ecips_utils.imageProcessing import binarizeInputImage
from ecips_utils import ecips_config
import os
# import cv2


def test_binarize_input_image():
    '''tests the binarizeInputImage function'''

    image_path = os.environ['WORKSPACE'] + '/ecips_testing/ecips_test_files/raw_images/003668.png'
    # groundTruth = '/ECIPs/ecips_testing/ecips_test_files/binarized_images/003697.png'
    # groundTruth = cv2.imread(groundTruth)

    output_image = None
    kernel_size = 2
    adaptive_thresholding = True
    global_thresholding = False
    binarize_erode = ecips_config.BINARIZE_ERODE
    binarize_dilate = ecips_config.BINARIZE_DILATE
    # kernel_size = # Set erosion and dilation kernel size

    assert isinstance(kernel_size, int), 'Wrong type'
    assert isinstance(adaptive_thresholding, bool), 'Wrong type'
    assert isinstance(global_thresholding, bool), 'Wrong type'
    assert isinstance(binarize_erode, bool), 'Wrong type'
    assert isinstance(binarize_dilate, bool), 'Wrong type'
    assert isinstance(image_path, str), 'Wrong type'
    assert image_path[-4:] in '.png' or image_path[-5:] in '.jpeg' or image_path[-4:] in '.jpg',\
        'Unsupported extensions'
    output_image = binarizeInputImage.binarizeInputImage(image_path, kernel_size, adaptive_thresholding,
                                                         global_thresholding, binarize_erode, binarize_dilate)
    assert output_image is not None, "Program error"
    # assert np.equal(outputImage, groundTruth) , "Program error"
    return output_image


# def test_logging_config(logging_path=ecips_config.LOGGING_PATH, logging_level=ecips_config.LOGGING_LEVEL):
#     '''tests the logging_config function'''
#
#     assert isinstance(logging_path, str), 'Wrong type'
#     assert isinstance(logging_level, int), 'Wrong type'
#     assert logging_path[-8:] == '/logging', 'Not saving to logging directory'
#     logging = None
#     logging = ecips_logging.logging_config()
#     assert logging is not None, "Program error"
#     return logging
