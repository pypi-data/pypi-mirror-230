import argparse
import pandas as pd
import json


def load_data_from_log(path_to_comms_log):

    hazmat_df = pd.DataFrame(columns=["filepath", "class_id", "conf", "x1", "y1", "x2", "y2"])  #

    with open(path_to_comms_log, "r") as f:
        log_contents = f.readlines()

    hazmat_kword = "JSON results for"
    for line in log_contents:
        if hazmat_kword in line:
            json_dict = json.loads(line[line.find("{"):].replace("'", '"'))
            image_dict = json_dict["images"][0]  # there will only be one image per json
            image_path = image_dict["filepath"]
            hazmat_dict = image_dict["hazmat_labels"]
            for hazmat_detection in hazmat_dict:
                score = hazmat_detection["score"]
                class_id = hazmat_detection["class"]
                x1 = hazmat_detection["x1"]
                x2 = hazmat_detection["x2"]
                y1 = hazmat_detection["y1"]
                y2 = hazmat_detection["y2"]
                hazmat_df.loc[len(hazmat_df)] = [image_path, class_id, score, x1, y1, x2, y2]

    return hazmat_df


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


def create_scp_env(hazmat_df, output_name):
    """
    Function to create a .sh file that will allow up to SCP files back to a local device
    """
    fpath_str = 'export SPOT_CHK_IMGS="'
    for partial_filepath in hazmat_df["filepath"]:
        fpath_str += "${ROOT_DIR}/"+partial_filepath+" "
    fpath_str += '"\n'

    env_file_name = output_name+"_scp_env.sh"
    with open(env_file_name, 'w') as env_file:
        env_file.write('export ROOT_DIR="/images/APBS-1/"\n')
        env_file.write(fpath_str)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--log_filepath", help="Input path to the comms log for Hazmat detections")
    parser.add_argument("-o", "--output", help="Path to where you'd like to save the hazmat output")
    parser.add_argument("-t", "--output_type", help="How you'd like to save the output.  Options include 'csv', 'json',"
                                                    "'pkl' or 'all'. 'all' will save all types", default='all',
                        choices=['all', 'csv', 'json'])
    parser.add_argument("-s", "--scp", help="Bool to create a .env file that will assist with SCPing the images from "
                                            "remote to local")

    args = parser.parse_args()
    filepath = args.log_filepath
    output_path = args.output
    output_type = args.output_type

    hazmat_df = load_data_from_log(filepath)

    output_name = output_path + "/" + filepath.split("/")[-1].split(".")[0] + "_hazmat_summary"

    save_log_data(hazmat_df, output_name, output_type)

    if args.scp:
        create_scp_env(hazmat_df, output_name)

    print(f"In total, there were {len(hazmat_df)} total hazmat detections sent to WebAPAT")
