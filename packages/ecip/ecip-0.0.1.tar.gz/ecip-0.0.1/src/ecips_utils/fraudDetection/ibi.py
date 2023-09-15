import re
import base64
from datetime import datetime, timedelta
from Levenshtein import distance

from ecips_utils.fraudDetection.fraud_config import DATE_RE, SERIAL_RE, \
    MIN_SERIAL_LEN, MAX_SERIAL_LEN, \
    MIN_DATE_LEN, MAX_DATE_LEN, MIN_SERIAL_CONF, \
    DATE_FORMATS


def extract_mailing_date_ocr(ocr_results, barcode_date_all_formats):
    """Extract human-readable date from ocr results

    Parameters:
        ocr_results (array): The bounding box, text, and confidence returned by EasyOCR for each detected line

    Returns:
        date_found (string), confidence (int): The date string found from ocrResults, None if no date is found, and the
            confidence of the ocr detection returned by EasyOCR, None if no date is found
    """

    date_found = None
    confidence = None
    raw_text = None
    metrics = {'ocr_date_found': False}

    min_l_dist = 20

    for (bbox, text, prob) in ocr_results:
        if MIN_DATE_LEN <= len(text) <= MAX_DATE_LEN:  # don't check line if too long or too short to be a date
            date_decoded = re.search(DATE_RE, text, re.IGNORECASE)

            if date_decoded is not None:
                ocr_decoded_date = date_decoded[0].replace(' ', '')

                for barcode_date in barcode_date_all_formats:
                    l_dist_computed = distance(ocr_decoded_date, barcode_date)
                    if l_dist_computed < min_l_dist:
                        min_l_dist = l_dist_computed
                        date_found = ocr_decoded_date
                        confidence = prob
                        raw_text = text

    if date_found is not None:
        metrics['ocr_date_found'] = True
        metrics['raw_text'] = raw_text
        metrics['confidence'] = confidence

    return date_found, metrics


def extract_serial_num_ocr(ocr_results):
    """Extract human-readable serial number from ocr results

    Parameters:
        ocr_results (array): The bounding box, text, and confidence returned by EasyOCR for each detected line

    Returns: serial_num_found (string), confidence (int): The most likely serial num string found from ocrResults,
        None if no serial number is found, and the confidence of the ocr detection returned by EasyOCR, None if no
        serial number is found
    """

    serial_num_found = None
    confidence = None
    raw_text = None
    # flag to prefer longer serial numbers
    pref_long = 1
    min_len = MIN_SERIAL_LEN
    for (bbox, text, prob) in ocr_results:
        # check if the label is the special datamatrix type by checking for "date of sale" line
        if distance(text.split(" ")[0].lower(), "date") < 2:
            # prefer short string if special label detected
            pref_long = -1
            min_len = 7
            continue
        if min_len < len(text) < MAX_SERIAL_LEN:
            serial_num = re.search(SERIAL_RE, text, re.IGNORECASE)
            if serial_num is not None and prob > MIN_SERIAL_CONF and min_len < len(serial_num[0]):
                if serial_num_found is None or (pref_long * len(serial_num[0]) > pref_long * len(serial_num_found)):
                    serial_num_found = serial_num[0]
                    confidence = prob
                    raw_text = text

    metrics = {'ocr_sn_found': True if serial_num_found else False,
               'raw_text': raw_text,
               'confidence': confidence,
               'valid_serial_number': serial_num_found,
               'special_data_matrix_label_detected': True if pref_long == -1 else False
               }

    return serial_num_found, metrics


def create_all_formats_of_date(mailing_date):
    formatted_dates = []
    for format_i in DATE_FORMATS:
        formatted = mailing_date.strftime(format_i)
        if re.search('[a-zA-Z]', formatted):
            formatted_dates.append(formatted)
            formatted_dates.append(formatted.upper())
            formatted_dates.append(formatted.lower())
        else:
            formatted_dates.append(mailing_date.strftime(format_i))

    return formatted_dates


def create_10_day_window(mailing_date):
    window_dates = []
    for date_delta in range(0, 11):
        formatted_dates = create_all_formats_of_date(mailing_date + timedelta(days=date_delta))
        window_dates.extend(formatted_dates)

    return window_dates


def is_mailing_date_valid(mailing_date):
    """Check if date is valid. Reformat the date if it is valid, else return an empty string.

    Parameters:
        mailing_date: str
            String representation of the extracted Date

    Returns:
        mailing_date: str
            Reformatted date (%Y-%m-%d) if date is valid, else an empty string
    """

    # Validate year
    if len(mailing_date) == 8:
        try:
            # Validate the month and day
            mailing_date = datetime.strptime(mailing_date, "%Y%m%d")
            return mailing_date

        except ValueError:
            return None

    return None


def extract_mailing_date_barcode(barcode):
    """
    Method to extract the mailing date from the IBI barcode.
    Logic built in to extract dates automatically from an IBI label and an IMI label.
    Reference Docs: APBS Spec from WebAPAT, PES Data dictionary shared by WebAPAT

    Parameters:
        barcode: str
            The IBI barcode as read from the PRLM file

    Returns:
        mailing_date: str
            The string representation of the extracted date.

        is_imi: bool
            Flag to indicate if the date was extracted from an IBI label or IMI label
    """
    is_imi = False
    metrics = {'is_date_valid': False}
    formatted_dates_10_day_window = None

    # Convert base64 barcode to binary representation and
    # regroup to form the bytes representation of the string
    bytes_repr = ["{:08b}".format(x) for x in base64.b64decode(barcode)]

    # Extract the 4 bytes corresponding to the date
    lsb_msb = "".join(bytes_repr[22:26][::-1])

    # Convert binary to decimal
    try:
        mailing_date = str(int(lsb_msb, 2))
    except ValueError:
        mailing_date = ''
    metrics['barcode_date_decimal'] = mailing_date

    # Check if extracted date is valid
    mailing_date = is_mailing_date_valid(mailing_date)
    if mailing_date is not None:
        metrics['is_date_valid'] = True

    else:
        # If date is invalid, then the barcode is an IMI barcode not an IBI barcode.
        # Extract different byte groups for the IMI barcode
        lsb_msb = "".join(bytes_repr[17:21][::-1])

        try:
            mailing_date = str(int(lsb_msb, 2))
        except ValueError:
            mailing_date = ''

        metrics['barcode_date_decimal'] = mailing_date

        mailing_date = is_mailing_date_valid(mailing_date)

        if mailing_date is not None:
            is_imi = True
            metrics['is_date_valid'] = True

    metrics['is_imi'] = is_imi

    if mailing_date is not None:
        formatted_dates_10_day_window = create_10_day_window(mailing_date)
        mailing_date = mailing_date.strftime("%Y-%m-%d")

    return mailing_date, formatted_dates_10_day_window, metrics


def extract_serial_number_barcode(barcode, is_imi):
    """
    Method to extract the human-readable serial number from the IBI barcode.
    Logic built in to extract serial numbers automatically from an IBI label and an IMI label.
    Reference Docs: APBS Spec from WebAPAT, PES Data dictionary shared by WebAPAT

    Parameters:
        barcode: str
            The IBI barcode as read from the PRLM file

        is_imi: bool
            Flag to indicate if the date was extracted from an IBI label or IMI label

    Returns:
        serial_number: str
            Serial Number extracted. Might be missing a few zeroes in the serial number.
    """

    metrics = {}

    # Define decoding schema for IBI and IMI labels
    # Serial Number in IBI = IBI Vendor ID + PSD Model Number + PSD Serial Number
    # Serial Number in IMI = Provider ID + Model ID + PES Serial Number
    decoding_schema = {
        'ibi': {'id_model_num': (6, 10), 'serial_number': (10, 14)},
        'imi': {'id_model_num': (1, 5), 'serial_number': (5, 9)}
    }

    if is_imi:
        label = 'imi'
    else:
        label = 'ibi'

    # Convert base64 barcode to binary representation and
    # regroup to form the bytes representation of the string
    bytes_repr = ["{:08b}".format(x) for x in base64.b64decode(barcode)]

    # Extract ID and Model number - convert binary to ascii
    vendor_id_model_num_bytes = bytes_repr[decoding_schema[label]['id_model_num'][0]:
                                           decoding_schema[label]['id_model_num'][1]]
    vendor_id_model_num_ascii = ''.join([chr(int(byte_x, 2)) for byte_x in vendor_id_model_num_bytes])
    metrics['vendor_id_model_num_ibi_barcode'] = vendor_id_model_num_ascii

    # Extract serial number - convert binary to decimal
    lsb_msb = "".join(bytes_repr[decoding_schema[label]['serial_number'][0]:
                                 decoding_schema[label]['serial_number'][1]][::-1])
    serial_number = str(int(lsb_msb, 2))
    metrics['PSD_PES_serial_number_barcode'] = serial_number

    # Human-readable IBI serial number
    human_readable_sn = vendor_id_model_num_ascii + serial_number

    return human_readable_sn, vendor_id_model_num_ascii, serial_number, metrics


def check_ibi_or_imi(barcode):
    is_imi = None

    # CHeck if IBI
    bytes_repr = ["{:08b}".format(x) for x in base64.b64decode(barcode)]
    lsb_msb = "".join(bytes_repr[22:26][::-1])
    mailing_date = str(int(lsb_msb, 2))
    mailing_date = is_mailing_date_valid(mailing_date)

    if mailing_date:
        is_imi = False
    else:
        # Check if IMI
        lsb_msb = "".join(bytes_repr[17:21][::-1])
        mailing_date = str(int(lsb_msb, 2))
        mailing_date = is_mailing_date_valid(mailing_date)
        if mailing_date:
            is_imi = True

    return is_imi
