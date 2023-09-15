import numpy as np
import math
from shapely.geometry import Polygon
import cv2
import logging

try:
    import cupy as cp
except Exception:
    logging.info("Cuda not supported")

# preproc
MEAN = 255 * np.array([0.485, 0.456, 0.406])
STD = 255 * np.array([0.229, 0.224, 0.225])


def preprocess(oimg, dtype, width, height):
    """
    This function preprocess an image using a mix of gpu and cpu.
    Input:
        oimg - original image to be processed
        dtype - data type necessary for barcode model
    Output:
        processed_img - new image following preprocessing
        oimg - original image to be processed
    """

    img = cv2.resize(oimg, (width, height))

    img = cp.asarray(img)
    img = (img - cp.asarray(MEAN)) / cp.asarray(STD)
    swapped = cp.moveaxis(img, 2, 0)
    img = cp.expand_dims(swapped, 0)
    img = cp.asnumpy(img)

    return img.astype(dtype), oimg


def cropbarcode(img_batch, detections, dtype, bar_w, bar_h, dig_w, dig_h):
    """
    This function crops an image from the proposed barcode region given by the barcode model.
    Input:
        img_batch - list containing a single image to be manipulated
        detections - detections obtained from the barcode model
        dtype - the dtype expected by the digit model
    Output:
        cropped_img - the image cropped to the barcode region
    """

    for img in img_batch:
        ratio = [img.shape[0] / bar_w, img.shape[1] / bar_h]
        bbox = detections["box"][0]
        bbox[-1] *= 180 / np.pi

        # Get source points for barcode
        bbox = (
            (bbox[0] + bbox[2] / 2, bbox[1] + bbox[3] / 2),
            (bbox[2], bbox[3]),
            bbox[4],
        )
        box = cv2.boxPoints(bbox)
        box[:, 0] *= ratio[1]
        box[:, 1] *= ratio[0]
        box = np.int0(box)
        src_pts = box.astype("float32")

        # Get height and width of barcode
        height = int(bbox[1][1] * ratio[1])
        width = int(bbox[1][0] * ratio[0])

        # corrdinate of the points in box points after the rectangle has been
        # straightened
        dst_pts = np.array(
            [[0, height - 1], [0, 0], [width - 1, 0], [width - 1, height - 1]],
            dtype="float32",
        )

        # the perspective transformation matrix
        M = cv2.getPerspectiveTransform(src_pts, dst_pts)

        # directly warp the rotated rectangle to get the straightened rectangle
        img = cv2.warpPerspective(img, M, (width, height))
        img = cv2.resize(img, (dig_w, dig_h))
        img = cp.asarray(img)
        img = (img - cp.asarray(MEAN)) / cp.asarray(STD)

        swapped = cp.moveaxis(img, 2, 0)
        img = cp.expand_dims(swapped, 0)
        img = cp.asnumpy(img)

    return [img.astype(dtype)]


def convert_box(box):
    """
    This function takes a model derived region proposal and returns a formal bbox.

    Input:
        box - box proposed by models.

    Output:
        bbox - of form [x1, y1, w, h, theta] or [x1, y1, w, h]
    """
    if len(box) == 6:
        x1, y1, x2, y2, theta = [
            box[0],
            box[1],
            box[2],
            box[3],
            np.arctan2(box[4], box[5]),
        ]
        w = x2 - x1 + 1
        h = y2 - y1 + 1
        return [x1, y1, w, h, theta]
    else:
        x1, y1, x2, y2 = [box[0], box[1], box[2], box[3]]
        w = x2 - x1 + 1
        h = y2 - y1 + 1
        return [x1, y1, w, h]


def build_box(box):
    """
    Builds bounding box from corrdinates supplied.

    Inputs:
        box - of form [x1,y1,w,h,theta] or [x1,y1,w,h]

    Outputs:
        bbox - bounding box with 4 corner points.
    """

    # assign points
    x1 = box[0]
    y1 = box[1]
    x2 = x1 + box[2]
    y2 = y1 - box[3]

    # build box
    if len(box) == 4:
        bbox = [(x1, y1), (x1, y2), (x2, y2), (x2, y1)]

    else:
        theta = box[4]
        rot_mat = np.array(
            [[math.cos(theta), -math.sin(theta)], [math.sin(theta), math.cos(theta)]]
        )

        # rotate points
        x11 = x1 * rot_mat[0][0] + y1 * rot_mat[0][1]
        y11 = x1 * rot_mat[1][0] + y1 * rot_mat[1][1]

        # (x1,y2)
        x12 = x1 * rot_mat[0][0] + y2 * rot_mat[0][1]
        y12 = x1 * rot_mat[1][0] + y2 * rot_mat[1][1]

        # (x2,y2)
        x22 = x2 * rot_mat[0][0] + y2 * rot_mat[0][1]
        y22 = x2 * rot_mat[1][0] + y2 * rot_mat[1][1]

        # (x2,y1)
        x21 = x2 * rot_mat[0][0] + y1 * rot_mat[0][1]
        y21 = x2 * rot_mat[1][0] + y1 * rot_mat[1][1]

        bbox = [(x11, y11), (x12, y12), (x22, y22), (x21, y21)]

    return bbox


def get_iou(boxA, boxB, model="bar"):
    """
    Calculate the Intersection over Union (IoU) of two bounding boxes.

    Parameters
    ----------
    boxA : list
        [x1,y1,w,h,theta] or [x1,y1,w,h]
    boxB : list
        [x1,y1,w,h,theta] or [x1,y1,w,h]

    Returns
    -------
    float
        in [0, 1]
    """

    # build box
    bb1 = build_box(boxA)
    bb2 = build_box(boxB)
    polygon1 = Polygon(bb1)
    polygon2 = Polygon(bb2)

    # calculate IoU
    intersection = polygon1.intersection(polygon2)
    union = polygon1.union(polygon2)
    iou = intersection.area / union.area

    return iou


def process_odtk_results(results, score_thres, resize=1280, max_size=1280, rotated=True):
    """
    This function inference results data and prepares it for post processing via nms
    Inputs:
        results - inference results from models
        score_thres - score threshold for filtering out candidates
        rotated - flag for dictating how data should be processed
    Output:
        array - object prepared for post processing via nms
    """
    scores = results["scores"][0].squeeze()
    classes = results["classes"][0].squeeze()
    boxes = results["boxes"][0].squeeze()
    attr_resize = results["attr_resize"][0].squeeze()
    ratio = resize / min(attr_resize)
    if ratio * max(attr_resize) > max_size:
        ratio = max_size / max(attr_resize)

    if rotated:
        scores, classes, boxes = process_odtk_rotated_result(
            scores, classes, boxes, score_thres, ratio=ratio
        )
    else:
        scores, classes, boxes = process_odtk_aligned_result(
            scores, classes, boxes, score_thres, ratio=ratio
        )

    if boxes is None:  # no box had a high enough score
        array = None
    elif len(scores) == 1:
        array = np.concatenate((boxes, scores, classes), axis=1)
    else:
        array = np.concatenate((boxes, scores, classes), axis=1)
        # sort array by box scores
        array = array[np.argsort(-array[:, -2], kind="quicksort")]
    return array


def process_odtk_rotated_result(scores, classes, boxes, score_thres, ratio=1):
    # certain models are always exported with the rotated flag
    # rotated variables are x0, y0, x1, y1, xangle, yangle
    boxes = np.array([boxes[i: i + 6] for i in range(0, len(boxes), 6)])
    boxes[:4] /= ratio
    # filter candidate boxes
    indices = np.where(scores > score_thres)[0]
    logging.debug(indices)
    if len(indices) > 0:
        scores = scores[indices].reshape(-1, 1)
        classes = classes[indices].reshape(-1, 1)
        # Converts boxes to x0, y0, w, h, theta
        boxes = np.apply_along_axis(convert_box, 1, boxes)
        boxes = boxes[indices]
    else:
        scores = None
        classes = None
        boxes = None

    return scores, classes, boxes


def process_odtk_aligned_result(scores, classes, boxes, score_thres, ratio=1):
    # certain models are never exported with the rotated flag
    # If not rotated variables are x,y, w, h

    boxes = np.array([boxes[i: i + 4] for i in range(0, len(boxes), 4)])
    boxes[:4] /= ratio
    indices = np.where(scores > score_thres)[0]
    logging.debug(indices)
    if len(indices) > 0:
        scores = scores[indices].reshape(-1, 1)
        classes = classes[indices].reshape(-1, 1)
        boxes = boxes[indices]
    else:
        scores = None
        classes = None
        boxes = None

    return scores, classes, boxes


def prep_nms(results, score_thres, rotated=True):
    """
    This function inference results data and prepares it for post processing via nms
    Inputs:
        results - inference results from models
        score_thres - score threshold for filtering out candidates
        rotated - flag for dictating how data should be processed
    Output:
        array - object prepared for post processing via nms
    """
    scores = results["scores"][0].squeeze()
    classes = results["classes"][0].squeeze()
    boxes = results["boxes"][0].squeeze()

    if rotated:
        # certain models are always exported with the rotated flag
        boxes = np.array([boxes[i: i + 6] for i in range(0, len(boxes), 6)])

        # filter candidate boxes
        indices = np.where(scores > score_thres)
        scores = scores[indices].reshape(-1, 1)
        classes = classes[indices].reshape(-1, 1)
        boxes = np.apply_along_axis(convert_box, 1, boxes)
        boxes = boxes[indices]
    else:
        # certain models are never exported with the rotated flag
        boxes = [boxes[i: i + 4] for i in range(0, len(boxes), 4)]
        indices = np.where(scores > score_thres)
        scores = scores[indices].reshape(-1, 1)
        classes = classes[indices].reshape(-1, 1)
        boxes = np.apply_along_axis(convert_box, 1, boxes)
        boxes = boxes[indices]

    if len(boxes) == 0:  # no box had a high enough score
        array = None
    else:
        array = np.concatenate((boxes, scores, classes), axis=1)
        # sort array by box scores
        array = array[np.argsort(-array[:, -2], kind="quicksort")]
    return array


def nms(array, iou_thres, rotated=True, out_dict=True, sort_bar=False):
    """
    This function is an implementation of non-maximum suppression

    Inputs:
        array - a numpy array containing the candidate boxes with associated scores, and classes
        iou_thres - iou threshold to use
        rotated - flag indicating if input data has a rotation field
        out_dict -  flag indicating if the output should be a dict object. Else a list is returned
        sort_bar - flag inidcating to sort the output per digit model output needs
    Outputs:
        filtered down list of candidate boxes and associated scores, in dictionary or list form.
    """
    skip_boxes = []
    scope = array.shape[0] - 1
    for index in range(scope):
        if index in skip_boxes:
            continue
        else:
            if not rotated:
                # get ious
                ious = [
                    get_iou(array[index][0:4], array[index2][0:4])
                    for index2 in range(index + 1, scope)
                ]

                # keep track of boxes that can be pruned
                skip_boxes.extend(
                    [i + index for i in range(len(ious)) if ious[i] > iou_thres]
                )

            else:
                # get ious
                ious = [
                    get_iou(array[index][0:5], array[index2][0:5])
                    for index2 in range(index + 1, scope)
                ]

                # keep track of boxes that can be pruned
                skip_boxes.extend(
                    [i + index for i in range(len(ious)) if ious[i] > iou_thres]
                )

    # prune candidate boxes
    final_array = np.delete(array, skip_boxes, axis=0)
    if sort_bar:
        # set in proper order
        final_array = final_array[np.argsort(final_array[:, 0], kind="quicksort")]

    # prepare for return
    if len(final_array) == 1:
        candidate_boxes = np.array([final_array[0][:-2]])
        classes = np.array([final_array[0][-1]])
        scores = np.array([final_array[0][-2]])
    else:
        for i in range(len(final_array)):
            if i == 0:
                candidate_boxes = np.array(final_array[i][:-2])
                classes = np.array(final_array[i][-1])
                scores = np.array([final_array[i][-2]])
            else:
                candidate_boxes = np.vstack((candidate_boxes, final_array[i][:-2]))
                classes = np.vstack((classes, final_array[i][-1]))
                scores = np.vstack((scores, final_array[i][-2]))

    if out_dict:
        # create output
        output = {"box": candidate_boxes, "class": classes, "score": scores}
        return output
    else:
        return candidate_boxes, classes, scores
