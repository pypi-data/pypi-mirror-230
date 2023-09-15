import glob
import time

import numpy as np

from ecips_triton_ensemble import ECIPsApplicationTritonModels

n = 6
resize = 800
max_size = 1280
mean = np.array([0.485, 0.456, 0.406])
std = np.array([0.229, 0.224, 0.225])
batch_size = 1


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


if __name__ == "__main__":
    pkl_file = "/home/garveyer/ECIP-Application_feature_nvidia_dali_enhancements/notebooks/cv2_warp_results.pickle"
    cv2_results = load_cv2_warp_results(pkl_file)
    print("num cv2 results: ", len(cv2_results))

    filepath_glob = "/data/BCR/test_deck/*.tif*"
    filepaths = glob.glob(filepath_glob)

    start_time = time.time()
    problem_filenames = []
    pyzbar_decodes = 0
    not_decoded = 0
    error = 0
    invalid = 0

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
            # et_all = time.time()
            cv2_decodes = False
            try:
                cv_barcode, cv_pyzbar_img = cv2_results[filename]
                cv2_decodes = True
            except KeyError:
                # If a key error occurs then that image wasnt decoded by pyzbar with cv2
                pass
            # print(f"processing time step: {et_step-st_step} | full {et_all-et_step}")
            # if not np.array_equiv(img_pyzbar_out, img_pyzbar_out_step):
            # plt.clf()
            # plt.figure(0)
            # plt.imshow(img_pyzbar_out[0])
            # plt.figure(1)
            # plt.imshow(img_pyzbar_out_step[0])
            # plt.show()
            # problem_filenames.append(filename)
            # if cv2_decodes and not tracking_num_pyzbar:
            #     print(f'File decoded: {filename}, result: {cv_barcode}')
            #     not_decoded += 1

            if tracking_num_pyzbar:
                # print(filename)
                barcode_class = str(barcode_class).strip("b'")
                tracking_num_pyzbar = str(tracking_num_pyzbar).strip("b'")
                valid = is_valid_domestic(tracking_num_pyzbar) or is_valid_s10(tracking_num_pyzbar)
                if valid:
                    pyzbar_decodes += 1
                    print("PyZbar result: ", tracking_num_pyzbar)
                else:
                    invalid += 1
        except Exception as e:
            print("Error on file: ", filename)
            print("Error: ", e)
            error += 1

        del barcode_reconstruction_obj

    end_time = time.time()
    print("num decoded barcodes: ", pyzbar_decodes)
    print("num decoded with cv not dali: ", not_decoded)
    print("num invalid: ", invalid)
    print("num errors: ", error)
    print("Problem files: ", problem_filenames)
    print("Processing time per image: ", ((end_time - start_time) / len(filepaths)))
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
