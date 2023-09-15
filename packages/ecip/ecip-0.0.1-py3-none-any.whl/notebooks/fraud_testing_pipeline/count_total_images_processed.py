import glob
import sys
import os

sys.path.append(os.getcwd())
from ecips_utils.prlmProcessing.read_PRLM import PRLMFile

if __name__ == "__main__":
    path_to_all_images = "/data/Fraud/datasets/fraud_images_for_review/images_from_2023_01_13/ALL_IMAGES/"

    all_prlm_files = glob.glob(path_to_all_images + "/**/**/**/*.zip")

    total_image_count = 0
    for prlm_file in all_prlm_files:

        prlm_obj = PRLMFile(prlm_file)
        total_image_count += len(prlm_obj.prlm_filepaths)
        print(f"{prlm_file} file contained {len(prlm_obj.prlm_filepaths)} total images")

    print(f"Total prlms processed: {len(all_prlm_files)} \n"
          f"Total images in all PRLMs: {total_image_count}")
