import argparse
import csv
import glob
import json
import os
import shutil
import zipfile


def get_mailpiece_ids(files, mappings):
    dict = {}
    with open(mappings, 'r') as f:
        reader = csv.reader(f)
        # skip header
        reader.__next__()
        for row in reader:
            mpe, mp, prlm, is_fraud = row[1], row[4], row[2], row[-1]
            if mpe == "APPS":
                mp = f'{mp}'
            # elif mpe != "APBS":
            #     continue
            dict[mp] = {"prlm": prlm, "fraud": is_fraud, "mpe": mpe}

    for file in files:
        if len(file[file.rindex('/'):file.rindex('_')]) >= 4:
            img_name = file[file.rindex('_')+1:-6]
        else:
            img_name = file[-14:-6]
        # print(dict.keys())
        if dict[img_name]['mpe'] == "APPS":
            if 'current_filename' in dict[img_name].keys():
                dict[img_name]['current_filename'].append(file)
            else:
                dict[img_name]['current_filename'] = [file]
        else:
            dict[img_name]['current_filename'] = file
    return dict


def get_real_filenames(prlm_files, mailpiece_dict):
    for prlm_file in prlm_files:
        # print(prlm_file)
        mpe = prlm_file[prlm_file.rindex('/') + 1:prlm_file.rindex('/') + 5]
        # print(mpe)
        if mpe == 'APPS':
            for key, values in mailpiece_dict.items():
                if values['mpe'] == 'APPS':
                    mailpiece_dict[key]['prlm_file'] = prlm_file
        if mpe == 'SPSS':
            for key, values in mailpiece_dict.items():
                if values['mpe'] == 'SPSS':
                    mailpiece_dict[key]['prlm_file'] = prlm_file
        if mpe == 'APBS':
            site = prlm_file[prlm_file.rindex('/') + 6:]
            prlm = site[:site.index('_')]
            with open(prlm_file, 'r') as f:
                reader = csv.reader(f)
                # skip PRLM header
                reader.__next__()
                reader.__next__()

                # process each row...
                for row in reader:
                    mp = row[0]
                    if mp in mailpiece_dict.keys():
                        if prlm == mailpiece_dict[mp]['prlm'].split(' ')[0]:
                            mailpiece_dict[mp]['real_name'] = row[-1][9:]

    return mailpiece_dict


def get_new_val_path(prlm_file):
    prlm_name = os.path.basename(prlm_file)
    prlm_name_split = prlm_name.split('_')
    machine_folder = f'{prlm_name_split[0]}_{prlm_name_split[1]}'
    date = prlm_name_split[-1][:-5]
    date = f'{date[:4]}-{date[4:6]}-{date[6:8]}'
    run = prlm_name_split[-2]
    return f'{machine_folder}/{date}/{run}/'


def move_prlm(prlm_files, base_filepath):
    for prlm_file in prlm_files:
        prlm_filepath = f'{base_filepath}/{get_new_val_path(prlm_file)}'
        if not os.path.exists(prlm_filepath):
            os.makedirs(prlm_filepath)
            new_zip = f'{prlm_filepath}{os.path.basename(prlm_file)}.zip'
            with zipfile.ZipFile(new_zip, 'w') as zip_object:
                zip_object.write(prlm_file)


def move_images_to_all(new_filepath, image_dict):
    for key, value in image_dict.items():

        if 'current_filename' not in value:
            continue
        mpe = value['mpe']
        current_file = value['current_filename']
        print(current_file)
        prlm = value['prlm']
        # print(value)
        if mpe == 'APPS':
            for file in current_file:
                new_file = file
                trunc_file = new_file[new_file.rindex("/") + 1:]
                prlm_file = value['prlm_file']
                prlm_name_split = prlm_file[prlm_file.rindex('/'):].split("_")
                if f'{prlm.split(" ")[0]}' not in ["BUSSE", "NORTH", "CITY"]:
                    continue
                # print(prlm_name_split)
                date = prlm_name_split[-1][:-5]
                date = f'{date[:4]}-{date[4:6]}-{date[6:8]}'
                run = prlm_name_split[-2]
                # print("trun_file")
                # print(value)
                sub_run = trunc_file[:trunc_file.index("_")]
                # print(f'{prlm.split(" ")[0]}')
                sub_run_path = f'{new_filepath}/{mpe}_{prlm.split(" ")[0]}/{date}/{run}/{sub_run}/'
                full_image_filepath = f'{sub_run_path}{trunc_file}'

                if not os.path.exists(sub_run_path):
                    os.mkdir(sub_run_path)
                shutil.copy(file, full_image_filepath)
        if mpe == 'SPSS':
            new_file = current_file
            trunc_file = new_file[new_file.rindex("/") + 1:]
            prlm_file = value['prlm_file']
            prlm_name_split = prlm_file[prlm_file.rindex('/'):].split("_")
            if f'{prlm.split(" ")[0]}' not in ["BUSSE", "NORTH", "CITY"]:
                continue
            # print(prlm_name_split)
            date = prlm_name_split[-1][:-5]
            date = f'{date[:4]}-{date[4:6]}-{date[6:8]}'
            run = prlm_name_split[-2]
            # print("trun_file")
            # print(value)
            sub_run = trunc_file[:trunc_file.index("_")]
            # print(f'{prlm.split(" ")[0]}')
            sub_run_path = f'{new_filepath}/{mpe}_{prlm.split(" ")[0]}/{date}/{run}/{sub_run}/'
            full_image_filepath = f'{sub_run_path}{trunc_file}'

            if not os.path.exists(sub_run_path):
                os.mkdir(sub_run_path)
            shutil.copy(file, full_image_filepath)

        else:
            if prlm != 'NORTH HOUSTON PDC':
                continue
            new_file = value['real_name']
            sub_run = new_file[:new_file.rindex("/")]
            sub_run_path = f'{new_filepath}/{mpe}_{prlm.split(" ")[0]}{sub_run}/'
            full_image_filepath = f'{new_filepath}/{mpe}_{prlm.split(" ")[0]}{new_file}'

            if not os.path.exists(sub_run_path):
                os.mkdir(sub_run_path)

            shutil.copy(current_file, full_image_filepath)


def move_images_to_fraud_type(new_filepath, image_dict, fraud_type):
    for key, value in image_dict.items():
        mpe = value['mpe']
        current_file = value['current_filename']
        # prlm = value['prlm']

        if mpe == 'APPS':
            for file in current_file:
                new_file = file

                is_fraud = value['fraud']

                trunc_file = new_file[new_file.rindex("/"):]
                # new path
                full_filepath = f'{new_filepath}/{fraud_type}{trunc_file}'

                # copy file
                shutil.copy(file, full_filepath)

                # append to gt
                gt = f'{new_filepath}/{fraud_type}/{fraud_type}_gt_results.json'

                with open(gt) as file:
                    file_data = json.load(file)

                file_data[trunc_file[1:]] = is_fraud

                with open(gt, 'w') as file:
                    json.dump(file_data, file)

        else:
            new_file = value['real_name']
            is_fraud = value['fraud']

            trunc_file = new_file[new_file.rindex("/"):]
            # new path
            full_filepath = f'{new_filepath}/{fraud_type}{trunc_file}'

            # copy file
            shutil.copy(current_file, full_filepath)

            # append to gt
            gt = f'{new_filepath}/{fraud_type}/{fraud_type}_gt_results.json'
            with open(gt) as file:
                file_data = json.load(file)

            file_data[trunc_file[1:]] = is_fraud

            with open(gt, 'w') as file:
                json.dump(file_data, file)


def main(prlm_folder, image_folder, grid_csv, version, fraud_type):
    # Get folder structure
    ALL_IMAGES_PATH = '/data/Fraud/datasets/validation_set/invalid_eVS_permit_numbers/ALL_IMAGES'

    prlm_files = glob.glob(f'{prlm_folder}/*.prlm')
    # print(prlm_files)
    # Move the PRLMs to appropriate folder
    # move_prlm(prlm_files, ALL_IMAGES_PATH)

    # Process input images to get correct filepaths
    image_files = glob.glob(f'{image_folder}/*.tiff')

    mailpiece_dict = get_mailpiece_ids(image_files, grid_csv)
#     print(mailpiece_dict)
    full_dict = get_real_filenames(prlm_files, mailpiece_dict)

#     # Move the images to the all images location
    move_images_to_all(ALL_IMAGES_PATH, full_dict)

    # # Move images to fraud type
    # FRAUD_TYPE_PATH = f'/data/Fraud/datasets/validation_set/{version}'
    # move_images_to_fraud_type(FRAUD_TYPE_PATH, full_dict, fraud_type)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--prlms",
                        help="""
                                Directory path to prlm file downloaded from webapat corresponding to the input images.
                                Example: ~/Downloads/webapat/PRLM
                             """
                        )

    parser.add_argument("-i", "--image_folder",
                        help="""
                                Directory path to folder with images downloaded from webapat to add to validation
                                dataset
                                Example: ~/Downloads/webapat/images
                            """
                        )
    parser.add_argument("-c", "--grid_csv",
                        help="""
                                Path to csv with information about the table downloaded from webapat
                                Example: ~/Downloads/webapat/grid_csv.csv
                            """
                        )

    parser.add_argument("-v", "--version",
                        help="""
                               Version of validation set to add to
                               Example: v1.0.1
                            """
                        )
    parser.add_argument("-f", "--fraud_type",
                        help="""
                               Type of fraud detected out of the following:
                               SN, Date, MBC, PI, STC
                            """
                        )

    args = parser.parse_args()

    main(args.prlms, args.image_folder, args.grid_csv, args.version, args.fraud_type)
