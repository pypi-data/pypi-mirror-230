# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#  * Neither the name of NVIDIA CORPORATION nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS ``AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT OWNER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Modified by Emma Garvey on 8/26/2022

import json
import os
import re

import easyocr
import numpy as np
import torch
import triton_python_backend_utils as pb_utils
from pyzbar.pyzbar import decode, ZBarSymbol

# triton_python_backend_utils is available in every Triton Python model. You
# need to use this module to create inference requests and responses. It also
# contains some utility functions for extracting information from model_config
# and converting Triton input/output types to numpy types.

IMPB_OCR_CONFIDENCE = float(os.getenv("IMPB_OCR_CONFIDENCE", default=0.3))


def get_paragraph(raw_result, x_ths=1, y_ths=0.5, mode='ltr'):
    # create basic attributes
    box_group = []
    for box in raw_result:
        certainty = box[2]
        if certainty > IMPB_OCR_CONFIDENCE:
            all_x = [int(coord[0]) for coord in box[0]]
            all_y = [int(coord[1]) for coord in box[0]]
            min_x = min(all_x)
            max_x = max(all_x)
            min_y = min(all_y)
            max_y = max(all_y)
            height = max_y - min_y
            # last element indicates group
            box_group.append([box[1], min_x, max_x, min_y, max_y, height, 0.5 * (min_y + max_y), 0])
    # cluster boxes into paragraph
    current_group = 1
    while len([box for box in box_group if box[7] == 0]) > 0:
        box_group0 = [box for box in box_group if box[7] == 0]  # group0 = non-group
        # new group
        if len([box for box in box_group if box[7] == current_group]) == 0:
            box_group0[0][7] = current_group  # assign first box to form new group
        # try to add group
        else:
            current_box_group = [box for box in box_group if box[7] == current_group]
            mean_height = np.mean([box[5] for box in current_box_group])
            min_gx = min([box[1] for box in current_box_group]) - x_ths * mean_height
            max_gx = max([box[2] for box in current_box_group]) + x_ths * mean_height
            min_gy = min([box[3] for box in current_box_group]) - y_ths * mean_height
            max_gy = max([box[4] for box in current_box_group]) + y_ths * mean_height
            add_box = False
            for box in box_group0:
                same_horizontal_level = (min_gx <= box[1] <= max_gx) or (min_gx <= box[2] <= max_gx)
                same_vertical_level = (min_gy <= box[3] <= max_gy) or (min_gy <= box[4] <= max_gy)
                if same_horizontal_level and same_vertical_level:
                    box[7] = current_group
                    add_box = True
                    break
            # cannot add more box, go to next group
            if not add_box:
                current_group += 1
    # arrage order in paragraph
    result = []
    for i in set(box[7] for box in box_group):
        current_box_group = [box for box in box_group if box[7] == i]
        mean_height = np.mean([box[5] for box in current_box_group])
        min_gx = min([box[1] for box in current_box_group])
        max_gx = max([box[2] for box in current_box_group])
        min_gy = min([box[3] for box in current_box_group])
        max_gy = max([box[4] for box in current_box_group])

        text = ''
        while len(current_box_group) > 0:
            highest = min([box[6] for box in current_box_group])
            candidates = [box for box in current_box_group if box[6] < highest + 0.4 * mean_height]
            # get the far left
            if mode == 'ltr':
                most_left = min([box[1] for box in candidates])
                for box in candidates:
                    if box[1] == most_left:
                        best_box = box
            elif mode == 'rtl':
                most_right = max([box[2] for box in candidates])
                for box in candidates:
                    if box[2] == most_right:
                        best_box = box
            text += ' ' + best_box[0]
            current_box_group.remove(best_box)

        result.append([[[min_gx, min_gy], [max_gx, min_gy], [max_gx, max_gy], [min_gx, max_gy]], text[1:]])

    return result


def is_valid_s10(text):
    try:
        first_2chars = text[:2]
        last_2chars = text[-2:]
        middle_digits = text[2:-2]
    except IndexError:
        return False
    return (first_2chars.isalpha() or last_2chars.isalpha()) and middle_digits.isdigit() and len(text) > 10


def is_valid_domestic(text):
    try:
        first_digit = text[0]
    except IndexError:
        return False
    return first_digit == '9' and len(text) > 18


def postprocess_barcode_ocr(ocr_result, barcode_type):
    barcode_ocr = None
    if ocr_result is not None:

        ocr_result_domestic = get_paragraph(ocr_result)

        for item in ocr_result_domestic:
            text = item[1]

            if barcode_type == 'impb':
                is_valid_barcode = is_valid_domestic(text)
            else:  # 's10':
                is_valid_barcode = is_valid_s10(text)

            if is_valid_barcode:
                barcode_ocr = re.sub(r'[\W_]+', '', text)
                break

    return barcode_ocr


class TritonPythonModel:
    """Your Python model must use the same class name. Every Python model
    that is created must have "TritonPythonModel" as the class name.
    """

    def initialize(self, args):
        """`initialize` is called only once when the model is being loaded.
        Implementing `initialize` function is optional. This function allows
        the model to intialize any state associated with this model.

        Parameters
        ----------
        args : dict
          Both keys and values are strings. The dictionary keys and values are:
          * model_config: A JSON string containing the model configuration
          * model_instance_kind: A string containing model instance kind
          * model_instance_device_id: A string containing model instance device ID
          * model_repository: Model repository path
          * model_version: Model version
          * model_name: Model name
        """

        # You must parse model_config. JSON string is not parsed here
        self.model_config = model_config = json.loads(args['model_config'])

        # Get configurations
        shipping_label_ocr_config = pb_utils.get_output_config_by_name(
            model_config, "shipping_label_OCR")

        # Convert Triton types to numpy types
        self.shipping_label_ocr_dtype = pb_utils.triton_string_to_numpy(
            shipping_label_ocr_config['data_type'])

        # set confidence threshold
        self.detection_confidence = json.loads(os.getenv("SHIPPING_LABEL_MODEL_SCORE_THRES",
                                                         default='''
                                                                 {"0": "0.65",
                                                                 "1": "0.65",
                                                                 "2": "0.65",
                                                                 "3": "0.65",
                                                                 "4": "0.65",
                                                                 "5": "0.65",
                                                                 "6": "0.65",
                                                                 "7": "0.65",
                                                                 "8": "0.65",
                                                                 "9": "0.65",
                                                                 "10": "0.4",
                                                                 "11": "0.4",
                                                                 "12": "0.64",
                                                                 "13": "0.4",
                                                                 "14": "0.4",
                                                                 "15": "0.4",
                                                                 "16": "0.6",
                                                                 "17": "0.55",
                                                                 "18": "0.4",
                                                                 "19": "0.4",
                                                                 "20": "0.65",
                                                                 "21": "0.90"
                                                                 }
                                                                 '''
                                                         ))
        # Convert json string format requirements to {int: float}
        self.detection_confidence = {int(class_id): float(self.detection_confidence[class_id])
                                     for class_id in self.detection_confidence}

        # define class names
        self.class_ids = json.loads(os.getenv("SHIPPING_LABEL_MODEL_CLASSES",
                                              default='''
                                              {"0": "background",
                                              "1": "s10",
                                              "2": "impb",
                                              "3": "address-block",
                                              "4": "pvi",
                                              "5": "first-class",
                                              "6": "priority",
                                              "7": "ibi",
                                              "8": "imb",
                                              "9": "address-block-handwritten",
                                              "10": "permit-imprint",
                                              "11": "Lithium_UN_Label",
                                              "12": "No_Fly",
                                              "13": "Finger_Large",
                                              "14": "Finger_Small",
                                              "15": "Cargo_Air_Only",
                                              "16": "hazmat",
                                              "17": "express",
                                              "18": "fcm",
                                              "19": "Cremated_Remains",
                                              "20": "stamp",
                                              "21": "ground-advantage"
                                              }
                                              '''
                                              ))

        # Convert the json string format to ints
        self.class_ids = {int(class_id): self.class_ids[class_id] for class_id in self.class_ids}
        self.labels_to_extract = json.loads(os.getenv("SHIPPING_LABEL_MODEL_LABELS_TO_CROP",
                                                      default="[5, 7, 2, 6, 10, 1, 17, 16, 18, 21]"))
        self.mail_class_letter_classes = json.loads(os.getenv("SHIPPING_LABEL_MODEL_MAILCLASSLETTER_CLASSES",
                                                              default="[5, 6, 16, 17, 18, 21]"))
        self.MCB_LABEL_ID = json.loads(os.getenv("SHIPPING_LABEL_MODEL_MCB_CLASS_ID",
                                                 default="99"))

        # Update the class_id dictionary with the MCB values
        self.class_ids[int(self.MCB_LABEL_ID)] = "mail_class_banner"

        # Initialize the easy ocr reader
        if torch.cuda.is_available():
            # need to run only once to load model into memory
            self.reader = easyocr.Reader(["en"], model_storage_directory="/easyocr",
                                         recog_network='latin_g2', download_enabled=False)
        else:
            self.reader = None

        # Identify relevant barcode decoder symbology:
        self.USPS_SYMBOLOGY = [ZBarSymbol.CODE128, ZBarSymbol.CODE39]

        # set default values if not found
        self.cropped_labels = None
        self.cropped_label_classes = None
        self.has_orientation = None

        # Flag to OCR the letter indicator:
        self.OCR_LETTER_INDICATOR = json.loads(os.getenv("OCR_LETTER_INDICATOR", default='true').lower())

    def crop_label_from_package(self, input_list):

        inference_request = pb_utils.InferenceRequest(
            model_name='ensemble_model_crop_label',
            requested_output_names=['cropped_labels', 'classes_out', 'orientation_out'],
            inputs=input_list,
            preferred_memory=pb_utils.PreferredMemory(pb_utils.TRITONSERVER_MEMORY_CPU))

        inference_response = inference_request.exec()

        if inference_response.has_error():
            raise pb_utils.TritonModelException(inference_response.error().message())
        else:
            # Extract the output tensors from the inference response.
            cropped_labels = pb_utils.get_output_tensor_by_name(inference_response, 'cropped_labels').as_numpy()
            cropped_label_classes = pb_utils.get_output_tensor_by_name(inference_response, 'classes_out').as_numpy()
            has_orientation = pb_utils.get_output_tensor_by_name(inference_response, 'orientation_out').as_numpy()

        return cropped_labels, cropped_label_classes, bool(has_orientation)

    def perform_label_OCR(self):
        """

        """
        ocr_result_dict = {"IBI_date": None,
                           "IBI_serial_number": None,
                           "IBI_mail_class": None,
                           "barcode_ocr": [],
                           "barcode_decode": [],
                           "barcodes": [],
                           "permit_imprint": None,
                           "mail_class_banner": None,
                           "mail_class_letter": None,
                           "mail_class_letter_ocr": None
                           }

        canvas_size = 400
        label_rotation_info = None if self.has_orientation else [180]
        for cropped_image, label_class in zip(self.cropped_labels, self.cropped_label_classes):
            try:
                display_nm = self.class_ids[int(label_class)]
            except KeyError:
                # Skip this label (255)
                continue
            cropped_image = cropped_image[0]
            if display_nm == 'impb' or display_nm == 's10':
                # OCR and Pyzbar
                barcode_decode = self.pyzbar(cropped_image)
                if barcode_decode is not [] and barcode_decode is not None:
                    # Remove any ' or " from the string
                    barcode_decode = barcode_decode.replace("'", "").replace('"', '')
                else:
                    barcode_decode = None

                # We will perform OCR on the IMPB even if decoded
                if display_nm == 'impb':
                    ocr_result = self.reader.readtext(cropped_image,
                                                      allowlist='0123456789',
                                                      width_ths=1.0,
                                                      canvas_size=canvas_size,
                                                      rotation_info=label_rotation_info)
                    ocr_result = postprocess_barcode_ocr(ocr_result, "impb")

                    if ocr_result is None:
                        ocr_result = self.reader.readtext(cropped_image,
                                                          allowlist='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                                                          width_ths=1.0,
                                                          canvas_size=canvas_size,
                                                          rotation_info=label_rotation_info)
                        ocr_result = postprocess_barcode_ocr(ocr_result, "s10")

                elif display_nm == 's10':
                    ocr_result = self.reader.readtext(cropped_image,
                                                      allowlist='0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ',
                                                      width_ths=1.0,
                                                      canvas_size=canvas_size,
                                                      rotation_info=label_rotation_info)
                    ocr_result = postprocess_barcode_ocr(ocr_result, "s10")

                ocr_result_dict["barcode_decode"].append(barcode_decode)
                ocr_result_dict["barcode_ocr"].append(ocr_result)
                ocr_result_dict["barcodes"].append([barcode_decode, ocr_result])

            if int(label_class) in self.mail_class_letter_classes:
                ocr_result_dict["mail_class_letter"] = display_nm

                if self.OCR_LETTER_INDICATOR:
                    print("OCR letter indicator flag is true", flush=True)
                    ocr_result_dict["mail_class_letter_ocr"] = self.reader.readtext(cropped_image,
                                                                                    allowlist='FPEHG',
                                                                                    width_ths=400,
                                                                                    height_ths=400,
                                                                                    text_threshold=0.8,
                                                                                    canvas_size=100,
                                                                                    min_size=400)
            if display_nm == 'mail_class_banner':
                ocr_result_dict["mail_class_banner"] = self.reader.readtext(cropped_image,
                                                                            allowlist="ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                                                                                      "abcdefghijklmnopqrstuvwxyz123-",
                                                                            canvas_size=300,
                                                                            width_ths=1.0,
                                                                            rotation_info=label_rotation_info)

            if display_nm == 'permit-imprint':
                # OCR and classify
                ocr_result_dict["permit_imprint"] = self.reader.readtext(cropped_image,
                                                                         decoder='beamsearch',
                                                                         contrast_ths=0,
                                                                         height_ths=0.8,
                                                                         width_ths=10,
                                                                         allowlist="abcdefghijklmnopqrstuvwxyz -"
                                                                                   "1234567890.",
                                                                         slope_ths=0.4,
                                                                         batch_size=20,
                                                                         canvas_size=canvas_size,
                                                                         rotation_info=label_rotation_info)

            if display_nm == 'ibi':
                # OCR and extract date and serial num
                ibi_ocr = self.reader.readtext(cropped_image,
                                               decoder='beamsearch',
                                               contrast_ths=0,
                                               height_ths=0.8,
                                               width_ths=1,
                                               blocklist="$!;,%^@~+_=[]¬()#<>'"+'"',
                                               slope_ths=0.4,
                                               batch_size=20,
                                               canvas_size=canvas_size,
                                               rotation_info=label_rotation_info)
                ocr_result_dict["IBI_date"] = ibi_ocr
                ocr_result_dict["IBI_serial_number"] = ibi_ocr

        return ocr_result_dict

    def pyzbar(self, image):
        """The pyzbar function takes an image, tries to decode it
        if the initial decode was not successful, we apply image processing
        and attempt to decode it once more. If the barcode is unable to be decoded,
        returns None

        Args:
            image (np.array): the cropped barcode image to decode

        Returns:
            str: the decoded barcode (None if not able to decode)
        """

        barcode = decode(image, symbols=self.USPS_SYMBOLOGY)

        if not barcode:
            return None

        barcode_data = barcode[0].data.decode()

        if 'x1d' in barcode_data:
            barcode_data = barcode_data.split('\x1d')[-1]

        return barcode_data

    def execute(self, requests):
        """`execute` MUST be implemented in every Python model. `execute`
        function receives a list of pb_utils.InferenceRequest as the only
        argument. This function is called when an inference request is made
        for this model. Depending on the batching configuration (e.g. Dynamic
        Batching) used, `requests` may contain multiple requests. Every
        Python model, must create one pb_utils.InferenceResponse for every
        pb_utils.InferenceRequest in `requests`. If there is an error, you can
        set the error argument when creating a pb_utils.InferenceResponse

        Parameters
        ----------
        requests : list
          A list of pb_utils.InferenceRequest

        Returns
        -------
        list
          A list of pb_utils.InferenceResponse. The length of this list must
          be the same as `requests`
        """

        responses = []

        # Every Python backend must iterate over everyone of the requests
        # and create a pb_utils.InferenceResponse for each of them.
        for request in requests:
            # Get INPUT0
            in_0 = pb_utils.get_input_tensor_by_name(request, "img_bytestring")
            in_1 = pb_utils.get_input_tensor_by_name(request, "scores")
            scores = in_1.as_numpy()[0].squeeze()
            in_2 = pb_utils.get_input_tensor_by_name(request, "boxes")
            boxes = in_2.as_numpy()[0].squeeze()
            in_3 = pb_utils.get_input_tensor_by_name(request, "classes")
            classes = in_3.as_numpy()[0].squeeze()

            labels_to_OCR = False

            for box, cls, score in zip(boxes, classes, scores):

                confidence = float(score)
                class_id = int(cls)

                if confidence > self.detection_confidence[class_id]:
                    class_id = int(cls)
                    if class_id in self.labels_to_extract:
                        # extract all relevant labels
                        labels_to_OCR = True
                        self.cropped_labels, self.cropped_label_classes,\
                            self.has_orientation = self.crop_label_from_package([in_0, in_1, in_2, in_3])
                        # Exit the for loop, OCR extracted labels
                        break

            if labels_to_OCR:
                ocr_results = self.perform_label_OCR()
            else:
                ocr_results = {"IBI_date": None,
                               "IBI_serial_number": None,
                               "IBI_mail_class": None,
                               "barcode_ocr": [],
                               "barcode_decode": [],
                               "barcodes": [],
                               "permit_imprint": None,
                               "mail_class_banner": None,
                               "mail_class_letter": None,
                               "mail_class_letter_ocr": None
                               }

            out_json = pb_utils.Tensor("shipping_label_OCR",
                                       np.array(ocr_results).astype(self.shipping_label_ocr_dtype))

            inference_response = pb_utils.InferenceResponse(
                output_tensors=[out_json])
            responses.append(inference_response)

        # Release any stored memory:
        torch.cuda.empty_cache()
        return responses

    def finalize(self):
        """`finalize` is called only once when the model is being unloaded.
        Implementing `finalize` function is OPTIONAL. This function allows
        the model to perform any necessary clean ups before exit.
        """
        print('Cleaning up...')
