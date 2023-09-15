import argparse
import csv
import glob
import sys
import os
import shutil
from zipfile import ZipFile
from ecips_utils.prlmProcessing.read_PRLM import PRLMFile
sys.path.append(os.getcwd())


PROJECT_ROOT_DIR = "/" + os.path.join(*os.path.split(os.getcwd())[0].split("/")[:-1])
os.environ['INVALID_PERMIT_FILE'] = PROJECT_ROOT_DIR + "/Docker/Invalid_eVS_Permit_List.xlsx"
os.environ['STC_DB_FILE'] = PROJECT_ROOT_DIR + "/Docker/stc_db.json"


def convert_to_prlm(csv_file, output_path, images, simulated_apps="/APPS-060/2023-03-06/01-248/", sub_run="01"):
    with open(csv_file, "r") as webapat_csv:
        webapat_prlm = csv.reader(webapat_csv)
        webapat_prlm.__next__()
        if not os.path.exists(f"{output_path}{simulated_apps}"):
            os.makedirs(f"{output_path}{simulated_apps}")
        output_prlm = output_path + f"{simulated_apps}/WebAPAT_generated_PRLM.PRLM"
        with open(output_prlm, "w") as csv_file:
            writer = csv.writer(csv_file, delimiter=',')
            for line in webapat_prlm:
                # ln_contents = line.split(",")
                if line[0] == "No Image":
                    continue
                if line[1] == "APPS":
                    mail_id = line[4]
                else:
                    mail_id = '00' + line[4]  # .lstrip("0")
                bcr = line[13]
                outline = [mail_id, "", "", "", "", "", "", "", "", bcr, "", "", "", "", "", "",
                           ""]  # f"{mail_id},,,,,,,,{bcr},,,,,,,,,"
                writer.writerow(outline)

    # Zip prlm tp zip
    zipfile = output_prlm + ".zip"
    with ZipFile(zipfile, 'w') as zip_file:
        zip_file.write(output_prlm)

    if not os.path.exists(f"{output_path}{simulated_apps}/{sub_run}"):
        os.makedirs(f"{output_path}{simulated_apps}/{sub_run}")
    for image in images:
        shutil.copy(image, f"{output_path}{simulated_apps}/{sub_run}")

    return output_prlm


def test_prlm(output_path, all_images):
    zip_prlm = output_path + ".zip"

    prlm = PRLMFile(zip_prlm)

    ibi = prlm.get_ibi_barcodes()
    impb = prlm.get_impb_barcodes()
    images = prlm.get_image_filepaths()

    print(f'images in prlm: {len(images)}')
    print(f'images in folder: {len(all_images)}')
    if (len(images) == len(all_images)) and (len(ibi) > 0) and (len(impb) > 0):
        print("Success")
    else:
        print("Failure in PRLM creation, investigate further")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_file", help="Input path to the export.csv file form WebAPAT")
    parser.add_argument("-o", "--output", help="Path to where you'd like to save simulated directory")
    parser.add_argument("-p", "--images", help="Path to images we want to add to our new simulated directory")

    args = parser.parse_args()
    csv_file = args.input_file
    output_path = args.output
    images = glob.glob(args.images+"/*.tif*")

    output_prlm = convert_to_prlm(csv_file, output_path, images)
    test_prlm(output_prlm, images)
