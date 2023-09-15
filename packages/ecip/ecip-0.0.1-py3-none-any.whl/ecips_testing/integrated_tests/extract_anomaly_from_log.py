import argparse
import pandas as pd
import json


def load_data_from_log(path_to_comms_log):

    anomaly_df = pd.DataFrame(columns=["filepath", "conf", "anomaly_type", "barcode"])  #

    with open(path_to_comms_log, "r") as f:
        log_contents = f.readlines()

    anomaly_kword = "WebAPAT for Anomaly Detection:"
    for line in log_contents:
        if anomaly_kword in line:
            json_dict_string = line[line.find("{"):].replace("'", '"').replace("None", '"none"')
            json_dict = json.loads(json_dict_string)
            image_dict = json_dict["images"]
            for anomaly_image in image_dict:
                image_path = anomaly_image["filepath"]
                anomaly_dict = anomaly_image["anomaly_types"]
                if "06" in anomaly_image["anomaly_type"]:
                    print("06 dteected")
                for anomaly_detection in anomaly_dict:
                    confidence = anomaly_detection["confidence"]
                    anom_type = anomaly_detection["anomaly_type"]
                    barcode = anomaly_image["barcodes"][0]["barcode"]

                    anomaly_df.loc[len(anomaly_df)] = [image_path, confidence, anom_type, barcode]

    return anomaly_df


def save_log_data(hazmat_df, output_name, output_type):

    if output_type in ['csv', 'all']:
        hazmat_df.to_csv(output_name+".csv")

        # save it as a csv

    if output_type in ['json', 'all']:
        # save it as a json
        hazmat_df.to_json(output_name+".json")

    if output_type in ['pkl', 'all']:
        # save it as a pkl
        hazmat_df.to_pickle(output_name + ".pkl")

    print(f"Exported {output_name} to file type: {output_type}")


def create_scp_env(anomaly_df, output_name):
    """
    Function to create a .sh file that will allow up to SCP files back to a local device
    """
    fpath_str = ''
    for anomaly_id in anomaly_df["anomaly_type"].unique():
        fpath_str += f'export SPOT_CHK_IMGS_ANOMALY_{anomaly_id}="'
        for partial_filepath in anomaly_df.loc[anomaly_df['anomaly_type'] == anomaly_id]["filepath"]:
            if "PSOC" in partial_filepath:
                root_dir = "/images/SPSS-1/"
            else:
                root_dir = "/images/APBS-1/"
            fpath_str += f"{root_dir}"+partial_filepath+" "
        fpath_str += '"\n'

    env_file_name = output_name+"_scp_env.sh"
    with open(env_file_name, 'w') as env_file:
        # env_file.write('export ROOT_DIR="/images/APBS-1/"\n')
        env_file.write(fpath_str)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--log_filepath", help="Input path to the comms log for Anomaly detections",
                        default="/home/garveyer/data/spot_check_imgs/1.10.1_rc1/8_21_2023/prlm_comms_8_21.log")
    parser.add_argument("-o", "--output", help="Path to where you'd like to save the hazmat output",
                        default="/home/garveyer/data/spot_check_imgs/1.10.1_rc1/8_21_2023/")
    parser.add_argument("-t", "--output_type", help="How you'd like to save the output.  Options include 'csv', 'json',"
                                                    "'pkl' or 'all'. 'all' will save all types", default='all',
                        choices=['all', 'csv', 'json'])
    parser.add_argument("-s", "--scp", help="Bool to create a .env file that will assist with SCPing the images from "
                                            "remote to local", default=False)

    args = parser.parse_args()
    filepath = args.log_filepath
    output_path = args.output
    output_type = args.output_type

    anomaly_df = load_data_from_log(filepath)

    output_name = output_path + "/" + filepath.split("/")[-1].split(".")[0] + "_anomaly_summary"

    save_log_data(anomaly_df, output_name, output_type)

    if args.scp:
        create_scp_env(anomaly_df, output_name)

    print(f"In total, there were {len(anomaly_df)} total anomaly detections sent to WebAPAT")
