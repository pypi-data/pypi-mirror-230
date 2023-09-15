import pathlib
from pathlib import Path
from datetime import datetime
from ecips_utils import ecips_config
import os
import glob
import logging
from dateutil.parser import parse as date_parser


def calculate_ecips_path(filepath,
                         plantName=ecips_config.ECIPS_DEVICE_MAPPING['name'],
                         mpeDeviceMapping=ecips_config.get_mpe_mappings()):

    """
    This function calculates package details from the MPE path to include day


    Parameters:
    item (PackageImage): an img created by OpenCV imread Function

    Returns:
    results_dict = {"img_filepath": filepath,
                    "mpe_device": mpeDevice,
                    "year": year,
                    "month": monthOfYear,
                    "day": dayOfMonth,
                    "plant_name": plantName,
                    "mpe_ip": mpeDeviceMapping[mpeDevice]}

    """

    fileDate = datetime.utcfromtimestamp(os.path.getmtime(filepath))

    filepath = pathlib.Path(filepath)
    mpeDevice = list(filepath.parents)[-3].stem

    try:
        mpe_ip = mpeDeviceMapping[mpeDevice]
    except KeyError:
        mpe_ip = "0.0.0.0"

    results_dict = {"img_filepath": filepath,
                    "mpe_device": mpeDevice,
                    "year": fileDate.year,
                    "month": fileDate.month,
                    "day": fileDate.day,
                    "plant_name": plantName,
                    "mpe_ip": mpe_ip}

    return results_dict


def calcDateFromJson(result_dict):
    """
    This is a helper function that creates a datetime from a json

    return:
       datetime

    """

    return datetime(year=int(result_dict['year']),
                    month=int(result_dict['month']),
                    day=int(result_dict['day']))


def calcRunFinished(filepath):
    """
    Helper function to determine whether the complete run is complete and prlm ready to be processed
    return:
        boolean
    """
    if "SPSS" in filepath or "PSM" in filepath:
        avl_file = filepath.split(".")[0] + ".avl"
        if os.path.exists(avl_file):
            return True
        return False
    return True


def calcIfFileInDateRange(filepath, start, end):
    """
    This is a helper function calculates weather a filepath is within an explicit time window

    return:
       datetime

    """

    fileTime = calcDateFromJson(calculate_ecips_path(filepath))

    if start <= fileTime <= end:
        return True
    else:
        return False


def jsonList(ecips_image_directory, start, end):
    """
    This is a helper function to create a list of jsons to function based on time and folder structure

    return:
       path_list = ['path/tofile1.json', 'path/tofile2.json']

    """
    path_list = []

    for path in Path(ecips_image_directory).rglob('*.json'):

        if calcIfFileInDateRange(path, start, end):
            path_list.append(str(path))

    return path_list


def calcIfFileInDateRangeCTime(filepath, start, end):
    """
    This is a helper function calculates weather a filepath is within an explicit time window

    return:
       datetime

    """

    fileTime = datetime.fromtimestamp(os.path.getctime(filepath))

    if start <= fileTime <= end:
        return True
    else:
        return False


def imageList(ecips_image_directory, start, end):
    """
    This is a helper function to create a list of jsons to function based on time and folder structure

    return:
       path_list = ['path/tofile1.json', 'path/tofile2.json']

    """
    path_list = []
    for extension in ecips_config.ECIPS_MPE_FILE_EXTENSION_PATTERN:
        for path in Path(ecips_image_directory).rglob(extension):

            if calcIfFileInDateRangeCTime(path, start, end):
                path_list.append(str(path))

    return path_list


def get_current_directory(ecips_image_directory=ecips_config.ECIPS_MPE_LANDING_ZONE_PATH):
    """
    This is a helper function that gets the latest directory that mpe devices
    have been syncing to.

    Output:
        directories_list - directories current mpes of interest are syncing to
    """

    mpe_listings = ecips_config.get_mpe_mappings()
    directories_list = []

    logging.info("Gather parent mpe directories")
    for mpe in mpe_listings:
        directories = glob.glob(ecips_image_directory + mpe + '/*')

        if len(directories) > 0:
            # sort just in case
            directories = sort_dirs_by_date(directories)

            # grab last two days of directories to handle close to midnight edge cases
            directories = directories[-2:]

            directories_list.extend(directories)

    return directories_list


def sort_dirs_by_date(directories):
    """
    This is a helper function orders a list of directories by the date parsed from it with the
    standard dateutil package.

    Input:
      directories - list of directories to be ordered by date (least to greatest).

     Output:
      ordered_dirs - list of directories ordered by least to greatest.
    """

    logging.info("Sorting the directories by date.")
    date_dict = {directory: date_parser(Path(directory).stem) for directory in directories}
    ordered_dirs = {k: v for k, v in sorted(date_dict.items(), key=lambda item: item[1])}
    return list(ordered_dirs.keys())


def get_files(directories, file_ext=ecips_config.ECIPS_MPE_FILE_EXTENSION_PATTERN):
    """
    This is a helper function that grabs all the relevant files from the directory(ies) provided.

    Input:
        directories - list of directories relevant files should be taken from

    Output:
        filepaths - all the relevant files that were gathered
    """

    filepaths = []
    for directory in directories:
        logging.info("Gathering relevant files in directory {}".format(directory))
        for extension in file_ext:
            filepaths.extend(list(map(str, Path(directory).rglob(extension))))

    return filepaths


def get_mpe_images(start, end):
    """
    This is a helper function that gathers all releveant mpe images.

    Output:
    path_list - image filepaths gathered from mpe within the last two days
    within the start and end time
    """

    logging.info("Starting to gather all relevant images from MPE's of interest")

    # only getting the last two directories to handle close to midnight edge cases
    directories = get_current_directory()
    image_filepaths = get_files(directories)

    logging.info(f"Grabbing images within {start} and {end} time window")
    path_list = []
    for path in image_filepaths:
        if calcIfFileInDateRangeCTime(path, start, end):
            path_list.append(str(path))

    return path_list


def get_prlm(start, end):
    """
    This is a helper function that gathers all relevant mpe prlm files.

    Output:
    path_list - prlm filepaths gathered from mpe witin the last two days
    within the start and end time
    """

    logging.info("Starting to gather all relevant prlm files from MPE's of interest")

    # only getting the last two directories to handle close to midnight edge cases
    directories = get_current_directory()
    prlm_filepaths = get_files(directories, file_ext=ecips_config.ECIPS_PRLM_FILE_EXTENSION_PATTERN)

    logging.info(f"Grabbing prlm files within {start} and {end} time window")
    path_list = []
    for path in prlm_filepaths:
        if calcIfFileInDateRangeCTime(path, start, end) and calcRunFinished(path):
            path_list.append(str(path))
    return path_list


def get_mpe_name(filepath):
    for mt in ecips_config.MPE_LIST:
        if mt in filepath:
            return mt
    # NOTE: This shouldn't happen since unsupported machine types are filtered
    # out when looking for PRLM files
    return ''
