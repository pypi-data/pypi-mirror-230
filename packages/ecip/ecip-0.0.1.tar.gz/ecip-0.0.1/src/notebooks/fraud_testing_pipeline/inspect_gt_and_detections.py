import glob
import pandas as pd
import cv2
from fraud_performance_evaluation import open_gt_dict
from fraud_results_analysis_tool import main as view_image

DATASET_TAG = "v1.0.2"
RELEASE_TAG = "v1.6.8_rc2"
FRAUD_TYPES = ["MCB", "STC", "PI", "Date", "IMPB", "invalid_SN", "SN"]
DATASET_DIR = "/data/Fraud/datasets/validation_set/" + DATASET_TAG + "/"

def investigate_gt_detections(detections, gt_results, metrics):
    missing_files_from_gt = pd.DataFrame(columns=detections.columns)
    gt_results_df = pd.DataFrame.from_dict(gt_results, orient="index", columns=["fraud_status"])
    val_counts = gt_results_df.value_counts()
    tp_count = 0

    fraud_gt = gt_results_df[gt_results_df["fraud_status"] == "fraud"]
    fraud_detections = detections[detections["is_fraud"] == True]

    filenames_only = []
    for i, fraud_detection in fraud_detections.iterrows():
        filename = fraud_detection.filepath.split("/")[-1]
        filenames_only.append(filename)
        try:
            fraud_status = gt_results[filename]
        except KeyError:
            missing_files_from_gt.loc[len(missing_files_from_gt)] = fraud_detection
            continue

        if fraud_status == "fraud":
            # this is the case where the gt says it is fraud AND we detected it as such, a TP
            tp_count += 1
            see_fraud_image(metrics, fraud_detection, is_fraud=True)
            print(filename)

        else:
            # this is the case where the label is a FP
            # the fraud status could be either "not_fraud" or "na"
            # and either way we should investigate further
            # see_fraud_image(metrics, fraud_detection)
            pass

    fraud_detections["filename"] = filenames_only

    filenames_only = []
    for i, detection in detections.iterrows():
        filename = detection.filepath.split("/")[-1]
        filenames_only.append(filename)
    detections["filename"] = filenames_only

    tp_count2 = 0
    missing_files_from_detections = {}
    files_to_investigate = pd.DataFrame(columns=detections.columns)
    for i, fraud in fraud_gt.iterrows():
        # all of the fraud that we have labeled BUT was not detected (FNs)

        # is True fraud but not detected
        filename = i

        tp_result = fraud_detections[fraud_detections.filename == filename]

        if len(tp_result) < 1:
            # we labeled this as fraudulent but no fraud was detected, look at greater detections
            # to determine what happened
            try:
                fn_result = detections[detections.filename == filename]
                files_to_investigate.loc[len(files_to_investigate)] = fn_result.values[0]
                see_fraud_image(metrics, fn_result, is_fraud=True)
                print(filename)
            except IndexError:
                missing_files_from_detections[filename] = fraud


        else:
            # look at the TP
            # we labeled this as fraudulent and detected it as fraudulent
            tp_count2 += 1
            see_fraud_image(metrics, tp_result)
            print(filename)

    return missing_files_from_gt, files_to_investigate, pd.DataFrame.from_dict(missing_files_from_detections,
                                                                               orient="index", columns=["fraud_status"])


def see_fraud_image(metrics, fraud_detection, is_fraud=False):
    text = ""
    for m in metrics:
        text += f"\n{m}: {fraud_detection[m]}\n"
    try:
        img_to_view = cv2.imread(fraud_detection['filepath'])
    except TypeError:
        filepath = fraud_detection['filepath'].values[0]
        img_to_view = cv2.imread(filepath)
    try:
        result, reason, comments, quitApp = view_image(is_fraud, "Date", text, img_to_view)
    except:
        pass


if __name__ == "__main__":
    validation_results = glob.glob(f'/data/Fraud/test_results/validation_results/validation_set_{DATASET_TAG}_results/{RELEASE_TAG}/analysis/*.csv')
    fraud_of_interest = ["Date"]
    # fraud_of_interest = ["MCB", "STC", "Date", "IMPB", "invalid_SN", "SN"]
    output_dir = f'/data/Fraud/test_results/validation_results/validation_set_{DATASET_TAG}_results/{RELEASE_TAG}/data_investigation/'
    metrics_of_interest = ["impb_decoded_MPE", "impb_OCR", "fraud_confidence", "yolo_conf", "fraud_logic_executed"]

    for fraud in fraud_of_interest:
        for csv_results_file in validation_results:
            if fraud in csv_results_file:
                fraud_type = fraud

                csv_results = pd.read_csv(csv_results_file)
                gt_dict = open_gt_dict(fraud_type, DATASET_DIR)

                missing_files_from_gt, fn_to_investigate, missing_from_df = investigate_gt_detections(csv_results, gt_dict, metrics_of_interest)
                missing_files_from_gt.to_csv(output_dir + fraud_type + "_missing_from_gt_files.csv")
                missing_from_df.to_csv(output_dir + fraud_type + "_missing_from_detection_files.csv")
                fn_to_investigate.to_csv(output_dir + fraud_type + "_fn_to_investigate.csv")
