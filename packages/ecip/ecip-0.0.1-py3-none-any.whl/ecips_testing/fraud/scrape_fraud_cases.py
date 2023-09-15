import argparse
import glob
import os
import shutil
import json
import datetime


def scrape_fraud(date_folder, target_dir, folder_dir):
    tmp_folder = date_folder[:date_folder.rindex("/")]
    mpe_folder = tmp_folder[tmp_folder.rindex("/")+1:]
    for run in glob.iglob(date_folder+"/*"):
        fraud_json = run+"/Fraud_WebAPAT_message.json"
        ocr = run+"/raw_OCR_results.json"
        if os.path.exists(fraud_json) and os.path.exists(ocr):
            prlm = glob.glob(run+"/*.zip")[0]
            prlm_copied = False
            with open(fraud_json) as file:
                file_data = json.load(file)
            for fraud_case in file_data['images']:
                fraud_types = fraud_case["fraud_type"].split(",")[:-1]
                for ft in fraud_types:
                    tif_file = fraud_case["filepath"]
                    json_file = tif_file[:tif_file.rindex(".")]+".json"
                    current_image_filepath = date_folder[:date_folder.rindex("/")]+"/"+tif_file
                    current_json_filepath = date_folder[:date_folder.rindex("/")]+"/"+json_file
                    fraud_filepath = target_dir+"/"+folder_dir[ft]+"/"
                    images_filepath = target_dir+"/ALL_IMAGES/"+mpe_folder+"/"+tif_file[:tif_file.rindex("/")]
                    if not os.path.exists(images_filepath):
                        os.makedirs(images_filepath)
                    shutil.copy(current_image_filepath, fraud_filepath)
                    shutil.copy(current_image_filepath, images_filepath)
                    shutil.copy(current_json_filepath, images_filepath)
                    if not prlm_copied:
                        images_filepath = images_filepath[:images_filepath.rindex("/")]
                        if "SPSS" in mpe_folder:
                            images_filepath = images_filepath[:images_filepath.rindex("/")]
                        shutil.copy(prlm, images_filepath)
                        shutil.copy(fraud_json, images_filepath)
                        shutil.copy(ocr, images_filepath)
                        prlm_copied = True


def main(home, directories, days):
    folder_dir = {
        "mismatch_humanReadableSN_decodedIBISN": "SN",
        "mismatch_mailclass_servicetype": "STC",
        "mismatch_mailclass_lettercode": "MCB",
        "invalid_ePostage": "invalid_epostage",
        "mismatch_humanReadableDate_decodedIBIDate": "Date",
        "invalid_eVS_permit": "evs_invalid_permit",
        "missing_eVS_validation": "evs_missing_validation",
        "mismatch_hr_impb": "IMPB",
        "invalid_IBI_SN": "invalid_SN",
        }
    current_date = datetime.datetime.now()
    last_date = current_date - datetime.timedelta(days=days)
    target_dir = home + "/images_from_" + current_date.strftime("%Y_%m_%d")
    os.makedirs(target_dir)
    os.makedirs(target_dir+"/ALL_IMAGES")
    for folder in folder_dir.values():
        os.makedirs(target_dir + "/" + folder)

    for directory in directories:
        for filename in glob.iglob(directory+"/*"):
            date = datetime.datetime.strptime(filename.split('/')[-1], '%Y-%m-%d')
            if last_date <= date <= current_date:
                scrape_fraud(filename, target_dir, folder_dir)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--directories', nargs='+', required=True,
                        help="""
                        list of directories to scrape for webapat fraud results. Expect the file structure to follow
                        that of /data/Fraud/dataset/validation_set/v1.0.0/ALL_IMAGES/{mpe}
                        where the folders are named for dates
                        Ex:
                        -d '/images/APBS-0/' 'images/APPS-1/'
                        """)
    parser.add_argument('--home', required=True,
                        help="""
                        directory to put the images folder in. Best practice is to put it in your home directory.
                        Specify full path
                        Ex:
                        -home '/home/username'
                        """)
    parser.add_argument('--range', required=True, type=int,
                        help="""
                        Range of days to check for fraud images
                        Ex:
                        --range 1
                        """)
    args = parser.parse_args()
    main(args.home, args.directories, args.range)
