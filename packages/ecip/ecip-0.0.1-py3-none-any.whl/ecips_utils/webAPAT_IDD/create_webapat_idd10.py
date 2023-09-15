import logging
import pathlib
import numpy as np

import ecips_utils.packageObject.packageclass as pc
import ecips_utils.fraudDetection.fraud_detection as fraud
import ecips_utils.anomalyDetection.anomaly_detection as anomaly
from celery import Celery
from ecips_utils import ecips_config

IP = ecips_config.ECIPS_DEVICE_MAPPING["ip"]

# Load Celery App
app = Celery(
    "tasks_comms",
    broker=ecips_config.CELERY_BROKER,
    backend=ecips_config.CELERY_BACKEND,
)

webapat_secret_key = ecips_config.ECIPS_WEBAPAT_SECRET_KEY
webapat_url = ecips_config.ECIPS_WEBAPAT_URL


def generate_ImageObject_from_json(img_filepath):
    Image = pc.ImageObject(img_filepath, load_from_json=True)

    if not Image.json_written:
        logging.info(f"Unable to load image object from json for image: {img_filepath}, "
                     f"because the json was not"
                     f"written to the disk")
        return None

    return Image


def generate_HazmatObject(ImageObject):
    Hazmat = pc.HazmatClass(ImageObject)
    return Hazmat


def generate_ReconstructedBarcodeObject(ImageObject):
    Barcode = pc.ReconstructedBarcodeClass(ImageObject)
    return Barcode


def generate_BarcodeObject(ImageObject):
    Barcode = pc.BarcodeClass(ImageObject)
    return Barcode


def generate_FraudDetectorObject(ImageObject):
    ibi_barcode = generate_IBIBarcodeObject(ImageObject)
    mail_class = generate_MailClassObject(ImageObject)
    permit_imprint = generate_PermitImprintObject(ImageObject)
    impb_barcode = generate_IMPBBarcodeObject(ImageObject)

    fraud_detector = fraud.FraudDetectionClass(ImageObject, ibi_barcode, mail_class, permit_imprint, impb_barcode)
    return fraud_detector


def generate_AnomalyDetectorObject(ImageObject):
    mail_class = generate_MailClassObject(ImageObject, look_for_fraud=False, look_for_anomaly=True)
    permit_imprint = generate_PermitImprintObject(ImageObject)

    anomaly_detector = anomaly.AnomalyDetectionClass(ImageObject, mail_class, permit_imprint)
    return anomaly_detector


def generate_IBIBarcodeObject(ImageObject):
    ibi_barcode = pc.IBIClass(ImageObject)

    return ibi_barcode


def generate_IMPBBarcodeObject(ImageObject):
    impb_barcode = pc.IMPBBarcodeClass(ImageObject)

    return impb_barcode


def generate_MailClassObject(ImageObject, look_for_fraud=True, look_for_anomaly=False):
    mail_class = pc.MailMarkingsClass(ImageObject)

    if look_for_fraud:
        mail_class.generate_fraud_results()

    if look_for_anomaly:
        mail_class.generate_anomaly_results()

    return mail_class


def generate_PermitImprintObject(ImageObject):
    permit_imprint = pc.PermitImprintClass(ImageObject)

    return permit_imprint


def calculate_webapat_img_base(
        img_filepath,
        mpeDeviceMapping=ecips_config.get_mpe_mappings(),
):
    """
    This function calculates package details from the MPE path to include day


    Parameters:
    item (PackageImage): an img created by OpenCV imread Function

    Returns:
    results_dict = {"filepath": webapat_relpath,
                    "ecip_ip": IP,
                    "mpe_device_ip": mpe_ip,
                    }

    """
    logging.debug(f"Calculating package details for MPE path {img_filepath} to include day.")
    filepath = pathlib.Path(img_filepath)
    mpeDevice = list(filepath.parents)[-3].stem
    mpe_devicepath = list(filepath.parents)[-3]
    webapat_relpath = str(filepath.relative_to(mpe_devicepath))
    # Set the missing device flag to False initially
    missing_device_flag = False

    try:
        mpe_ip = mpeDeviceMapping[mpeDevice]
    except KeyError:
        mpe_ip = "0.0.0.0"
        logging.warning(f"KeyError for {filepath} on {mpeDevice}. mpe_ip set to 0.0.0.0 \n"
                        f"The mpe device mappings are as follows: {mpeDeviceMapping}")
        missing_device_flag = True

    results_dict = {
        "filepath": webapat_relpath,
        "ecip_ip": IP,
        "mpe_device_ip": mpe_ip,
    }
    logging.info(f"Results dict for {filepath}: {results_dict}")
    return results_dict, missing_device_flag


def create_img_list():
    # Generates list of image dictionaries for webapat message.
    pass


def create_hazmat_dict(HazmatObject):
    num_hazmat_labels = len(HazmatObject.detection_scores)
    haz_dict_list = []

    if ecips_config.ECIPS_INFERENCE_SERVER_USE_HAZMAT_YOLO:
        detections = np.array(HazmatObject.detection_polygons).reshape((num_hazmat_labels, 4, 2))
        for i in range(num_hazmat_labels):
            polygon = detections[i]
            x1, y1, x2, y2 = find_hazmat_xy(polygon)
            hazmat_dict = {"score": float(HazmatObject.detection_scores[i]),
                           "class": float(HazmatObject.detection_classes[i]),
                           "x1": float(x1),
                           "y1": float(y1),
                           "x2": float(x2),
                           "y2": float(y2),
                           "model_version": HazmatObject.model_version}
            try:
                hazmat_dict["description"] = next(item["name"] for item in HazmatObject.classnum_to_classstring
                                                  if item["id"] == (HazmatObject.detection_classes[i] + 1))
            except StopIteration:
                hazmat_dict["description"] = "Class not found"
            haz_dict_list.append(hazmat_dict)
    else:  # Using the Retinanet model
        detections = np.array(HazmatObject.detection_polygons).reshape((num_hazmat_labels, 4))
        for i in range(num_hazmat_labels):
            x1, y1, x2, y2 = detections[i]
            hazmat_dict = {"score": float(HazmatObject.detection_scores[i]),
                           "class": float(HazmatObject.detection_classes[i]),
                           "x1": float(x1),
                           "y1": float(y1),
                           "x2": float(x2),
                           "y2": float(y2),
                           "model_version": HazmatObject.model_version}
            try:
                hazmat_dict["description"] = next(item["name"] for item in HazmatObject.classnum_to_classstring
                                                  if item["id"] == (HazmatObject.detection_classes[i] + 1))
            except StopIteration:
                hazmat_dict["description"] = "Class not found"
            haz_dict_list.append(hazmat_dict)
    return num_hazmat_labels, haz_dict_list


def find_hazmat_xy(hazmat_polygon):
    x_list = []
    y_list = []
    for i in hazmat_polygon:
        x_list.append(i[0])
        y_list.append(i[1])
    x1 = min(x_list)
    y1 = min(y_list)
    x2 = max(x_list)
    y2 = max(y_list)
    return x1, y1, x2, y2


def create_barcode_dict(BarcodeObject):
    # Currently setting risk score to default 1.
    barcode_dict = {"risk_score": 1.0,
                    "barcode": int(BarcodeObject.detected_digits[0]),
                    "barcode_type": list(BarcodeObject.detection_classes)}
    return barcode_dict


def create_reconstructed_barcode_dict(ReconstructedBarcodeObject):
    if ReconstructedBarcodeObject is not None:
        # Currently setting risk score to default 1.
        barcode_dict = {"risk_score": 1.0,
                        "barcode": str(ReconstructedBarcodeObject.barcode),
                        "barcode_type": str(ReconstructedBarcodeObject.barcode_class)}
    else:
        barcode_dict = {"risk_score": 1.0,
                        "barcode": str(None),
                        "barcode_type": str(None)}
    return barcode_dict


def create_fraud_barcode_dict(ImageObject):
    # Currently setting risk score to default 1.
    barcode_dict = {"risk_score": 1.0,
                    "barcode": str(ImageObject.impb_barcode_results.barcode),
                    "barcode_type": "UCC/EAN 128" if ImageObject.impb_barcode_results.barcode else str(None)}
    return barcode_dict


def create_barcode_list(ImageObject):
    # Example of image with multiple valid barcodes?
    # Currently only identifying one barcode per image.
    pass


def generate_webapat_hazmat_message(image_filepath):
    HazmatImage = generate_ImageObject_from_json(image_filepath)

    if HazmatImage is None:
        raise FileNotFoundError(f"The JSON for image {image_filepath}, was not written. Unable to construct"
                                f"Hazmat Results to send to WebAPAT")

    # The image may be just one of several views of the package.  In order to
    # reconstruct the barcode accurately, we need to look at all package sides.
    Package = pc.PackageObject(Image=HazmatImage)

    Hazmat = generate_HazmatObject(HazmatImage)
    # As of v1.6.8, we will reconstruct all barcode on the package
    barcode_list = Package.get_reconstructed_barcodes(get_first=ecips_config.ECIPS_RECONSTRUCT_SINGLE_IMPB_BARCODE)

    results_dict = {"secretkey": webapat_secret_key,
                    "action": "hz_orig_list_from_ecip"
                    }
    image_dict, missing_device = calculate_webapat_img_base(HazmatImage.img_filepath)

    # Setting number of barcodes as 1 for now until we can generate barcode list
    image_dict["num_barcodes"] = len(barcode_list)
    barcode_dict_list = []
    for Barcode in barcode_list:
        barcode_dict_list.append(create_reconstructed_barcode_dict(Barcode))
    image_dict['barcodes'] = barcode_dict_list

    # Setting number of hazmat labels as 1 for now until we can generate hazmat list
    num_hazmat_labels, hazmat_dict_list = create_hazmat_dict(Hazmat)
    image_dict['num_hazmat_labels'] = num_hazmat_labels
    image_dict["hazmat_labels"] = hazmat_dict_list

    results_dict["images"] = [image_dict]
    return results_dict, missing_device


def generate_webapat_bcr_message(Image):
    # Barcode = generate_ReconstructedBarcodeObject(Image)
    Package = pc.PackageObject(Image=Image, single_view=True)

    # As of v1.6.8, we will reconstruct all barcode on the package
    barcode_list = Package.get_reconstructed_barcodes(get_first=ecips_config.ECIPS_RECONSTRUCT_SINGLE_IMPB_BARCODE)
    image_dict, missing_device = calculate_webapat_img_base(Image.img_filepath)
    image_dict["num_barcodes"] = len(barcode_list)

    barcode_dict_list = []
    barcode_successfully_reconstructed = False
    for Barcode in barcode_list:
        if Barcode.send_bcr_result:
            barcode_dict_list.append(create_reconstructed_barcode_dict(Barcode))
            barcode_successfully_reconstructed = True
    image_dict['barcodes'] = barcode_dict_list

    if barcode_successfully_reconstructed:
        return image_dict, barcode_successfully_reconstructed
    else:
        return {}, barcode_successfully_reconstructed


def generate_webapat_fraud_message(Image):

    fraud_result = Image.fraud_results
    is_fraudulent = fraud_result.fraud_found()

    if is_fraudulent:

        image_dict, missing_device = calculate_webapat_img_base(Image.img_filepath)
        fraud_dict = fraud_result.get_fraud_types_dict()
        # Setting number of barcodes as 1 for now until we can generate barcode list
        image_dict["fraud_type"] = fraud_result.get_fraud_type()
        image_dict["num_barcodes"] = 1
        barcode_dict = create_fraud_barcode_dict(Image)
        image_dict['barcodes'] = [barcode_dict]
        image_dict['num_fraud_types'] = len(fraud_dict)
        image_dict['fraud_types'] = fraud_dict
        image_dict['volume'] = Image.package_volume

        return image_dict
    else:
        # fraud was not detected, do not send result
        return {}


def generate_webapat_anomaly_message(Image):
    anomaly_results = Image.anomaly_results
    is_anomalous = anomaly_results.anomaly_found()

    if is_anomalous:

        image_dict, _ = calculate_webapat_img_base(Image.img_filepath)
        anomaly_dict = anomaly_results.get_anomaly_types_dict()

        # Setting number of barcodes as 1 for now until we can generate barcode list
        image_dict["anomaly_type"] = anomaly_results.get_anomaly_type()
        image_dict["num_barcodes"] = 1
        barcode_dict = create_fraud_barcode_dict(Image)
        image_dict['barcodes'] = [barcode_dict]
        image_dict['num_anomaly_types'] = len(anomaly_dict)
        image_dict['anomaly_types'] = anomaly_dict

        return image_dict
    else:
        # no anomalies detected, return empty dictionary
        return {}
