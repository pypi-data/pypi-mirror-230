import os
import sys
import orjson
import requests
from tqdm import tqdm
import argparse

PROJECT_ROOT_DIR = "/"+os.path.join(*os.path.split(os.getcwd())[0].split("/"))
os.environ['INVALID_PERMIT_FILE'] = PROJECT_ROOT_DIR + "/Docker/Invalid_eVS_Permit_List.xlsx"
os.environ['STC_DB_FILE'] = PROJECT_ROOT_DIR + "/Docker/stc_db.json"

from ecips_tasks.tasks import compute_OCR_from_filepath
from ecips_utils import ecips_config
from ecips_utils.fraudDetection.fraud_config import FRAUD_TYPES
from ecips_utils.packageObject.packageclass import ImageObject
from ecips_utils.prlmProcessing.read_PRLM import PRLMFile
from ecips_utils.create_webapat_idd9 import generate_webapat_bcr_message, \
    generate_webapat_fraud_message

def compute_feature_from_filepath(
    img_filepath,
    port,
    write_tofile=True,
    algorithm="",
    send_hazmat_to_webapat=False,
):
    """
    This Function calculates keypoints and descriptors based on the algorithms selected
    Supported Algorithms are orb, sift and pysift from a filepath.  It then writes the resulting json to file


    Parameters:
    img_filepath: an img created by OpenCV imread Function


    Returns:
    keypoints: Keypoint Values
    descriptors: [nxm] array

    """

    # Instantiate Image Object:
    image = ImageObject(img_filepath)

    # Load imagery & confirm it is valid
    image.check_img_valid()

    if image.is_valid_img():
        # Call the triton inference server
        try:
            image.update_grpc_url(f'localhost:{port}')
            image.get_triton_response()
        except Exception as e:
            raise Exception(f"Error occurred during call to Triton Inference Server: {e}")
        # Extract the ECIP's attributes from the response
        # If the triton response did not return a too small image
        if image.is_valid_img():
            image.extract_from_response()

            # Generate the json file with all results
            results_dict, results_json = image.generate_results_json()

            # Write the json file to the disk
            if write_tofile:
                filepath = image.json_filepath[image.json_filepath.rindex("/"):]
                with open(filepath, "wb") as fp:
                    fp.write(orjson.dumps(results_dict, option=orjson.OPT_SERIALIZE_NUMPY))

                # R.lpush("dailyJson_filePath", filepath)
                image.json_written = True

            return results_json


def compute_feature_test(directory, all_images, port):
    print(f"{len(all_images)} Images total found to process in directory {directory} ")
    for image in tqdm(all_images, desc="computing features from image files"):
        results = compute_feature_from_filepath(image, port)


def compute_OCR_from_filepath(
    filepath,
    ibi,
    impb,
    port,
    ecips_serving_url=ecips_config.ECIPS_INFERENCE_SERVER_URL,
    perform_bcr=True,
    detect_fraud=True
):
    image = ImageObject(filepath, load_from_json=True)
    image.update_grpc_url(f"localhost:{port}")

    if not image.json_written:
        return {"bcr_results": {}, "fraud_results": {}, "raw_ocr_results": {}}

    try:
        image.get_triton_response(model_name='shipping_label_ocr')
    except Exception as e:
        raise Exception(f"Error occurred during call to Triton Inference Server: {e}")

    image.extract_from_response(model_name='shipping_label_ocr')

    barcode_metrics = image.bcr_metrics

    # initialize to empty string
    fraud_json = {}
    bcr_json = {}

    # initialize to False:
    send_bcr_result = False

    if perform_bcr and (impb is None or impb == ''):
        bcr_json, send_bcr_result = generate_webapat_bcr_message(image)

    if detect_fraud:
        if ibi:
            image.add_ibi_label(ibi)
        if impb:
            image.add_impb_label(impb_decoded=impb)
        elif send_bcr_result:
            # The impb barcode was able to be reconstructed
            # TODO: do we want to compare to >1 barcode?
            image.add_impb_label(impb_reconstructed=barcode_metrics[0]['barcode'])

        fraud_json, send_fraud_result = generate_webapat_fraud_message(image)

    results_json = {"bcr_results": bcr_json,
                    "fraud_results": fraud_json,
                    "raw_ocr_results": {filepath: image.ocr_results}}

    return results_json


def process_prlm_start(
    prlm_file,
    port,
    webapat_url="https://56.76.171.26/ecip-api/api/EcipRequest",
    webapat_secret_key="testing-79a1-40a3-8f0b-6513658be4ac",
):
    prlm_obj = PRLMFile(prlm_file)
    images_to_bcr = prlm_obj.get_images_to_bcr()
    ibi_barcode_dict = prlm_obj.get_ibi_barcodes()
    impb_barcode_dict = prlm_obj.get_impb_barcodes()
    images_in_prlm = prlm_obj.get_image_filepaths()

    prlm_info = {"filepath": prlm_file,
                 "total_packages_wout_barcode": prlm_obj.total_packages_wout_barcode,
                 "total_packages": prlm_obj.total_packages,
                 "images_to_bcr": len(images_to_bcr),
                 "device_key": prlm_obj.device_key}

    if ecips_config.ECIPS_PERFORM_BCR or ecips_config.ECIPS_DETECT_FRAUD:
        # for img_file in images_in_prlm:
        #     print(img_file)
        # return
        ocr_results = [
            compute_OCR_from_filepath(img_file, ibi_barcode_dict[img_file], impb_barcode_dict[img_file], port) for
            img_file in images_in_prlm]

        process_ocr_results(ocr_results, prlm_info)


def process_ocr_results(ocr_results,
                        prlm_info,
                        webapat_url=ecips_config.ECIPS_WEBAPAT_URL,
                        webapat_secret_key=ecips_config.ECIPS_WEBAPAT_SECRET_KEY,
                        ):
    root_prlm_dir = prlm_info["filepath"].split(prlm_info["filepath"].split("/")[-1])[0]

    if ecips_config.ECIPS_PERFORM_BCR:
        # Count how many images were successfully reconstructed
        images_w_barcode_ct = 0
        img_base_out = []
        for result in ocr_results:
            try:
                bcr_result = result["bcr_results"]
            except TypeError:
                # If an error occurred on the task, then we cannot grab results as a dict
                continue
            if bcr_result != {} and type(bcr_result) == dict:
                # Adds 0 if false, 1 if True to count the number of successfully reconstructed barcodes
                images_w_barcode_ct += 1
                img_base_out.append(bcr_result)

        if images_w_barcode_ct > 0:
            for json_index in range(0, len(img_base_out), ecips_config.ECIPS_WEBAPAT_MAX_JSON_IMGS):
                results_json = {
                    "secretkey": webapat_secret_key,
                    "action": "rbc_orig_list_from_ecip",
                    "images": img_base_out[json_index:json_index + ecips_config.ECIPS_WEBAPAT_MAX_JSON_IMGS]
                }

                bcr_request = requests.post(
                    webapat_url,
                    json=results_json,
                    verify="/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem",
                    headers={"Content-type": "application/json", "Accept": "text/plain"},
                    timeout=ecips_config.ECIPS_WEBAPAT_TIMEOUT
                )
                bcr_request = bcr_request.json()

            if ecips_config.WRITE_BCR_RESULTS:
                filepath_json = root_prlm_dir + "BCR_WebAPAT_message.json"
                results_json = {
                    "secretkey": webapat_secret_key,
                    "action": "rbc_orig_list_from_ecip",
                    "images": img_base_out
                }
                with open(filepath_json, "wb") as fp:
                    fp.write(orjson.dumps(results_json, option=orjson.OPT_SERIALIZE_NUMPY))

        else:
            bcr_request = {}

    if ecips_config.ECIPS_DETECT_FRAUD:
        # Count how many images were successfully reconstructed
        fraud_type_count = {fraud_type: 0 for fraud_type in FRAUD_TYPES}
        images_w_fraud_ct = 0
        img_base_out = []
        for result in ocr_results:
            try:
                fraud_results = result["fraud_results"]
            except TypeError:
                # If an error occurred on the task, then we cannot grab results as a dict
                continue
            if fraud_results != {} and type(fraud_results) == dict:
                images_w_fraud_ct += 1
                fraud_type_detected = fraud_results["fraud_type"].split(',')[:-1]
                for fraud in fraud_type_detected:
                    fraud_type_count[fraud] += 1
                img_base_out.append(fraud_results)

        if images_w_fraud_ct > 0:
            for json_index in range(0, len(img_base_out), ecips_config.ECIPS_WEBAPAT_MAX_JSON_IMGS):
                results_json = {
                    "secretkey": webapat_secret_key,
                    "action": "fr_orig_list_from_ecip",
                    "images": img_base_out[json_index:json_index + ecips_config.ECIPS_WEBAPAT_MAX_JSON_IMGS]
                }

                fraud_request = requests.post(
                    webapat_url,
                    json=results_json,
                    verify="/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem",
                    headers={"Content-type": "application/json", "Accept": "text/plain"},
                    timeout=ecips_config.ECIPS_WEBAPAT_TIMEOUT
                )
                fraud_request = fraud_request.json()

            if ecips_config.WRITE_FRAUD_RESULTS:
                filepath_json = root_prlm_dir + "Fraud_WebAPAT_message.json"
                results_json = {
                    "secretkey": webapat_secret_key,
                    "action": "fr_orig_list_from_ecip",
                    "images": img_base_out
                }
                with open(filepath_json, "wb") as fp:
                    fp.write(orjson.dumps(results_json, option=orjson.OPT_SERIALIZE_NUMPY))

        else:
            fraud_request = {}

        if ecips_config.WRITE_OCR_RESULTS:
            json_out = {}
            # write the OCR results to a json file
            for result in ocr_results:
                raw_ocr_results = result["raw_ocr_results"]
                if raw_ocr_results != {} and type(raw_ocr_results) == dict:
                    # Adds 0 if false, 1 if True to count the number of successfully reconstructed barcodes
                    json_out.update(raw_ocr_results)

            filepath_json = root_prlm_dir + "raw_OCR_results.json"
            with open(filepath_json, "wb") as fp:
                fp.write(orjson.dumps(json_out, option=orjson.OPT_SERIALIZE_NUMPY))

        return {"bcr_request_results": bcr_request, "fraud_request_results": fraud_request}


def process_prlms(prlms, port):
    print(f"{len(prlms)} prlms total found to process in directory {prlms[0]} ")

    for prlm in tqdm(prlms, desc="Processing PRLMs"):
        process_prlm_start(prlm, port)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("-d", "--directory",
                        help="""
                                Validation directory path of data to run fraud on. Must be in the typical format
                                Example: /data/Fraud/datasets/validation_set/v1.0.0/ALL_IMAGES
                            """,
                        default="/data/Fraud/datasets/validation_set/v1.0.2/ALL_IMAGES"
                        )
    parser.add_argument("-p", "--port",
                        help="""
                                   port ecips_serving is running on 
                               """,
                        default="8001"
                        )

    args = parser.parse_args()

    # all_images = glob.glob(args.directory+"/**/*.tif*", recursive=True)
    # if not os.path.exists(args.output_dir):
    #     os.makedirs(args.output_dir+"/image_jsons/")
    # compute_feature_test(args.directory, all_images, args.port)
    prlms = [args.directory]
    process_prlms(prlms, args.port)
