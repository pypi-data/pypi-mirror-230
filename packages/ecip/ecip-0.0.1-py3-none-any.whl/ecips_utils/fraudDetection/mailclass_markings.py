import json
from Levenshtein import distance

import pandas as pd

from ecips_utils.fraudDetection.fraud_config import (
    MAX_DIST_FIRST_CLASS,
    MAX_DIST_PRIORITY_MAIL,
    MAX_DIST_EXPRESS_MAIL,
    MAX_DIST_GA_MAIL,
    MCB_OCR_THRESH
)


def get_fpe_from_service_desc(mail_class_code, text_description):
    """Classifies the 800+ different STC codes into 2 categories, 'Priority' or 'First-Class', 'Express' or 'Hazmat".

    Parameters:
        mail_class_code: str
            Class of code for the STC

    Returns:
        str
            Returns the class name if found, else an empty string
    """
    if "hazmat" in text_description.lower():
        return 'hazmat'
    if "hazard" in text_description.lower():
        return 'hazmat'
    if "ground adv" in text_description.lower():
        return 'ground-advantage'

    if mail_class_code == 'FC':
        return 'first-class'
    elif mail_class_code == 'PM':
        return 'priority'
    elif mail_class_code == 'EX':
        return 'express'
    else:
        return None


def create_stc_database(raw_stc_filepath, save_to_file=False, filepath=None):
    """Read the Excel file containing different Service Type Codes and create a mapping from the STC to mail class.
    Save the mapping as a .json file.

    Parameters:
        raw_stc_filepath: str
            Input filepath to the Excel sheet containing the STC info
        save_to_file: bool, optional, default: False
            Indicates if the STC to mail class mapping should be saved
        filepath: str, optional, default: None
            Filepath for the saved output mapping. Required if save_to_file is True.

    Returns:
        dict{}
            The stc_db dictionary with STC mapped to the Mail Class, {'001': 'First-Class', '026': 'Priority'...}
    """

    raw_stc_df = pd.read_excel(raw_stc_filepath, dtype=str)

    stc_class = []
    for code, desc in zip(raw_stc_df['Class of Mail Code:'], raw_stc_df['Service Description:']):
        stc_class.append(get_fpe_from_service_desc(code, desc))

    raw_stc_df['stc_class'] = stc_class
    stc_db = dict(zip(raw_stc_df['Service Type Code:'], raw_stc_df['stc_class']))

    if save_to_file:
        with open(filepath, 'w', encoding='utf-8') as fp:
            json.dump(stc_db, fp)

    return stc_db


def extract_mail_class_banner_ocr(ocr_results):
    """Method to parse OCR results to extract Mail Class from the banner
    Parameters:
        ocr_results
            OCR results from triton -> [bbox, text, probability]

    Returns:
        str
            Mail class decoded from the banner, i.e. Priority, First Class
    """
    keyword_dict = {'express': 'express',
                    'priority': 'priority',
                    'first': 'first-class',
                    'class': 'first-class',
                    'ground': 'ground-advantage',
                    'advantage': 'ground-advantage'}

    keyword_confidences = {
                           'express': MAX_DIST_EXPRESS_MAIL,
                           'priority': MAX_DIST_PRIORITY_MAIL,
                           'first': MAX_DIST_FIRST_CLASS,
                           'class': MAX_DIST_FIRST_CLASS,
                           'ground': MAX_DIST_GA_MAIL,
                           'advantage': MAX_DIST_GA_MAIL}

    mail_class_from_banner = None

    mcb_metrics = {'is_mailclass_detected_ocr': False}

    # First pick out the text from banner, assuming it is the largest piece of text detected
    biggest_area = 0
    mcb_result = None

    for (box, text, prob) in ocr_results:
        height = box[3][1] - box[0][1]
        width = box[1][0] - box[0][0]
        area = height * width
        if area > biggest_area:
            biggest_area = area
            mcb_result = [box, text, prob]
    text, prob = mcb_result[1], mcb_result[2]
    # Detect class from the mcb_result
    # If OCR prob is lower than threshold we don't have enough data to determine fraud
    if prob <= MCB_OCR_THRESH:
        return mail_class_from_banner, mcb_metrics

    text = text.lower()

    for keyword in keyword_dict:
        if keyword in text:
            mail_class_from_banner = keyword_dict[keyword]
            mcb_metrics = {'is_mailclass_detected_ocr': True,
                           'raw_text': text,
                           'confidence': prob,
                           'exact_text_to_keyword_match': True,
                           'mailclass_mapped': mail_class_from_banner
                           }
            return mail_class_from_banner, mcb_metrics

    # There were no exact matches, so we divide the expected text into chunks and compare lev distances
    for keyword in keyword_dict:
        len_kword = len(keyword)
        max_dist_kword = keyword_confidences[keyword]

        chunks = [text[i: i + len_kword] for i in range(0, len(text) - (len_kword - 1)) if len(text) >= len_kword]
        class_results = [keyword if distance(chunk, keyword) < max_dist_kword
                         else None for chunk in chunks]
        if keyword in class_results:
            mail_class_from_banner = keyword_dict[keyword]
            raw_text = text
            confidence = prob
            mcb_metrics = {'is_mailclass_detected_ocr': True,
                           'raw_text': raw_text,
                           'confidence': confidence,
                           'exact_text_to_keyword_match': False,
                           'mailclass_mapped': mail_class_from_banner
                           }
            return mail_class_from_banner, mcb_metrics

    return mail_class_from_banner, mcb_metrics
