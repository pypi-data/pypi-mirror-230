import cv2
import numpy as np
import tritonclient.grpc as grpcclient
from PIL import Image


class ECIPsApplicationTritonModels:
    """
    The ECIPsApplicationTritonModels object loads an image and enables
    a user to grab inputs/outputs from each of the individual models in the
    triton ensemble

    Args:
        filename (str): the path to the image you'd like to test
        #TODO Update this to work with a list of files directory to many files
    """

    def __init__(self, filename=None, hostname='localhost:8001'):
        """ __init__ runs when we create a new instance of the BArcode Reconstruction object
        We take a filename a input and load the file as an image
        """

        self.image = None

        if filename is not None:
            self.load_img(filename)

        self.mean = np.array([0.485, 0.456, 0.406])
        self.std = np.array([0.229, 0.224, 0.225])

        self.hostname = hostname

    def load_img(self, filename):
        """ load_image takes a filepath, loads the image to a np.array and saves
        to the class variable self.image

        Args:
            filename (str): the path to the image file
        """
        image = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
        # print(image.shape)
        self.image = np.expand_dims(image, axis=0)

    def preprocess(self):
        """ preprocess grabs the inputs and outputs from the preprocess model
        from the barcode_digit_ensemble

        Returns:
            preprocessed_img (np.array): the preprocessed image scaled by value, ratios
            ratios (np.array): the ratio by which the image is scaled later in the
            ensemble model pipeline
        """
        with grpcclient.InferenceServerClient(self.hostname) as client:
            input_image = self.image[0, :, :]
            input_name = "INPUT0"
            dtype = "UINT8"
            input0 = grpcclient.InferInput(input_name, input_image.shape, dtype)
            input0.set_data_from_numpy(input_image)
            output0 = grpcclient.InferRequestedOutput("OUTPUT0")
            output1 = grpcclient.InferRequestedOutput("OUTPUT1")
            input_list = [input0]
            output_list = [output0, output1]
            response = client.infer(
                "preprocess", input_list, request_id=str("1"), outputs=output_list, client_timeout=5.0
            )
            preprocessed_img = response.as_numpy("OUTPUT0")
            ratios = response.as_numpy("OUTPUT1")
            return preprocessed_img, ratios

    def barcode(self, preprocessed_img):
        """ barcode grabs the inputs and outputs from the barcode model
            in the barcode_digit_ensemble

        Args:
            preprocessed_img (np.array): the preprocessed image that was shared by the
            preprocess model

        Returns:
            scores (np.array): confidence scores returned by barcode detection model
            boxes (np.array): bounding boxes that describe where a barcode is detected
            classes (np.array): classes returned from the barcode detection model. As of
            5/5/2022 the barcode model only detects one class
        """
        with grpcclient.InferenceServerClient(self.hostname) as client:
            input_name = "input_1"
            dtype = "FP32"
            input0 = grpcclient.InferInput(input_name, preprocessed_img.shape, dtype)
            input0.set_data_from_numpy(preprocessed_img)
            output0 = grpcclient.InferRequestedOutput("scores")
            output1 = grpcclient.InferRequestedOutput("boxes")
            output2 = grpcclient.InferRequestedOutput("classes")
            input_list = [input0]
            output_list = [output0, output1, output2]

            response = client.infer(
                "barcode", input_list, request_id=str("1"), outputs=output_list, client_timeout=5.0
            )

            scores = response.as_numpy("scores")
            boxes = response.as_numpy("boxes")
            classes = response.as_numpy("classes")
            return scores, boxes, classes

    def shipping_label_yolov5(self, preprocessed_img):
        """ shipping_label_yolov5 grabs the inputs and outputs from the shipping_label_yolo model
            in the
            in the

        Args:
            preprocessed_img (np.array): the preprocessed image

        Returns:
            #TBD

        """
        with grpcclient.InferenceServerClient(self.hostname) as client:
            input_name = "images"
            dtype = "FP32"
            input0 = grpcclient.InferInput(input_name, preprocessed_img.shape, dtype)
            input0.set_data_from_numpy(preprocessed_img)
            output0 = grpcclient.InferRequestedOutput("output")
            output1 = grpcclient.InferRequestedOutput("350")
            output2 = grpcclient.InferRequestedOutput("416")
            output3 = grpcclient.InferRequestedOutput("482")
            input_list = [input0]
            output_list = [output0, output1, output2, output3]

            response = client.infer(
                "shipping_label_yolov5", input_list, request_id=str("1"), outputs=output_list, client_timeout=5.0
            )

            output = response.as_numpy("output")
            output_350 = response.as_numpy("350")
            output_416 = response.as_numpy("416")
            output_482 = response.as_numpy("482")
            return output, output_350, output_416, output_482

    def shipping_label_yolov8(self, preprocessed_img):
        """ shipping_label_yolov8 grabs the inputs and outputs from the shipping_label_yolo model
            in the
            in the

        Args:
            preprocessed_img (np.array): the preprocessed image

        Returns:
            #TBD

        """
        with grpcclient.InferenceServerClient(self.hostname) as client:
            input_name = "images"
            dtype = "FP16"
            input0 = grpcclient.InferInput(input_name, preprocessed_img.shape, dtype)
            input0.set_data_from_numpy(preprocessed_img)
            output0 = grpcclient.InferRequestedOutput("output0")
            output1 = grpcclient.InferRequestedOutput("output1")
            input_list = [input0]
            output_list = [output0, output1]

            response = client.infer(
                "shipping_label_yolov8", input_list, request_id=str("1"), outputs=output_list, client_timeout=5.0
            )

            output_0 = response.as_numpy("output0")
            output_1 = response.as_numpy("output1")

            return output_0, output_1

    def hazmat_yolov8(self, preprocessed_img):
        """ hazmat_yolov8 grabs the inputs and outputs from the hazmat_yolov8 model

        Args:
            preprocessed_img (np.array): the preprocessed image from the hazmat preprocessing yolov8 model

        Returns:
            output (np.array): the unprocessed output form the yolov8 model

        """
        with grpcclient.InferenceServerClient(self.hostname) as client:
            input_name = "images"
            dtype = "FP16"
            input0 = grpcclient.InferInput(input_name, preprocessed_img.shape, dtype)
            input0.set_data_from_numpy(preprocessed_img)
            output0 = grpcclient.InferRequestedOutput("output0")
            input_list = [input0]
            output_list = [output0]

            response = client.infer(
                "hazmat_yolov8", input_list, request_id=str("1"), outputs=output_list, client_timeout=5.0
            )

            output = response.as_numpy("output0")
            return output

    def hazmat_yolov5(self, preprocessed_img):
        """ hazmat_yolov5 grabs the inputs and outputs from the hazmat_yolov5 model

        Args:
            preprocessed_img (np.array): the preprocessed image from the hazmat preprocessing yolov5 model

        Returns:
            output (np.array): the unprocessed output form the yolov5 model

        """
        with grpcclient.InferenceServerClient(self.hostname) as client:
            input_name = "images"
            dtype = "FP32"
            input0 = grpcclient.InferInput(input_name, preprocessed_img.shape, dtype)
            input0.set_data_from_numpy(preprocessed_img)
            output0 = grpcclient.InferRequestedOutput("output0")
            input_list = [input0]
            output_list = [output0]

            response = client.infer(
                "hazmat_yolov5", input_list, request_id=str("1"), outputs=output_list, client_timeout=5.0
            )

            output = response.as_numpy("output0")
            return output

    def preprocessing_yolo(self, filepath):
        """ preprocessing_yolo sends in a filepath to the preprocessing_yolo model and
        a dali model opens, preprocesses and returns the preprocessed image as well as the
        dimensions of the original image

        Args:
            filepath (str): the input filepath

        Returns:
            preprocessed_image (np.array): the preprocessed image (normalized, padded, resized)
            og_dims (np.array): the dimensions of the original input image

        """
        file_bytestring = filepath

        with grpcclient.InferenceServerClient(self.hostname) as client:
            input_name = "DALI_INPUT_0"
            dtype = "UINT8"
            input0 = grpcclient.InferInput(input_name, file_bytestring.shape, dtype)
            input0.set_data_from_numpy(file_bytestring)
            output0 = grpcclient.InferRequestedOutput("DALI_OUTPUT_0")
            output1 = grpcclient.InferRequestedOutput("DALI_OUTPUT_1")
            # output2 = grpcclient.InferRequestedOutput("DALI_OUTPUT_2")
            input_list = [input0]
            output_list = [output0, output1]

            response = client.infer(
                "dali_preprocessing_yolov8", input_list, request_id=str("1"), outputs=output_list, client_timeout=5.0
            )

            preprocessed_image = response.as_numpy("DALI_OUTPUT_0")
            og_dims = response.as_numpy("DALI_OUTPUT_1")
            return preprocessed_image, og_dims

    def postprocessing_yolo(self, yolo_input, og_dims, is_rotated):
        """ preprocessing_yolo sends in a filepath to the preprocessing_yolo model and
        a dali model opens, preprocesses and returns the preprocessed image as well as the
        dimensions of the original image

        Args:
            yolo_input (np.array): the output from the yolo path model

        Returns:
            scores (np.array): detections scores
            boxes (np.array): bounding boxes
            classes (np.array): the class id of the detections

        """
        with grpcclient.InferenceServerClient(self.hostname) as client:
            input0 = grpcclient.InferInput("yolo_input", yolo_input.shape, "FP32")
            input0.set_data_from_numpy(yolo_input)
            input1 = grpcclient.InferInput("og_dims", og_dims.shape, "INT32")
            input1.set_data_from_numpy(og_dims)
            input2 = grpcclient.InferInput("is_rotated", is_rotated.shape, "INT32")
            input2.set_data_from_numpy(is_rotated)
            output0 = grpcclient.InferRequestedOutput("scores")
            output1 = grpcclient.InferRequestedOutput("boxes")
            output2 = grpcclient.InferRequestedOutput("classes")
            input_list = [input0, input1, input2]
            output_list = [output0, output1, output2]

            response = client.infer(
                "postprocessing_yolov8", input_list, request_id=str("1"), outputs=output_list, client_timeout=5.0
            )

            scores = response.as_numpy("scores")[0]
            boxes = response.as_numpy("boxes")[0]
            classes = response.as_numpy("classes")[0]
            return scores, boxes, classes

    def dali_preprocessing(self, image_filepath):
        """
        dali preprocessing loads images for both the retina net and yolo models

        Args:
            image_filepath: The path to the image

        Returns:

        """
        # with open(image_filepath, 'rb') as f:
        #     file_bytestring = np.frombuffer(f.read(), dtype=np.uint8)
        #     file_bytestring = np.expand_dims(file_bytestring, axis=0)
        file_bytestring = image_filepath

        with grpcclient.InferenceServerClient(self.hostname) as client:

            input_name = "DALI_INPUT_0"
            dtype = "UINT8"
            input0 = grpcclient.InferInput(input_name, file_bytestring.shape, dtype)
            input0.set_data_from_numpy(file_bytestring)
            output0 = grpcclient.InferRequestedOutput("DALI_OUTPUT_0")
            output1 = grpcclient.InferRequestedOutput("DALI_OUTPUT_1")
            # output2 = grpcclient.InferRequestedOutput("DALI_OUTPUT_2")
            input_list = [input0]
            output_list = [output0, output1]
            response = client.infer(
                "dali_preprocessing", input_list, request_id=str("1"), outputs=output_list, client_timeout=5.0
            )
            image_retina = response.as_numpy("DALI_OUTPUT_0")
            # image_yolo = response.as_numpy("DALI_OUTPUT_1")
            og_dims = response.as_numpy("DALI_OUTPUT_1")

            return image_retina, og_dims

    def dali_preprocessing_yolov8(self, loaded_img):
        """
        dali preprocessing loads images for both the retina net and yolo models

        Args:
            loaded_img: the image which has been loaded as a file bytestring by the dali_load_img model

        Returns:
             shipping_label_image (np.array): The preprocessed image in a format compatible with the shipping label model
            hazmat_image (np.array): The preprocessed image in a format compatible with the hazmat model
            og_dims (np.array): The dimensions of the original image prior to pre-processing

        """

        with grpcclient.InferenceServerClient(self.hostname) as client:

            input_name = "DALI_INPUT_0"
            dtype = "UINT8"
            input0 = grpcclient.InferInput(input_name, loaded_img.shape, dtype)
            input0.set_data_from_numpy(loaded_img)
            output0 = grpcclient.InferRequestedOutput("DALI_OUTPUT_0")
            output1 = grpcclient.InferRequestedOutput("DALI_OUTPUT_1")
            output2 = grpcclient.InferRequestedOutput("DALI_OUTPUT_2")
            input_list = [input0]
            output_list = [output0, output1, output2]
            response = client.infer(
                "dali_preprocessing_yolov8", input_list, request_id=str("1"), outputs=output_list, client_timeout=5.0
            )
            shipping_label_image = response.as_numpy("DALI_OUTPUT_0")
            hazmat_image = response.as_numpy("DALI_OUTPUT_1")
            og_dims = response.as_numpy("DALI_OUTPUT_2")

            return shipping_label_image, hazmat_image, og_dims

    def dali_preprocessing_hazmat(self, image):
        """
        dali preprocessing loads images for both the retina net and yolo models

        Args:
            image_filepath: The path to the image

        Returns:

        """
        # with open(image_filepath, 'rb') as f:
        #     file_bytestring = np.frombuffer(f.read(), dtype=np.uint8)
        #     file_bytestring = np.expand_dims(file_bytestring, axis=0)
        # file_bytestring = 255 * np.array(Image.open(image_filepath)).astype(np.uint8)

        with grpcclient.InferenceServerClient(self.hostname) as client:

            input_name = "DALI_INPUT_0"
            dtype = "UINT8"
            input0 = grpcclient.InferInput(input_name, image.shape, dtype)
            input0.set_data_from_numpy(image)
            output0 = grpcclient.InferRequestedOutput("DALI_OUTPUT_0")
            output1 = grpcclient.InferRequestedOutput("DALI_OUTPUT_1")
            output2 = grpcclient.InferRequestedOutput("DALI_OUTPUT_2")
            input_list = [input0]
            output_list = [output0, output1, output2]
            response = client.infer(
                "dali_preprocessing_hazmat", input_list, request_id=str("1"), outputs=output_list, client_timeout=5.0
            )
            image = response.as_numpy("DALI_OUTPUT_0")
            og_dims = response.as_numpy("DALI_OUTPUT_1")
            is_rotated = response.as_numpy("DALI_OUTPUT_2")

            return image, og_dims, is_rotated

    def crop_barcode(self, ratios, scores, boxes, classes):
        """ crop_barcode grabs the inputs and outputs from the crop_barcode model
            in the barcode_digit_ensemble

        Args:
            ratios (np.array): the ratio by which the image is scaled later in the
            ensemble model pipeline
            scores (np.array): confidence scores returned by barcode detection model
            boxes (np.array): bounding boxes that describe where a barcode is detected
            classes (np.array): classes returned from the barcode detection model. As of
            5/5/2022 the barcode model only detects one class

        Returns:
            cropped_image (np.array): the image of only the barcode cropped from the original
            image

        """
        with grpcclient.InferenceServerClient(self.hostname) as client:
            # ratios = np.expand_dims(ratios, axis=0)

            input0 = grpcclient.InferInput("image_in", self.image.shape, "UINT8")
            input0.set_data_from_numpy(self.image)

            input1 = grpcclient.InferInput("ratios_in", ratios.shape, "FP32")
            input1.set_data_from_numpy(ratios)

            input2 = grpcclient.InferInput("scores_in", scores.shape, "FP32")
            input2.set_data_from_numpy(scores)

            input3 = grpcclient.InferInput("boxes_in", boxes.shape, "FP32")
            input3.set_data_from_numpy(boxes)

            input4 = grpcclient.InferInput("classes_in", classes.shape, "FP32")
            input4.set_data_from_numpy(classes)

            output0 = grpcclient.InferRequestedOutput("image_out")
            output1 = grpcclient.InferRequestedOutput("matrix_out")
            output2 = grpcclient.InferRequestedOutput("dims_out")

            input_list = [input0, input1, input2, input3, input4]
            output_list = [output0, output1, output2]

            response = client.infer(
                "crop_barcode", input_list, request_id=str("1"), outputs=output_list, client_timeout=5.0
            )

            image = response.as_numpy("image_out")
            matrix = response.as_numpy("matrix_out")
            dims = response.as_numpy("dims_out")
            return image, matrix, dims

    def dali_crop_gpu(self, image, matrix, dims, rotation):
        """ crop_barcode grabs the inputs and outputs from the crop_barcode model
            in the barcode_digit_ensemble

        Args:
            ratios (np.array): the ratio by which the image is scaled later in the
            ensemble model pipeline
            scores (np.array): confidence scores returned by barcode detection model
            boxes (np.array): bounding boxes that describe where a barcode is detected
            classes (np.array): classes returned from the barcode detection model. As of
            5/5/2022 the barcode model only detects one class

        Returns:
            cropped_image (np.array): the image of only the barcode cropped from the original
            image

        """
        with grpcclient.InferenceServerClient(self.hostname) as client:
            # ratios = np.expand_dims(ratios, axis=0)

            input0 = grpcclient.InferInput("DALI_INPUT_0", image.shape, "UINT8")
            input0.set_data_from_numpy(image)

            input1 = grpcclient.InferInput("DALI_INPUT_1", matrix.shape, "FP32")
            input1.set_data_from_numpy(matrix)

            input2 = grpcclient.InferInput("DALI_INPUT_2", dims.shape, "FP32")
            input2.set_data_from_numpy(dims)

            input3 = grpcclient.InferInput("DALI_INPUT_3", rotation.shape, "FP32")
            input3.set_data_from_numpy(rotation)

            output0 = grpcclient.InferRequestedOutput("DALI_OUTPUT_0")

            input_list = [input0, input1, input2, input3]
            output_list = [output0]

            response = client.infer(
                "dali_crop_gpu", input_list, request_id=str("1"), outputs=output_list, client_timeout=5.0
            )

            cropped_image = response.as_numpy("DALI_OUTPUT_0")

            return cropped_image

    def read_barcode_ensemble(self, cropped_image):
        """ The read_barcode_ensemble function returns the inputs and outputs from the entire
        read_barcode_ensemble model pipeline.

        Args:
            cropped_image (np.array): the image of only the barcode cropped from the original
            image
        Returns:
            digits (np.array): an array of the digits that were detected on the barcode
            tracking_num (str): the decoded barcode if able to decode, otherwise None
            barcode_class (str): the name of the class of barcode. As of 5/5/2022 this
            either "S10" or "domestic"

        """
        with grpcclient.InferenceServerClient(self.hostname) as client:
            input_name = "cropped_in"
            dtype = "FP32"
            input0 = grpcclient.InferInput(input_name, cropped_image.shape, dtype)
            input0.set_data_from_numpy(cropped_image)
            output0 = grpcclient.InferRequestedOutput("DIGITS")
            output1 = grpcclient.InferRequestedOutput("TRACKING_NUM_PYZBAR")
            output2 = grpcclient.InferRequestedOutput("BARCODE_CLASS")
            input_list = [input0]
            output_list = [output0, output1, output2]

            response = client.infer(
                "read_barcode_ensemble", input_list, request_id=str("1"), outputs=output_list, client_timeout=5.0
            )

            digits = response.as_numpy("DIGITS")
            tracking_num_pyzbar = response.as_numpy("TRACKING_NUM_PYZBAR")
            barcode_class = response.as_numpy("BARCODE_CLASS")
            return digits, tracking_num_pyzbar, barcode_class

    def ensemble_model_shipping_label(self, image):
        """ The read_barcode_ensemble function returns the inputs and outputs from the entire
        read_barcode_ensemble model pipeline.

        Args:
            image (np.array): scanned image of a package
        Returns:
            scores (np.array): confidence scores returned by shipping label detection model
            boxes (np.array): bounding boxes that describe where an item in the shipping label is
            classes (np.array): classes returned from the shipping label detection

        """
        # with open(image_filepath, 'rb') as f:
        #     file_bytestring = np.frombuffer(f.read(), dtype=np.uint8)
        #     file_bytestring = np.expand_dims(file_bytestring, axis=0)

        with grpcclient.InferenceServerClient(self.hostname) as client:
            input_name = "IMAGE"
            dtype = "UINT8"
            input0 = grpcclient.InferInput(input_name, image.shape, dtype)
            input0.set_data_from_numpy(image)
            output0 = grpcclient.InferRequestedOutput("scores_out")
            output1 = grpcclient.InferRequestedOutput("boxes_out")
            output2 = grpcclient.InferRequestedOutput("classes_out")
            input_list = [input0]
            output_list = [output0, output1, output2]

            response = client.infer(
                "ensemble_model_shipping_label_yolov8", input_list, request_id=str("1"),
                outputs=output_list, client_timeout=5.0
            )

            scores = response.as_numpy("scores_out")[0]
            boxes = response.as_numpy("boxes_out")[0]
            classes = response.as_numpy("classes_out")[0]
            return scores, boxes, classes

    def ensemble_model_hazmat_yolov5(self, image):
        """ The read_barcode_ensemble function returns the inputs and outputs from the entire
        read_barcode_ensemble model pipeline.

        Args:
            image (np.array): scanned image of a package
        Returns:
            scores (np.array): confidence scores returned by shipping label detection model
            boxes (np.array): bounding boxes that describe where an item in the shipping label is
            classes (np.array): classes returned from the shipping label detection

        """
        # with open(image_filepath, 'rb') as f:
        #     file_bytestring = np.frombuffer(f.read(), dtype=np.uint8)
        #     file_bytestring = np.expand_dims(file_bytestring, axis=0)

        with grpcclient.InferenceServerClient(self.hostname) as client:
            input_name = "IMAGE"
            dtype = "UINT8"
            input0 = grpcclient.InferInput(input_name, image.shape, dtype)
            input0.set_data_from_numpy(image)
            output0 = grpcclient.InferRequestedOutput("scores_out")
            output1 = grpcclient.InferRequestedOutput("boxes_out")
            output2 = grpcclient.InferRequestedOutput("classes_out")
            input_list = [input0]
            output_list = [output0, output1, output2]

            response = client.infer(
                "ensemble_model_shipping_label", input_list, request_id=str("1"),
                outputs=output_list, client_timeout=5.0
            )

            scores = response.as_numpy("scores_out")[0]
            boxes = response.as_numpy("boxes_out")[0]
            classes = response.as_numpy("classes_out")[0]
            return scores, boxes, classes

    def ensemble_model_crop_label(self, image_filepath, scores, boxes, classes):
        """ The read_barcode_ensemble function returns the inputs and outputs from the entire
        read_barcode_ensemble model pipeline.

        Args:
            image (np.array): scanned image of a package
        Returns:
            scores (np.array): confidence scores returned by shipping label detection model
            boxes (np.array): bounding boxes that describe where an item in the shipping label is
            classes (np.array): classes returned from the shipping label detection

        """
        with open(image_filepath, 'rb') as f:
            file_bytestring = np.frombuffer(f.read(), dtype=np.uint8)
            file_bytestring = np.expand_dims(file_bytestring, axis=0)

        with grpcclient.InferenceServerClient(self.hostname) as client:

            input0 = grpcclient.InferInput("img_bytestring", file_bytestring.shape, "UINT8")
            input0.set_data_from_numpy(file_bytestring)
            input1 = grpcclient.InferInput("scores", scores.shape, "FP32")
            input1.set_data_from_numpy(scores)
            input2 = grpcclient.InferInput("boxes", boxes.shape, "FP32")
            input2.set_data_from_numpy(boxes)
            input3 = grpcclient.InferInput("classes", classes.shape, "FP32")
            input3.set_data_from_numpy(classes)

            output0 = grpcclient.InferRequestedOutput("cropped_labels")
            output1 = grpcclient.InferRequestedOutput("classes_out")

            input_list = [input0, input1, input2, input3]
            output_list = [output0, output1]

            response = client.infer(
                "ensemble_model_crop_label", input_list, request_id=str("1"),
                outputs=output_list, client_timeout=5.0
            )

            cropped_labels = response.as_numpy("cropped_labels")
            classes = response.as_numpy("classes_out")
            return cropped_labels, classes

    def shipping_label_ocr(self, image_filepath, scores, boxes, classes):
        """ The read_barcode_ensemble function returns the inputs and outputs from the entire
        read_barcode_ensemble model pipeline.

        Args:
            image (np.array): scanned image of a package
        Returns:
            scores (np.array): confidence scores returned by shipping label detection model
            boxes (np.array): bounding boxes that describe where an item in the shipping label is
            classes (np.array): classes returned from the shipping label detection

        """
        with open(image_filepath, 'rb') as f:
            file_bytestring = np.frombuffer(f.read(), dtype=np.uint8)
            file_bytestring = np.expand_dims(file_bytestring, axis=0)

        with grpcclient.InferenceServerClient(self.hostname) as client:
            input0 = grpcclient.InferInput("img_bytestring", file_bytestring.shape, "UINT8")
            input0.set_data_from_numpy(file_bytestring)
            input1 = grpcclient.InferInput("scores", scores.shape, "FP32")
            input1.set_data_from_numpy(scores)
            input2 = grpcclient.InferInput("boxes", boxes.shape, "FP32")
            input2.set_data_from_numpy(boxes)
            input3 = grpcclient.InferInput("classes", classes.shape, "FP32")
            input3.set_data_from_numpy(classes)

            output0 = grpcclient.InferRequestedOutput("shipping_label_OCR")

            input_list = [input0, input1, input2, input3]
            output_list = [output0]

            response = client.infer(
                "shipping_label_ocr", input_list, request_id=str("1"),
                outputs=output_list, client_timeout=5.0
            )

            OCR_json = response.as_numpy("shipping_label_OCR")
            return OCR_json

    def extract_crop_args(self, image_filepath, scores, boxes, classes):
        """ The read_barcode_ensemble function returns the inputs and outputs from the entire
        read_barcode_ensemble model pipeline.

        Args:
            image (np.array): scanned image of a package
        Returns:
            scores (np.array): confidence scores returned by shipping label detection model
            boxes (np.array): bounding boxes that describe where an item in the shipping label is
            classes (np.array): classes returned from the shipping label detection

        """
        with open(image_filepath, 'rb') as f:
            file_bytestring = np.frombuffer(f.read(), dtype=np.uint8)
            file_bytestring = np.expand_dims(file_bytestring, axis=0)

        with grpcclient.InferenceServerClient(self.hostname) as client:
            input0 = grpcclient.InferInput("img_bytestring_in", file_bytestring.shape, "UINT8")
            input0.set_data_from_numpy(file_bytestring)
            input1 = grpcclient.InferInput("scores_in", scores.shape, "FP32")
            input1.set_data_from_numpy(scores)
            input2 = grpcclient.InferInput("boxes_in", boxes.shape, "FP32")
            input2.set_data_from_numpy(boxes)
            input3 = grpcclient.InferInput("classes_in", classes.shape, "FP32")
            input3.set_data_from_numpy(classes)

            output0 = grpcclient.InferRequestedOutput("img")
            output1 = grpcclient.InferRequestedOutput("matrix_out")
            output2 = grpcclient.InferRequestedOutput("dims_out")
            output3 = grpcclient.InferRequestedOutput("cropped_label_classes")
            output4 = grpcclient.InferRequestedOutput("rotation_out")
            output5 = grpcclient.InferRequestedOutput("label_orientations")

            input_list = [input0, input1, input2, input3]
            output_list = [output0, output1, output2, output3, output4, output5]

            response = client.infer(
                "extract_crop_args", input_list, request_id=str("1"),
                outputs=output_list, client_timeout=5.0
            )

            img_batch = response.as_numpy("img")
            matrix_out = response.as_numpy("matrix_out")
            dims_out = response.as_numpy("dims_out")
            rotation_out = response.as_numpy("rotation_out")
            cropped_label_classes = response.as_numpy("cropped_label_classes")
            orientations = response.as_numpy("label_orientations")

            return img_batch, matrix_out, dims_out, rotation_out, cropped_label_classes, orientations

    def read_barcode_digits(self, cropped_image):
        """ read_barcode_digits grabs the inputs and outputs from the read_barcode_digits model
            in the read_barcode_ensemble

        Args:
            cropped_image (np.array): the image of only the barcode cropped from the original
            image

        Returns:
            scores (np.array): confidence scores returned by digits detection model
            boxes (np.array): bounding boxes that describe where each digit is detected
            classes (np.array): classes returned from the digits detection model. As of
            5/5/2022 the digits detection model detects digits 0-9
        """
        with grpcclient.InferenceServerClient(self.hostname) as client:
            input_name = "input_1"
            dtype = "FP32"
            input0 = grpcclient.InferInput(input_name, cropped_image.shape, dtype)
            input0.set_data_from_numpy(cropped_image)
            output0 = grpcclient.InferRequestedOutput("scores")
            output1 = grpcclient.InferRequestedOutput("boxes")
            output2 = grpcclient.InferRequestedOutput("classes")
            input_list = [input0]
            output_list = [output0, output1, output2]

            response = client.infer(
                "read_barcode_digits", input_list, request_id=str("1"), outputs=output_list, client_timeout=5.0
            )

            scores = response.as_numpy("scores")
            boxes = response.as_numpy("boxes")
            classes = response.as_numpy("classes")
            return scores, boxes, classes

    def read_barcode_pyzbar(self, cropped_image):
        """ read_barcode_pyzbar grabs the inputs and outputs from the read_barcode_pyzbar model
            in the read_barcode_ensemble

        Args:
            cropped_image (np.array): the image of only the barcode cropped from the original
            image

        Returns:
            tracking_num (str): the decoded barcode if able to decode, otherwise None
            barcode_class (str): the name of the class of barcode. As of 5/5/2022 this
            either "S10" or "domestic"
        """
        with grpcclient.InferenceServerClient(self.hostname) as client:
            input_name = "cropped_image_in"
            dtype = "UINT8"
            input0 = grpcclient.InferInput(input_name, cropped_image.shape, dtype)
            input0.set_data_from_numpy(cropped_image)
            output0 = grpcclient.InferRequestedOutput("tracking_num_pyzbar")
            output1 = grpcclient.InferRequestedOutput("barcode_class")
            input_list = [input0]
            output_list = [output0, output1]

            response = client.infer(
                "read_barcode_pyzbar", input_list, request_id=str("1"), outputs=output_list, client_timeout=5.0
            )

            tracking_num = response.as_numpy("tracking_num_pyzbar")
            barcode_class = response.as_numpy("barcode_class")
            return tracking_num, barcode_class

    def post_process_digits(self, scores, boxes, classes):
        """ post_process_digits grabs the inputs and outputs from the post_process_digits model
            in the read_barcode_ensemble

        Args:
            scores (np.array): confidence scores returned by digits detection model
            boxes (np.array): bounding boxes that describe where each digit is detected
            classes (np.array): classes returned from the digits detection model. As of
            5/5/2022 the digits detection model detects digits 0-9

        Returns:
            digits (np.array): an array of the digits that were detected on the barcode

        """
        with grpcclient.InferenceServerClient(self.hostname) as client:
            input0 = grpcclient.InferInput("scores_in", scores.shape, "FP32")
            input0.set_data_from_numpy(scores)

            input1 = grpcclient.InferInput("boxes_in", boxes.shape, "FP32")
            input1.set_data_from_numpy(boxes)

            input2 = grpcclient.InferInput("classes_in", classes.shape, "FP32")
            input2.set_data_from_numpy(classes)

            output0 = grpcclient.InferRequestedOutput("digits")

            input_list = [input0, input1, input2]
            output_list = [output0]

            response = client.infer(
                "postprocess_digits", input_list, request_id=str("1"), outputs=output_list, client_timeout=5.0
            )

            digits = response.as_numpy("digits")
            return digits

    def barcode_digit_ensemble(self):
        """ The barcode_digit_ensemble function returns the inputs and outputs from the entire
        barcode_digit_ensemble model.

        Args:
            None
        Returns:
            digits (np.array): an array of the digits that were detected on the barcode
            tracking_num (str): the decoded barcode if able to decode, otherwise None
            barcode_class (str): the name of the class of barcode. As of 5/5/2022 this
            either "S10" or "domestic"

        """
        with grpcclient.InferenceServerClient(self.hostname) as client:
            input_name = "IMAGE"
            dtype = "UINT8"
            input0 = grpcclient.InferInput(input_name, self.image.shape, dtype)
            input0.set_data_from_numpy(self.image)
            output0 = grpcclient.InferRequestedOutput("digits_out")
            output1 = grpcclient.InferRequestedOutput("tracking_num_pyzbar_out")
            output2 = grpcclient.InferRequestedOutput("barcode_class_out")
            output3 = grpcclient.InferRequestedOutput("preprocessed_image")
            output4 = grpcclient.InferRequestedOutput("ratios")
            output5 = grpcclient.InferRequestedOutput("IMAGE_out")
            output6 = grpcclient.InferRequestedOutput("MATRIX_BARCODE")
            output7 = grpcclient.InferRequestedOutput("MATRIX_ADDRESS")
            output8 = grpcclient.InferRequestedOutput("DIMS")
            output9 = grpcclient.InferRequestedOutput("IMAGE_digits_out")
            output10 = grpcclient.InferRequestedOutput("IMAGE_pyzbar_out")

            input_list = [input0]
            output_list = [output0, output1, output2, output3, output4, output5, output6,
                           output7, output8, output9, output10]

            response = client.infer(
                "barcode_digit_ensemble", input_list, request_id=str("1"), outputs=output_list, client_timeout=5.0
            )

            digits = np.squeeze(response.as_numpy("digits_out")[0]).reshape(-1)
            tracking_num_pyzbar = response.as_numpy("tracking_num_pyzbar_out")
            barcode_class = response.as_numpy("barcode_class_out")
            preprocessed_img = response.as_numpy("preprocessed_image")
            ratios = response.as_numpy("ratios")
            img_to_crop = response.as_numpy("IMAGE_out")
            matrix_barcode = response.as_numpy("MATRIX_BARCODE")
            matrix_address = response.as_numpy("MATRIX_ADDRESS")
            dims = response.as_numpy("DIMS")
            img_digits_out = response.as_numpy("IMAGE_digits_out")
            img_pyzbar_out = response.as_numpy("IMAGE_pyzbar_out")
            return digits, tracking_num_pyzbar, barcode_class, preprocessed_img, ratios, img_to_crop, matrix_barcode, \
                matrix_address, dims, img_digits_out, img_pyzbar_out

    def ensemble_model_dali(self, image):
        """ The ensemble_model_dali function returns the inputs and outputs from the entire
        ensemble_model_dali model.

        Args:
            None
        Returns:


        """
        # with open(image_filepath, 'rb') as f:
        #     file_bytestring = np.frombuffer(f.read(), dtype=np.uint8)
        # image = np.expand_dims(image, axis=0)

        with grpcclient.InferenceServerClient(self.hostname) as client:
            input_name = "IMAGE"
            dtype = "UINT8"
            input0 = grpcclient.InferInput(input_name, image.shape, dtype)
            input0.set_data_from_numpy(image)
            output0 = grpcclient.InferRequestedOutput("stamp_scores")
            output1 = grpcclient.InferRequestedOutput("attrs_resize")
            output2 = grpcclient.InferRequestedOutput("hazmat_scores")
            output3 = grpcclient.InferRequestedOutput("smaller_resized_image")

            input_list = [input0]
            output_list = [output0, output1, output2, output3]

            response = client.infer(
                "ensemble_model_dali", input_list, request_id=str("1"), outputs=output_list, client_timeout=5.0
            )

            stamp_score = response.as_numpy("stamp_scores")
            attr_resize = response.as_numpy("attrs_resize")
            hazmat_score = response.as_numpy("hazmat_scores")
            small_img = response.as_numpy("smaller_resized_image")

            return stamp_score, attr_resize, hazmat_score, small_img

    def ensemble_model_ecips(self, image_filepath):
        """ The ensemble_model_dali function returns the inputs and outputs from the entire
        ensemble_model_dali model.

        Args:
            None
        Returns:


        """
        with open(image_filepath, 'rb') as f:
            file_bytestring = np.frombuffer(f.read(), dtype=np.uint8)
            file_bytestring = np.expand_dims(file_bytestring, axis=0)

        with grpcclient.InferenceServerClient(self.hostname) as client:
            input_name = "IMAGE_BYTESTRING"
            dtype = "UINT8"
            input0 = grpcclient.InferInput(input_name, file_bytestring.shape, dtype)
            input0.set_data_from_numpy(file_bytestring)
            # output0 = grpcclient.InferRequestedOutput("ATTRS_RESIZE")
            # output1 = grpcclient.InferRequestedOutput("HAZMAT_SCORES")
            output2 = grpcclient.InferRequestedOutput("YOLO_SCORES")
            output3 = grpcclient.InferRequestedOutput("YOLO_BOXES")
            output4 = grpcclient.InferRequestedOutput("YOLO_CLASSES")
            # output5 = grpcclient.InferRequestedOutput("STAMP_SCORES")
            # output6 = grpcclient.InferRequestedOutput("STAMP_BOXES")
            # output7 = grpcclient.InferRequestedOutput("STAMP_CLASSES")
            # output8 = grpcclient.InferRequestedOutput("HAZMAT_BOXES")
            # output9 = grpcclient.InferRequestedOutput("HAZMAT_CLASSES")
            output10 = grpcclient.InferRequestedOutput("HAZMAT_YOLO_SCORES")
            output11 = grpcclient.InferRequestedOutput("HAZMAT_YOLO_BOXES")
            output12 = grpcclient.InferRequestedOutput("HAZMAT_YOLO_CLASSES")

            input_list = [input0]
            output_list = [ output2, output3, output4,
                           output10, output11, output12]

            response = client.infer(
                "ensemble_model_ecip", input_list, request_id=str("1"), outputs=output_list, client_timeout=5.0
            )

            og_dims = response.as_numpy("ATTRS_RESIZE")
            yolo_scores = response.as_numpy("YOLO_SCORES")
            yolo_boxes = response.as_numpy("YOLO_BOXES")
            yolo_classes = response.as_numpy("YOLO_CLASSES")
            hazmat_scores = response.as_numpy("HAZMAT_SCORES")
            stamp_scores = response.as_numpy("STAMP_SCORES")
            hazmat_yolo_scores = response.as_numpy("HAZMAT_YOLO_SCORES")
            hazmat_yolo_boxes = response.as_numpy("HAZMAT_YOLO_BOXES")
            hazmat_yolo_classes = response.as_numpy("HAZMAT_YOLO_CLASSES")

            return og_dims, yolo_scores, yolo_boxes, yolo_classes, hazmat_scores, stamp_scores, \
                   hazmat_yolo_scores, hazmat_yolo_boxes, hazmat_yolo_classes

    def ensemble_model_hazmat(self, image_filepath):
        """ The ensemble_model_dali function returns the inputs and outputs from the entire
        ensemble_model_dali model.

        Args:
            None
        Returns:


        """
        with open(image_filepath, 'rb') as f:
            file_bytestring = np.frombuffer(f.read(), dtype=np.uint8)
            file_bytestring = np.expand_dims(file_bytestring, axis=0)

        with grpcclient.InferenceServerClient(self.hostname) as client:
            input_name = "IMAGE_BYTESTRING"
            dtype = "UINT8"
            input0 = grpcclient.InferInput(input_name, file_bytestring.shape, dtype)
            input0.set_data_from_numpy(file_bytestring)
            output0 = grpcclient.InferRequestedOutput("processed_hazmat_scores")
            output1 = grpcclient.InferRequestedOutput("processed_hazmat_boxes")
            output2 = grpcclient.InferRequestedOutput("processed_hazmat_classes")
            output3 = grpcclient.InferRequestedOutput("smaller_resized_image")

            input_list = [input0]
            output_list = [output0, output1, output2, output3]

            response = client.infer(
                "ensemble_model_hazmat", input_list, request_id=str("1"), outputs=output_list, client_timeout=5.0
            )

            scores = response.as_numpy("processed_hazmat_scores")
            boxes = response.as_numpy("processed_hazmat_boxes")
            classes = response.as_numpy("processed_hazmat_classes")

            return scores, boxes, classes

    def dali_load_img(self, image_filepath):
        """ The ensemble_model_dali function returns the inputs and outputs from the entire
        ensemble_model_dali model.

        Args:
            None
        Returns:


        """
        with open(image_filepath, 'rb') as f:
            file_bytestring = np.frombuffer(f.read(), dtype=np.uint8)
            file_bytestring = np.expand_dims(file_bytestring, axis=0)

        with grpcclient.InferenceServerClient(self.hostname) as client:
            input_name = "DALI_INPUT_0"
            dtype = "UINT8"
            input0 = grpcclient.InferInput(input_name, file_bytestring.shape, dtype)
            input0.set_data_from_numpy(file_bytestring)
            output0 = grpcclient.InferRequestedOutput("DALI_OUTPUT_0")

            input_list = [input0]
            output_list = [output0]

            response = client.infer(
                "dali_load_img", input_list, request_id=str("1"), outputs=output_list, client_timeout=5.0
            )

            loaded_img = response.as_numpy("DALI_OUTPUT_0")

            return loaded_img

    # def dali_resize_gpu(self, image):
    #     """ dali_resize_gpu grabs the inputs and outputs from the dali_resize_gpu model
    #
    #     Returns:
    #         preprocessed_img (np.array): the preprocessed image scaled by value, ratios
    #         ratios (np.array): the ratio by which the image is scaled later in the
    #         ensemble model pipeline
    #     """
    #     with grpcclient.InferenceServerClient(self.hostname) as client:
    #         # input_image = 255 * np.array(Image.open(img_filepath)).astype(np.uint8)
    #         # input_image = input_image[None, :, :, None]
    #         # with open(img_filepath, 'rb') as file:
    #         #     img_buffer = file.read()
    #         #
    #         # input_image = np.array(img_buffer, dtype="uint8")
    #         input_image = image
    #         input_image = np.expand_dims(input_image, axis=-1)
    #
    #         input_name = "DALI_INPUT_0"
    #         dtype = "UINT8"
    #         input0 = grpcclient.InferInput(input_name, input_image.shape, dtype)
    #         input0.set_data_from_numpy(input_image)
    #         output0 = grpcclient.InferRequestedOutput("DALI_OUTPUT_0")
    #         output1 = grpcclient.InferRequestedOutput("DALI_OUTPUT_1")
    #         output2 = grpcclient.InferRequestedOutput("DALI_OUTPUT_2")
    #         input_list = [input0]
    #         output_list = [output0, output1, output2]
    #         response = client.infer(
    #             "dali_resize_gpu", input_list, request_id=str("1"), outputs=output_list, client_timeout=5.0
    #         )
    #         preprocessed_img = response.as_numpy("DALI_OUTPUT_0")
    #         smaller_resized_img = response.as_numpy("DALI_OUTPUT_1")
    #         attrs_resize = response.as_numpy("DALI_OUTPUT_2")
    #         return preprocessed_img, smaller_resized_img, attrs_resize

    def dali_test(self, img_filepath):
        """ dali_resize_gpu grabs the inputs and outputs from the dali_resize_gpu model

        Returns:
            preprocessed_img (np.array): the preprocessed image scaled by value, ratios
            ratios (np.array): the ratio by which the image is scaled later in the
            ensemble model pipeline
        """
        with grpcclient.InferenceServerClient(self.hostname) as client:
            input_image = 255 * np.array(Image.open(img_filepath)).astype(np.uint8)
            input_image = input_image[None, :, :, None]

            input_image = np.expand_dims(input_image, axis=-1)

            input_name = "DALI_INPUT_0"
            dtype = "UINT8"
            input0 = grpcclient.InferInput(input_name, input_image.shape, dtype)
            input0.set_data_from_numpy(input_image)
            output0 = grpcclient.InferRequestedOutput("DALI_OUTPUT_0")
            input_list = [input0]
            output_list = [output0]
            response = client.infer(
                "dali_test", input_list, request_id=str("1"), outputs=output_list, client_timeout=5.0
            )
            preprocessed_img = response.as_numpy("DALI_OUTPUT_0")
            return preprocessed_img
