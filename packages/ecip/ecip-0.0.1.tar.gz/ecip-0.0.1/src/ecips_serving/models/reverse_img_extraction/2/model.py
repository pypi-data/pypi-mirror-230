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
import time
import cv2 as cv
import numpy as np
import triton_python_backend_utils as pb_utils
# triton_python_backend_utils is available in every Triton Python model. You
# need to use this module to create inference requests and responses. It also
# contains some utility functions for extracting information from model_config
# and converting Triton input/output types to numpy types.


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
        reverse_img_descriptors_config = pb_utils.get_output_config_by_name(
            model_config, "descriptors")

        # Convert Triton types to numpy types
        self.reverse_img_descriptors_dtype = pb_utils.triton_string_to_numpy(
            reverse_img_descriptors_config['data_type'])

        reverse_img_keypoints_config = pb_utils.get_output_config_by_name(
            model_config, "keypoints")

        # Convert Triton types to numpy types
        self.reverse_img_keypoints_dtype = pb_utils.triton_string_to_numpy(
            reverse_img_keypoints_config['data_type'])

        # set confidence threshold
        self.sift = cv.SIFT_create()

        self.logger = pb_utils.Logger

    def calc_sift(self, img):
        kp, des = self.sift.detectAndCompute(img, None)

        return des

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
            img = pb_utils.get_input_tensor_by_name(request, "images").as_numpy()[0]
            time_1 = time.time()
            self.logger.log_verbose(f"img shape = {img.shape}")
            img = img.transpose(1, 2, 0).astype(np.float32)
            img_gray = (cv.cvtColor(img, cv.COLOR_RGB2GRAY)*255).astype(np.uint8)
            img_gray = cv.resize(img_gray, (640, 640))

            time_1b = time.time()
            self.logger.log_verbose(f"img_gray shape = {img_gray.shape}")
            self.logger.log_verbose(f"img_gray dtype = {img_gray.dtype}")
            self.logger.log_verbose(f"img_gray min = {np.min(img_gray)}")
            self.logger.log_verbose(f"img_gray max = {np.max(img_gray)}")

            descriptors = self.calc_sift(img_gray)
            time_2 = time.time()
            keypoints = np.asarray([])

            if descriptors is None:
                # This occurs when the image is all white/black -  no noticeable features
                descriptors = np.asarray([])
            out_kp = pb_utils.Tensor("keypoints",
                                     keypoints.astype(self.reverse_img_keypoints_dtype))
            out_desc = pb_utils.Tensor("descriptors",
                                       descriptors.astype(self.reverse_img_descriptors_dtype))
            inference_response = pb_utils.InferenceResponse(
                output_tensors=[out_kp, out_desc])
            responses.append(inference_response)

        self.logger.log_verbose(f"Time to load rev-search image: {time_1b - time_1}")
        self.logger.log_verbose(f"Time to calc sift descriptors: {time_2 - time_1b}")
        return responses

    def finalize(self):
        """`finalize` is called only once when the model is being unloaded.
        Implementing `finalize` function is OPTIONAL. This function allows
        the model to perform any necessary clean ups before exit.
        """
        print('Cleaning up...')
