import copy
import glob
import time

import cv2
import matplotlib.pyplot as plt
import numpy as np

from ecips_triton_ensemble import BarcodeReconstructionEnsemble


def cv2_affine(img, bbox):
    # theta = bbox[-1]
    bbox[-1] *= 180 / np.pi
    bbox = ((bbox[0] + bbox[2] / 2, bbox[1] + bbox[3] / 2), (bbox[2], bbox[3]), bbox[4])

    box = cv2.boxPoints(bbox)
    box = np.int0(box)

    # buffer = 20  # buffer pixels
    width = int(bbox[1][0])  #
    height = int(bbox[1][1])

    src_pts = box.astype("float32")
    dst_pts = np.array([[0, height - 1],
                        [0, 0],
                        [width - 1, 0],
                        [width - 1, height - 1]], dtype="float32")

    M = cv2.getAffineTransform(src_pts[1:4], dst_pts[1:4])
    img = cv2.warpAffine(img, M, (width, height))

    return img


def get_crop_args_cv(bbox, og_dims, shift_to_address=False):
    # theta = bbox[-1]
    bbox[-1] *= 180 / np.pi
    # print("Theta (deg): ", bbox[-1])
    buffer = 0.08 * bbox[3]  # buffer is 8% of height
    # print("buffer:", buffer)
    bbox = ((bbox[0] + bbox[2] / 2, bbox[1] + bbox[3] / 2), (bbox[2] + buffer, bbox[3] + buffer), bbox[4])

    box = cv2.boxPoints(bbox)
    box = np.int0(box)

    width = int(bbox[1][0])
    height = int(bbox[1][1])

    #     theta = bbox[-1]
    # print("Theta (rad): ", theta)

    # TODO: Try to run affine transformation only once because it is compute intensive
    # TODO: Revisit the way we are adding in the buffer. Does it add buffer effectively?
    M, src = get_matrix_cv(box, width, height, shift_to_address)
    dims = np.array((width, height))
    dims = np.expand_dims(dims, axis=0)
    # print("Dims", dims)

    return M, dims, src


def get_matrix_cv(box, width, height, shift_to_address):
    src_pts = box.astype("float32")
    # print(src_pts)
    dst_pts = np.array([[0, height - 1],
                        [0, 0],
                        [width - 1, 0],
                        [width - 1, height - 1]], dtype="float32")
    # print(dst_pts)

    #     src_pts = np.array([src_pts[1], src_pts[0], src_pts[2]])
    #     dst_pts = np.array([dst_pts[1], dst_pts[0], dst_pts[2]])

    #     M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    #     print("Matrix: ", M)
    #     print("Width: ", width)
    #     print("Height ", height)
    #     M = M[:2, :]
    #     M = np.expand_dims(M, axis=0)

    #     print("source: ", src_pts)
    #     print("dst: ", dst_pts)

    M2 = cv2.getAffineTransform(src_pts[0:3], dst_pts[0:3])

    if shift_to_address:
        # print(f"width: {width}, height: {height}")
        trans_mat = np.array([[1, 0, 0],
                              [0, 1, height],
                              [0, 0, 1]])
        #         print(M2.shape)
        #         print(M2)
        M2 = np.vstack((M2, [0, 0, 1]))
        #         print(M2)

        # combine the transforms
        M2 = (np.matmul(trans_mat, M2))
        M2 = M2[:2, :]
    #         print(M2)
    #     M2 = np.expand_dims(M2, axis=0)
    # print("Matrix 2: ", M2)

    return M2, src_pts


def crop_args(score, box, ratio, image, shift_to_address, plot=False):
    og_img_dims = image.shape[1:3]
    # print(og_img_dims)
    if score > 0.5:
        box[:4] /= ratio
        x1, y1, x2, y2, theta = [box[0], box[1], box[2], box[3], np.arctan2(box[4], box[5])]
        w = x2 - x1 + 1
        h = y2 - y1 + 1
        _box = [x1, y1, w, h, theta]
        # print("_box: ", _box)
        #         M, dims, src = get_crop_args(_box, og_img_dims)
        M, dims, src = get_crop_args_cv(_box, og_img_dims, shift_to_address)

        # print("Using cv2 warp Perspective Transform")
        # cv2_image = cv2_warp_box(image, _box)
        # plt.imshow(cv2_image)
        # plt.show()

        # print("Using cv2 warp affine Transform")
        # affine_image = cv2_affine(image, _box)
        # plt.imshow(affine_image)
        # plt.show()

        image = np.stack([image for i in range(3)], axis=-1)
        # image = np.expand_dims(image, axis=0)
        # theta = theta * 180 / np.pi
        #         print("theta plot", theta)
        #         if theta > 90:
        #             theta = abs(theta - 180)
        #         print("theta plot", theta)
        #     print(theta * 180 / np.pi)
        #     image_2 = cv2.warpAffine(img, M, (w, h))

        if plot:
            plt.figure('og image')
            plt.imshow(image[0])
            #     print(src[0])
            #         plt.plot(x1, y1, marker='v', color='cyan')
            plt.plot(src[0][0], src[0][1], marker='x', color='red')
            plt.plot(src[1][0], src[1][1], marker='x', color='blue')
            plt.plot(src[2][0], src[2][1], marker='x', color='green')
            plt.plot(src[3][0], src[3][1], marker='x', color='yellow')

            plt.show()

    else:
        _box = [-1]
        image = np.zeros((1280, 1280, 3)).astype("uint8")
        M = np.random.rand(2, 3)

        dims = np.array([[100, 200]], dtype='int64')

    # image = image.astype('float32')
    M = M.astype('float32')
    M = np.expand_dims(M, axis=0)
    dims = dims.astype('float32')

    # print("Matrix dtype: ", M.dtype)
    # print("Matrix shape: ", M.shape)
    # print("Dims dtype: ", dims.dtype)
    # print("Dims shape: ", dims.shape)
    # print("Image dtype: ", image.dtype)
    # print("Image shape: ", image.shape)

    return image, M, dims


def run_ensemble(og_image):
    preprocessed_img, ratios = barcode_reconstruction_obj.preprocess()
    scores, boxes, classes = barcode_reconstruction_obj.barcode(preprocessed_img)
    #
    score = scores.flatten()[0]
    box = boxes.flatten()[0:6]
    ratio = ratios[0]
    # image1 = copy.copy(og_image)
    image, M, dims = crop_args(score, copy.copy(box), ratio, og_image, shift_to_address=False, plot=False)
    dims = np.array([[dims[0][1], dims[0][0]]])
    cropped_img_digits, cropped_img_pyzbar = barcode_reconstruction_obj.dali_crop_gpu(image, M, dims)

    # image2 = copy.copy(og_image)
    image_address, M_address, dims_address = crop_args(score, copy.copy(box), ratio, og_image, shift_to_address=True,
                                                       plot=False)
    dims_address = np.array([[dims_address[0][1], dims_address[0][0]]])
    cropped_img_digits, cropped_img_pyzbar_address = barcode_reconstruction_obj.dali_crop_gpu(image_address, M_address,
                                                                                              dims_address)

    return cropped_img_pyzbar_address, cropped_img_pyzbar


if __name__ == "__main__":
    filepath_glob = "/home/garveyer/data/Project_T_dataset/Domestic_barcodes/*.tif*"
    filepaths = glob.glob(filepath_glob)
    out_dir = "/data/Project_T_Dataset/AddressBlocks/"

    start_time = time.time()
    pyzbar_decodes = 0
    for filename in filepaths:
        print(filename)
        root_name = filename.split('/')[-1]
        barcode_reconstruction_obj = BarcodeReconstructionEnsemble(filename)
        # preprocessed_img, ratios = barcode_reconstruction_obj.preprocess()
        address_block, barcode_block = run_ensemble(barcode_reconstruction_obj.image)

        # plt.figure('address block')
        # plt.imshow(address_block[0])
        out_name = out_dir + root_name
        cv2.imwrite(out_name, address_block[0])

        # plt.figure('barcode')
        # plt.imshow(barcode_block[0])
        # plt.show()
