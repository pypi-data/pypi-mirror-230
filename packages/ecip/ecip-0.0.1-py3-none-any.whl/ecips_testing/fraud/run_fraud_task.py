import glob
import argparse
import json
import os
from ecips_tasks.tasks_comms import process_ocr_results
from ecips_utils.prlmProcessing.read_PRLM import PRLMFile


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory", help="Path to the directory containing prlm files you want to process")

    args = parser.parse_args()
    directory = args.directory

    os.environ["WRITE_BCR_RESULTS"] = False
    os.environ["WRITE_OCR_RESULTS"] = False
    os.environ["ECIPS_PERFORM_BCR"] = False

    prlms = glob.glob(directory + "/**/*.zip*", recursive=True)
    for prlm_file in prlms:
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

        raw_ocr_file = prlm_file[:prlm_file.rindex("/")] + "raw_OCR_results.json"
        with open(raw_ocr_file) as file:
            raw_ocr = json.load(file)

        process_ocr_results(raw_ocr.values(), prlm_info)
