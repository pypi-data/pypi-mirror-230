# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#  * Neither the name of NVIDIA CORPORATION nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import json
import cv2
import os
import copy
import numpy as np
import math
# triton_python_backend_utils is available in every Triton Python model. You
# need to use this module to create inference requests and responses. It also
# contains some utility functions for extracting information from model_config
# and converting Triton input/output types to numpy types.
import triton_python_backend_utils as pb_utils

# Rotation Constants based on analysis conducted 7/7/2023 on the relationship between letter indicators and IMPBs
LETTER_TO_IMPB_REL_ANGLE = 70.0  # degrees
ROTATE_90_THRESH = LETTER_TO_IMPB_REL_ANGLE  # 70 degrees
ROTATE_180_THRESH = LETTER_TO_IMPB_REL_ANGLE + 90.0  # 160 degrees
ROTATE_270_THRESH = LETTER_TO_IMPB_REL_ANGLE + 180.0  # 250 degrees
NO_ROTATION_THRESH = LETTER_TO_IMPB_REL_ANGLE + 270.0  # 340 degrees


def get_crop_args(box, theta, shift, apply_rotation=True, edge_condition=False, has_orientation=False):
    """
    The get crop args function takes the bounding box of the detection and the estimated relative location of
    the letter indicator to the IMPB box to return the rotation matrix that will be used to crop the label from
    the over all image.  It also takes an optional shift argument which should be set to true to perform a relative
    shift from the letter indicator to the mail class banner.

    Args:
        box (np.array): the bounding box of the label
        shift (bool): The True of False boolean value if we should perform a relative shift to the mail class banner
        theta (int): rotation angle of the vector connecting the impb centroid to the letter indicator centroid
        apply_rotation (bool): Defaults to True. This is the flag that tells if it is okay to apply a rotation to the
            label based on the dimensions.  For IMPB, permit-imprint, and IBI labels this is true because they should
            always be wider than they are tall.  For letter indicators, we cannot make an orientation assumption based
            on the width or height because it is nearly square
        edge_condition (bool): Defaults to False. This flag determines if an edge condition has already been detected.
            In this context, an edge condition occurs when we close to two possible orientation configurations and need
            to check the label dimensions to determine the correct orientation.
        has_orientation (bool): Defaults to False. This flag determines if the package label has an inferred
            orientation. This is True for cases that have BOTH an IMPB and a letter indicator and False otherwise.
    Returns:
        M (np.array): the extracton matrix for the label
        dims (np.array): the dimensions of the label in (h, w) format
        rotate (float): The rotation angle that should be applied by the dali_crop_gpu model.
            Should be in [0, 90, 180, 270]
        edge_condition (bool): (T/F) if the edge condition (described above) was detected on the label.  This value will
            propagate to other labels on the package since not all labels can be used to identify an edge condition.
    """

    # Get the height and width of the bbox dimensions
    height = dist(box[0], box[1])
    width = dist(box[1], box[2])

    # Get the matrix, bbox dimensions and rotation flag
    if has_orientation:
        M, dims, rotate, edge_condition = get_matrix(box, width, height, shift, theta, apply_rotation, edge_condition)
    else:
        M, dims, rotate = get_unoriented_matrix(box, width, height, apply_rotation)

    dims = np.array(dims)
    dims = np.expand_dims(dims, axis=0)
    dims = np.array([[dims[0][1], dims[0][0]]], dtype='float32')

    return M, dims, rotate, edge_condition


def get_matrix(box, width, height, shift, theta=None, apply_rotation=True, edge_condition=False):
    """
    the get_matrix function will return the rotation matrix of a label component as well as the size and
    a rotation flag.

    Args:
        box (np.array): the bounding box of the label
        width (int): the width of the label
        height (int): the height of the label
        shift (bool): The True of False boolean value if we should perform a relative shift to the mail class banner
        theta (int): rotation angle of the vector connecting the impb centroid to the letter indicator centroid
        apply_rotation (bool): Defaults to True. This is the flag that tells if it is okay to apply a rotation to the
            label based on the dimensions.  For IMPB, permit-imprint, and IBI labels this is true because they should
            always be wider than they are tall.  For letter indicators, we cannot make an orientation assumption based
            on the width or height because it is nearly square
        edge_condition (bool): Defaults to False. This flag determines if an edge condition has already been detected.
            In this context, an edge condition occurs when we close to two possible orientation configurations and need
            to check the label dimensions to determine the correct orientation.


    Returns:
        M (np.array): the rotation matrix to extract the label from the original image
        dims (np.array): the dimensions of the final bbox
        rotate (np.array): Angle to rotate the bbox. 0 if no rotation.  90 if a 90degree rotation
        edge_condition (bool): Defaults to False. This flag determines if an edge condition has already been detected.
            In this context, an edge condition occurs when we close to two possible orientation configurations and need
            to check the label dimensions to determine the correct orientation.

    """

    # The source points (original box location)
    src_pts = box.astype("float32")
    # The destination points (final box location)
    dst_pts = np.array([[0, height - 1],
                        [0, 0],
                        [width - 1, 0],
                        [width - 1, height - 1]], dtype="float32")

    # Affine transformation from source to destination
    M = cv2.getAffineTransform(src_pts[0:3], dst_pts[0:3])

    if theta <= ROTATE_90_THRESH or theta > (ROTATE_90_THRESH - 90) % 360:
        if not apply_rotation and not edge_condition:
            rotate = 90.0
        else:
            if not edge_condition and height > width:
                # In this orientation, height SHOULD be gt width, if not we have an edge condition
                rotate = 90.0
            else:
                edge_condition = True
                # edge condition, check if we are closer to the 180 or NO rotation thresholds
                if abs(theta - ROTATE_90_THRESH) < abs((theta - NO_ROTATION_THRESH) % 360):
                    # apply the 180 rotation
                    rotate = 180.0
                else:
                    # apply no rotation
                    rotate = 0.0

    elif theta <= ROTATE_180_THRESH:
        if not apply_rotation and not edge_condition:
            rotate = 180.0
        else:
            if not edge_condition and height < width:
                rotate = 180.0
            else:
                edge_condition = True
                # edge condition, check if we are closer to the 90 or 180 rotation thresholds
                if abs(theta - ROTATE_180_THRESH) > abs(theta - ROTATE_90_THRESH):
                    # apply the 90 rotation
                    rotate = 90.0
                else:
                    # apply 270 rotation
                    rotate = 270.0

    elif theta <= ROTATE_270_THRESH:
        if not apply_rotation and not edge_condition:
            rotate = 270.0
        else:
            if not edge_condition and height > width:
                # In this orientation, height SHOULD be gt width, if not we have an edge condition
                rotate = 270.0
            else:
                # edge condition, check if we are closer to the 180 or 270 rotation thresholds
                edge_condition = True
                if abs(theta - ROTATE_180_THRESH) < abs(theta - ROTATE_270_THRESH):
                    # apply the 180 rotation
                    rotate = 180.0
                else:
                    # apply no rotation
                    rotate = 0.0

    else:
        if not apply_rotation and not edge_condition:
            rotate = 0.0
        else:
            if not edge_condition and height < width:
                rotate = 0.0

            else:
                # edge condition, check if we are closer to the 270 or no rotation thresholds
                edge_condition = True
                if abs(theta - ROTATE_270_THRESH) > abs(theta - NO_ROTATION_THRESH):
                    # apply the 90 rotation
                    rotate = 90.0
                else:
                    # apply 270 rotation
                    rotate = 270.0

    # If we want to shift to the mail class banner, adjust the matrix
    if shift:
        M, width, height, dali_rotation = get_banner_matrix(M, height, width, rotate)
        # We apply rotation when we extract, not sure why, but it changes the dali rotation angle
        rotate = dali_rotation

    M = np.expand_dims(M, axis=0)
    dims = (width, height)

    return M, dims, rotate, edge_condition


def get_unoriented_matrix(box, width, height, apply_rotation=True):
    """
    the get_matrix function will return the rotation matrix of a label component as well as the size and
    a rotation flag.

    Args:
        box (np.array): the bounding box of the label
        width (int): the width of the label
        height (int): the height of the label
        apply_rotation (bool): Defaults to True. This is the flag that tells if it is okay to apply a rotation to the
            label based on the dimensions.  For IMPB, permit-imprint, and IBI labels this is true because they should
            always be wider than they are tall.  For letter indicators, we cannot make an orientation assumption based
            on the width or height because it is nearly square

    Returns:
        M (np.array): the rotation matrix to extract the label from the original image
        dims (np.array): the dimensions of the final bbox
        rotate (np.array): Angle to rotate the bbox. 0 if no rotation.  90 if a 90degree rotation

    """
    # The source points (original box location)
    src_pts = box.astype("float32")
    # The destination points (final box location)
    dst_pts = np.array([[0, height - 1],
                        [0, 0],
                        [width - 1, 0],
                        [width - 1, height - 1]], dtype="float32")

    # Affine transformation from source to destination
    M = cv2.getAffineTransform(src_pts[0:3], dst_pts[0:3])
    M = np.expand_dims(M, axis=0)
    dims = (width, height)

    if height > width and apply_rotation:
        rotate = 90.0
    else:
        rotate = 0.0

    return M, dims, rotate


# def get_image_rotation(theta, anticipated_orientation, edge_condition,
#                        anticipated_rotation, edge_condition_rotation_1,
#                        edge_condition_rotation_2, edge_condition_threshold_1,
#                        edge_condition_threshold_2):
#     """
#     The get image rotation function returns the correct rotation angle that should be applied tothe
#     dali crop gpu pipeline such that the label is always in the upright orientation
#
#     Args:
#         theta (float): the angle created by the vector that connects the impb to the letter indicator
#         anticipated_orientation (bool): T/F value if the label is in the anticipated orientation. For rotations
#             at 0.0 or 180 degrees, the anticipated orientation is horizantal (h<w).  For rotations at 90.0 or 270,
#             the anticipated orientation is vertical (h>w)
#         edge_condition (bool): T/F value if the label has met an edge condition where it may be close to more than one
#         anticipated rotations.  If this flag is true, we check for other cases to determine the appropriate rotation
#         edge_condition_rotation_1 (float): The rotation to apply if edge condition 1 is met
#         edge_condition_rotation_2 (float): The rotation to apply if edge condition 2 is met
#         edge_condition_threshold_1 (float): The threshold at which edge condition 1 is met
#         edge_condition_threshold_2 (float): The threshold at which edge condition 2 is met
#
#
#     Returns:
#         rotation_angle (float): The angle that the label should be rotated by in the Dali crop gpu pipeline.  Must be
#         0.0, 90.0, 180.0 or 270.0
#         edge_condition (bool): T/F if an edge condition was detected. Propagates to other labels on the package
#     """
#     if not edge_condition and anticipated_orientation:
#         rotation_angle = anticipated_rotation
#
#     else:
#         # edge condition, check which condition threshold is closer, then apply that rotation
#         edge_condition = True
#         if abs(theta - edge_condition_threshold_1) > abs(theta - edge_condition_threshold_2):
#             # apply the edge condition 2 rotation
#             rotation_angle = edge_condition_rotation_2
#         else:
#             # apply the edge condition 1 rotation
#             rotation_angle = edge_condition_rotation_1
#
#     return rotation_angle, edge_condition


def get_banner_matrix(M, height, width, rotation_angle):
    """
    the get_banner_matrix function shifts the original label extraction matrix to a new location specific to the
    mail class banner and returns the new matrix

    Args:
        M (np.array): the rotation matrix to extract the label from the original image
        height (int): the height of the original label
        width (int): the width of the original label
        rotation_angle (float): rotation angle of the vector connecting the impb centroid to the letter indicator
            centroid

    Returns:
        M (np.array): the new rotation matrix to extract the label from the original image
        height (int): the new height of the original label
        width (int): the new width of the original label
        dali_rotation (float): The rotation angle that should be sent to Dali.  Depending on the configuration,
            this varies
    """
    theta = rotation_angle * (math.pi / 180)
    max_dim = height if height > width else width

    if rotation_angle == 0.0:  # TR
        x_shift = 0.0
        y_shift = -0.85
        dali_rotation = 0.0

    elif rotation_angle == 90.0:
        x_shift = 3.5
        y_shift = 0.35
        dali_rotation = 180.0

    elif rotation_angle == 180.0:
        x_shift = 1.0
        y_shift = 0.05
        dali_rotation = 0.0

    else:
        x_shift = 2.6
        y_shift = 1.35
        dali_rotation = 180

    width = int(3.75 * max_dim)
    height = int(0.5 * max_dim)
    M = get_transition_matrix(M, theta, max_dim, y_shift, x_shift)

    return M, width, height, dali_rotation


def get_transition_matrix(M, theta, max_dim, y_shift, x_shift):
    """
    The get_transition_matrix takes the original matrix and a series of transformation values and
        returns the new extraction matrix with transforms applied

    Args:
        M (np.array): the original matrix
        theta (float): rotation of the extraction
        max_dim (int): The max dimension of the label, either w or h.
        y_shift (float): how far to shift in the y direction
        x_shift (float): how far to shift in the x direction

    Returns:
        M_shift (np.array): the translated matrix

    """
    trans_mat = np.array([[math.cos(theta), -1 * math.sin(theta), x_shift * max_dim],
                          [math.sin(theta), math.cos(theta), y_shift * max_dim],
                          [0, 0, 1]])
    M_shift = np.vstack((copy.copy(M), [0, 0, 1]))

    # combine the transforms
    M_shift = (np.matmul(trans_mat, M_shift))
    M_shift = M_shift[:2, :]

    return M_shift


def dist(point_1, point_2):
    """
    Returns the absolute distance between two points
    """
    distance = math.sqrt(((int(point_1[0]) - int(point_2[0])) ** 2) + ((int(point_1[1]) - int(point_2[1])) ** 2))
    return distance


def reorganize_boxes_and_classes(confident_label_boxes, confident_label_classes, classes_to_sort):
    """
    The purpose of this function is to reorganize the confidence_label_boxes and classes such that
    mail class letter detections are always last.  This is because we need to process the other classes first
    in order to set the correct orientation

    Args:
        confident_label_boxes (np.array): An array of the label boxes
        confident_label_classes (np.array): An array of the label classes
        classes_to_sort (list): The classes that will be arranged into last position

    Returns:
        confident_label_boxes_out (np.array): An array of the label boxes after rearranging
        confident_label_classes_out (np.array): An array of the label classes after rearranging
    """
    confident_label_boxes_out = copy.copy(confident_label_boxes)
    confident_label_classes_out = copy.copy(confident_label_classes)

    for i, (box, cls_id) in enumerate(zip(confident_label_boxes, confident_label_classes)):
        if cls_id in classes_to_sort:
            # Remove the class from its current location and append to the end
            confident_label_boxes_out = np.delete(confident_label_boxes_out, i, axis=0)
            confident_label_boxes_out = np.concatenate((confident_label_boxes_out, [box]), axis=0)
            # Remove the class from its current location and append to the end
            confident_label_classes_out = np.delete(confident_label_classes_out, i, axis=0)
            confident_label_classes_out = np.concatenate((confident_label_classes_out, [cls_id]), axis=0)

    return confident_label_boxes_out, confident_label_classes_out


def get_location_vector(impb_box, letter_box):
    """
    Get the location vector that describes the relationship between the impb box and the letter box

    Args:
        impb_box (np.array): the bounding box of the IMPB box
        letter_box (np.array): the bounding box of the IMPB box

    Returns:
        impb_cent (list(float)): The xy coordinates of the impb box centroid
        letter_cent (list(float)): The xy coordinates of the letter box centroid
        r (float): The r-vector in polar coordinates between the two centroids
        theta (float): The rotational angle in polar coordinates between the two centroids

    """
    if impb_box is None or letter_box is None:
        # neither can be none
        # no impb box found to determine rel loc
        return None, None, None, 0.0

    impb_cent = centroid(impb_box)
    letter_cent = centroid(letter_box)

    r, theta = cart_to_pol(letter_cent[0], letter_cent[1], impb_cent[0], impb_cent[1])

    return impb_cent, letter_cent, r, theta


def centroid(points):
    """
    Returns the centroid point of a group of points
    """
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]

    _len = len(points)

    centroid_x = sum(x_coords) / _len
    centroid_y = sum(y_coords) / _len

    return [centroid_x, centroid_y]


def cart_to_pol(x, y, x_c=0, y_c=0, deg=True):
    """
    converts cartesian to polar coordinates

    Center defaults to 0,0 but can optionally be updated
    """
    complex_format = x - x_c + 1j * (y - y_c)
    return np.abs(complex_format), np.angle(complex_format, deg=deg) % 360


# Functions Defined by Dave to get the return address location. Not currently in ise but may be useful in the future
def get_crop_args_return_address(box, theta, shift, apply_rotation=True, edge_condition=False, has_orientation=False):
    """
    The get crop args function takes the bounding box of the detection and the estimated relative location of
    the letter indicator to the IMPB box to return the rotation matrix that will be used to crop the label from
    the over all image.  It also takes an optional shift argument which should be set to true to perform a relative
    shift from the letter indicator to the mail class banner.

    Args:
        box (np.array): the bounding box of the label
        shift (bool): The True of False boolean value if we should perform a relative shift to the mail class banner
        theta (int): rotation angle of the vector connecting the impb centroid to the letter indicator centroid
        apply_rotation (bool): Defaults to True. This is the flag that tells if it is okay to apply a rotation to the
            label based on the dimensions.  For IMPB, permit-imprint, and IBI labels this is true because they should
            always be wider than they are tall.  For letter indicators, we cannot make an orientation assumption based
            on the width or height because it is nearly square
        edge_condition (bool): Defaults to False. This flag determines if an edge condition has already been detected.
            In this context, an edge condition occurs when we close to two possible orientation configurations and need
            to check the label dimensions to determine the correct orientation.
        has_orientation (bool): Defaults to False. This flag determines if the package label has an inferred
            orientation. This is True for cases that have BOTH an IMPB and a letter indicator and False otherwise.
    Returns:
        M (np.array): the extracton matrix for the label
        dims (np.array): the dimensions of the label in (h, w) format
        rotate (float): The rotation angle that should be applied by the dali_crop_gpu model.
            Should be in [0, 90, 180, 270]
        edge_condition (bool): (T/F) if the edge condition (described above) was detected on the label.  This value will
            propagate to other labels on the package since not all labels can be used to identify an edge condition.
    """

    # Get the height and width of the bbox dimensions
    height = dist(box[0], box[1])
    width = dist(box[1], box[2])

    # Get the matrix, bbox dimensions and rotation flag
    if has_orientation:
        M, dims, rotate, edge_condition = get_matrix_return_addr(box, width, height, shift, theta, apply_rotation,
                                                                 edge_condition)
    else:
        M, dims, rotate = get_unoriented_matrix(box, width, height, apply_rotation)

    dims = np.array(dims)
    dims = np.expand_dims(dims, axis=0)
    dims = np.array([[dims[0][1], dims[0][0]]], dtype='float32')

    return M, dims, rotate, edge_condition


def get_matrix_return_addr(box, width, height, shift, theta=None, apply_rotation=True, edge_condition=False):
    """
    the get_matrix function will return the rotation matrix of a label component as well as the size and
    a rotation flag.

    Args:
        box (np.array): the bounding box of the label
        width (int): the width of the label
        height (int): the height of the label
        shift (bool): The True of False boolean value if we should perform a relative shift to the mail class banner
        theta (int): rotation angle of the vector connecting the impb centroid to the letter indicator centroid
        apply_rotation (bool): Defaults to True. This is the flag that tells if it is okay to apply a rotation to the
            label based on the dimensions.  For IMPB, permit-imprint, and IBI labels this is true because they should
            always be wider than they are tall.  For letter indicators, we cannot make an orientation assumption based
            on the width or height because it is nearly square
        edge_condition (bool): Defaults to False. This flag determines if an edge condition has already been detected.
            In this context, an edge condition occurs when we close to two possible orientation configurations and need
            to check the label dimensions to determine the correct orientation.


    Returns:
        M (np.array): the rotation matrix to extract the label from the original image
        dims (np.array): the dimensions of the final bbox
        rotate (np.array): Angle to rotate the bbox. 0 if no rotation.  90 if a 90degree rotation
        edge_condition (bool): Defaults to False. This flag determines if an edge condition has already been detected.
            In this context, an edge condition occurs when we close to two possible orientation configurations and need
            to check the label dimensions to determine the correct orientation.

    """

    # The source points (original box location)
    src_pts = box.astype("float32")
    # The destination points (final box location)
    dst_pts = np.array([[0, height - 1],
                        [0, 0],
                        [width - 1, 0],
                        [width - 1, height - 1]], dtype="float32")

    # Affine transformation from source to destination
    M = cv2.getAffineTransform(src_pts[0:3], dst_pts[0:3])

    if theta <= ROTATE_90_THRESH or theta > (ROTATE_90_THRESH - 90) % 360:
        if not apply_rotation and not edge_condition:
            rotate = 90.0
        else:
            if not edge_condition and height > width:
                # In this orientation, height SHOULD be gt width, if not we have an edge condition
                rotate = 90.0
            else:
                edge_condition = True
                # edge condition, check if we are closer to the 180 or NO rotation thresholds
                if abs(theta - ROTATE_90_THRESH) < abs((theta - NO_ROTATION_THRESH) % 360):
                    # apply the 180 rotation
                    rotate = 180.0
                else:
                    # apply no rotation
                    rotate = 0.0

    elif theta <= ROTATE_180_THRESH:
        if not apply_rotation and not edge_condition:
            rotate = 180.0
        else:
            if not edge_condition and height < width:
                rotate = 180.0
            else:
                edge_condition = True
                # edge condition, check if we are closer to the 90 or 180 rotation thresholds
                if abs(theta - ROTATE_180_THRESH) > abs(theta - ROTATE_90_THRESH):
                    # apply the 90 rotation
                    rotate = 90.0
                else:
                    # apply 270 rotation
                    rotate = 270.0

    elif theta <= ROTATE_270_THRESH:
        if not apply_rotation and not edge_condition:
            rotate = 270.0
        else:
            if not edge_condition and height > width:
                # In this orientation, height SHOULD be gt width, if not we have an edge condition
                rotate = 270.0
            else:
                # edge condition, check if we are closer to the 180 or 270 rotation thresholds
                edge_condition = True
                if abs(theta - ROTATE_180_THRESH) < abs(theta - ROTATE_270_THRESH):
                    # apply the 180 rotation
                    rotate = 180.0
                else:
                    # apply no rotation
                    rotate = 0.0

    else:
        if not apply_rotation and not edge_condition:
            rotate = 0.0
        else:
            if not edge_condition and height < width:
                rotate = 0.0

            else:
                # edge condition, check if we are closer to the 270 or no rotation thresholds
                edge_condition = True
                if abs(theta - ROTATE_270_THRESH) > abs(theta - NO_ROTATION_THRESH):
                    # apply the 90 rotation
                    rotate = 90.0
                else:
                    # apply 270 rotation
                    rotate = 270.0

    # If we want to shift to the mail class banner, adjust the matrix
    if shift:
        M, width, height, dali_rotation = get_addr_matrix(M, height, width, rotate)
        # We apply rotation when we extract, not sure why, but it changes the dali rotation angle
        rotate = dali_rotation

    M = np.expand_dims(M, axis=0)
    dims = (width, height)

    return M, dims, rotate, edge_condition


def get_addr_matrix(M, height, width, rotation_angle, debug=False):
    """
    the get_banner_matrix function shifts the original label extraction matrix to a new location specific to the
    mail class banner and returns the new matrix

    Args:
        M (np.array): the rotation matrix to extract the label from the original image
        height (int): the height of the original label
        width (int): the width of the original label
        rotation_angle (float): rotation angle of the vector connecting the impb centroid to the letter indicator
            centroid

    Returns:
        M (np.array): the new rotation matrix to extract the label from the original image
        height (int): the new height of the original label
        width (int): the new width of the original label
        dali_rotation (float): The rotation angle that should be sent to Dali.  Depending on the configuration,
            this varies
    """
    theta = rotation_angle * (math.pi / 180)
    if debug:
        print(f"{theta}")
        print(f"{rotation_angle}")

    max_dim = height if height > width else width

    if rotation_angle == 0.0:  # TR
        x_shift = 0.30
        y_shift = -1.12
        dali_rotation = 0.0

    elif rotation_angle == 90.0:
        x_shift = 1.9
        y_shift = 1.2
        dali_rotation = 180.0

    elif rotation_angle == 180.0:
        x_shift = 1.0
        y_shift = 0.05
        dali_rotation = 0.0

    else:
        x_shift = 1.0
        y_shift = 2.0
        dali_rotation = 180

    width = int(2.0 * max_dim)
    height = int(1 * max_dim)
    if debug:
        print(f"{width}")
        print(f"{height}")

    M = get_transition_matrix(M, theta, max_dim, y_shift, x_shift)

    return M, width, height, dali_rotation


class TritonPythonModel:
    """Your Python model must use the same class name. Every Python model
    that is created must have "TritonPythonModel" as the class name.
    """

    def initialize(self, args):
        """`initialize` is called only once when the model is being loaded.
        Implementing `initialize` function is optional. This function allows
        the model to intialize any state associated with this model.

        Parameters
        ----------
        args : dict
          Both keys and values are strings. The dictionary keys and values are:
          * model_config: A JSON string containing the model configuration
          * model_instance_kind: A string containing model instance kind
          * model_instance_device_id: A string containing model instance device ID
          * model_repository: Model repository path
          * model_version: Model version
          * model_name: Model name
        """
        self.logger = pb_utils.Logger

        # You must parse model_config. JSON string is not parsed here
        self.model_config = model_config = json.loads(args["model_config"])

        # Get configurations
        matrix_out_config = pb_utils.get_output_config_by_name(model_config, "matrix_out")
        # Convert Triton types to numpy types
        self.matrix_out_dtype = pb_utils.triton_string_to_numpy(
            matrix_out_config["data_type"]
        )
        cropped_label_classes_config = pb_utils.get_output_config_by_name(model_config, "cropped_label_classes")
        # Convert Triton types to numpy types
        self.cropped_label_classes_dtype = pb_utils.triton_string_to_numpy(
            cropped_label_classes_config["data_type"]
        )
        dims_out_config = pb_utils.get_output_config_by_name(model_config, "dims_out")
        # Convert Triton types to numpy types
        self.dims_out_dtype = pb_utils.triton_string_to_numpy(
            dims_out_config["data_type"]
        )

        img_out_config = pb_utils.get_output_config_by_name(model_config, "img")
        # Convert Triton types to numpy types
        self.img_dtype = pb_utils.triton_string_to_numpy(
            img_out_config["data_type"]
        )

        rotation_out_config = pb_utils.get_output_config_by_name(model_config, "rotation_out")
        # Convert Triton types to numpy types
        self.rotation_out_dtype = pb_utils.triton_string_to_numpy(
            rotation_out_config["data_type"]
        )

        orientation_out_config = pb_utils.get_output_config_by_name(model_config, "label_orientations")
        # Convert Triton types to numpy types
        self.orientation_dtype = pb_utils.triton_string_to_numpy(
            orientation_out_config["data_type"]
        )

        self.mean = np.array([0.485, 0.456, 0.406])
        self.std = np.array([0.229, 0.224, 0.225])
        # different YOLO classes have different detection confidences
        self.detection_confidence = json.loads(os.getenv("SHIPPING_LABEL_MODEL_SCORE_THRES",
                                                         default='''
                                                         {"0": "0.65",
                                                         "1": "0.65",
                                                         "2": "0.65",
                                                         "3": "0.65",
                                                         "4": "0.65",
                                                         "5": "0.65",
                                                         "6": "0.65",
                                                         "7": "0.65",
                                                         "8": "0.65",
                                                         "9": "0.65",
                                                         "10": "0.4",
                                                         "11": "0.4",
                                                         "12": "0.64",
                                                         "13": "0.4",
                                                         "14": "0.4",
                                                         "15": "0.4",
                                                         "16": "0.6",
                                                         "17": "0.55",
                                                         "18": "0.4",
                                                         "19": "0.4",
                                                         "20": "0.65",
                                                         "21": "0.90"
                                                         }
                                                         '''
                                                         ))
        # Convert json string format requirements to {int: float}
        self.detection_confidence = {int(class_id): float(self.detection_confidence[class_id])
                                     for class_id in self.detection_confidence}

        self.labels_to_extract = json.loads(os.getenv("SHIPPING_LABEL_MODEL_LABELS_TO_CROP",
                                                      default="[5, 7, 2, 6, 10, 1, 17, 16, 18,21]"))
        self.mail_class_letter_classes = json.loads(os.getenv("SHIPPING_LABEL_MODEL_MAILCLASSLETTER_CLASSES",
                                                    default="[5, 6, 16, 17, 18,21]"))
        self.impb_barcode_classes = json.loads(os.getenv("SHIPPING_LABEL_MODEL_IMPB_CLASSES",
                                                         default="[2, 1]"))
        self.MCB_LABEL_ID = json.loads(os.getenv("SHIPPING_LABEL_MODEL_MCB_CLASS_ID",
                                                 default="99"))

    def validate_mailclass_letter(self, box):

        height = dist(box[0], box[1])
        width = dist(box[1], box[2])

        if width > height:
            ratio = height / width
        else:
            ratio = width / height

        if ratio < .8:  # thought here, the label should be pretty square (ratio ~= 1)
            return False

        return True

    def intersects(self, box1, box2):

        (x1, y1), r1 = cv2.minEnclosingCircle(box1)
        (x2, y2), r2 = cv2.minEnclosingCircle(box2)

        center_dist = dist([x1, y1], [x2, y2])
        radius_sum = r1 + r2

        if center_dist > radius_sum:
            return False
        return True
        # x_left = max(box1[0][0], box2[0][0])
        # y_top = max(box1[2][1], box2[2][1])
        # x_right = min(box1[2][0], box2[2][0])
        # y_bottom = min(box1[0][1], box2[0][1])
        #
        # if x_right < x_left or y_bottom < y_top:
        #     return False
        # return True

    def check_double_detection(self, classes, boxes, scores):
        classes = np.intp(classes)
        # check for more than one IMPB
        impb_detections = []
        mailclass_letter_detections = []
        for cls in self.impb_barcode_classes:
            impb_detections = np.concatenate((impb_detections, np.where(classes == cls)[0]))

        if len(impb_detections) > 1:
            for i in range(0, len(impb_detections)-1):
                box1 = boxes[int(impb_detections[i])]
                score1 = scores[int(impb_detections[i])]
                box2 = boxes[int(impb_detections[i + 1])]
                score2 = scores[int(impb_detections[i + 1])]

                if score1 < self.detection_confidence[int(impb_detections[i])] \
                        or score2 < self.detection_confidence[int(impb_detections[i])]:
                    continue

                if not self.intersects(box1, box2):
                    return True

        for cls in self.mail_class_letter_classes:
            mailclass_letter_detections = np.concatenate((mailclass_letter_detections, np.where(classes == cls)[0]))

        if len(mailclass_letter_detections) > 1:
            for i in range(0, len(mailclass_letter_detections) - 1):
                box1 = boxes[int(mailclass_letter_detections[i])]
                score1 = scores[int(mailclass_letter_detections[i])]
                box2 = boxes[int(mailclass_letter_detections[i + 1])]
                score2 = scores[int(mailclass_letter_detections[i + 1])]

                if score1 < self.detection_confidence[int(mailclass_letter_detections[i])] \
                        or score2 < self.detection_confidence[int(mailclass_letter_detections[i])]:
                    continue

                if not self.intersects(box1, box2):
                    return True

        return False

    def execute(self, requests):
        """`execute` MUST be implemented in every Python model. `execute`
        function receives a list of pb_utils.InferenceRequest as the only
        argument. This function is called when an inference request is made
        for this model. Depending on the batching configuration (e.g. Dynamic
        Batching) used, `requests` may contain multiple requests. Every
        Python model, must create one pb_utils.InferenceResponse for every
        pb_utils.InferenceRequest in `requests`. If there is an error, you can
        set the error argument when creating a pb_utils.InferenceResponse

        Parameters
        ----------
        requests : list
          A list of pb_utils.InferenceRequest

        Returns
        -------
        list
          A list of pb_utils.InferenceResponse. The length of this list must
          be the same as `requests`
        """

        responses = []

        # Every Python backend must iterate over everyone of the requests
        # and create a pb_utils.InferenceResponse for each of them.
        for request in requests:

            img = pb_utils.get_input_tensor_by_name(request, "img_bytestring_in").as_numpy()[0]
            scores = pb_utils.get_input_tensor_by_name(request, "scores_in").as_numpy()[0].squeeze()
            boxes = pb_utils.get_input_tensor_by_name(request, "boxes_in").as_numpy()[0].squeeze()
            classes = pb_utils.get_input_tensor_by_name(request, "classes_in").as_numpy()[0].squeeze()

            identity_matrix = np.array([[1, 0, 0],
                                        [0, 1, 0]])

            cropped_classes = np.full((20, 1), -1, dtype='uint8')
            M_array = np.full((20, 2, 3), identity_matrix, dtype='float32')
            dims_array = np.ones((20, 2), dtype='float32')
            img_array = np.full((20, img.size), img)
            rotation_array = np.zeros((20, 1), dtype='float16')
            # maybe here we do a check of double detections?
            double_detection = self.check_double_detection(classes, boxes, scores)
            self.logger.log_verbose(f"\nDouble Detection found: {double_detection}")

            i = 0
            mcl_box = None
            impb_box = None
            edge_condition = False
            most_confident_mailclass = 0
            orientation_array = 0

            confident_label_boxes = np.zeros((20, 4, 2), dtype='float32')
            confident_label_classes = np.zeros((20, 1), dtype='float32')

            if not double_detection:
                for box, cls, score in zip(boxes, classes, scores):
                    class_id = int(cls)
                    if score > self.detection_confidence[class_id]:
                        if cls in self.labels_to_extract:
                            confident_label_boxes[i] = box
                            confident_label_classes[i] = cls
                            i += 1

                            if cls in self.mail_class_letter_classes:
                                # check that mailclass is valid shape and not cropped
                                if not self.validate_mailclass_letter(box):
                                    continue

                                # take the most confident mail class letter
                                if most_confident_mailclass >= score:
                                    continue
                                most_confident_mailclass = score
                                mcl_box = box

                            if cls in self.impb_barcode_classes:
                                impb_box = box

                if i == 0:
                    i = 1
                confident_label_boxes = confident_label_boxes[:i]
                confident_label_classes = confident_label_classes[:i]

                # Get the vector that describes the orientation of the package
                # based on the relative location of the letter code and IMPB labels
                _, _, r, theta = get_location_vector(impb_box, mcl_box)
                # If we have an r vector, we were able to derive orientation, otherwise we dont know the orientation
                orientation_array = 1 if r else 0
                has_orientation = bool(orientation_array)

                # We need to ensure that we process the mailclass banner related classes last in order to
                # Extract the correct orientation in the even of an edge condition
                confident_label_boxes, \
                    confident_label_classes = reorganize_boxes_and_classes(confident_label_boxes,
                                                                           confident_label_classes,
                                                                           self.mail_class_letter_classes
                                                                           )
                i = 0
                for label_box, label_class in zip(confident_label_boxes, confident_label_classes):
                    shift_to_banner = False
                    if label_class in self.mail_class_letter_classes:
                        # First extract the letter indicator, iterate by one, and extract the banner
                        M_array[i], dims_array[i], \
                            rotation_array[i], edge_condition = get_crop_args(label_box, theta,
                                                                              shift=shift_to_banner,
                                                                              apply_rotation=False,
                                                                              edge_condition=edge_condition,
                                                                              has_orientation=has_orientation)
                        cropped_classes[i] = label_class
                        img_array[i] = img
                        i += 1

                        if has_orientation:
                            # We ONLY want to extract the banner matrix if we know the orientation
                            # If not, we cannot trust this extraction, so we should skip it
                            M_array[i], dims_array[i], \
                                rotation_array[i], edge_condition = get_crop_args(label_box, theta,
                                                                                  shift=True,
                                                                                  apply_rotation=False,
                                                                                  edge_condition=edge_condition,
                                                                                  has_orientation=has_orientation)
                            # We need to define a new ID for the mail class banner since it is not a yolo detection
                            cropped_classes[i] = self.MCB_LABEL_ID
                            img_array[i] = img
                            i += 1
                        continue

                    M_array[i], dims_array[i], \
                        rotation_array[i], edge_condition = get_crop_args(label_box, theta,
                                                                          shift=shift_to_banner,
                                                                          edge_condition=edge_condition,
                                                                          has_orientation=has_orientation)
                    cropped_classes[i] = label_class
                    img_array[i] = img
                    i += 1

            if i == 0:
                i = 1

            # trim the results according to the number of labels we processed
            cropped_classes = cropped_classes[:i]
            M_array = M_array[:i]
            dims_array = dims_array[:i]
            rotation_array = rotation_array[:i]
            img_array = img_array[:i]

            out_matrix = pb_utils.Tensor(
                "matrix_out", M_array.astype(self.matrix_out_dtype)
            )
            out_dims = pb_utils.Tensor(
                "dims_out", dims_array.astype(self.dims_out_dtype)
            )
            out_rotation = pb_utils.Tensor(
                "rotation_out", rotation_array.astype(self.rotation_out_dtype)
            )
            out_classes = pb_utils.Tensor(
                "cropped_label_classes", cropped_classes.astype(self.cropped_label_classes_dtype)
            )
            out_img = pb_utils.Tensor(
                "img", img_array.astype(self.img_dtype)
            )
            out_orientation = pb_utils.Tensor(
                "label_orientations", np.array(orientation_array).astype(self.orientation_dtype)
            )

            inference_response = pb_utils.InferenceResponse(output_tensors=[out_matrix, out_dims, out_rotation,
                                                                            out_classes, out_img, out_orientation])
            responses.append(inference_response)

        return responses

    def finalize(self):
        """`finalize` is called only once when the model is being unloaded.
        Implementing `finalize` function is OPTIONAL. This function allows
        the model to perform any necessary clean ups before exit.
        """
        print("Cleaning up...")
