import argparse
import io
import os
import sys
import time
import logging

import cv2
from PIL import Image
import numpy as np

from bosdyn.api import network_compute_bridge_service_pb2_grpc
from bosdyn.api import network_compute_bridge_pb2
from bosdyn.api import image_pb2
from bosdyn.api import header_pb2
import bosdyn.client
import bosdyn.client.util
import grpc
from concurrent import futures
import tensorflow as tf

import queue
import threading
from google.protobuf import wrappers_pb2
from object_detection.utils import label_map_util

kServiceAuthority = "fetch-tutorial-worker.spot.robot"

class TensorFlowObjectDetectionModel:
    def __init__(self, model_path, label_path):
        self.detect_fn = tf.saved_model.load(model_path)
        self.category_index = label_map_util.create_category_index_from_labelmap(label_path, use_display_name=True)
        self.name = os.path.basename(os.path.dirname(model_path))

    def predict(self, image):
        input_tensor = tf.convert_to_tensor(image)
        input_tensor = input_tensor[tf.newaxis, ...]
        detections = self.detect_fn(input_tensor)

        return detections
    
def process_thread(args, request_queue, response_queue):
    # Load the model(s)
    models = {}
    for model in args.model:
        this_model = TensorFlowObjectDetectionModel(model[0], model[1])
        models[this_model.name] = this_model

    print('')
    print('Service ' + args.name + ' running on port: ' + str(args.port))

    print('Loaded models:')
    for model_name in models:
        print('    ' + model_name)

    while True:
        request = request_queue.get()

        if isinstance(request, network_compute_bridge_pb2.ListAvailableModelsRequest):
            out_proto = network_compute_bridge_pb2.ListAvailableModelsResponse()
            for model_name in models:
                out_proto.models.data.append(network_compute_bridge_pb2.ModelData(model_name=model_name))
            response_queue.put(out_proto)
            continue
        else:
            out_proto = network_compute_bridge_pb2.NetworkComputeResponse()

        # Find the model
        if request.input_data.model_name not in models:
            err_str = 'Cannot find model "' + request.input_data.model_name + '" in loaded models.'
            print(err_str)

             # Set the error in the header.
            out_proto.header.error.code = header_pb2.CommonError.CODE_INVALID_REQUEST
            out_proto.header.error.message = err_str
            response_queue.put(out_proto)
            continue

        model = models[request.input_data.model_name]

        # Unpack the incoming image.
        if request.input_data.image.format == image_pb2.Image.FORMAT_RAW:
            pil_image = Image.open(io.BytesIO(request.input_data.image.data))
            if request.input_data.image.pixel_format == image_pb2.Image.PIXEL_FORMAT_GREYSCALE_U8:
                # If the input image is grayscale, convert it to RGB.
                image = cv2.cvtColor(pil_image, cv2.COLOR_GRAY2RGB)

            elif request.input_data.image.pixel_format == image_pb2.Image.PIXEL_FORMAT_RGB_U8:
                # Already an RGB image.
                image = pil_image

            else:
                print('Error: image input in unsupported pixel format: ', request.input_data.image.pixel_format)
                response_queue.put(out_proto)
                continue

        elif request.input_data.image.format == image_pb2.Image.FORMAT_JPEG:
            dtype = np.uint8
            jpg = np.frombuffer(request.input_data.image.data, dtype=dtype)
            image = cv2.imdecode(jpg, -1)

            if len(image.shape) < 3:
                # If the input image is grayscale, convert it to RGB.
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)

        image_width = image.shape[0]
        image_height = image.shape[1]

        detections = model.predict(image)
        num_objects = 0

        # All outputs are batches of tensors.
        # Convert to numpy arrays, and take index [0] to remove the batch dimension.
        # We're only interested in the first num_detections.
        num_detections = int(detections.pop('num_detections'))
        detections = {key: value[0, :num_detections].numpy()
                       for key, value in detections.items()}

        boxes = detections['detection_boxes']
        classes = detections['detection_classes']
        scores = detections['detection_scores']

        for i in range(boxes.shape[0]):
            if scores[i] < request.input_data.min_confidence:
                continue

            box = tuple(boxes[i].tolist())

            # Boxes come in with normalized coordinates.  Convert to pixel values.
            box = [box[0] * image_width, box[1] * image_height, box[2] * image_width, box[3] * image_height]

            score = scores[i]

            if classes[i] in model.category_index.keys():
                label = model.category_index[classes[i]]['name']
            else:
                label = 'N/A'

            num_objects += 1

            print('Found object with label: "' + label + '" and score: ' + str(score))

