import logging
import numpy as np
from datetime import date

from ecips_utils.fraudDetection.fraud_config import get_stc_db


def is_valid_barcode(barcode, reconstructed_with_OCR=False):
    """
    The is_valid_barcode function parses the bcr field and removes
    invalid components of the barcodes then checks if the result is
    valid

    Parameters:
        barcode : str
            The barcode
    Returns:
        bcr : str
            The barcode reformatted
        valid : bool
            bool that describes if the barcode is valid
    """
    valid = False

    logging.debug(f"The following barcode being tested for validity: {barcode}")

    # removes preceeding 8 digit non human readable string
    bcr, is_impb, is_s10 = parse_bcr_field(barcode)

    if is_impb:
        if reconstructed_with_OCR:
            if len(bcr) == 23 or len(bcr) == 27:
                for i in range(len(bcr)):
                    bcr_clean = bcr[0: i:] + bcr[i + 1::]
                    valid = validate_impb_barcode(bcr_clean)
                    if valid:
                        bcr = bcr_clean
                        break
            else:
                valid = validate_impb_barcode(bcr)
        else:
            # The case where it was decoded with pyzbar so we do not need to apply certain checks
            # If we did apply those checks we may weed out fraudulent barcodes accidentally
            valid = validate_impb_barcode(bcr, decoded=True)
    elif is_s10:
        valid = validate_s10_barcode(bcr)

    # If the barcode is not valid, return empty string for barcode
    if not valid:
        logging.debug(f"The following barcode does not meet checksum requirements: {bcr}")
        bcr = ''
    else:
        logging.debug(f"The following barcode does meet checksum requirements: {bcr}")

    return bcr, valid


def parse_bcr_field(bcr):
    """
    The parse_bcr_function parses the bcr as sent from
    the PRLM file and returns a reformatted result.  If
    the barcode contains the 8-digit preceding digits
    they are removed.

    Parameters:
        bcr : str
            The barcode as read in the PRLM file
    Returns:
        bc : str
            The barcode reformatted
    """
    is_impb = False
    is_s10 = False

    if bcr.isnumeric():
        # impb barcodes should contain ONLY numbers, no characters
        is_impb = True
        # 22/26-digit barcode
        if len(bcr) == 22 or len(bcr) == 26:
            return bcr, is_impb, is_s10
        # 22-digit barcode with routing info
        if len(bcr) == 30:
            return bcr[8:], is_impb, is_s10
        # possibly 26 digit barcode with routing info
        if len(bcr) == 34:
            retval = bcr[8:]
            # this could be a 22 digit bc with 4 prelim digits
            if check_bc_first_digits(retval):
                return retval, is_impb, is_s10
            else:
                return retval[4:], is_impb, is_s10
    elif bcr.isalnum() and not bcr.isalpha() and not bcr.isnumeric():
        # S10 barcodes should contain both alpha and numeric characters
        is_s10 = True

    return bcr, is_impb, is_s10


def validate_impb_barcode(barcode, decoded=False):
    """
    The validate_barcode parses the barcode and returns a
    bool that describes if the barcode is valid or not

    Parameters:
        barcode : str
            The barcode as read in the PRLM file
    Returns:
         bool
            Boolean flag that describes if the barcode is valid
    """
    # length check
    if len(barcode) != 22 and len(barcode) != 26:
        return False
    else:
        valid_length = True

    # does it start with valid digits
    if not check_bc_first_digits(barcode):
        return False
    else:
        valid_first_dig = True

    # check if it has a valid checksum
    try:
        valid_checksum = gen_impb_cksum(barcode)
    except ValueError:
        # A value error can be returned when invalid chars are sent to
        # the checksum script. Earlier checks should ensure that only
        # numbers are sent but certain special characters (for ex: exponents) are considered
        # digits but will not convert to int()
        valid_checksum = False

    # `valid` flag is set to true with a valid length and first digit and checksum determinations
    # if any of these values are not true then the barcode is not valid
    valid = valid_length and valid_first_dig and valid_checksum

    # Check the rules if reconstructed with OCR and update `valid` flag
    if not decoded:
        # If this was an OCR reconstruction, apply additional rules
        valid = valid and execute_impb_validation_rules(barcode)

    return valid


def validate_s10_barcode(barcode):
    """
    The validate_s10_barcode parses the barcode and returns a
    bool that describes if the s10 barcode is valid or not

    Parameters:
        barcode : str
            The barcode as read in the PRLM file
    Returns:
         bool
            Boolean flag that describes if the barcode is valid
    """
    # length check
    if len(barcode) != 13:
        return False
    else:
        valid_length = True

    # does it start with valid digits
    if not check_s10_chars(barcode):
        return False
    else:
        valid_chars = True

    # check if it has a valid checksum
    barcode_digits = barcode[2:-2]

    try:
        valid_checksum = gen_s10_cksum(barcode_digits)
    except ValueError:
        # A value error can be returned when invalid chars are sent to
        # the checksum script. Earlier checks should ensure that only
        # numbers are sent but certain special characters (for ex: exponents) are considered
        # digits but will not convert to int() properly
        valid_checksum = False

    # returns true with a valid length and first digit and checksum determinations
    # if any of these values are not true than the barcode is not valid
    return valid_length and valid_chars and valid_checksum


def check_s10_chars(barcode):
    """
    The check s10 chars function verifies that the first and last two characters are letters
    and the middle values are digits

    Parameters:
        barcode : str
            The barcode returned from BCR
    Returns:
         bool
            Boolean flag that describes if the barcode has valid character distributions
    """
    first_2chars = barcode[:2]
    last_2chars = barcode[-2:]
    middle_digits = barcode[2:-2]

    return first_2chars.isalpha() and last_2chars.isalpha() and middle_digits.isdigit()


def check_bc_first_digits(barcode):
    """
    The check_bc_first_digits parses the barcode and returns a
    bool that describes if the barcode contains valid digits
    in the first two locations

    Parameters:
        barcode : str
            The barcode as read in the PRLM file
    Returns:
         bool
            Boolean flag that describes if the barcode has a valid starting
            byte
    """
    first_two = barcode[:2]
    valid_start = ["91", "92", "93", "94", "95"]
    return first_two in valid_start


def gen_impb_cksum(barcode, modulus=10):
    """
    The gen_impb_cksum parses the barcode and returns a
    bool that describes if the barcode contains valid digits
    in the first two locations

    Parameters:
        barcode : list(int)
            A list of all of the numeric values in barcode
        modulus : int
            the modulus given by USPS s10 spec document
    Returns:
         checksum: int
            checksum value to be returned.  Checksum is -1 if invalid
    """
    barcode_digit_list = [int(i) for i in barcode]

    dig_to_compute = barcode_digit_list[:-1]
    check_digit_barcode = barcode_digit_list[-1]

    try:
        checksum = modulus - (3 * sum(dig_to_compute[::2]) + sum(dig_to_compute[1::2])) % modulus
        if checksum == 10:
            checksum = 0
    except IndexError:
        checksum = -1

    return check_digit_barcode == checksum


def execute_impb_validation_rules(barcode):
    """
    execute_impb_validation_rules method checks for six additional rules defined to validate the IMPB barcode.
    Parameters:
        barcode: str
            IMPB barcode

    Returns:
        valid: bool
            This denotes if the barcode is valid or not based on the rules
    """

    # Barcodes starting with "91" should have a "14" for chars 3 and 4. No 3-digit STC Code is present.
    if barcode.startswith('91'):
        valid = barcode[2:4] == '14'

    # For IMPBs starting with "92", "93", "94" or "95", check if STC code is present in the list of valid STC codes
    else:
        stc_db = get_stc_db()  # Load stc_db
        stc = barcode[2:5]

        if stc_db != {}:
            valid = stc in stc_db
        else:
            valid = True  # just initializing

        if barcode.startswith('92'):  # For IMPBs starting with a "92", the 6th character should be "9"
            valid = valid and barcode[5] == '9'

        elif barcode.startswith('93'):  # For IMPBs starting with "93", the 6th character cannot be a "9"
            valid = valid and barcode[5] != '9'

        elif barcode.startswith('94'):  # For IMPBs starting with "94", the 6th & 7th char should be a valid source ID
            valid = valid and int(barcode[5:7]) <= 37

        else:  # If IMPB starts with 95, check the 6th character and Julian date
            valid_95 = False
            if int(barcode[5]) < 5:  # 6th character should be a valid device ID < 5
                # Characters 13-16 are the Julian Date, 13th char is the year and the rest is days passed from Jan 1
                jd_current_year = date.today().year % 10
                if jd_current_year - 1 <= int(barcode[12]) <= jd_current_year and int(barcode[13:16]) <= 366:
                    valid_95 = True

            valid = valid and valid_95

    return valid


def gen_s10_cksum(barcode, modulus=11):
    """
    The gen_s10_cksum returns the checksum value according to s10 spec documents

    Parameters:
        barcode : list(int)
            A list of all of the numeric values in barcode
        modulus : int
            the modulus given by USPS s10 spec document
    Returns:
         checksum: int
            checksum value to be returned.  Checksum is -1 if invalid
    """
    barcode_digit_list = [int(i) for i in barcode]

    dig_to_compute = barcode_digit_list[:-1]
    check_digit_barcode = barcode_digit_list[-1]

    # These weight factors are given in S10 spec document
    weight_factor = np.array([8, 6, 4, 2, 3, 5, 9, 7])

    # converting to np array for arithmetic processes
    barcode = np.array(dig_to_compute)

    # multiply the piecewise and compute the sum of the weighted values
    weighted_vals = weight_factor * barcode
    sum_weighted_vals = weighted_vals.sum()

    # divide sum by modulus and subtract remainder result from modulus to get the check digit
    check_digit_calc = modulus - (sum_weighted_vals % modulus)

    # if the check digit is 10 or 11, then adjust according to S10 UPU standard document
    if check_digit_calc == 10:
        check_digit_calc = 0
    elif check_digit_calc == 11:
        check_digit_calc = 5

    return check_digit_calc == check_digit_barcode
