import csv
import logging
import os
import sys
import zipfile
from io import TextIOWrapper

from ecips_utils import ecips_config
from ecips_utils.barcodeValidation.check_barcode import is_valid_barcode

# Increasing the csv field size limit to remedy errors on large PRLM files (on EPPS) specifically
csv.field_size_limit(sys.maxsize)


class PRLMFile:
    """
    A class used to represent PRLM files. A filepath is sent and
    the PRLM file is read and processed.  A list of barcodes and
    their corresponding image filepaths can be accessed using the
    get_barcodes() method

    Attributes
    barcode_dict : dict{}
        A dictionary of barcodes with key values defined as the image filepaths
    device_key : str
        The name of the MPE that processed the images
    """

    def __init__(self, filepath):
        """
        Parameters:
              filepath : str
                The filepath to the prlm file
        """
        self.filepath = filepath
        # The barcode dict contains all of the imgs/barcode pairs (even if barcode is missing)
        self.barcode_dict = {}
        # The images to bcr contains only the paths to images that need BCR because they are missing a barcode
        self.images_to_bcr = []
        # The IBI barcode dict contains all of the imgs/ibi barcode pairs (even if barcode is missing)
        self.ibi_barcode_dict = {}
        # The volume dict contains all of the imgs/volume pairs
        self.volume_dict = {}
        # The double scan dict contains all img/is_double_scan bool pairs
        self.double_scan_dict = {}
        # the prlm_filepaths var holds all of the filepaths pertaining to the prlm
        # regardless of bcr status
        self.prlm_filepaths = []

        # PRLM stats variables (updated in log_prlm_stats function)
        self.total_packages = None
        self.total_packages_wout_barcode = None

        # Grab the string that describes the MPE device
        self.device_key = self.get_machine_type(filepath)

        self.process_prlm_file(filepath)

        self.BARCODE_LOC = 10
        self.FILEPATH_LOC = 19

    def get_machine_type(self, prlm):
        for mt in ecips_config.MPE_LIST:
            if mt in prlm:
                return mt
        # NOTE: This shouldn't happen since unsupported machine types are filtered
        # out when looking for PRLM files
        return ''

    def process_apps_prlm(self, prlm_file):
        with zipfile.ZipFile(prlm_file) as zip_file:
            prlm_filename = zip_file.infolist()[0].filename
            with zip_file.open(prlm_filename, 'r') as f:
                reader = csv.reader(TextIOWrapper(f, 'latin-1'))
                # process each row
                for row in reader:
                    img_id = row[0][2:]
                    is_double_scan, impb = self.extract_impb_barcodes(row[9], "apps")
                    self.barcode_dict[img_id] = impb
                    self.double_scan_dict[img_id] = is_double_scan
                    if len(row) > 14:
                        try:
                            self.volume_dict[img_id] = self.calculate_volume(row[14])
                        except ValueError:
                            self.volume_dict[img_id] = self.find_volume(15, row)
                    else:
                        self.volume_dict[img_id] = 0
                    self.ibi_barcode_dict[img_id] = self.extract_ibi_barcode(row[9])

    def process_psm_prlm(self, prlm_file):

        with zipfile.ZipFile(prlm_file) as zip_file:
            prlm_filename = zip_file.infolist()[0].filename
            with zip_file.open(prlm_filename, 'r') as f:
                reader = csv.reader(TextIOWrapper(f, 'latin-1'))
                # process each row
                for row in reader:
                    img_id = row[0]
                    is_double_scan, impb = self.extract_impb_barcodes(row[9], 'apps')
                    self.barcode_dict[img_id] = impb
                    self.double_scan_dict[img_id] = is_double_scan

                    if len(row) > 14:
                        try:
                            self.volume_dict[img_id] = self.calculate_volume(row[14])
                        except ValueError:
                            self.volume_dict[img_id] = self.find_volume(15, row)
                    else:
                        self.volume_dict[img_id] = 0
                    self.ibi_barcode_dict[img_id] = self.extract_ibi_barcode(row[9])

    def process_spss_prlm(self, prlm_file):

        with zipfile.ZipFile(prlm_file) as zip_file:
            prlm_filename = zip_file.infolist()[0].filename
            with zip_file.open(prlm_filename, 'r') as f:
                reader = csv.reader(TextIOWrapper(f, 'latin-1'))
                # process each row
                for row in reader:
                    # Check for bad lines
                    if len(row) < 10:
                        continue
                    img_id = row[0]
                    is_double_scan, impb = self.extract_impb_barcodes(row[9], "spss")
                    self.barcode_dict[img_id] = impb
                    self.double_scan_dict[img_id] = is_double_scan
                    if len(row) > 14:
                        try:
                            self.volume_dict[img_id] = self.calculate_volume(row[14])
                        except ValueError:
                            self.volume_dict[img_id] = self.find_volume(15, row)
                    else:
                        self.volume_dict[img_id] = 0
                    self.ibi_barcode_dict[img_id] = self.extract_ibi_barcode(row[9], is_spss=True)

    def process_apbs_prlm_file(self, prlm_file):

        with zipfile.ZipFile(prlm_file) as zip_file:
            prlm_filename = zip_file.infolist()[0].filename
            with zip_file.open(prlm_filename, 'r') as f:
                reader = csv.reader(TextIOWrapper(f, 'latin-1'))
                # skip PRLM header
                reader.__next__()
                reader.__next__()

                # process each row...
                for row in reader:
                    filepath = self.get_apbs_file_name(row[-1], prlm_file)
                    is_double_scan, impb = self.extract_impb_barcodes(row[10], "apbs")
                    self.barcode_dict[filepath] = impb
                    self.double_scan_dict[filepath] = is_double_scan

                    if len(row) > 14:
                        try:
                            self.volume_dict[filepath] = self.calculate_volume(row[15])
                        except ValueError:
                            self.volume_dict[filepath] = self.find_volume(16, row)
                    else:
                        self.volume_dict[filepath] = 0
                    self.ibi_barcode_dict[filepath] = self.extract_ibi_barcode(row[10])

    def process_prlm_file(self, prlm_file):
        """
        Parameters:
              prlm_file : str
                The filepath to the prlm file
        """
        if self.device_key == 'APBS':
            self.process_apbs_prlm_file(prlm_file)

            for filename in self.barcode_dict:
                if self.barcode_dict[filename] == '':
                    self.images_to_bcr.append(filename)
                self.prlm_filepaths.append(filename)

        elif self.device_key == 'APPS' or self.device_key == 'EPPS':
            self.process_apps_prlm(prlm_file)
            self.gather_apps_images(prlm_file)

        elif self.device_key == 'PSM':
            self.process_psm_prlm(prlm_file)
            self.gather_apps_images(prlm_file)

        elif self.device_key == 'SPSS':
            self.process_spss_prlm(prlm_file)
            self.gather_spss_images(prlm_file)
        elif self.device_key == 'HOPS':
            self.process_apbs_prlm_file(prlm_file)

            for filename in self.barcode_dict:
                if self.barcode_dict[filename] == '':
                    self.images_to_bcr.append(filename)
                self.prlm_filepaths.append(filename)
        else:
            raise Exception("Not a valid device for PRLM file")

        self.log_prlm_stats(prlm_file)

    def log_prlm_stats(self, prlm_file):
        """
        The log_prlm_stats function will print relevent statistics about the PRLM
        file relating to the number of packages in the PRLM file, number of packages without
        a barcode
        Args:
            prlm_file (str): the filepath of the PRLM file
        Returns: None
        """
        # Get the total number of packages
        self.total_packages = len(self.prlm_filepaths)

        # Count the instances in the barcode dict where a barcode was unable to be validated (when dict value is '')
        self.total_packages_wout_barcode = len(self.images_to_bcr)

        # Log the results as debug output
        logging.debug(f"{self.total_packages} packages found in PRLM file {prlm_file}")
        logging.debug(f"{self.total_packages_wout_barcode} packages out of {self.total_packages} total packages "
                      f"in {prlm_file} do not contain valid barcodes and will be sent to BCR pipeline")

    def extract_impb_barcodes(self, bcr, mpe_type):
        impbs = set()
        for bc in bcr.split(' '):
            if mpe_type == 'spss':
                impbs.add(self.parse_spss_bc_field(bc))
            elif mpe_type == 'apps':
                impbs.add(self.parse_apps_bc_field(bc))
            else:
                impbs.add(self.parse_bcr_field(bc))

        if impbs == {''}:
            return False, ''
        else:
            # Only add images with valid barcodes
            valid_bcs = []
            for impb in impbs:
                is_valid = self.validate_barcode(impb)
                if is_valid:
                    valid_bcs.append(impb)
        if len(valid_bcs) > 1:
            return True, valid_bcs[0]
        if len(valid_bcs) > 0:
            return False, valid_bcs[0]
        return False, ''

    def parse_spss_bc_field(self, bc):
        # for bc in bcr.split(' '):
        if len(bc) == 22 or len(bc) == 26:
            return bc
        elif bc[:3] == '420' and len(bc) >= 30:
            if self.check_bc_first_digits(bc[8:]):

                return bc[8:]
            elif self.check_bc_first_digits(bc[12:]):
                return bc[12:]
        else:
            bc, valid = is_valid_barcode(bc)
            if valid:
                return bc
        return ''

    def parse_apps_bc_field(self, bc):
        # for bc in bcr.split(' '):
        # Short circuit on mass mailers
        psm_char = 'ï¿½'
        if '}' in bc:
            return ''
        if 'ñ' in bc:
            idx = bc.find('ñ', 1)
            if idx > 0:
                return bc[idx + 1:]
            else:
                return bc[1:]
        if '?' in bc:
            idx = bc.find('?', 1)
            if idx > 0:
                return bc[idx + 1:].replace("?", "")
            else:
                return bc[1:].replace("?", "")
        if psm_char in bc:
            idx = bc.find(psm_char, 1)
            if idx >= 0:
                bcr = bc[idx + len(psm_char):]
                bcr = bcr.replace(psm_char, "")
                return bcr
            else:
                return ''
        else:
            bc, valid = is_valid_barcode(bc)
            if valid:
                return bc
        return ''

    def parse_bcr_field(self, bc):
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
        # for bc in bcr.split(" "):
        # print (bc)
        # print (len(bc))
        if bc.isnumeric():
            # 22/26-digit barcode
            if len(bc) == 22 or len(bc) == 26:
                return bc
            # 22-digit barcode with routing info
            if len(bc) == 30:
                return bc[8:]
            # possibly 26 digit barcode with routing info
            if len(bc) == 34:
                retval = bc[8:]
                # this could be a 22 digit bc with 4 prelim digts
                if self.check_bc_first_digits(retval):
                    return retval
                else:
                    return retval[4:]
        else:
            bc, valid = is_valid_barcode(bc)
            if valid:
                return bc
        return bc

    def extract_ibi_barcode(self, barcodes, is_spss=False):
        """
        The extract_ibi_barcode function parses the bcr as sent from
        the PRLM file and returns the IBI barcode.

        Parameters:
            barcodes : str
                The barcode as read in the PRLM file
            is_spss: bool
                Flag to process IBI barcodes differently depending on MPE
        Returns:
            ibi : str
                The IBI barcode
        """

        ibi = None
        barcodes = barcodes.split(" ")

        if ']' in barcodes:
            if barcodes.index(']') + 1 < len(barcodes):
                ibi = barcodes[barcodes.index(']') + 1]

                if is_spss:
                    if len(ibi) > 128:
                        ibi = ibi[3:]
                    elif len(ibi) < 128:
                        ibi = None
                else:
                    ibi = ibi.split('#')[-1]

        return ibi

    def find_volume(self, start_index, row):
        volume = 0
        for i in range(start_index, len(row)):
            if len(row[i]) > 0 and row[i][0] == "V":
                volume = self.calculate_volume(row[i])
        return volume

    def calculate_volume(self, volume_col):
        """
            The calculate_volume function parses the volume specs as sent from
            the PRLM file and returns the calculated package volume

            Parameters:
                volume_col : str
                    The volume specs as read in the PRLM file
            Returns:
                volume : int
                    The package volume
        """
        v, l, w, h = volume_col.split(" ")
        volume = int(l) * int(h) * int(w)
        return volume

    def validate_barcode(self, barcode):
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
        _, valid = is_valid_barcode(barcode)

        return valid

    def check_bc_first_digits(self, barcode):
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

    def get_apbs_file_name(self, fname, prlm_file):
        file_path_list = fname.split('/')
        webapat_path = os.path.join(file_path_list[-4], file_path_list[-3],
                                    file_path_list[-2], file_path_list[-1])
        path_abs = os.path.join(prlm_file.split(file_path_list[-4])[0], webapat_path)

        return path_abs

    def gather_apps_images(self, prlm_file):
        # extract the mail id from the file name
        def get_mail_id(fname):
            idx_start = fname.rfind('_') + 1
            idx_end = fname.find('.', idx_start) - 1
            return fname[idx_start:idx_end]

        basedir = os.path.dirname(prlm_file)
        # Walk through all tif files and add any which are not listed in the images
        # dictionary
        for entry in os.listdir(basedir):
            img_dir_path = os.path.join(basedir, entry)
            if os.path.isdir(img_dir_path):
                for img in os.listdir(img_dir_path):
                    if "tif" in img.split('.')[-1]:
                        mail_id = get_mail_id(img)
                        # print ("Mail id : ", mail_id, " : ", img)
                        if mail_id in self.barcode_dict.keys():
                            full_path = os.path.join(img_dir_path, img)
                            if self.barcode_dict[mail_id] == '':
                                if full_path not in self.images_to_bcr:
                                    self.images_to_bcr.append(full_path)
                            if full_path not in self.prlm_filepaths:
                                self.barcode_dict[full_path] = self.barcode_dict[mail_id]
                                self.ibi_barcode_dict[full_path] = self.ibi_barcode_dict[mail_id]
                                self.volume_dict[full_path] = self.volume_dict[mail_id]
                                self.double_scan_dict[full_path] = self.double_scan_dict[mail_id]
                                self.prlm_filepaths.append(full_path)

    def gather_spss_images(self, prlm_file):
        # extract the mail id from the file name
        def get_mail_id(fname):
            return fname.split('_')[2]

        basedir = os.path.dirname(prlm_file)
        # Walk through all tif files and add any which are not listed in the images
        # dictionary
        # images_to_bcr = []
        # new_images = {}  # NOTE: transform to dict format expected downstream
        for entry in os.listdir(os.path.join(basedir, 'PSOC-1')):
            img_dir_path = os.path.join(*[basedir, 'PSOC-1', entry])
            # print ("Checking ", img_dir_path)
            if os.path.isdir(img_dir_path):
                for img in os.listdir(img_dir_path):
                    if "tif" in img.split('.')[-1]:
                        mail_id = get_mail_id(img)
                        # print ("Mail id : ", mail_id, " : ", img)
                        if mail_id in self.barcode_dict.keys():
                            full_path = os.path.join(img_dir_path, img)
                            if self.barcode_dict[mail_id] == '':
                                if full_path not in self.images_to_bcr:
                                    self.images_to_bcr.append(full_path)
                            if full_path not in self.prlm_filepaths:
                                self.barcode_dict[full_path] = self.barcode_dict[mail_id]
                                self.ibi_barcode_dict[full_path] = self.ibi_barcode_dict[mail_id]
                                self.volume_dict[full_path] = self.volume_dict[mail_id]
                                self.double_scan_dict[full_path] = self.double_scan_dict[mail_id]
                                self.prlm_filepaths.append(full_path)

    def gen_cksum(self, barcode, modulus=10):
        """
        The gen_cksum parses the barcode and returns a
        bool that describes if the barcode contains valid digits
        in the first two locations

        Parameters:
            barcode : str
                The barcode as read in the PRLM file
        Returns:
             checksum: int
                checksum value to be returned.  Checksum is -1 if invalid
        """
        try:
            checksum = modulus - (3 * sum(barcode[::2]) + sum(barcode[1::2])) % modulus
            if checksum == 10:
                checksum = 0
        except Exception:
            checksum = -1
        return checksum

    def get_impb_barcodes(self):
        """
        The get_impb_barcodes returns the barcode dictionary

        Returns:
             barcode_dict: dict{}
                The barcode dictionary with filenames as key values
        """
        return self.barcode_dict

    def get_ibi_barcodes(self):
        """
        The get_ibi_barcodes returns the IBI barcode dictionary

        Returns:
             ibi_barcode_dict: dict{}
                The IBI barcode dictionary with filenames as key values
        """
        return self.ibi_barcode_dict

    def get_images_to_bcr(self):
        """
        The get_images_to_bcr returns the barcode dictionary

        Returns:
             images_to_bcr: list
                The list of filepaths to images that need BCR performed
        """
        return self.images_to_bcr

    def get_image_filepaths(self):
        """
        The get_image_filepaths returns a list of all the image filepaths in the file
        Returns:
             image_filepaths: list
                The list of filepaths to images in the PRLM file
        """

        return self.prlm_filepaths

    def get_package_volume(self):
        """
        The get_package_volume returns the volume dictionary

        Returns:
             volume_dict: dict
                img/volume pairs for all images in prlm
        """
        return self.volume_dict

    def get_double_scans(self):
        """
        The get_package_volume returns the volume dictionary

        Returns:
             volume_dict: dict
                img/volume pairs for all images in prlm
        """
        return self.double_scan_dict
