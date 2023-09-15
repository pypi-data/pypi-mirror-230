import glob
import math
# import sys
import time

import cv2
import numpy as np

# sys.path.append("/home/garveyer/ECIP-Application_fraud_architecture/")
from ecips_utils.prlmProcessing.read_PRLM import PRLMFile

from ecips_triton_ensemble import ECIPsApplicationTritonModels

n = 6
resize = 800
max_size = 1280
mean = np.array([0.485, 0.456, 0.406])
std = np.array([0.229, 0.224, 0.225])
batch_size = 1

names = ['Lithium_UN_Label',
         'Lithium__Class_9',
         'Lithium_Battery_Label',
         'Biohazard',
         'No_Fly',
         'Finger_Small',
         'Finger_Large',
         'Cargo_Air_Only',
         'Hazmat_Surface_Only',
         'unknown',
         'address-block',
         'address-block-handwritten',
         'first-class',
         'ibi',
         'imb',
         'impb',
         'priority',
         'permit-imprint',
         'pvi',
         's10',
         'Cremated_Remains']

class_map_dict = {1: 'Lithium_UN_Label',
                  2: 'Lithium__Class_9',
                  3: 'Lithium_Battery_Label',
                  4: 'Biohazard',
                  5: 'No_Fly',
                  6: 'Finger_Small',
                  7: 'Finger_Large',
                  8: 'Cargo_Air_Only',
                  10: 'Hazmat_Surface_Only',
                  11: 'unknown',
                  12: 'address-block',
                  13: 'address-block-handwritten',
                  14: 'first-class',
                  15: 'ibi',
                  16: 'imb',
                  17: 'impb',
                  18: 'priority',
                  19: 'permit-imprint',
                  20: 'pvi',
                  21: 's10',
                  22: 'Cremated_Remains'}
category_id_2 = [(0, 0, 255), (0, 255, 0), (255, 0, 0), (255, 255, 0), (255, 0, 255), (0, 255, 255), (50, 200, 255),
                 (255, 30, 30), (30, 30, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255), (25, 255, 63),
                 (255, 30, 30), (30, 30, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255), (85, 69, 255),
                 (255, 30, 30), (30, 30, 255)]


def get_matrix(box, width, height):
    src_pts = box.astype("float32")
    dst_pts = np.array([[0, height - 1],
                        [0, 0],
                        [width - 1, 0],
                        [width - 1, height - 1]], dtype="float32")

    M_barcode = cv2.getAffineTransform(src_pts[0:3], dst_pts[0:3])

    # trans_mat = np.array([[1, 0, 0],
    #                       [0, 1, height],
    #                       [0, 0, 1]])
    # #         print(M2.shape)
    # #         print(M2)
    # M_address = np.vstack((copy.copy(M_barcode), [0, 0, 1]))
    # #         print(M2)
    #
    # # combine the transforms
    # M_address = (np.matmul(trans_mat, M_address))
    # M_address = M_address[:2, :]

    M_barcode = np.expand_dims(M_barcode, axis=0).astype('float32')
    # M_address = np.expand_dims(M_address, axis=0)

    return M_barcode


def get_crop_args(box, width, height):
    # bbox[-1] *= 180 / np.pi
    # buffer = 0.0 * bbox[3]  # buffer is 8% of height
    #
    # if bbox[2] < 0 or bbox[3] < 0:
    #     # If any of the xy coordinates are negative, raise assertion error (returns identity matrix and empty img)
    #     raise AssertionError("Bounding boxes must not have negative coordinates")

    # bbox = ((bbox[0] + bbox[2] / 2, bbox[1] + bbox[3] / 2), (bbox[2] + buffer, bbox[3] + buffer), bbox[4])
    #
    # box = cv2.boxPoints(bbox)
    # box = np.int0(box)

    # width = int(bbox[1][0])
    # height = int(bbox[1][1])

    # TODO: Try to run affine transformation only once because it is compute intensive
    # TODO: Revisit the way we are adding in the buffer. Does it add buffer effectively?
    M_barcode = get_matrix(box, width, height)
    dims = np.array((width, height))
    dims = np.expand_dims(dims, axis=0)
    dims = np.array([[dims[0][1], dims[0][0]]], dtype='float32')

    return M_barcode, dims

# def crop_example(image, ratio, scores, boxes):
#     score = scores[0].squeeze()[0]
#     boxes = boxes[0].squeeze()
#     ratio = ratio[0]
#     box = np.array([boxes[i: i + n] for i in range(0, len(boxes), n)])[0]
#     og_img_dims = image.shape[1:3]
#
#     if score > 0.5:
#         box[:4] /= ratio
#         x1, y1, x2, y2, theta = [box[0], box[1], box[2], box[3], np.arctan2(box[4], box[5])]
#         w = x2 - x1 + 1
#         h = y2 - y1 + 1
#         _box = [x1, y1, w, h, theta]
#         # M, dims, src = get_crop_args_cv(_box, og_img_dims)
#         # M, dims, src = get_crop_args(_box, og_img_dims)
#         image = np.stack([image for i in range(3)], axis=-1)
#         M = np.expand_dims(M, axis=0)
#         # theta = theta * 180 / np.pi
#         #     print(theta * 180 / np.pi)n
#         #     image_2 = cv2.warpAffine(img, M, (w, h))
#         # plt.clf()
#         # fig, ax = plt.subplots(1)
#         # ax.imshow(image[0, :, :, :])
#         # rect = patch.Rectangle(xy=(src[1]), width=w, height=h, angle=(theta), fill=False, color='red')
#         #
#         # ax.add_patch(rect)
#         # plt.plot(x1, y1, marker='v', color='cyan')
#         # plt.plot(src[0][0], src[0][1], marker='x', color='red')
#         # plt.plot(src[1][0], src[1][1], marker='x', color='blue')
#         # plt.plot(src[2][0], src[2][1], marker='x', color='green')
#         # plt.plot(src[3][0], src[3][1], marker='x', color='yellow')
#         #
#         # plt.show()
#
#     else:
#         _box = [-1]
#         image = np.zeros((1, 1280, 1280, 3)).astype("float32")
#         M = np.ones((1, 2, 3))
#         dims = np.ones((1, 2))
#     return image, M, dims


def run_ensemble():
    preprocessed_img, ratios = barcode_reconstruction_obj.preprocess()
    scores, boxes, classes = barcode_reconstruction_obj.barcode(preprocessed_img)
    #
    image_out, matrix_out, dims_out = barcode_reconstruction_obj.crop_barcode(ratios, scores, boxes, classes)
    # image_out, matrix_out, dims_out = crop_example(og_image, ratios, scores, boxes)
    # plt.figure(0)
    # plt.imshow(image_out[0, :, :])
    # dims_out = np.array([[dims_out[0][1], dims_out[0][0]]], dtype='float32')

    # out_box = boxes.flatten()[:6]
    # out_box[:4] /= ratios[0][0]
    # x1, y1, x2, y2, theta = [out_box[0], out_box[1], out_box[2], out_box[3], np.arctan2(out_box[4], out_box[5])]
    # w = x2 - x1 + 1
    # h = y2 - y1 + 1
    # box = [x1, y1, w, h, theta]
    #
    # box[-1] *= 180 / np.pi
    # box = ((box[0] + box[2] / 2, box[1] + box[3] / 2), (box[2], box[3]), box[4])
    #
    # box = cv2.boxPoints(box)
    # box = np.int0(box)
    # #     print(src[0])
    # #         plt.plot(x1, y1, marker='v', color='cyan')
    # plt.figure('og image with detection')
    # plt.imshow(image_out[0])
    # plt.plot(box[0][0], box[0][1], marker='x', color='red')
    # plt.plot(box[1][0], box[1][1], marker='x', color='blue')
    # plt.plot(box[2][0], box[2][1], marker='x', color='green')
    # plt.plot(box[3][0], box[3][1], marker='x', color='yellow')
    # plt.show()

    cropped_img_digits, cropped_img_pyzbar = barcode_reconstruction_obj.dali_crop_gpu(image_out, matrix_out, dims_out)
    # pipeline = pipe_crop(image_out[0], matrix_out[0], dims_out)
    # outputs = run(pipeline)
    # digits_img, pyzbar_img = outputs
    # pyzbar_img = pyzbar_img.as_cpu()
    # pyzbar_img = pyzbar_img.as_array()

    # plt.clf()
    # plt.figure(0)
    # plt.imshow(cropped_img_pyzbar[0, :, :, :])
    # plt.show()

    # plt.figure(2)
    # plt.imshow(cropped_img_digits[0, 0, :, :])
    # plt.show()
    # print(
    #     f"Pyzbar img type: {cropped_img_pyzbar.dtype} Pyzbar shape: {cropped_img_pyzbar.shape} "
    #     f"Pyzbar sum {np.sum(cropped_img_pyzbar)}")

    # Each step in the ensemble
    tracking_num_pyzbar, barcode_class = barcode_reconstruction_obj.read_barcode_pyzbar(cropped_img_pyzbar)

    scores_d, boxes_d, classes_d = barcode_reconstruction_obj.read_barcode_digits(cropped_img_digits)
    digits = barcode_reconstruction_obj.post_process_digits(scores_d, boxes_d, classes_d)

    # digits, tracking_num_pyzbar, barcode_class, preprocessed_img, ratios, img_to_crop, matrix, dims, \
    # img_digits_out, img_pyzbar_out

    return digits, tracking_num_pyzbar, barcode_class, preprocessed_img, ratios, image_out, matrix_out, dims_out, \
        cropped_img_digits, cropped_img_pyzbar


def is_valid_s10(barcode_text):
    first_2chars = barcode_text[:2]
    last_2chars = barcode_text[-2:]
    middle_digits = barcode_text[2:-2]
    return (first_2chars.isalpha() and last_2chars.isalpha()) and middle_digits.isdigit() and len(barcode_text) > 10


def is_valid_domestic(barcode_text):
    first_digit = barcode_text[0]
    first_3digits = barcode_text[:3]
    return (first_digit == '9' or first_3digits == '420') and len(barcode_text) > 18


def load_cv2_warp_results(filepath):
    import pickle
    with open(filepath, 'rb') as file:
        data = pickle.load(file)

    return data


def dist(point_1, point_2):

    distance = math.sqrt(((int(point_1[0])-int(point_2[0]))**2)+((int(point_1[1])-int(point_2[1]))**2))
    return distance


def get_barcode_yolo(boxes, classes, scores, image_path, triton_ensemble):
    image = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
    image = np.expand_dims(image, axis=0)
    image = np.stack([image for i in range(3)], axis=-1)
    detected = False

    for box, cls, score in zip(boxes[0], classes[0], scores[0]):
        display_nm = names[int(cls.flatten())]
        confidence = float(score.flatten())

        box = np.int0(box)

        if confidence > 0.4 and (display_nm == 'impb' or display_nm == 's10'):

            height = dist(box[0], box[1])
            width = dist(box[1], box[2])

            M_barcode, dims = get_crop_args(box, width, height)
            detected = True

            break

        else:
            # _box = [-1]
            # image = np.zeros((1, 1280, 1280, 3)).astype("uint8")
            M_barcode = np.array([[[1, 0, 0],
                                   [0, 1, 0]]], dtype='float32')
            dims = np.array([[100, 200]], dtype='float32')

    img_digits, img_pyzbar = triton_ensemble.dali_crop_gpu(image, M_barcode, dims)
    # plt.clf()
    # plt.figure("pyzbar crop yolo")
    # plt.imshow(img_pyzbar[0])
    # plt.show()
    digits_out, tracking_num_pyzbar, barcode_class = triton_ensemble.read_barcode_ensemble(img_digits, img_pyzbar)

    return digits_out, tracking_num_pyzbar, barcode_class, detected


if __name__ == "__main__":
    pkl_file = "/home/garveyer/ECIP-Application_feature_nvidia_dali_enhancements/notebooks/cv2_warp_results.pickle"
    cv2_results = load_cv2_warp_results(pkl_file)
    print("num cv2 results: ", len(cv2_results))

    filepath_glob = "/data/BCR/test_deck/*.tif*"
    filepaths = glob.glob(filepath_glob)

    start_time = time.time()
    problem_filenames = []
    pyzbar_decodes = 0
    pyzbar_decodes_yolo = 0
    not_decoded = 0
    error = 0
    invalid = 0
    invalid_yolo = 0
    og_detected_ct = 0
    yolo_detected_ct = 0
    use_PRLM = True

    if use_PRLM:
        prlm_file = "/data/PRLM_files/APBS/01-439/Run_0001.PRLM.zip"
        prlm_obj = PRLMFile(prlm_file)
        images_to_bcr = prlm_obj.get_images_to_bcr()
        filepaths = []
        for img_path in images_to_bcr:
            filepaths.append(img_path.replace("/Run_0001.PRLM.zip/2022-08-25/01-439", ""))
        print(
            f"Number of images to perform BCR on: {len(images_to_bcr)}.  *Note: this value likely exceeds the "
            f"number of packages without barcodes*")
        # print(f"Images sent to BCR: {images_to_bcr}")

    for filename in filepaths:
        # print(filename)
        barcode_reconstruction_obj = ECIPsApplicationTritonModels(filename)
        try:
            # preprocessed_img, ratios = barcode_reconstruction_obj.preprocess()
            # st_step = time.time()
            # digits_step, tracking_num_pyzbar_step, barcode_class_step, preprocessed_img_step, ratios_step,
            # img_to_crop_step, matrix_step, dims_step, \
            # img_digits_out_step, img_pyzbar_out_step = run_ensemble(barcode_reconstruction_obj.image)
            # et_step = time.time()
            digits, tracking_num_pyzbar, barcode_class, \
                preprocessed_img, ratios, img_to_crop, matrix_barcode, \
                matrix_address, dims, img_digits_out, \
                img_pyzbar_out = barcode_reconstruction_obj.barcode_digit_ensemble()
            detected_og = False if img_pyzbar_out.shape == (1, 100, 200, 3) else True
            og_dims, yolo_scores, yolo_boxes, yolo_classes = barcode_reconstruction_obj.ensemble_model_dali(filename)
            digits_yolo, tracking_num_yolo, barcode_class_yolo, detected_yolo = \
                get_barcode_yolo(yolo_boxes[0],
                                 yolo_classes[0],
                                 yolo_scores[0],
                                 filename,
                                 barcode_reconstruction_obj)

            if detected_og:
                # print(filename)
                og_detected_ct += 1
                if tracking_num_pyzbar:
                    barcode_class = str(barcode_class).strip("b'")
                    tracking_num_pyzbar = str(tracking_num_pyzbar).strip("b'")
                    valid = is_valid_domestic(tracking_num_pyzbar) or is_valid_s10(tracking_num_pyzbar)
                    if valid:
                        pyzbar_decodes += 1
                        print("PyZbar result: ", tracking_num_pyzbar)
                    else:
                        invalid += 1
            if detected_yolo:
                # print(filename)
                yolo_detected_ct += 1
                if tracking_num_yolo:
                    barcode_class = str(barcode_class_yolo).strip("b'")
                    tracking_num_yolo = str(tracking_num_yolo).strip("b'")
                    valid = is_valid_domestic(tracking_num_yolo) or is_valid_s10(tracking_num_yolo)
                    if valid:
                        pyzbar_decodes_yolo += 1
                        print("PyZbar result yolo: ", tracking_num_yolo)
                    else:
                        invalid_yolo += 1
        # print("\n")
        except Exception as e:
            print("Error on file: ", filename)
            print("Error: ", e)
            error += 1

        del barcode_reconstruction_obj

    end_time = time.time()
    print("OG num barcodes detected: ", og_detected_ct)
    print("YOLO num barcodes detected: ", yolo_detected_ct)

    print("OG num decoded barcodes: ", pyzbar_decodes)
    print("YOLO num decoded barcodes: ", pyzbar_decodes_yolo)
    # print("num decoded with cv not dali: ", not_decoded)
    print("OG num invalid: ", invalid)
    print("YOLO num invalid: ", invalid_yolo)

    print(f"BCR summary for PRLM file: {prlm_file}: \n"
          f"\t\t\t\t {prlm_obj.total_packages_wout_barcode} packages out of {prlm_obj.total_packages} "
          f"total packages required BCR \n"
          f"\t\t\t\t In total, BCR was performed on {len(images_to_bcr)} images \n"
          f"\t\t\t\t After reconstruction (OG), {pyzbar_decodes} images returned a valid barcode "
          f"\t\t\t\t After reconstruction (YOLO), {pyzbar_decodes_yolo} images returned a valid barcode "
          f"and were sent to WebAPAT")

    # print("num errors: ", error)
    # print("Problem files: ", problem_filenames)
    # print("Processing time per image: ", ((end_time - start_time) / len(filepaths)))
    # barcode_reconstruction_obj = ECIPsApplicationTritonModels(filename)
    # test_output = barcode_reconstruction_obj.dali_test(filename)

    # start_time = time.time()
    # preprocessed_img, ratios = barcode_reconstruction_obj.preprocess()
    # end_time = time.time()
    # print("Original Processing time: ", (end_time - start_time))

    # start_time = time.time()
    # preprocessed_img_dali, smaller_img_dali, og_dim_dali = barcode_reconstruction_obj.dali_resize_gpu(filename_tiff)
    # end_time = time.time()
    # print("Dali Processing time: ", (end_time - start_time))

    # plt.figure(0)
    # plt.imshow(preprocessed_img[0, 0, :, :])

    # output_img = np.transpose(preprocessed_img[0, :, :, :], (1, 2, 0))
    # output_img = ((output_img * barcode_reconstruction_obj.std) + barcode_reconstruction_obj.mean) * 255
    # saved = cv2.imwrite('/home/garveyer/ECIP_barcode_reconstruction/test_output/preprocessing.jpeg', output_img)

    # plt.figure(1)
    # plot_out = np.repeat(preprocessed_img_dali[0, :, :][..., np.newaxis], 3, axis=2)
    # plot_out = ((plot_out / 255) - barcode_reconstruction_obj.mean) / barcode_reconstruction_obj.std
    # plt.imshow(plot_out)
    # output_img_dali = np.repeat(preprocessed_img_dali[0, :, :][..., np.newaxis], 3, axis=2)
    # saved = cv2.imwrite(
    #     '/home/garveyer/ECIP_barcode_reconstruction/test_output/dali_gpu_paste_nomirror_bicubic_result.jpeg',
    #     output_img_dali)
    # plt.show()

    # print("Arrays are the same: ", np.array_equiv(preprocessed_img, preprocessed_img_dali))

    # digits, tracking_num_pyzbar, barcode_class = run_ensemble(preprocessed_img)

    # digits_dali, tracking_num_pyzbar_dali, barcode_class_dali = run_ensemble(preprocessed_img_dali)
    # start_time = time.time()
    # digits, tracking_num_pyzbar, barcode_class = barcode_reconstruction_obj.barcode_digit_ensemble()
    # end_time = time.time()
    # print("Time to Process one image: ", end_time - start_time)

    #
    # print("Original Results")
    # print(digits)
    # print(tracking_num_pyzbar)
    # print(barcode_class)
    #
    # print("Dali Results")
    # print(digits_dali)
    # print(tracking_num_pyzbar_dali)
    # print(barcode_class_dali)
