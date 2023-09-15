# Define function 'binarizeInputImage.py'
import cv2
import numpy as np
from ecips_utils import ecips_config as ecips_config


def binarizeInputImage(imagePath,
                       kernel_size=2,
                       adaptive_thresholding=True,
                       global_thresholding=False,
                       binarize_erode=ecips_config.BINARIZE_ERODE,
                       binarize_dilate=ecips_config.BINARIZE_DILATE):
    # kernel_size = # Set erosion and dilation kernel size

    # Create erosion and dilation kernel
    kernel = np.ones((kernel_size, kernel_size), np.uint8)

    # Read in the image
    im = cv2.imread(imagePath)

    # Convert color image to grayscale
    img = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    # Global thresholding
    if global_thresholding:
        ret, th1 = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)

    # Adaptive thresholding
    if adaptive_thresholding:
        outputImage = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                            cv2.THRESH_BINARY, 11, 3)
    # cv.imwrite('/data/Media_Images/test_bin2.jpg',theshIm)

    # Erode image
    if binarize_erode:
        outputImage = cv2.erode(outputImage, kernel, iterations=1)

    # Dilate image
    if binarize_dilate:
        outputImage = cv2.dilate(outputImage, kernel, iterations=1)

    # Return image
    return outputImage
