import glob
import logging
import json
import os
import time
from datetime import datetime

import cv2
import numpy as np
import orjson
import redis
from Levenshtein import distance
from PIL import Image, UnidentifiedImageError
from tritonclient.utils import InferenceServerException

from ecips_tasks.tasks_triton import (
    extract_stamp_metrics,
    extract_shipping_label_metrics,
    extract_hazmat_yolo_metrics,
    extract_OG_hazmat_metrics,
    extract_ocr_result,
    extract_descriptors,
    extract_bcr_metrics,
    run_ensemble_grpc_filename
)
from ecips_utils import (ecips_config, ecips_path, ecips_logging)
from ecips_utils.anomalyDetection.anomaly_config import ANOMALY_TYPES
from ecips_utils.anomalyDetection.anomaly_config import HAZMAT_SYMBOL_STC_ANOMALY, \
    HAZMAT_LETTER_INDICATOR_STC_ANOMALY, HIGH_CONF_HAZMAT_YOLO_SCORE_THRES, GROUND_ADVANTAGE_BANNER_STC_ANOMALY, \
    NON_GROUND_ADVANTAGE_INDICATOR_STC_ANOMALY, GROUND_ADVANTAGE_INDICATOR_STC_ANOMALY, \
    GROUND_ADVANTAGE_PERMIT_IMPRINT_INDICIA_STC_ANOMALY
from ecips_utils.anomalyDetection.anomaly_detection import AnomalyDetectionClass
from ecips_utils.anomalyDetection.anomaly_logic import is_anomaly_01, is_anomaly_02, is_anomaly_03, is_anomaly_04, \
    is_anomaly_05, is_anomaly_06
from ecips_utils.barcodeValidation import check_barcode
from ecips_utils.fraudDetection.fraud_config import DETECT_IBI_DATE_MISMATCH, DETECT_IBI_SN_MISMATCH, \
    DETECT_INVALID_IBI_SN, \
    MAX_LEVENSHTEIN_DIST_IBI_DATE, \
    MAX_LEVENSHTEIN_DIST_IBI_DATE_LEVEL_1, \
    MAX_LEVENSHTEIN_DIST_IBI_DATE_LEVEL_2, \
    CONF_THRESHOLD_LEVEL_1, \
    CONF_THRESHOLD_LEVEL_2, \
    MAX_LEVENSHTEIN_DIST_IBI_SN, \
    MAX_LEVENSHTEIN_DIST_IBI_SN_SPECIAL_DM, \
    MAX_DIST_IMPB, \
    DATE_FORMATS
from ecips_utils.fraudDetection.fraud_config import DETECT_SERVICETYPE_MISMATCH, DETECT_MAILCLASS_LETTERCODE_MISMATCH, \
    DETECT_IMPB_HR_MISMATCH
from ecips_utils.fraudDetection.fraud_config import get_stc_db, FRAUD_TYPES
from ecips_utils.fraudDetection.fraud_detection import FraudDetectionClass
from ecips_utils.fraudDetection.ibi import (
    extract_mailing_date_barcode,
    extract_mailing_date_ocr,
    extract_serial_number_barcode,
    extract_serial_num_ocr,
    check_ibi_or_imi
)
from ecips_utils.fraudDetection.mailclass_markings import (
    extract_mail_class_banner_ocr,
)
from ecips_utils.fraudDetection.permit_imprint import is_fraud_permit_imprint

IP = ecips_config.ECIPS_DEVICE_MAPPING["ip"]

# Globals
DEL_ARRAY = np.array([0.08838835] * 128)
R = redis.Redis(host=ecips_config.CELERY_BACKEND.split(":")[1].replace("//", ""))


class PackageObject:

    def __init__(self, package_root=None, Image=None, single_view=False):
        """  Can pass either the package_root or a single loaded package image
        to instantiate the Package Object

        Args:
            package_root (str): The path to the root package, excluding any specific
            image viewpoints. for example: '/images/APPS-020/2022-10-01/01-248/20/20221001_205848_01_2_294446' and NOT
            /images/APPS-020/2022-10-01/01-248/20/20221001_205848_01_2_294446P.tif

            Image (ImageObject): The Image object for one of the package viewpoints. See ImageObject Class below.
        """
        if package_root:
            all_pkg_img_paths = glob.glob(package_root + "*.tif")
            self.ImageList = ImageObjectList(all_pkg_img_paths)
        elif Image:
            if single_view:
                all_pkg_img_paths = [Image.img_filepath]
            elif Image.package_view is not None:
                all_pkg_img_paths = glob.glob(Image.filename_root[:-1] + "*.tif*")
            else:
                all_pkg_img_paths = [Image.img_filepath]

            # Remove the loaded image path from the list and continue (dont want to load 2x)
            all_pkg_img_paths.remove(Image.img_filepath)
            self.ImageList = ImageObjectList(all_pkg_img_paths, Image)
        else:
            raise ValueError("Instantiate the Package object with either the root package ID"
                             "or with a single loaded Package Image of the ImageObject Class")

    def get_available_views(self):
        return self.ImageList.available_views

    def get_reconstructed_barcodes(self, get_first=True):
        """
        The get_reconstructed_barcodes function will return the first valid IMPB barcode found on the
        package. It considers all image views of a package.

        Args:
            get_first (bool): Boolean flag to return only the first successfully reconstructed barcode.
            If set to False, all of the successfully reconstructed barcodes are returned.
        Returns:
            barcode (ReconstructedBarcodeClass): An object of the reconstructed barcode class. This object
            contains a valid IMPB barcode according to the rules contained in
            /ecips_utils/barcodeValidation/check_barcode.py

        """
        reconstructed_barcodes = []

        for image in self.ImageList.imageObjects:
            # Call for BCR on the barcode
            # TODO: only run shipping label ocr on IMPB barcode
            # Bool value to describe if an IMPB barcode was even detected
            barcode_detected = False if image.barcode_metrics["detected_barcode"] == [-1] else True
            if not image.bcr_metrics and barcode_detected:
                # If the bcr metrics have not been collected, AND we have detected an IMPB with yolo, then perform OCR
                image.get_triton_response(model_name='shipping_label_ocr')
                image.extract_from_response(model_name='shipping_label_ocr')

            barcodes = ReconstructedBarcodesClass(image).reconstructed_barcodes

            for barcode in barcodes:
                if barcode.send_bcr_result:
                    if get_first:
                        return [barcode]
                    else:
                        reconstructed_barcodes.append(barcode)

        return reconstructed_barcodes

    def get_hazmat_status(self, high_conf_threshold=False):
        contains_hazmat = False

        for image in self.ImageList.imageObjects:
            hazmat_count = image.hazmat_metrics["num_hazmat_labels"]

            if hazmat_count > 0:
                if not high_conf_threshold:
                    # If we dont care to filter by the higher confidence threshold
                    contains_hazmat = True
                    break
                else:
                    # We only want to filter by very confident thresholds to reduce any FPs
                    hazmat_conf = image.hazmat_metrics["hazmat_scores"]
                    hazmat_class = image.hazmat_metrics["hazmat_classes"]
                    for conf, hazmat_class in zip(hazmat_conf, hazmat_class):
                        class_id_key = str(int(hazmat_class))
                        class_id_conf = HIGH_CONF_HAZMAT_YOLO_SCORE_THRES[class_id_key]
                        if class_id_conf != "" and conf > float(class_id_conf):
                            contains_hazmat = True
                            break

        return contains_hazmat


class ImageObjectList:
    def __init__(self, img_filepaths, loaded_img=None):
        self.imageObjects = self.load_images(img_filepaths, loaded_img)

        self.available_views = ''
        if len(self.imageObjects) > 1:
            # Only update the available views if more than one view is present
            for image in self.imageObjects:
                self.available_views += image.package_view

    def load_images(self, img_filepaths, loaded_img=None):
        if loaded_img:
            # If we already have a loaded image, we dont need to load twice and lose time recomputing info
            imageObjects = [loaded_img]
        else:
            imageObjects = []

        for filepath in img_filepaths:
            image = ImageObject(filepath, load_from_json=True)

            if not image.json_written:
                # If the json has not yet been written to the disk, generate it now
                self.generate_ecips_ensemble_results(image)

            imageObjects.append(image)

        return imageObjects

    @staticmethod
    def generate_ecips_ensemble_results(image,
                                        write_tofile=True,
                                        algorithm=ecips_config.ECIPS_REVERSE_IMAGE_ALGORITHM):
        image.check_img_valid()

        if image.is_valid_img():
            # Call the triton inference server
            try:
                image.get_triton_response()
            except Exception as e:
                raise Exception(f"Error occurred during call to Triton Inference Server: {e}")
            # Extract the ECIP's attributes from the response
            image.extract_from_response()
            # Extract the feature descriptors for the image

            # Generate the json file with all results
            results_dict, results_json = image.generate_results_json()

            # Write the json file to the disk
            if write_tofile:
                image.write_to_json(results_dict)

                logging.debug(f"Results for {image.img_filepath}: {results_dict}. Writing complete.")


class ImageObject:

    def __init__(self, img_filepath, load_from_json=False):
        self.img_filepath = img_filepath
        self.img = None
        self.triton_response = None
        self.valid_image = None
        self.json_filepath = os.path.splitext(self.img_filepath)[0] + ".json"
        self.json_written = False
        self.timestamp_json_written = None

        self.barcode_metrics = None
        self.package_metrics = None
        self.pvi_metrics = None
        self.stamp_metrics = None
        self.hazmat_metrics = None

        # Package Label Initializations:
        self.ibi_barcode = None
        self.mail_class = None
        self.permit_imprint = None
        self.impb_barcode_label = None

        self.descriptors = None
        self.ocr_results = None
        self.ibi_barcode_results = None

        self.bcr_metrics = None
        self.raw_yolo_results = None
        self.date_processed = None
        self.ibi_barcode_results = None
        self.impb_barcode_results = None
        self.package_volume = 0
        self.package_required_bcr = False
        self.contains_hazmat = None
        self.impb_decoded = None
        self.impb_reconstructed = None
        self.impb_barcode_label = None
        self.mail_class_banner = None
        self.mail_class_letter = None

        self.fraud_attributes = self.initialize_fraud_attributes()
        self.fraud_results = None
        self.is_fraudulent = False
        self.anomaly_attributes = self.initialize_anomaly_attributes()
        self.anomaly_results = None
        self.is_anomalous = False

        # The URL path to ecips_serving
        self.grpc_url = 'ecips_serving:8001'

        if load_from_json:
            self.load_results_from_json()

        self.filename_root, filename_ext = os.path.splitext(self.img_filepath)

        # If the last character of the root path is an alpha character, then there are multiple
        # images of the package from different views.  In this instance, we want to check every image
        # for a valid barcode.  When a valid barcode is found we send it via the webAPAT message
        if self.filename_root[-1].isalpha():
            self.package_view = self.filename_root[-1]
        else:
            self.package_view = None

    def update_grpc_url(self, new_url):
        self.grpc_url = new_url

    def add_ibi_label(self, ibi):
        self.ibi_barcode_results = ibi

    def add_volume(self, volume):
        self.package_volume = volume

    def add_impb_label(self, impb_decoded=None, impb_reconstructed=None):
        if impb_decoded and self.impb_decoded is None:
            self.package_required_bcr = False
            # Remove the preceeding digits (420xxx) if they are present
            impb_decoded, _, _ = check_barcode.parse_bcr_field(impb_decoded)
            self.impb_decoded = BarcodeClass(impb_decoded, self.barcode_metrics)
            self.impb_barcode_results = self.impb_decoded
        elif impb_reconstructed and self.impb_reconstructed is None:
            self.package_required_bcr = True
            self.impb_reconstructed = ReconstructedBarcodeClass(self.bcr_metrics[0], self.barcode_metrics)
            self.impb_barcode_results = self.impb_reconstructed.accepted_barcode

    def load_img(self):
        # TODO: Address the TIFF Image file Error:
        # self.img = 255 * np.array(Image.open(self.img_filepath)).astype(np.uint8)
        # TypeError: int() argument must be a string, a bytes-like object or a number, not 'TiffImageFile'
        self.img = 255 * np.array(Image.open(self.img_filepath)).astype(np.uint8)

    def is_valid_img(self):
        return self.valid_image

    def check_img_valid(self):
        try:
            self.load_img()
        except UnidentifiedImageError:
            self.valid_image = False
            logging.error(
                f"Encountered a potentially corrupt image for {self.img_filepath}; no json will be created. "
                f"Ending processing to compute features from {self.img_filepath}"
            )
            ecips_logging.inc_redis_counter("corrupt_image_count")
            ecips_config.ECIPS_CORRUPT_IMAGE_COUNT += 1
        except OSError:
            self.valid_image = False
            logging.error(
                f"Encountered a potentially corrupt image for {self.img_filepath}; no json will be created. "
                f"Ending processing to compute features from {self.img_filepath}"
            )
            ecips_logging.inc_redis_counter("corrupt_image_count")
            ecips_config.ECIPS_CORRUPT_IMAGE_COUNT += 1

        if self.img is None:
            self.valid_image = False
            logging.error(
                f"Encountered a potentially corrupt image for {self.img_filepath}; no json will be created. "
                f"Ending processing to compute features from {self.img_filepath}"
            )
            ecips_logging.inc_redis_counter("corrupt_image_count")
            ecips_config.ECIPS_CORRUPT_IMAGE_COUNT += 1

        else:
            self.valid_image = True

    def get_triton_response(self, model_name='ensemble_model_ecip'):
        triton_calls = 0
        exception_list = []

        while triton_calls < ecips_config.ECIPS_INFERENCE_SERVER_MAX_RETRIES:
            try:
                self.generate_triton_response(model_name)
                # If the triton server returned a response, break
                return
            except Exception as e:
                exception_list.append(e)
                triton_calls += 1

        raise TimeoutError(f"Max Tries ({ecips_config.ECIPS_INFERENCE_SERVER_MAX_RETRIES}) "
                           f"to the inference server exceeded on file {self.img_filepath}. \n"
                           f"The following errors occurred: {exception_list}")

    def generate_triton_response(self, model_name='ensemble_model_ecip'):

        if model_name == 'ensemble_model_ecip':
            triton_args = self.img_filepath
        elif model_name == 'shipping_label_ocr':
            yolo_scores = np.array(self.raw_yolo_results["yolo_scores"], dtype='float32').reshape((1, 100, 1, 1))
            yolo_boxes = np.array(self.raw_yolo_results["yolo_boxes"], dtype='float32').reshape((1, 100, 4, 2))
            yolo_classes = np.array(self.raw_yolo_results["yolo_classes"], dtype='float32').reshape((1, 100, 1, 1))
            triton_args = [self.img_filepath, yolo_scores, yolo_boxes, yolo_classes]

        self.date_processed = datetime.utcnow()

        try:
            self.triton_response = run_ensemble_grpc_filename(triton_args,
                                                              model_name=model_name,
                                                              url=self.grpc_url)
        except AssertionError as e_msg:
            self.valid_image = False
            ecips_logging.inc_redis_counter("small_image_count")
            logging.error(f"Encountered an image too small to be a package. File {self.img_filepath}"
                          f"raises an Assertion Error, due to small image dimensions. {e_msg}")
        except InferenceServerException as e:
            logging.warning(f"Triton Inference Server encountered an exception {e.message()}")
            raise Exception("Triton Inference Server Exception", e.message())

        logging.debug(f"Ending call to Triton Inference server for {self.img_filepath} on {self.date_processed}")

    # put in ecips_tasks.tasks_triton
    def extract_from_response(self, model_name='ensemble_model_ecip'):
        if model_name == 'ensemble_model_ecip':
            self.pvi_metrics, self.package_metrics, \
                self.barcode_metrics, self.raw_yolo_results = extract_shipping_label_metrics(self.triton_response)
            self.descriptors = extract_descriptors(self.triton_response)
            self.hazmat_metrics = extract_hazmat_yolo_metrics(self.triton_response)
            self.stamp_metrics = extract_stamp_metrics(self.triton_response)

            # If the flag to use the yolo model for hazmat is False, then use the old Hazmat model
            logging.debug(f"ECIP-Application is using the yolo model (T/F): "
                          f"{ecips_config.ECIPS_INFERENCE_SERVER_USE_HAZMAT_YOLO}")
            logging.debug(
                f"ECIP-Application is using the retinanet model (T/F): "
                f"{not ecips_config.ECIPS_INFERENCE_SERVER_USE_HAZMAT_YOLO}")
            if not ecips_config.ECIPS_INFERENCE_SERVER_USE_HAZMAT_YOLO:
                self.hazmat_metrics = None
                self.hazmat_metrics = extract_OG_hazmat_metrics(self.triton_response)
        else:
            self.ocr_results = extract_ocr_result(self.triton_response)
            self.bcr_metrics = extract_bcr_metrics(self.triton_response)

    def generate_results_json(self):

        # ecips_path.calculate_ecips_path calculates image characteristics based on file path
        logging.debug(f"Compiling results for {self.img_filepath}")
        results_dict = ecips_path.calculate_ecips_path(self.img_filepath)
        results_dict.update(
            {
                "img_filepath": self.img_filepath,
                "key_pointsBytes": "df.xpos.values, df.ypos.values",
                "descriptorList": self.descriptors.astype(np.float32).tobytes().hex(),
                "dateProcessed": self.date_processed.isoformat(),
            }
        )

        for key in self.barcode_metrics.keys():
            results_dict.update({key: self.barcode_metrics[key]})
        for key in self.stamp_metrics.keys():
            results_dict.update({key: self.stamp_metrics[key]})
        for key in self.hazmat_metrics.keys():
            results_dict.update({key: self.hazmat_metrics[key]})
        for key in self.package_metrics.keys():
            results_dict.update({key: self.package_metrics[key]})
        # PVI Model accuracy is not verified
        for key in self.pvi_metrics.keys():
            results_dict.update({key: self.pvi_metrics[key]})
        for key in self.raw_yolo_results.keys():
            results_dict.update({key: self.raw_yolo_results[key]})

        results_json = orjson.loads(orjson.dumps(results_dict, option=orjson.OPT_SERIALIZE_NUMPY))

        return results_dict, results_json

    def write_to_json(self, results_dict):
        filepath = self.json_filepath

        with open(filepath, "wb") as fp:
            fp.write(orjson.dumps(results_dict, option=orjson.OPT_SERIALIZE_NUMPY))

        R.lpush("dailyJson_filePath", filepath)
        self.json_written = True
        logging.info(f"{self.img_filepath} successfully written to {filepath}")

    def load_results_from_json(self):
        results_json = self.read_from_json()

        if self.json_written:
            try:
                self.barcode_metrics = {key: results_json[key] for key in ecips_config.BARCODE_METRIC_KEYS}
                self.package_metrics = {key: results_json[key] for key in ecips_config.PACKAGE_METRIC_KEYS}
                self.pvi_metrics = {key: results_json[key] for key in ecips_config.PVI_METRIC_KEYS}
                self.stamp_metrics = {key: results_json[key] for key in ecips_config.STAMP_METRIC_KEYS}
                self.hazmat_metrics = {key: results_json[key] for key in ecips_config.HAZMAT_METRIC_KEYS}
                self.raw_yolo_results = {key: results_json[key] for key in ecips_config.YOLO_METRIC_KEYS}
            except KeyError:
                self.json_written = False
                logging.info(f"Json metrics not updated for {self.img_filepath} because the json file contains results "
                             f"from a previous version of ECIP Application")

        else:
            logging.info(f"Json metrics not updated for {self.img_filepath} because the json file is not written")

    def read_from_json(self):
        filepath = self.json_filepath

        try:
            self.timestamp_json_written = time.ctime(os.path.getmtime(filepath))
            with open(filepath, "rb") as f:
                results_json = orjson.loads(f.read())
                self.json_written = True
                return results_json

        except FileNotFoundError:
            logging.info(f"The json filepath {filepath}, is not written to the disk.  Likely because the image"
                         f"file was corrupt: {self.img_filepath}")
            self.json_written = False

    def initialize_fraud_attributes(self):
        fraud_attributes = {}
        # Initialize fraud type presence dictionary
        fraud_attributes.update({f"{fraud_type}_present": False for fraud_type in FRAUD_TYPES})
        # Initialize hazmat type presence dictionary
        fraud_attributes.update({f"{fraud_type}_conf": 0.0 for fraud_type in FRAUD_TYPES})

        return fraud_attributes

    def initialize_anomaly_attributes(self):
        anomaly_attributes = {}
        # Initialize anomaly type presence dictionary
        anomaly_attributes.update({f"anomaly_{anomaly_type.anomaly_id}_present": False
                                   for anomaly_type in ANOMALY_TYPES})
        # Initialize hazmat type presence dictionary
        anomaly_attributes.update({f"anomaly_{anomaly_type.anomaly_id}_conf": 0.0
                                   for anomaly_type in ANOMALY_TYPES})

        return anomaly_attributes

    def get_hazmat_status(self, high_conf_threshold=False):
        # If self.contains hazmat has not yet been defined, then check if the package has hazmat
        if self.contains_hazmat is None:

            self.contains_hazmat = False
            hazmat_count = self.hazmat_metrics["num_hazmat_labels"]

            if hazmat_count > 0:
                if not high_conf_threshold:
                    # If we dont care to filter by the higher confidence threshold
                    self.contains_hazmat = True
                else:
                    # We only want to filter by very confident thresholds to reduce any FPs
                    hazmat_conf = self.hazmat_metrics["hazmat_scores"]
                    hazmat_class = self.hazmat_metrics["hazmat_classes"]
                    for conf, hazmat_class in zip(hazmat_conf, hazmat_class):
                        class_id_key = str(int(hazmat_class))
                        class_id_conf = HIGH_CONF_HAZMAT_YOLO_SCORE_THRES[class_id_key]
                        if class_id_conf != "" and conf > float(class_id_conf):
                            self.contains_hazmat = True
                            break

        return self.contains_hazmat

    def scan_package_for_fraud(self):
        if not self.impb_barcode_results:
            # If there is no valid IMPB, initialize the barecode as '' (Invalid)
            self.impb_barcode_results = BarcodeClass('', self.barcode_metrics)
        # First, we have to add all of the labels to the Image object if they
        # do not already exist
        if not self.ibi_barcode:
            self.ibi_barcode = IBIClass(self.ibi_barcode_results,
                                        self.ocr_results['IBI_date'],
                                        self.raw_yolo_results)
        if not self.mail_class:
            self.mail_class = MailMarkingsClass(self.impb_barcode_results,
                                                self.ocr_results['mail_class_letter'],
                                                self.ocr_results['mail_class_banner'],
                                                self.raw_yolo_results,
                                                self.get_hazmat_status(high_conf_threshold=True))
        if not self.permit_imprint:
            self.permit_imprint = PermitImprintClass(self.impb_barcode_results,
                                                     self.ocr_results['permit_imprint'],
                                                     self.raw_yolo_results)
        if not self.impb_barcode_label:
            if self.impb_reconstructed is None:
                # Update the reconstruction object if it doesnt alreayd exist
                self.impb_reconstructed = ReconstructedBarcodeClass(self.bcr_metrics[0] if self.bcr_metrics
                                                                    else self.bcr_metrics, self.barcode_metrics)

            self.impb_barcode_label = IMPBBarcodeClass(self.impb_decoded,
                                                       self.impb_reconstructed,
                                                       self.raw_yolo_results)

        self.ibi_barcode.scan_label_for_fraud()
        self.mail_class.scan_label_for_fraud()
        self.permit_imprint.scan_label_for_fraud()
        self.impb_barcode_label.scan_label_for_fraud()

        # Update the fraud attributes
        self.update_fraud_attributes()
        self.update_label_attributes()

    def update_fraud_attributes(self):
        self.fraud_results = FraudDetectionClass(self.ibi_barcode,
                                                 self.mail_class,
                                                 self.permit_imprint,
                                                 self.impb_barcode_label)

        if self.fraud_results.fraud_found():
            self.is_fraudulent = True
            fraud_results = self.fraud_results.get_fraud_types_dict()
            for fraud_result in fraud_results:
                fraud_type = fraud_result["fraud_type"]
                self.fraud_attributes[f"{fraud_type}_present"] = True
                self.fraud_attributes[f"{fraud_type}_conf"] = fraud_result["confidence"]

    def update_label_attributes(self):
        if self.mail_class_letter is None:
            self.mail_class_letter = self.mail_class.mail_class_from_img
        if self.mail_class_banner is None:
            self.mail_class_banner = self.mail_class.mail_class_from_banner

    def scan_package_for_anomaly(self):
        if not self.impb_barcode_results:
            # If there is no valid IMPB, initialize the barecode as '' (Invalid)
            self.impb_barcode_results = BarcodeClass('', self.barcode_metrics)

        if not self.mail_class:
            self.mail_class = MailMarkingsClass(self.impb_barcode_results,
                                                self.ocr_results['mail_class_letter'],
                                                self.ocr_results['mail_class_banner'],
                                                self.raw_yolo_results,
                                                self.get_hazmat_status(high_conf_threshold=True))
        if not self.permit_imprint:
            self.permit_imprint = PermitImprintClass(self.impb_barcode_results,
                                                     self.ocr_results['permit_imprint'],
                                                     self.raw_yolo_results)

        # Scan the attributes of the package for anomalies
        self.mail_class.scan_label_for_anomalies()
        self.permit_imprint.scan_label_for_anomalies()

        # Update the anomaly attributes
        self.update_anomaly_attributes()
        self.update_label_attributes()

    def update_anomaly_attributes(self):
        self.anomaly_results = AnomalyDetectionClass(self.mail_class,
                                                     self.permit_imprint)

        if self.anomaly_results.anomaly_found():
            self.is_anomalous = True
            anomaly_results = self.anomaly_results.get_anomaly_types_dict()
            for anomaly_result in anomaly_results:
                anomaly_type = anomaly_result["anomaly_type"]
                self.anomaly_attributes[f"anomaly_{anomaly_type}_present"] = True
                self.anomaly_attributes[f"anomaly_{anomaly_type}_conf"] = anomaly_result["confidence"]

    def get_machine_type(self):
        for mt in ecips_config.MPE_LIST:
            if mt in self.img_filepath:
                return mt
        # NOTE: This shouldn't happen since unsupported machine types are filtered
        # out when looking for PRLM files
        return ''

    def get_run_name(self):
        if 'SPSS' in self.img_filepath:
            # SPSS Structures are slightly different
            return self.img_filepath.split("/")[-4]
        else:
            # APBS, APPS Structures are more regular
            return self.img_filepath.split("/")[-3]

    def get_hazmat_attributes(self):

        if self.hazmat_metrics and self.hazmat_metrics["num_hazmat_labels"] > 0:
            hazmat_attributes = {
                "hazmat_detected": True,
                "hazmat_type": ecips_config.ECIPS_YOLO_HAZMAT_MAPPINGS[int(self.hazmat_metrics["hazmat_classes"][0])],
                "num_hazmat": self.hazmat_metrics["num_hazmat_labels"],
                "hazmat_bbox": self.hazmat_metrics["detected_hazmat"]
            }
        else:
            hazmat_attributes = {
                "hazmat_detected": False,
                "hazmat_type": None,
                "num_hazmat": 0,
                "hazmat_bbox": None
            }

        return hazmat_attributes

    def get_image_data(self):
        impb_bcr = self.impb_reconstructed.accepted_barcode.barcode if self.impb_reconstructed is not None else None
        successful_bcr = (self.package_required_bcr and self.impb_reconstructed.send_bcr_result)
        send_to_loki_flag = self.contains_hazmat or self.is_fraudulent or self.is_anomalous or successful_bcr

        image_attributes = {
            "absolute_image_path": self.img_filepath,
            "absolute_json_path": self.json_filepath,
            "relative_webapat_image_path": os.path.join(*self.img_filepath.split("/")[2:]),
            "timestamp_json_written": self.timestamp_json_written,
            "timestamp_image_processed_for_prlm": self.date_processed,
            "package_view": self.package_view,
            "ibi": self.ibi_barcode_results,
            "package_volume": self.package_volume,
            "required_bcr": self.package_required_bcr,
            "mpe_impb": self.impb_decoded.barcode if self.impb_decoded is not None else None,
            "reconstructed_impb": impb_bcr,
            "date_processed": self.date_processed,
            "run": self.get_run_name(),
            "MPE": self.get_machine_type(),
            "MCB_Detected": self.mail_class_banner,
            "MCL_Detected": self.mail_class_letter,
            "raw_ocr_results": self.ocr_results,
            "send_to_loki": send_to_loki_flag
        }

        # Add in the Fraud attributes
        image_attributes.update(self.fraud_attributes)

        # Add in the Anomaly attributes
        image_attributes.update(self.anomaly_attributes)

        # Add in the hazmat attributes
        image_attributes.update(self.get_hazmat_attributes())

        # Add in the barcode attributes
        if self.package_required_bcr:
            image_attributes.update(self.impb_reconstructed.get_reconstructed_barcode_attributes())
        elif self.impb_barcode_results:
            image_attributes.update(self.impb_barcode_results.get_barcode_attributes())

        for item in image_attributes:
            image_attributes[item] = json.dumps(str(image_attributes[item]))
        return image_attributes


class DetectionClass:

    def __init__(self, detection):
        self.detection = detection
        self.classnum_to_classstring = {}
        self.detection_polygons = []
        self.detection_scores = []
        self.detection_classes = []
        self.model_version = None
        self.valid = False

    def is_valid(self, conf=0.9):
        for x in self.detection_scores:
            if x > conf:
                self.valid = True
                break
            else:
                pass


class ShippingLabelDetectionClass(DetectionClass):

    def __init__(self, raw_yolo_results, detection):
        super().__init__(detection)
        self.raw_yolo_results = raw_yolo_results
        self.detection_scores = raw_yolo_results['yolo_scores']
        self.detection_classes = raw_yolo_results['yolo_classes']
        self.detection_polygons = raw_yolo_results['yolo_boxes']
        self.classstring_to_classnum = ecips_config.ECIPS_SHIPPING_LABEL_CLASSES

        self.detection_name = detection
        if detection is None:
            self.detection_id = None
        else:
            self.detection_id = float(self.classstring_to_classnum[self.detection_name])

    def get_detection_confidence(self):
        if self.detection_id in self.detection_classes:
            detection_index = self.detection_classes.index(self.detection_id)
            return self.detection_scores[detection_index]
        else:
            return None


class BarcodeClass(DetectionClass):

    def __init__(self, impb_barcode, barcode_metrics, is_ocr_reconstruction=False, detection="barcode"):
        super().__init__(detection)
        self.barcode_metrics = barcode_metrics
        self.classnum_to_classstring = {}

        # The IMPB barcode tracking number
        self.barcode = impb_barcode
        # Metrics that describe the detection of the IMPB barcode
        self.detection_polygons = self.barcode_metrics["detected_barcode"]
        self.detection_scores = self.barcode_metrics['barcode_scores']
        self.detected_digits = self.barcode_metrics['detected_digits']
        self.digit_scores = self.barcode_metrics['digit_scores']
        self.model_version = self.barcode_metrics['Barcode_model_version']
        self.digit_model_version = self.barcode_metrics['Digit_model_version']

        # Initialization to None
        self.stc_code = None
        self.mid = None
        self.is_stc_code_valid = None
        self.mailclass_from_stc = None
        self.is_label_400_class = None

        # Reconstruction Status, always false for Barcode Class
        # Updates to True when inherited by reconstructed barcode class
        self.is_ocr_reconstruction = is_ocr_reconstruction

        # Check if the impb structure is valid
        self.is_valid_barcode = self.is_valid_impb()

        if self.is_valid_barcode:
            # Defined when called, initialized to None
            # Check if the barcode is of class "Label 400"
            self.is_label_400_class = self.get_label_400_status()

            if not self.is_label_400_class:
                self.stc_code, self.is_stc_code_valid, self.mailclass_from_stc = self.get_stc_mailclass()
                self.mid = self.extract_mid()

    def get_label_400_status(self):
        """
        Method to extract the status of the barcode to determine if it can be classified as a "label 400" case
        For background, label 400 cases DO NOT contain a valid STC code

        Returns:
              is_label_400 (bool):
                    T/F if the label is classified as a label 400. If True, there is no STC to extract
        """
        is_label_400 = False
        if self.barcode.startswith('9114'):
            is_label_400 = True

        return is_label_400

    def get_stc_mailclass(self, stc_db=get_stc_db()):
        """Method to extract the Service Type Code (STC) from the IMPB barcode as processed from the PRLM file.
        Logic to extract STC follows the IMPB spec found on WebAPAT

        Parameters:
            stc_db: dict
                Dictionary with the STC code mapped to the Mail Class. Used to verify the extracted STC

        Returns:
            stc_code (str):
                Returns a valid STC of length 3 or an empty string
            is_stc_code_valid (bool):
                Returns True if the STC code is valid, else False
            mailclass_from_stc (str):
                Returns the mail class that corresponds to the STC code

        """

        stc = None
        mail_class_from_stc = None
        is_stc_code_valid = False

        if self.barcode[0:2] in ['91', '92', '93', '94', '95']:
            stc = self.barcode[2:5]

        # Verify extracted STC is valid
        if stc in stc_db:
            mail_class_from_stc = stc_db[stc]
            is_stc_code_valid = True
        else:
            stc = None

        return stc, is_stc_code_valid, mail_class_from_stc

    def extract_mid(self):
        """Method to extract the Mailer ID (MID) from the IMPB barcode as processed from the PRLM file.
        Logic to extract STC follows the IMPB spec found on postalpro

        Returns:
            str
                Returns a valid MID of length 6 or 9, or an empty string
        """
        if self.barcode.isnumeric():
            channel_application_identifier = self.barcode[:2]
            if channel_application_identifier == '92':
                mid = self.barcode[5:14]  # 9-digit mid

            elif channel_application_identifier == '93':
                mid = self.barcode[5:11]  # 6-digit mid

            elif channel_application_identifier == '94':
                if self.barcode[7] == '9':
                    mid = self.barcode[7:16]  # 9-digit mid
                else:
                    mid = self.barcode[7:13]  # 6-digit mid
            else:
                # channel is either 91 (legacy) which we don't have guidance for
                # or channel is 95 which does not have a mid
                mid = None

        else:
            # We have an S10 barcode which does not have a MID
            mid = None
        return mid

    def is_valid_impb(self):
        # Confirm if the barcode is valid using checksum, update values accordingly
        if self.barcode is not None:
            self.barcode, is_valid = check_barcode.is_valid_barcode(self.barcode, self.is_ocr_reconstruction)
        else:
            is_valid = False

        return is_valid

    def get_barcode_attributes(self):
        barcode_attributes = {
            "barcode": self.barcode,
            "barcode_type": "impb",
            "barcode_conf": self.detection_scores[0],
            "is_ocr_reconstruction": self.is_ocr_reconstruction,
            "is_valid_barcode": self.is_valid_barcode,
            "is_label_400_class": self.is_label_400_class,
            "stc_code": self.stc_code,
            "is_stc_code_valid": self.is_stc_code_valid,
            "mailclass_from_stc": self.mailclass_from_stc,
            "mailer_id": self.mid
        }

        return barcode_attributes


class ReconstructedBarcodesClass:
    def __init__(self, image_object):
        self.bcr_metrics = image_object.bcr_metrics
        self.barcode_detection_metrics = image_object.barcode_metrics

        # As of v1.6.8 we can reconstruct multiple barcodes
        self.reconstructed_barcodes = []
        if self.bcr_metrics:
            # If there are reconstructed barcodes, add them to a list
            for bcr_results in self.bcr_metrics:
                self.reconstructed_barcodes.append(ReconstructedBarcodeClass(bcr_results,
                                                                             self.barcode_detection_metrics))


class ReconstructedBarcodeClass:
    def __init__(self, bcr_metrics, barcode_detection_metrics):
        self.bcr_metrics = bcr_metrics
        self.barcode_detection_metrics = barcode_detection_metrics

        if bcr_metrics:
            self.barcode_decode = BarcodeClass(self.bcr_metrics["barcode_decode"],
                                               self.barcode_detection_metrics)
            self.barcode_ocr = BarcodeClass(self.bcr_metrics["barcode_ocr"],
                                            self.barcode_detection_metrics,
                                            is_ocr_reconstruction=True)
        else:
            self.bcr_metrics = {}
            self.barcode_decode = BarcodeClass(None,
                                               self.barcode_detection_metrics)
            self.barcode_ocr = BarcodeClass(None,
                                            self.barcode_detection_metrics,
                                            is_ocr_reconstruction=True)
        self.risk_score = None
        self.barcode_present = None
        self.barcode_reconstructed = None
        self.barcode = None
        self.barcodes = None
        self.barcode_class = None
        self.send_bcr_result = None

        # Update what the accepted barcode reconstruction is
        if self.barcode_decode.is_valid_barcode:
            self.accepted_barcode = self.barcode_decode
            self.reconstructed_with_ocr = False
        else:
            self.accepted_barcode = self.barcode_ocr
            self.reconstructed_with_ocr = True

        self.update_barcode_values()
        self.increment_reconstructed_method_counters()

    def update_barcode_values(self):
        if self.bcr_metrics:
            self.risk_score = self.bcr_metrics["barcode_risk_score"]
            self.barcode_present = self.bcr_metrics["barcode_present"]
            self.barcode_reconstructed = self.bcr_metrics["barcode_reconstructed"]
            self.barcode = self.bcr_metrics["barcode"]
            self.barcode_class = self.bcr_metrics["barcode_class"]

        self.bcr_metrics['barcode_present'] = str(self.accepted_barcode.is_valid_barcode).upper()
        self.bcr_metrics['barcode_reconstructed'] = str(self.accepted_barcode.is_valid_barcode).upper()
        self.send_bcr_result = self.accepted_barcode.is_valid_barcode
        self.bcr_metrics["barcode"] = self.accepted_barcode.barcode

    def increment_reconstructed_method_counters(self):
        # Only increment the counters if the reconstruction was successful
        if self.send_bcr_result:
            if self.reconstructed_with_ocr:
                # Increment the redis counter for bcr with ocr
                ecips_logging.inc_redis_counter("reconstructed_with_OCR")
            else:
                # Increment the redis counter for bcr with pyzbar
                ecips_logging.inc_redis_counter("reconstructed_with_pyzbar")

    def get_reconstructed_barcode_attributes(self):
        reconstructed_barcode_attr = {
            "successfully_reconstructed": self.send_bcr_result,
            "reconstructed_with_OCR": self.reconstructed_with_ocr,
            "reconstructed_with_pyzbar": self.send_bcr_result and not self.reconstructed_with_ocr,
            "OCR_result": self.barcode_ocr.barcode if self.barcode_ocr.is_valid_barcode else None,
            "pyzbar_result": self.barcode_decode.barcode if self.barcode_decode.is_valid_barcode else None,
        }

        # Update the dictionary with the accepted attributes from the accepted Barcode class
        reconstructed_barcode_attr.update(self.accepted_barcode.get_barcode_attributes())

        return reconstructed_barcode_attr


class HazmatClass(DetectionClass):

    def __init__(self, image_object, detection="hazmat"):
        super().__init__(detection)
        self.hazmat_metrics = image_object.hazmat_metrics
        if ecips_config.ECIPS_INFERENCE_SERVER_USE_HAZMAT_YOLO:
            self.classnum_to_classstring = [
                {"id": 2, "name": "Lithium_UN_Label", "supercategory": ""},
                {"id": 3, "name": "Lithium__Class_9", "supercategory": ""},
                {"id": 4, "name": "Lithium_Battery_Label", "supercategory": ""},
                {"id": 5, "name": "Biohazard", "supercategory": ""},
                {"id": 6, "name": "No_Fly", "supercategory": ""},
                {"id": 7, "name": "Finger_Small", "supercategory": ""},
                {"id": 8, "name": "Finger_Large", "supercategory": ""},
                {"id": 9, "name": "Cargo_Air_Only", "supercategory": ""},
                {"id": 10, "name": "Suspected_Label", "supercategory": ""},
                {"id": 17, "name": "Hazmat_Surface_Only", "supercategory": ""},
                {"id": 28, "name": "Cremated_Remains", "supercategory": ""}]
        else:
            self.classnum_to_classstring = [
                {"id": 1, "name": "Lithium_UN_Label", "supercategory": ""},
                {"id": 2, "name": "Lithium__Class_9", "supercategory": ""},
                {"id": 3, "name": "Lithium_Battery_Label", "supercategory": ""},
                {"id": 4, "name": "Biohazard", "supercategory": ""},
                {"id": 5, "name": "No_Fly", "supercategory": ""},
                {"id": 6, "name": "Finger_Small", "supercategory": ""},
                {"id": 7, "name": "Finger_Large", "supercategory": ""},
                {"id": 8, "name": "Cargo_Air_Only", "supercategory": ""},
                {"id": 9, "name": "Suspected_Label", "supercategory": ""},
                {"id": 10, "name": "Hazmat_Surface_Only", "supercategory": ""},
                {"id": 21, "name": "Cremated_Remains", "supercategory": ""}]
        self.detection_polygons = self.hazmat_metrics['detected_hazmat']
        self.detection_scores = self.hazmat_metrics['hazmat_scores']
        self.detection_classes = self.hazmat_metrics['hazmat_classes']
        self.model_version = self.hazmat_metrics["Hazmat_model_version"]
        self.num_hazmat_labels = self.hazmat_metrics["num_hazmat_labels"]
        self.hazmat_minconf = ecips_config.ECIPS_INFERENCE_HAZMAT_SCORE_THRES,
        self.valid_category_id_list = ecips_config.ECIPS_HAZMAT_VALID_ID,
        self.invalid_category_id_list = ecips_config.ECIPS_HAZMAT_INVALID_ID
        # self.is_valid()


class PVIClass(DetectionClass):

    def __init__(self, image_object, detection="pvi"):
        super().__init__(detection)
        self.pvi_metrics = image_object.pvi_metrics
        self.detection_scores = self.pvi_metrics["pvi_scores"]
        self.detection_polygons = self.pvi_metrics['detected_pvi']
        self.model_version = self.pvi_metrics['PVI_model_version']
        self.is_valid()


class StampClass(DetectionClass):

    def __init__(self, image_object, detection="stamp"):
        super().__init__(detection)
        self.stamp_metrics = image_object.stamp_metrics
        self.detection_scores = self.stamp_metrics["stamp_scores"]
        self.detected_polygons = self.stamp_metrics["detected_stamp"]
        self.model_version = self.stamp_metrics["Stamp_model_version"]
        self.num_stamps = self.stamp_metrics['num_stamps']
        self.is_valid()


class PackageClass(DetectionClass):

    def __init__(self, image_object, detection="package"):
        super().__init__(detection)
        self.package_metrics = image_object.package_metrics
        self.detection_scores = self.package_metrics["package_score"]
        self.model_version = self.package_metrics["Package_model_version"]
        self.is_valid()


class IBIClass(ShippingLabelDetectionClass):

    def __init__(self, ibi_decoded_results, ocr_results, raw_yolo_results, detection="ibi"):
        super().__init__(raw_yolo_results, detection)
        self.is_fraud = None
        self.fraud_type = []

        self.serial_number_ocr = None
        self.serial_number_extracted_barcode = None
        self.date_ocr = None
        self.confidence_date_ocr = None
        self.max_dist_date_by_conf = None
        self.date_extracted_barcode = None
        self.formatted_dates_10_day_window = None
        self.ocr_results = ocr_results
        self.ibi_barcode_results = ibi_decoded_results
        self.ibi_detection_conf = self.get_detection_confidence()

        # TODO: only get detection conf once
        self.fraud_metrics = {
            'ocr_results': {'date': {}, 'serial_number': {}},
            'barcode_results': {'date': {}, 'serial_number': {}},
            'yolo_conf': self.ibi_detection_conf
        }

        # Update the redis counters for decoded and detected IBIs
        self.increment_redis_IBI_counters()

        # get the Date and Serial number values
        self.initialize_date_indicators()
        self.initialize_serial_number_indicators()

    def scan_label_for_fraud(self):
        if DETECT_IBI_DATE_MISMATCH:
            self.compute_fraud_mismatch_date('dates_ibi',
                                             self.date_ocr, self.formatted_dates_10_day_window,
                                             'mismatch_humanReadableDate_decodedIBIDate')

        if DETECT_IBI_SN_MISMATCH:
            max_l_dist_allowed = MAX_LEVENSHTEIN_DIST_IBI_SN
            if "special_data_matrix_label_detected" in self.fraud_metrics['ocr_results']['serial_number']:
                if self.fraud_metrics['ocr_results']['serial_number']['special_data_matrix_label_detected']:
                    max_l_dist_allowed = MAX_LEVENSHTEIN_DIST_IBI_SN_SPECIAL_DM
            self.compute_fraud_mismatch_serial_number('serial_number_ibi',
                                                      self.serial_number_ocr, self.serial_number_extracted_barcode,
                                                      max_l_dist_allowed,
                                                      'mismatch_humanReadableSN_decodedIBISN')
        if DETECT_INVALID_IBI_SN:
            self.find_invalid_sn_construction('serial_number_construct_ibi',
                                              self.serial_number_ocr, self.serial_number_extracted_barcode,
                                              'invalid_IBI_SN')

        # TODO: Update the fraud metric dictionary

    def initialize_date_indicators(self):
        # Initializing Barcode Results
        if self.ibi_barcode_results is not None:
            self.date_extracted_barcode, self.formatted_dates_10_day_window, ibi_barcode_metrics = \
                extract_mailing_date_barcode(self.ibi_barcode_results)
            self.fraud_metrics['barcode_results']['date'] = ibi_barcode_metrics

        # Initializing OCR Results
        date_ocr = self.ocr_results
        if None not in [self.date_extracted_barcode, date_ocr]:
            self.date_ocr, ocr_metrics = extract_mailing_date_ocr(date_ocr,
                                                                  self.formatted_dates_10_day_window[:len(DATE_FORMATS)]
                                                                  )
            self.fraud_metrics['ocr_results']['date'] = ocr_metrics
            self.confidence_date_ocr = ocr_metrics['confidence'] if 'confidence' in ocr_metrics else None
            self.max_dist_date_by_conf = self.get_dynamic_max_l_distance_date() if 'confidence' in ocr_metrics else None

    def compute_fraud_mismatch_date(self, fraud_metric_key, ocr_results, barcode_results, mismatch_key):
        fraud_logic_executed = False
        l_distance_computed = None
        date_fraud = True
        self.fraud_metrics[fraud_metric_key] = {}
        self.fraud_metrics[fraud_metric_key]['matched_date'] = None

        # Check for mismatch if both ocr and barcode extracted metrics are valid
        if None not in [ocr_results, barcode_results]:
            fraud_logic_executed = True

            # Check if the date from OCR matches at least one of the formats of the PRLM date
            date_fraud, l_distance_computed = self.check_date_is_fraud(ocr_results, barcode_results[:len(DATE_FORMATS)],
                                                                       MAX_LEVENSHTEIN_DIST_IBI_DATE, date_fraud,
                                                                       fraud_metric_key)

            # If fraud is detected, then check if the OCR date falls within the 10 day window
            if date_fraud:
                date_fraud, l_distance_computed = self.check_date_is_fraud(ocr_results,
                                                                           barcode_results[len(DATE_FORMATS):],
                                                                           self.max_dist_date_by_conf, date_fraud,
                                                                           fraud_metric_key)

            if date_fraud:
                self.is_fraud = True
                self.fraud_type.append(mismatch_key)

        # Define fraud metrics
        self.build_fraud_metrics(fraud_metric_key, ocr_results, self.date_extracted_barcode,
                                 fraud_logic_executed, l_distance_computed)

    def initialize_serial_number_indicators(self):
        # Initializing OCR Results
        serial_num_ocr = self.ocr_results
        if serial_num_ocr is not None:
            self.serial_number_ocr, ocr_metrics = extract_serial_num_ocr(serial_num_ocr)
            self.fraud_metrics['ocr_results']['serial_number'] = ocr_metrics

        # Initializing Barcode Results
        if None not in [self.ibi_barcode_results, self.serial_number_ocr]:
            # Check if flag `is_imi` has already been computed and compute it if it doesn't exist
            if 'is_imi' in self.fraud_metrics['ocr_results']['date']:
                is_imi = self.fraud_metrics['ocr_results']['date']['is_imi']
            else:
                is_imi = check_ibi_or_imi(self.ibi_barcode_results)

            human_readable_serial_number, vendor_id, raw_sn, ibi_barcode_metrics = extract_serial_number_barcode(
                self.ibi_barcode_results, is_imi
            )
            self.serial_number_extracted_barcode = raw_sn if ocr_metrics[
                'special_data_matrix_label_detected'] else human_readable_serial_number

            self.fraud_metrics['barcode_results']['serial_number'] = ibi_barcode_metrics

    def compute_fraud_mismatch_serial_number(self, fraud_metric_key, ocr_results, barcode_results,
                                             max_dist_allowed, mismatch_key):
        fraud_logic_executed = False
        l_distance_computed = None

        # Check for mismatch if both ocr and barcode extracted metrics are valid
        if None not in [ocr_results, barcode_results]:
            fraud_logic_executed = True

            # Compute levenshetin distance ignoring the 0s present in both OCR SN and IBI barcode SN
            l_distance_computed = distance(ocr_results.replace('0', ''), barcode_results.replace('0', ''))

            if l_distance_computed > max_dist_allowed:
                self.is_fraud = True
                self.fraud_type.append(mismatch_key)

        # Define fraud metrics
        self.build_fraud_metrics(fraud_metric_key, ocr_results, barcode_results,
                                 fraud_logic_executed, l_distance_computed)

    def find_invalid_sn_construction(self, fraud_metric_key, ocr_results, barcode_results, mismatch_key):
        fraud_logic_executed = False

        # Check for mismatch if both ocr and barcode extracted metrics are valid
        if barcode_results is not None:
            fraud_logic_executed = True

            fraudulent_construct = self.is_fraudulent_IBI_construct(barcode_results)

            if fraudulent_construct:
                self.is_fraud = True
                self.fraud_type.append(mismatch_key)

        if ocr_results is not None:
            fraud_logic_executed = True

            fraudulent_construct = self.is_fraudulent_IBI_construct(ocr_results)

            if fraudulent_construct:
                self.is_fraud = True
                self.fraud_type.append(mismatch_key)

        # Define fraud metrics
        self.build_fraud_metrics(fraud_metric_key, ocr_results, barcode_results,
                                 fraud_logic_executed, None)

    def is_fraudulent_IBI_construct(self, serial_number):
        # Grab the first two digits of the SN, If they are "07" the IBI is fraudulent
        try:
            sn_identifier = serial_number[:2]
        except IndexError:
            # The SN isnt long enough to compute
            return False

        if sn_identifier == "07":
            return True
        else:
            return False

    def build_fraud_metrics(self, fraud_metric_key, ocr_results, barcode_results,
                            fraud_logic_executed, l_distance_computed):
        fraud_confidence = None
        if fraud_logic_executed:
            if fraud_metric_key == "invalid_IBI_SN":
                fraud_confidence = np.average([self.fraud_metrics["ocr_results"]["serial_number"]["confidence"],
                                               self.fraud_metrics["yolo_conf"]], weights=[.7, .3])

            elif fraud_metric_key == "serial_number_ibi":
                fraud_confidence = np.average([l_distance_computed / len(barcode_results),
                                               self.fraud_metrics["ocr_results"]["serial_number"][
                                                   "confidence"],
                                               self.fraud_metrics["yolo_conf"]], weights=[.6, .3, .1])

            elif fraud_metric_key == 'serial_number_construct_ibi':
                fraud_confidence = np.average([self.fraud_metrics["ocr_results"]["serial_number"]["confidence"],
                                               self.fraud_metrics["yolo_conf"]], weights=[.7, .3])

            else:
                if l_distance_computed is not None:
                    fraud_confidence = np.average([l_distance_computed / len(barcode_results),
                                                   self.fraud_metrics["ocr_results"]["date"][
                                                       "confidence"],
                                                   self.fraud_metrics["yolo_conf"]], weights=[.6, .3, .1])
                else:
                    fraud_confidence = np.average([self.fraud_metrics["ocr_results"]["date"][
                                                       "confidence"],
                                                   self.fraud_metrics["yolo_conf"]], weights=[.7, .1])
        if fraud_metric_key not in self.fraud_metrics:
            self.fraud_metrics[fraud_metric_key] = {}
        self.fraud_metrics[fraud_metric_key].update({'ocr': ocr_results,
                                                     'barcode': barcode_results,
                                                     'ocr_valid': True if ocr_results else False,
                                                     'barcode_valid': True if barcode_results else False,
                                                     'fraud_logic_executed': fraud_logic_executed,
                                                     'levenshtein_distance': l_distance_computed,
                                                     'fraud_confidence': fraud_confidence
                                                     })

    def describe_fraud_metrics(self):
        return self.fraud_metrics

    def get_dynamic_max_l_distance_date(self):
        # Set the max allowed Levenshtein distance based on the confidence of date OCR
        if self.confidence_date_ocr >= CONF_THRESHOLD_LEVEL_1:
            return MAX_LEVENSHTEIN_DIST_IBI_DATE_LEVEL_1
        if self.confidence_date_ocr >= CONF_THRESHOLD_LEVEL_2:
            return MAX_LEVENSHTEIN_DIST_IBI_DATE_LEVEL_2

        return MAX_LEVENSHTEIN_DIST_IBI_DATE

    def check_date_is_fraud(self, ocr_date, barcode_dates, max_dist_allowed, date_fraud, fraud_metric_key):
        self.fraud_metrics[fraud_metric_key]['matched_date'] = barcode_dates[0]
        best_dist = 1000
        for mailing_date_barcode in barcode_dates:
            l_distance_computed = distance(ocr_date, mailing_date_barcode)
            if l_distance_computed <= max_dist_allowed:
                self.fraud_metrics[fraud_metric_key]['matched_date'] = mailing_date_barcode
                best_dist = l_distance_computed
                date_fraud = False
                break
            if l_distance_computed < best_dist:
                self.fraud_metrics[fraud_metric_key]['matched_date'] = mailing_date_barcode
                best_dist = l_distance_computed

        return date_fraud, best_dist

    def increment_redis_IBI_counters(self):
        if self.ibi_barcode_results is not None:
            # increment the counter of IBIs decoded by the MPE
            ecips_logging.inc_redis_counter("ibi_decoded_by_mpe")

        if self.ocr_results is not None:
            # increment the counter of IBIs detected by the ECIP yolo model
            ecips_logging.inc_redis_counter("ibi_detected_by_yolo")


class PermitImprintClass(ShippingLabelDetectionClass):

    def __init__(self,
                 impb_barcode_results,
                 pi_ocr_results,
                 raw_yolo_results,
                 detection="permit-imprint"):
        super().__init__(raw_yolo_results, detection)

        self.ocr_results = pi_ocr_results
        self.impb_barcode_results = impb_barcode_results
        self.pi_detection_conf = self.get_detection_confidence()
        if self.impb_barcode_results:
            self.mail_class_from_stc = self.impb_barcode_results.mailclass_from_stc
        else:
            self.mail_class_from_stc = None

        self.is_fraud = None

        self.fraud_type = []

        self.fraud_metrics = {
            "all_detected_text": None,
            "classification_results": {
                "permit_imprint_class": None,  # epostage or evs or neither
                "edit_dist_to_class": None,  # how far off detected class label was from expected string
                "detected_class_text": None,
                "detected_class_text_confidence": None,
                "rotation_info": None,
            },
            "validation_results": {
                "detected_permit_number": None,
                "detected_permit_number_confidence": None,
                "detected_permit_invalid": None,
                "detected_business": None,
                "detected_business_confidence": None,
                "shippo_epostage": None,
                "mid": None
            },
            "yolo_conf": self.pi_detection_conf,
            "barcode_attributes": self.impb_barcode_results.get_barcode_attributes()

        }

        self.is_anomaly = None
        self.anomaly_type = []
        self.anomaly_metrics = {'anomaly_06': {},
                                "yolo_conf": self.pi_detection_conf,
                                "barcode_attributes": self.impb_barcode_results.get_barcode_attributes()
                                }

    def get_ocr_conf(self, results):
        if results["validation_results"]["detected_permit_number_confidence"] is not None:
            return results["validation_results"]["detected_permit_number_confidence"]
        elif results["validation_results"]["detected_business_confidence"] is not None:
            return results["validation_results"]["detected_business_confidence"]
        else:
            return 0

    def scan_label_for_fraud(self):
        permit_imprint_OCR = self.ocr_results

        if permit_imprint_OCR is not None and permit_imprint_OCR != []:
            try:
                fraud_detection_results = is_fraud_permit_imprint(permit_imprint_OCR, self.impb_barcode_results)
            except IndexError:
                # Occurs when the OCR result is not in a format thats expected,
                return
            self.is_fraud = fraud_detection_results.pop('is_fraud')

            self.fraud_metrics = {**fraud_detection_results, "yolo_conf": self.pi_detection_conf,
                                  "fraud_confidence": None if not self.is_fraud else
                                  np.mean([self.get_ocr_conf(fraud_detection_results),
                                           self.pi_detection_conf if self.pi_detection_conf is not None else 0])}

            if self.is_fraud:
                if self.fraud_metrics['classification_results']['permit_imprint_class'] == "epostage":
                    if self.fraud_metrics['validation_results']['shippo_epostage']:
                        self.fraud_type = ["invalid_shippo_ePostage"]
                    else:
                        self.fraud_type = ["invalid_ePostage"]
                else:
                    if self.fraud_metrics['validation_results']['detected_permit_invalid']:
                        # Increment the counter for the invalid Permit Number that we have detected
                        invalid_permit_no = self.fraud_metrics['validation_results']['detected_permit_number']
                        ecips_logging.inc_redis_counter(f"invalid_permit_no_{invalid_permit_no}")
                        mid = self.impb_barcode_results.mid
                        self.fraud_metrics['validation_results']['mid'] = mid
                        if mid:
                            # Must be a valid mid (not None)
                            ecips_logging.inc_redis_counter(f"invalid_permit_mid_{mid}")
                        self.fraud_type = ['invalid_eVS_permit']
                    else:
                        self.fraud_type = ["missing_eVS_validation"]

        self.update_fraud_dictionary()

    def describe_fraud_metrics(self, key=None):
        if key:
            return self.fraud_metrics[key]
        return self.fraud_metrics

    def update_fraud_dictionary(self):
        # TODO: separate creation of fraud dictionary
        pass

    def scan_label_for_anomalies(self):
        if self.impb_barcode_results is not None:
            if self.ocr_results is not None and self.ocr_results != [] and self.mail_class_from_stc is not None:
                self.is_anomaly, anomaly_key, anomaly_06_metrics = is_anomaly_06(self.ocr_results,
                                                                                 self.mail_class_from_stc)
                self.anomaly_metrics['anomaly_06'] = anomaly_06_metrics
                self.anomaly_metrics['yolo_conf'] = self.pi_detection_conf
                # Temp commenting this out because I want to generate the conf separately AND it raises a few errors
                # self.anomaly_metrics['anomaly_conf'] = np.average([self.yolo_conf,
                #                                                    anomaly_06_metrics['mail_class_conf']],
                #                                                   weights=[.10, .90])
                self.anomaly_metrics['anomaly_06']['anomaly_confidence'] = anomaly_06_metrics['mail_class_conf']

            if self.is_anomaly:
                self.anomaly_type.append(GROUND_ADVANTAGE_PERMIT_IMPRINT_INDICIA_STC_ANOMALY.anomaly_id)
                mid = self.impb_barcode_results.mid
                if mid:
                    # Must be a valid mid (not None)
                    redis_mid_var = f"{GROUND_ADVANTAGE_PERMIT_IMPRINT_INDICIA_STC_ANOMALY.anomaly_class}" \
                                    f"_anomaly_mid_{mid}"
                    ecips_logging.inc_redis_counter(redis_mid_var)

    def describe_anomaly_metrics(self, key=None):
        if key:
            return self.anomaly_metrics[key]
        return self.anomaly_metrics


class MailMarkingsClass(ShippingLabelDetectionClass):
    def __init__(self,
                 impb_barcode_results,
                 detected_mail_class,
                 banner_ocr_results,
                 raw_yolo_results,
                 contains_hazmat_markings):
        super().__init__(raw_yolo_results, detected_mail_class)

        # Defining the input variables
        self.mail_class_from_img = detected_mail_class
        self.impb_barcode_results = impb_barcode_results
        self.ocr_results = banner_ocr_results
        self.contains_hazmat_markings = contains_hazmat_markings
        self.mail_class_letter_detection_conf = self.get_detection_confidence()
        self.mail_class_from_stc = self.impb_barcode_results.mailclass_from_stc

        # Mail class banner information
        self.mcb_metrics = {}
        self.mail_class_from_banner = None
        self.initialize_mail_class_banner()

        # Fraud Metrics
        self.is_fraud = None
        self.fraud_type = []
        self.fraud_metrics = {'barcode_attributes': self.impb_barcode_results.get_barcode_attributes(),
                              'mailclass_lettercode': self.mcb_metrics,
                              'yolo_conf': self.mail_class_letter_detection_conf,
                              'mismatch_mailclass_servicetype': {},
                              'mismatch_mailclass_lettercode': {}
                              }

        # Anomaly Metrics
        self.is_anomaly = None
        self.anomaly_type = []
        self.anomaly_class = []
        self.anomaly_metrics = {'anomaly_01': {},
                                'anomaly_02': {},
                                'anomaly_03': {},
                                'anomaly_04': {},
                                'anomaly_05': {},
                                'barcode_attributes': self.impb_barcode_results.get_barcode_attributes(),
                                "mailclass_lettercode": self.mcb_metrics,
                                "yolo_conf": self.mail_class_letter_detection_conf}

    def scan_label_for_fraud(self):
        if DETECT_SERVICETYPE_MISMATCH:
            self.compute_fraud_mismatch('mismatch_mailclass_servicetype', self.mail_class_from_img,
                                        self.mail_class_from_stc, 'mismatch_mailclass_servicetype')
        else:
            self.fraud_metrics["mismatch_mailclass_servicetype"]["fraud_logic_executed"] = False

        if DETECT_MAILCLASS_LETTERCODE_MISMATCH:
            self.compute_fraud_mismatch('mismatch_mailclass_lettercode', self.mail_class_from_img,
                                        self.mail_class_from_banner, 'mismatch_mailclass_lettercode')
        else:
            self.fraud_metrics["mismatch_mailclass_lettercode"]["fraud_logic_executed"] = False

        self.update_fraud_dictionary()

    def update_fraud_dictionary(self):
        self.fraud_metrics['mailclass_lettercode']['mail_class_from_img'] = self.mail_class_from_img
        self.fraud_metrics['mailclass_lettercode']['ocr_results'] = self.ocr_results

        if self.fraud_metrics['mismatch_mailclass_servicetype']['fraud_logic_executed']:
            self.fraud_metrics['mismatch_mailclass_servicetype']['fraud_confidence'] = self.fraud_metrics["yolo_conf"]
        else:
            self.fraud_metrics['mismatch_mailclass_servicetype']['fraud_confidence'] = None

        if self.fraud_metrics['mismatch_mailclass_lettercode']['fraud_logic_executed']:
            self.fraud_metrics['mismatch_mailclass_lettercode']['fraud_confidence'] = np.average(
                [self.fraud_metrics['mailclass_lettercode']['confidence'], self.fraud_metrics["yolo_conf"]],
                weights=[.75, .25])
        else:
            self.fraud_metrics['mismatch_mailclass_lettercode']['fraud_confidence'] = None

    def scan_label_for_anomalies(self):
        # Check for various forms of mail class anomalies
        # Anomaly 01
        if HAZMAT_SYMBOL_STC_ANOMALY.is_active:
            is_anomaly, self.anomaly_metrics = is_anomaly_01(self.mail_class_from_stc,
                                                             self.anomaly_metrics,
                                                             self.contains_hazmat_markings)
            if is_anomaly:
                self.is_anomaly = True
                self.anomaly_type.append(HAZMAT_SYMBOL_STC_ANOMALY.anomaly_id)
                self.anomaly_class.append(HAZMAT_SYMBOL_STC_ANOMALY.anomaly_class)

        # Anomaly 02
        if HAZMAT_LETTER_INDICATOR_STC_ANOMALY.is_active:
            # Identical to compute Fraud mismatch without the keys
            is_anomaly, self.anomaly_metrics = is_anomaly_02(self.mail_class_from_stc,
                                                             self.mail_class_from_img,
                                                             self.anomaly_metrics)
            if is_anomaly:
                self.is_anomaly = True
                self.anomaly_type.append(HAZMAT_LETTER_INDICATOR_STC_ANOMALY.anomaly_id)
                self.anomaly_class.append(HAZMAT_LETTER_INDICATOR_STC_ANOMALY.anomaly_class)

        # Anomaly 03
        if GROUND_ADVANTAGE_INDICATOR_STC_ANOMALY.is_active:
            # Identical to compute Fraud mismatch without the keys
            is_anomaly, self.anomaly_metrics = is_anomaly_03(self.mail_class_from_stc,
                                                             self.mail_class_from_img,
                                                             self.anomaly_metrics)
            if is_anomaly:
                self.is_anomaly = True
                self.anomaly_type.append(GROUND_ADVANTAGE_INDICATOR_STC_ANOMALY.anomaly_id)
                self.anomaly_class.append(GROUND_ADVANTAGE_INDICATOR_STC_ANOMALY.anomaly_class)

        # Anomaly 04
        if NON_GROUND_ADVANTAGE_INDICATOR_STC_ANOMALY.is_active:
            # Identical to compute Fraud mismatch without the keys
            is_anomaly, self.anomaly_metrics = is_anomaly_04(self.mail_class_from_stc,
                                                             self.mail_class_from_img,
                                                             self.anomaly_metrics)
            if is_anomaly:
                self.is_anomaly = True
                self.anomaly_type.append(NON_GROUND_ADVANTAGE_INDICATOR_STC_ANOMALY.anomaly_id)
                self.anomaly_class.append(NON_GROUND_ADVANTAGE_INDICATOR_STC_ANOMALY.anomaly_class)

        # Anomaly 05
        if GROUND_ADVANTAGE_BANNER_STC_ANOMALY.is_active:
            # Identical to compute Fraud mismatch without the keys
            is_anomaly, self.anomaly_metrics = is_anomaly_05(self.mail_class_from_stc,
                                                             self.mail_class_from_banner,
                                                             self.anomaly_metrics)

            if is_anomaly:
                self.is_anomaly = True
                self.anomaly_type.append(GROUND_ADVANTAGE_BANNER_STC_ANOMALY.anomaly_id)
                self.anomaly_class.append(GROUND_ADVANTAGE_BANNER_STC_ANOMALY.anomaly_class)

        if self.is_anomaly:
            mid = self.impb_barcode_results.mid
            if mid:
                # Must be a valid mid (not None)
                # Update the value based on the anomaly_type
                self.anomaly_class = set(self.anomaly_class)
                for anomaly_class in self.anomaly_class:
                    ecips_logging.inc_redis_counter(f"{anomaly_class}_anomaly_mid_{mid}")

    def initialize_mail_class_banner(self):
        if self.ocr_results is not None and self.ocr_results != []:
            self.mail_class_from_banner, self.mcb_metrics = extract_mail_class_banner_ocr(self.ocr_results)

    def compute_fraud_mismatch(self, fraud_metrics_key, fraud_feature_img, fraud_feature_extracted, mismatch_key):
        if None in [fraud_feature_extracted, fraud_feature_img]:
            self.fraud_metrics[fraud_metrics_key]['fraud_logic_executed'] = False
        else:
            self.fraud_metrics[fraud_metrics_key]['fraud_logic_executed'] = True
            if fraud_feature_img != fraud_feature_extracted:
                if mismatch_key == "mismatch_mailclass_lettercode":
                    is_hazmat_edge_case = fraud_feature_img == "hazmat" and \
                                          fraud_feature_extracted == "ground-advantage"
                    if is_hazmat_edge_case:
                        # this is the case where a hazmat h indicator was detected but the banner is GA.  This is
                        # not considered Fraud or an Anomaly
                        return
                else:
                    self.is_fraud = True
                    self.fraud_type.append(mismatch_key)

    def describe_fraud_metrics(self):
        return self.fraud_metrics

    def describe_anomaly_metrics(self):
        return self.anomaly_metrics


class IMPBBarcodeClass(ShippingLabelDetectionClass):

    def __init__(self,
                 mpe_decoded_barcode,
                 impb_reconstruction,
                 raw_yolo_results,
                 detection="impb"):
        super().__init__(raw_yolo_results, detection)
        self.is_fraud = []
        self.fraud_type = []

        # We will use the pyzbar decoded barcode if present as our decoded barcode
        # If pyzbar was unable to decode, we will use the mpe decoded barcode
        self.decoded_barcode = impb_reconstruction.barcode_decode

        # I am removing this as we can introduce more FPs when we use the MPE decoded barcodes for this step
        self.mpe_decoded_barcode = mpe_decoded_barcode
        # if not self.decoded_barcode.is_valid:
        #     self.decoded_barcode = mpe_decoded_barcode

        self.barcode_ocr = impb_reconstruction.barcode_ocr
        self.impb_detection_conf = self.get_detection_confidence()

        self.fraud_metrics = {'decoded_impb_barcode': self.decoded_barcode.get_barcode_attributes(),
                              'OCR_impb_barcode': self.barcode_ocr.get_barcode_attributes(),
                              'yolo_conf': self.impb_detection_conf,
                              'impb_barcode': {}
                              }

    def scan_label_for_fraud(self):
        if DETECT_IMPB_HR_MISMATCH:
            if self.barcode_ocr.is_valid_barcode and self.decoded_barcode.is_valid_barcode:
                self.compute_fraud_mismatch('impb_barcode', self.barcode_ocr.barcode,
                                            self.decoded_barcode.barcode, 'mismatch_hr_impb',
                                            max_dist_allowed=MAX_DIST_IMPB)

        # Once we have checked all of the barcodes on the package for fraud, update the Fraud result
        # It is only true fraud if ALL of the comparisons were deemed fraudulent. If there is atleast one matching
        # barcode then it is NOt fraudulent and the result of a double scan
        if not self.is_fraud:
            # the case where we had no results to compare
            self.is_fraud = None
        else:
            # the case where we were able to make comparisons
            # ALL of the detections must be a mismatch for this to be Fraudulent, otherwise it is a double scan pkg
            if False in self.is_fraud:
                self.is_fraud = False
            else:
                self.is_fraud = True

    def compute_fraud_mismatch(self, fraud_metrics_key, fraud_feature_img, fraud_feature_extracted, mismatch_key,
                               max_dist_allowed):

        if None in [fraud_feature_extracted, fraud_feature_img]:
            self.fraud_metrics[fraud_metrics_key]['fraud_logic_executed'] = False
            self.fraud_metrics[fraud_metrics_key]['l_distance_computed'] = None
        else:
            self.fraud_metrics[fraud_metrics_key]['fraud_logic_executed'] = True

            l_distance_computed = distance(fraud_feature_img, fraud_feature_extracted)
            self.fraud_metrics[fraud_metrics_key]['l_distance_computed'] = l_distance_computed

            if l_distance_computed > max_dist_allowed:
                # a 'mismatching' barcode
                self.is_fraud.append(True)
                self.fraud_type.append(mismatch_key)
                self.fraud_metrics[fraud_metrics_key]['fraud_confidence'] = np.average(
                    [l_distance_computed / len(fraud_feature_img),
                     self.fraud_metrics['yolo_conf']],
                    weights=[.90, .10])
            else:
                # a 'matching' barcode
                self.is_fraud.append(False)

    def describe_fraud_metrics(self):
        return self.fraud_metrics


# TODO: find a more suitable location for this, maybe a reverse image search package?
def compute_feature_fromcv2(img, algorithm=ecips_config.ECIPS_REVERSE_IMAGE_ALGORITHM):
    """
    This Function calculates key points and descriptors based on the algorithms selected
    Supported Algorithms are orb, sift and pysift


    Parameters:
    img (cv2.imread()): an img created by OpenCV imread Function
    algorithm (str):  orb, sift or pysift to determine how to calculate keypoints and descriptors

    Returns:
    keypoints: Keypoint Values
    descriptors: [nxm] array

    """

    if algorithm == "orb":
        orb = cv2.ORB_create(nfeatures=ecips_config.ECIPS_REVERSE_IMAGE_NFEATURES)
        keypoints, descriptors = compute_feature_orb(img, orb)

    elif algorithm == "sift":
        sift = cv2.xfeatures2d.SIFT_create(
            nfeatures=ecips_config.ECIPS_REVERSE_IMAGE_NFEATURES,
            nOctaveLayers=ecips_config.ECIPS_REVERSE_IMAGE_SIFT_OCTAVES,
            contrastThreshold=ecips_config.ECIPS_REVERSE_IMAGE_SIFT_CONTRASTTHRESH,
            edgeThreshold=ecips_config.ECIPS_REVERSE_IMAGE_SIFT_EDGETHRESH,
            sigma=ecips_config.ECIPS_REVERSE_IMAGE_SIFT_SIGMA,
        )
        keypoints, descriptors = sift.detectAndCompute(img.astype("uint8"), None)

    elif algorithm == "pysift":
        import cudasift

        cu_data = cudasift.PySiftData(ecips_config.ECIPS_REVERSE_IMAGE_NFEATURES)
        cudasift.ExtractKeypoints(
            img,
            cu_data,
            ecips_config.ECIPS_REVERSE_IMAGE_SIFT_OCTAVES,
            ecips_config.ECIPS_REVERSE_IMAGE_SIFT_SIGMA,
            ecips_config.ECIPS_REVERSE_IMAGE_SIFT_EDGETHRESH,
        )

        keypoints, descriptors = cu_data.to_data_frame()
        descriptors = descriptors[~np.isclose(descriptors.sum(axis=1), 11.313706)]
        descriptors, index = np.unique(descriptors, axis=0, return_index=True)
        keypoints = keypoints.loc[index]
        cu_data.__deallocate__()

    return keypoints, descriptors


def compute_feature_orb(
        img, orb=cv2.ORB_create(nfeatures=ecips_config.REVERSE_IMAGE_SEARCH_FEATURE_SIZE)
):
    """
    This Function  uses orb to calculate key points and descriptors
    ORB is an open  source computer vision algorithm similar to sift with higher speed

    """

    keypoints_orb, descriptors = orb.detectAndCompute(img, None)

    return keypoints_orb, descriptors
