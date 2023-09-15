import glob
import json
import os
import shutil

import numpy as np
import pandas as pd

FRAUD_TYPES = ["MCB", "STC", "PI", "Date", "IMPB", "invalid_SN", "SN"]
PI_TYPES = ["PI_missing_eVS_validation", "PI_invalid_eVS_permit", "PI_invalid_ePostage"]
# FRAUD_TYPES = ["banner", "stc", "pi", "sn", "date"]
# GT_MAP =
FRAUD_TYPES_MAP = {"banner": "MCB", "stc": "STC", "pi": "PI", "sn": "SN", "date": "Date"}
RELEASE_TAG = "v1.6.8_rc2/"
DATASET_TAG = "v1.0.2"
TP_OUTPUT_DIR = "/data/Fraud/test_results/TP_fraud_detections/" + RELEASE_TAG + "/"
DATASET_DIR = "/data/Fraud/datasets/validation_set/" + DATASET_TAG + "/"
# DATASET_DIR = "/data/Fraud/datasets/fraud_images_for_review/images_from_2023_01_13/"
SAVE_GT = False
COMPUTE_PERFORMANCE = True
COPY_JSON = True


# def eval_IBI_fraud(prlm_extracted_ibi, all_ocr_results):
#     fraud_count = 0
#     for index, row in prlm_extracted_ibi.iterrows():
#         if row["fraud"] != '[]':
#             fraud_count += 1
#             try:
#                 fraud_type = row["fraud"]
#                 serial_num = row["serial number"]
#                 date = row["date"]
#                 ocr_result = all_ocr_results[row["filename"]]
#                 filename = root_dir + row["filename"]
#                 image = cv2.imread(filename)
#                 plt.clf()
#                 plt.figure("SN Mismatch example")
#                 plt.imshow(image)
#                 # plt.show()
#             except Exception as e:
#                 print(e)
#     print("Total fraud count: ", fraud_count)
def open_gt_dict(fraud_type, root_dir=DATASET_DIR):
    if fraud_type != "PI":
        gt = root_dir + fraud_type + "/" + fraud_type + "_gt_results.json"
        # gt = DATASET_DIR + FRAUD_TYPES_MAP[fraud_type] + "/" + FRAUD_TYPES_MAP[fraud_type] + "_gt_results.json"

        with open(gt, "r") as f:
            gt_data = json.load(f)

        return gt_data

    else:
        pi_gt = {}
        for pi_fraud in PI_TYPES:

            gt = root_dir + pi_fraud + "/" + fraud_type + "_gt_results.json"

            try:
                with open(gt, "r") as f:
                    pi_gt[pi_fraud] = json.load(f)
            except FileNotFoundError:
                print(
                    f"The file {gt} is not written to the disk. Double check that there are no examples of this fraud type")
                pi_gt[pi_fraud] = {}
                continue
        return pi_gt


def get_img_path(filepath, root_directory=DATASET_DIR):
    try:
        try:
            img_src = glob.glob(root_directory + "ALL_IMAGES/**/**/**/**/**/" + filepath)[0]
        except IndexError:
            img_src = glob.glob(root_directory + "ALL_IMAGES/**/**/**/**/" + filepath)[0]
    except:
        raise FileNotFoundError(f"The following file does not exist in the directory structure \n"
                                f"{filepath}: loooking in {root_directory + 'ALL_IMAGES/**/**/**/**/'} and \n"
                                f"{root_directory + 'ALL_IMAGES/**/**/**/**/**/'}")

    return img_src


def get_prlm_path(img_src):

    prlm_glob = os.path.split(img_src)[0]
    prlm_glob = prlm_glob.split("/")[:-2]
    prlm_glob = "/" + os.path.join(*prlm_glob) + "/*.zip"
    try:
        prlm_path = glob.glob(prlm_glob)[0]
    except IndexError:
        prlm_glob = os.path.split(img_src)[0]  # + "/*.zip"
        prlm_glob = prlm_glob.split("/")[:-1]  # + "/*.zip"
        prlm_glob = "/" + os.path.join(*prlm_glob) + "/*.zip"
        prlm_path = glob.glob(prlm_glob)[0]

    return prlm_path

def eval_STC_fraud(tp_results, fp_results, fn_results, tn_results):
    # Move TP results to new folder
    # save_fraud_examples(tp_results, fn_results, outdir)

    # Count & Plot OCR conf for FP and TP and TN
    # tp_conf = tp_results["confidence"]
    # fp_conf = fp_results["confidence"]
    # tn_conf = tn_results["confidence"]

    # plt.figure("Comparing OCR confidence Values")
    # plt.plot(tp_conf, 'rx', label="TPs")
    # plt.plot(fp_conf, 'bo', label="FPs")
    # plt.plot(tn_conf, 'g*', label="TNs")

    # Count num of OCR fails vs YOLO fails, what were the OCR and YOLO model conf at that moment?
    # failure_mode_cts = fp_results["reason"].value_counts()
    # print("Failure Mode counts for FPs: ")
    # print(failure_mode_cts)
    # ocr_failed_conf = fp_results[fp_results["reason"] == "ocr"]["confidence"]
    # print("OCR confidence summary stats for FPs: ")
    # print(f"Max Value: {ocr_failed_conf.max()}")
    # print(f"Min Value: {ocr_failed_conf.min()}")
    # print(f"Mean Value: {ocr_failed_conf.mean()}")
    # print(f"STD Value: {ocr_failed_conf.std()}")

    # plt.plot(ocr_failed_conf, 'mo', label="FPs - failure OCR")
    # plt.axhline(y=ocr_failed_conf.mean(), color='k', linestyle='-', label="mean_conf_FPs")
    # plt.legend()
    # plt.show()

    # Calculate the TP, FP rate
    try:
        tp_rate = tp_results.shape[0] / (tp_results.shape[0] + fn_results.shape[0])
    except ZeroDivisionError:
        tp_rate = None
    fp_rate = fp_results.shape[0] / (fp_results.shape[0] + tn_results.shape[0])
    tn_rate = tn_results.shape[0] / (fp_results.shape[0] + tn_results.shape[0])
    try:
        prec = tp_results.shape[0] / (tp_results.shape[0] + fp_results.shape[0])
        fn_rate = fn_results.shape[0] / (fn_results.shape[0] + tp_results.shape[0])
    except ZeroDivisionError:
        fn_rate = None
        prec = None

    return tp_rate, fn_rate, fp_rate, tn_rate, prec


def sort_PI_results(fp_analysis):
    pi_results = {}

    for pi_fraud in PI_TYPES:
        gt = DATASET_DIR + pi_fraud + "/" + fraud_type + "_gt_results.json"
        # gt = DATASET_DIR + FRAUD_TYPES_MAP[fraud_type] + "/" + FRAUD_TYPES_MAP[fraud_type] + "_gt_results.json"

        try:
            with open(gt, "r") as f:
                gt_data = json.load(f)
        except FileNotFoundError:
            print(f"The file {gt} is not written to the disk. Double check that there are no examples of this fraud type")
            continue
        fp_analysis = fp_analysis.drop_duplicates(subset=["filepath"])
        fp_analysis["result_classification"] = None

        for index, row in fp_analysis.iterrows():
            filepath_root = row["filepath"].split("/")[-1]
            try:
                gt_status = gt_data[filepath_root]
            except KeyError:
                print("Key Error on: ", filepath_root)
                continue

            try:
                fraud_status = True if not np.isnan(row["fraud_type"]) else False  # np.isnan(row["false_positive"])
            except TypeError:
                fraud_status = True
            # else:
            #     fraud_status = row["is_fraud"]

            if gt_status == "not_fraud":
                if fraud_status is True:
                    fp_analysis.at[index, "result_classification"] = "fp"
                else:
                    fp_analysis.at[index, "result_classification"] = "tn"

            elif gt_status == "fraud":
                if fraud_status is True:
                    fp_analysis.at[index, "result_classification"] = "tp"
                else:
                    fp_analysis.at[index, "result_classification"] = "fn"

            elif gt_status == "na":
                if fraud_status is True:
                    fp_analysis.at[index, "result_classification"] = "fp"
                else:
                    fp_analysis.at[index, "result_classification"] = "tn"

        tp_results = fp_analysis[fp_analysis["result_classification"] == "tp"]
        fp_results = fp_analysis[fp_analysis["result_classification"] == "fp"]
        fn_results = fp_analysis[fp_analysis["result_classification"] == "fn"]
        tn_results = fp_analysis[fp_analysis["result_classification"] == "tn"]

        pi_results[pi_fraud] = [tp_results, fp_results, fn_results, tn_results]

    return pi_results


def sort_results_compare(fp_analysis, fraud_type):

    gt = DATASET_DIR + fraud_type + "/" + fraud_type + "_gt_results.json"
    # gt = DATASET_DIR + FRAUD_TYPES_MAP[fraud_type] + "/" + FRAUD_TYPES_MAP[fraud_type] + "_gt_results.json"

    with open(gt, "r") as f:
        gt_data = json.load(f)

    fp_analysis = fp_analysis.drop_duplicates(subset=["filepath"])
    fp_analysis["result_classification"] = None

    for index, row in fp_analysis.iterrows():
        filepath_root = row["filepath"].split("/")[-1]
        try:
            gt_status = gt_data[filepath_root]
        except KeyError:
            print("Key Error on: ", filepath_root)
            continue
        if "PI" in fraud_type:
            # fraud_status =
            try:
                fraud_status = True if not np.isnan(row["fraud_type"]) else False  # np.isnan(row["false_positive"])
            except TypeError:
                fraud_status = True
        else:
            fraud_status = row["is_fraud"]

        if gt_status == "not_fraud":
            if fraud_status is True:
                fp_analysis.at[index, "result_classification"] = "fp"
            else:
                fp_analysis.at[index, "result_classification"] = "tn"

        elif gt_status == "fraud":
            if fraud_status is True:
                fp_analysis.at[index, "result_classification"] = "tp"
            else:
                fp_analysis.at[index, "result_classification"] = "fn"

        elif gt_status == "na":
            if fraud_status is True:
                fp_analysis.at[index, "result_classification"] = "fp"
            else:
                fp_analysis.at[index, "result_classification"] = "tn"

    if fraud_type == "invalid_SN":
        for filename in gt_data:
            fraud_result = gt_data[filename]
            if fraud_result == "not_fraud":
                fp_analysis = fp_analysis.append({"ocr": "",
                                                  "barcode": "",
                                                  "ocr_valid": "",
                                                  "barcode_valid": "",
                                                  "fraud_logic_executed": "",
                                                  "levenshtein_distance": "",
                                                  "ocr_sn_found": "",
                                                  "raw_text": "",
                                                  "confidence": "",
                                                  "valid_serial_number": "",
                                                  "special_data_matrix_label_detected": "",
                                                  "vendor_id_model_num_ibi_barcode": "",
                                                  "PSD_PES_serial_number_barcode": "",
                                                  "is_fraud": "",
                                                  "filepath": "",
                                                  "result_classification": "tn",
                                                  "reason": "",
                                                  "comments": ""
                                                  }, ignore_index=True)


    tp_results = fp_analysis[fp_analysis["result_classification"] == "tp"]
    fp_results = fp_analysis[fp_analysis["result_classification"] == "fp"]
    fn_results = fp_analysis[fp_analysis["result_classification"] == "fn"]
    tn_results = fp_analysis[fp_analysis["result_classification"] == "tn"]

    # for index, row in fp_analysis.iterrows():
    #     # if not np.isnan(row["false_positive"]):
    #     clss = str(row["result_classification"])
    #     result_classifications[clss] += 1
    #     result_confidences[clss].append(float(row["confidence"]))

    return tp_results, fp_results, fn_results, tn_results


def eval_MCB_fraud(tp_results, fp_results, fn_results, tn_results):
    # Move TP results to new folder
    # save_fraud_examples(tp_results, fn_results, outdir)

    # Count & Plot OCR conf for FP and TP and TN
    # tp_conf = tp_results["confidence"]
    # fp_conf = fp_results["confidence"]
    # tn_conf = tn_results["confidence"]

    # plt.figure("Comparing OCR confidence Values - "+outdir)
    # plt.plot(tp_conf, 'rx', label="TPs")
    # plt.plot(fp_conf, 'bo', label="FPs")
    # plt.plot(tn_conf, 'g*', label="TNs")

    # Count num of OCR fails vs YOLO fails, what were the OCR and YOLO model conf at that moment?
    # failure_mode_cts = fp_results["reason"].value_counts()
    # print("Failure Mode counts for FPs: ")
    # print(failure_mode_cts)
    # ocr_failed_conf = fp_results[fp_results["reason"] == "ocr"]["confidence"]
    # print("OCR confidence summary stats for FPs: ")
    # print(f"Max Value: {ocr_failed_conf.max()}")
    # print(f"Min Value: {ocr_failed_conf.min()}")
    # print(f"Mean Value: {ocr_failed_conf.mean()}")
    # print(f"STD Value: {ocr_failed_conf.std()}")

    # plt.plot(ocr_failed_conf, 'mo', label="FPs - failure OCR")
    # plt.axhline(y=ocr_failed_conf.mean(), color='k', linestyle='-', label="mean_conf_FPs")
    # plt.legend()
    # plt.show()

    # Calculate the TP, FP rate
    try:
        tp_rate = tp_results.shape[0] / (tp_results.shape[0] + fn_results.shape[0])
    except ZeroDivisionError:
        tp_rate = None
    fp_rate = fp_results.shape[0] / (fp_results.shape[0] + tn_results.shape[0])
    tn_rate = tn_results.shape[0] / (fp_results.shape[0] + tn_results.shape[0])
    try:
        prec = tp_results.shape[0] / (tp_results.shape[0] + fp_results.shape[0])
        fn_rate = fn_results.shape[0] / (fn_results.shape[0] + tp_results.shape[0])
    except ZeroDivisionError:
        fn_rate = None
        prec = None

    return tp_rate, fn_rate, fp_rate, tn_rate, prec


def eval_PI_fraud(PI_results):
    # Move TP results to new folder
    # save_fraud_examples(tp_results, fn_results, outdir)
    PI_metrics = {}
    for PI_type in PI_results:
        tp_results, fp_results, fn_results, tn_results = PI_results[PI_type]
        # Count & Plot OCR conf for FP and TP and TN
        tp_conf = tp_results["detected_class_text_confidence"]
        fp_conf = fp_results["detected_class_text_confidence"]
        tn_conf = tn_results["detected_class_text_confidence"]

        # plt.figure("Comparing OCR confidence Values")
        # plt.plot(tp_conf, 'rx', label="TPs")
        # plt.plot(fp_conf, 'bo', label="FPs")
        # plt.plot(tn_conf, 'g*', label="TNs")

        # Count num of OCR fails vs YOLO fails, what were the OCR and YOLO model conf at that moment?
        # failure_mode_cts = fp_results["reason"].value_counts()
        # print("Failure Mode counts for FPs: ")
        # print(failure_mode_cts)
        # ocr_failed_conf = fp_results[fp_results["reason"] == "misclassified"]["detected_class_text_confidence"]
        # print("OCR confidence summary stats for FPs: ")
        # print(f"Max Value: {ocr_failed_conf.max()}")
        # print(f"Min Value: {ocr_failed_conf.min()}")
        # print(f"Mean Value: {ocr_failed_conf.mean()}")
        # print(f"STD Value: {ocr_failed_conf.std()}")

        # plt.plot(ocr_failed_conf, 'mo', label="FPs - failure OCR")
        # plt.axhline(y=ocr_failed_conf.mean(), color='k', linestyle='-', label="mean_conf_FPs")
        # plt.legend()
        # plt.show()

        # Calculate the TP, FP rate
        try:
            tp_rate = tp_results.shape[0] / (tp_results.shape[0] + fn_results.shape[0])
        except ZeroDivisionError:
            tp_rate = None
        try:
            fp_rate = fp_results.shape[0] / (fp_results.shape[0] + tn_results.shape[0])
        except ZeroDivisionError:
            fp_rate = None
        try:
            tn_rate = tn_results.shape[0] / (fp_results.shape[0] + tn_results.shape[0])
        except ZeroDivisionError:
            tn_rate = None
        try:
            prec = tp_results.shape[0] / (tp_results.shape[0] + fp_results.shape[0])
            fn_rate = fn_results.shape[0] / (fn_results.shape[0] + tp_results.shape[0])
        except ZeroDivisionError:
            fn_rate = None
            prec = None

        PI_metrics[PI_type] = [tp_rate, fn_rate, fp_rate, tn_rate, prec]

    return PI_metrics


def process_fraud_results(fraud_results, fraud_type):
    if fraud_type != "PI":
        tp_results, fp_results, fn_results, tn_results = sort_results_compare(fraud_results, fraud_type)

    if fraud_type == "MCB":
        tp_rate, fn_rate, fp_rate, tn_rate, prec = eval_MCB_fraud(tp_results, fp_results, fn_results, tn_results)
        print(f"MCB results: \n"
              f"TP Rate: {tp_rate}\n"
              f"FN Rate: {fn_rate}\n"
              f"FP Rate: {fp_rate}\n"
              f"TN Rate: {tn_rate}\n")
    elif fraud_type == "STC":
        tp_rate, fn_rate, fp_rate, tn_rate, prec = eval_STC_fraud(tp_results, fp_results, fn_results, tn_results)
        print(f"STC results: \n"
              f"TP Rate: {tp_rate}\n"
              f"FN Rate: {fn_rate}\n"
              f"FP Rate: {fp_rate}\n"
              f"TN Rate: {tn_rate}\n")
    elif fraud_type == "PI":
        PI_results = sort_PI_results(fraud_results)
        PI_metrics = eval_PI_fraud(PI_results)
        print(f"PI results: \n"
              f"{PI_metrics}")
        return PI_metrics
    elif "SN" in fraud_type:
        tp_rate, fn_rate, fp_rate, tn_rate, prec = eval_MCB_fraud(tp_results, fp_results, fn_results, tn_results)
        print(f"SN results: \n"
              f"TP Rate: {tp_rate}\n"
              f"FN Rate: {fn_rate}\n"
              f"FP Rate: {fp_rate}\n"
              f"TN Rate: {tn_rate}\n")
    elif fraud_type == "Date":
        tp_rate, fn_rate, fp_rate, tn_rate, prec = eval_MCB_fraud(tp_results, fp_results, fn_results, tn_results)
        print(f"Date results: \n"
              f"TP Rate: {tp_rate}\n"
              f"FN Rate: {fn_rate}\n"
              f"FP Rate: {fp_rate}\n"
              f"TN Rate: {tn_rate}\n")

    return tp_rate, fn_rate, fp_rate, tn_rate, prec


def process_fraud_results_compare(fraud_results, fraud_type):
    if fraud_type != "PI":
        tp_results, fp_results, fn_results, tn_results = sort_results_compare(fraud_results, fraud_type)
    if fraud_type in ["banner", "MCB"]:
        tp_rate, fn_rate, fp_rate, tn_rate, prec = eval_MCB_fraud(tp_results, fp_results, fn_results, tn_results)
        print(f"MCB results: \n"
              f"TP Rate: {tp_rate}\n"
              f"FN Rate: {fn_rate}\n"
              f"FP Rate: {fp_rate}\n"
              f"TN Rate: {tn_rate}\n")
    elif fraud_type in ["stc", "STC"]:
        tp_rate, fn_rate, fp_rate, tn_rate, prec = eval_STC_fraud(tp_results, fp_results, fn_results, tn_results)
        print(f"STC results: \n"
              f"TP Rate: {tp_rate}\n"
              f"FN Rate: {fn_rate}\n"
              f"FP Rate: {fp_rate}\n"
              f"TN Rate: {tn_rate}\n")
    elif fraud_type == "PI":
        PI_results = sort_PI_results(fraud_results)
        PI_metrics = eval_PI_fraud(PI_results)
        print(f"PI results: \n"
              f"{PI_metrics}")
        return PI_metrics
    elif "SN" in fraud_type: # in ["sn", "SN"]:
        tp_rate, fn_rate, fp_rate, tn_rate, prec = eval_MCB_fraud(tp_results, fp_results, fn_results, tn_results)
        print(f"SN results: \n"
              f"TP Rate: {tp_rate}\n"
              f"FN Rate: {fn_rate}\n"
              f"FP Rate: {fp_rate}\n"
              f"TN Rate: {tn_rate}\n")
    elif fraud_type in ["date", "Date"]:
        tp_rate, fn_rate, fp_rate, tn_rate, prec = eval_MCB_fraud(tp_results, fp_results, fn_results, tn_results)
        print(f"Date results: \n"
              f"TP Rate: {tp_rate}\n"
              f"FN Rate: {fn_rate}\n"
              f"FP Rate: {fp_rate}\n"
              f"TN Rate: {tn_rate}\n")
    elif fraud_type in ["impb", "IMPB"]:
        tp_rate, fn_rate, fp_rate, tn_rate, prec = eval_MCB_fraud(tp_results, fp_results, fn_results, tn_results)
        print(f"IMPB results: \n"
              f"TP Rate: {tp_rate}\n"
              f"FN Rate: {fn_rate}\n"
              f"FP Rate: {fp_rate}\n"
              f"TN Rate: {tn_rate}\n")

    return tp_rate, fn_rate, fp_rate, tn_rate, prec


def save_fraud_examples(tp_results, fn_results, outdir):
    for index, row in tp_results.iterrows():
        source = row["filepath"]
        # root_name = source.split("/")[-1]
        dest = TP_OUTPUT_DIR + outdir
        shutil.copy(source, dest)

    for index, row in fn_results.iterrows():
        source = row["filepath"]
        # root_name = source.split("/")[-1]
        dest = TP_OUTPUT_DIR + outdir
        shutil.copy(source, dest)


def move_images_to_IS_folder(fraud_type, out_dir):
    gt = DATASET_DIR + fraud_type + "/" + fraud_type + "_gt_results.json"
    # gt = DATASET_DIR + FRAUD_TYPES_MAP[fraud_type] + "/" + FRAUD_TYPES_MAP[fraud_type] + "_gt_results.json"

    with open(gt, "r") as f:
        gt_data = json.load(f)

    for filepath in gt_data:
        status = gt_data[filepath]

        if status == "fraud":
            # move the image to the out_dir
            img_src = get_img_path(filepath)
            prlm_path = get_prlm_path(img_src)

            out_path = out_dir + fraud_type
            if not os.path.exists(out_path):
                os.makedirs(out_path)
            # copy the PRLM too
            shutil.copy(img_src, out_path)
            shutil.copy(prlm_path, out_path)



def move_images_to_validation_folder(ftype_csv, fraud_type):

    outdir = DATASET_DIR + fraud_type + "/"

    gt_dict = {}
    # Make a directory for the fraud type if it doesnt exist
    if not os.path.exists(outdir):
        os.makedirs(outdir)

    for index, row in ftype_csv.iterrows():
        # Copy image file
        source = row["filepath"]

        if fraud_type == "PI":
            PI_fraud_type = row["fraud_type"]
            PI_outdir = DATASET_DIR + fraud_type + "_" + PI_fraud_type + "/"


            if not os.path.exists(PI_outdir):
                os.makedirs(PI_outdir)

            shutil.copy(source, PI_outdir)

        try:
            shutil.copy(source, outdir)
        except PermissionError:
            pass


        # copy .json file
        if COPY_JSON:
            try:
                json_source = source.split(".")[0] + ".json"
                shutil.copy(json_source, outdir)
                if fraud_type == "PI":
                    shutil.copy(json_source, PI_outdir)
            except FileNotFoundError:
                # Im not sure why we wouldnt hve a json but it seems to occur
                validation_result = row["result_classification"]
                print(f" File missing json: {source} \n Validation result: {validation_result}")

                pass

        validation_result = row["result_classification"]
        if validation_result == "tp" or validation_result == "fn":
            gt = "fraud"
        elif validation_result == "fp" or validation_result == "tn":
            gt = "not_fraud"
        else:
            # Occurs when data needs further investigation
            gt = "na"

        root_name = source.split("/")[-1]
        gt_dict[root_name] = gt

    # Write the gt dict to .json
    json_path = outdir + fraud_type + "_gt_results.json"
    if fraud_type == "PI":
        json_path = PI_outdir + fraud_type + "_gt_results.json"
    if not os.path.exists(json_path):
        # Only write these results if the GT has not been written yet!!!
        # Saves you from over writing previous GT results
        with open(json_path, "w") as json_out:
            json.dump(gt_dict, json_out)
    else:
        # Update the old dictionary with new results
        with open(json_path, "r") as json_in:
            old_gt = json.load(json_in)

        old_gt.update(gt_dict)
        with open(json_path, "w") as json_out:
            json.dump(old_gt, json_out)


if __name__ == "__main__":
    validation_results = glob.glob(f'/data/Fraud/test_results/validation_results/validation_set_{DATASET_TAG}_results/{RELEASE_TAG}/analysis/*.csv')
    # validation_results = glob.glob(f'/data/Fraud/datasets/fraud_images_for_review/images_from_2023_01_13/results/fraud_annotations/*.csv')
    # validation_results = glob.glob(f'/data/Fraud/datasets/validation_set/v1.0.1/invalid_SN/invalid_SN_review_out.csv')
    EXTRACT_GT = False
    COMPARE_TO_GT = True
    SAVE_GT = False
    SEND_POS_TO_IS = False
    IS_DIR = "/data/Fraud/test_results/TP_fraud_detections/v1.6.4_rc2/"
    result_dict = {}

    if SEND_POS_TO_IS:
        for val_result_file in validation_results:
            for ftype in FRAUD_TYPES:
                if ftype in val_result_file:
                    fraud_type = ftype
                    break

            csv_results = pd.read_csv(val_result_file)
            move_images_to_IS_folder(fraud_type, out_dir=IS_DIR)

    if EXTRACT_GT:
        for val_result_file in validation_results:
            for ftype in FRAUD_TYPES:
                if ftype in val_result_file:
                    fraud_type = ftype
                    break

            csv_results = pd.read_csv(val_result_file)
            if SAVE_GT:
                move_images_to_validation_folder(csv_results, fraud_type)
            if fraud_type != "PI":
                tp_rate, fn_rate, fp_rate, tn_rate, prec = process_fraud_results_compare(csv_results, fraud_type)
                result_dict[fraud_type] = {"tp": tp_rate,
                                           "fn": fn_rate,
                                           "fp": fp_rate,
                                           "tn": tn_rate,
                                           "prec": prec}
            else:
                PI_results = process_fraud_results_compare(csv_results, fraud_type)
                for PI_type in PI_results:
                    tp_rate, fn_rate, fp_rate, tn_rate, prec = PI_results[PI_type]
                    result_dict[PI_type] = {"tp": tp_rate,
                                            "fn": fn_rate,
                                            "fp": fp_rate,
                                            "tn": tn_rate,
                                            "prec": prec}
        # output_results = pd.DataFrame.from_dict(result_dict)
        # output_results.to_csv(f"/data/Fraud/test_results/validation_results/{RELEASE_TAG}/result_summary.csv")
    if COMPARE_TO_GT:
        for val_result_file in validation_results:
            for ftype in FRAUD_TYPES:
                if ftype in val_result_file:
                    fraud_type = ftype
                    break

            csv_results = pd.read_csv(val_result_file)
            # if SAVE_GT:
            #     move_images_to_validation_folder(csv_results, fraud_type)
            if fraud_type != "PI":
                tp_rate, fn_rate, fp_rate, tn_rate, prec = process_fraud_results_compare(csv_results, fraud_type)
                result_dict[fraud_type] = {"tp": tp_rate,
                                           "fn": fn_rate,
                                           "fp": fp_rate,
                                           "tn": tn_rate,
                                           "prec": prec}
            else:
                PI_results = process_fraud_results_compare(csv_results, fraud_type)
                for PI_type in PI_results:
                    tp_rate, fn_rate, fp_rate, tn_rate, prec = PI_results[PI_type]
                    result_dict[PI_type] = {"tp": tp_rate,
                                               "fn": fn_rate,
                                               "fp": fp_rate,
                                               "tn": tn_rate,
                                               "prec": prec}
    output_results = pd.DataFrame.from_dict(result_dict)
    output_results.to_csv(f"/data/Fraud/test_results/validation_results/validation_set_{DATASET_TAG}_results/{RELEASE_TAG}/result_summary.csv")

    # output_results.to_csv(f"/data/Fraud/datasets/fraud_images_for_review/images_from_2023_01_13/results/result_summary.csv")
