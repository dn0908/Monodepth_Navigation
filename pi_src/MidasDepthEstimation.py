import time
import numpy as np
from picamera2 import Picamera2
import os

try:
    from tflite_runtime.interpreter import Interpreter
except ImportError:
    from tensorflow.lite.python.interpreter import Interpreter


class MidasDepthEstimator:
    def __init__(self):
        self.fps = 0
        self.time_last_prediction = time.time()
        self.frame_counter = 0

        # Initialize model
        self.initialize_model()

    def initialize_model(self):
        model_path = 'midasModel.tflite'

        # Verify the model exists
        if not os.path.isfile(model_path):
            raise FileNotFoundError(f"Model file not found at {model_path}")

        # Load the model
        self.interpreter = Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()

        # Get model input/output details
        self.get_model_input_details()
        self.get_model_output_details()

    def estimate_depth(self, image):
        input_tensor = self.prepare_input_for_inference(image)
        raw_disparity = self.inference(input_tensor)
        processed_disparity = self.process_raw_disparity(raw_disparity, image.shape)

        resized_disparity = np.resize(processed_disparity, (image.shape[0], image.shape[1]))
        return self.draw_depth(resized_disparity)

    def prepare_input_for_inference(self, image):
        # Convert RGB888 image to float32 and resize for the model
        img = image.astype(np.float32) / 255.0
        img = (img - np.array([0.485, 0.456, 0.406])) / np.array([0.229, 0.224, 0.225])
        img = np.resize(img, (self.input_height, self.input_width, 3))
        img = img.reshape(1, self.input_height, self.input_width, 3).astype(np.float32)
        return img

    def inference(self, img_input):
        self.interpreter.set_tensor(self.input_details[0]['index'], img_input)
        self.interpreter.invoke()
        output = self.interpreter.get_tensor(self.output_details[0]['index'])
        return output.reshape(self.output_height, self.output_width)

    def process_raw_disparity(self, raw_disparity, img_shape):
        # Normalize depth values to 0-255
        depth_min = raw_disparity.min()
        depth_max = raw_disparity.max()
        normalized_disparity = (255 * (raw_disparity - depth_min) / (depth_max - depth_min)).astype("uint8")
        return normalized_disparity

    def draw_depth(self, processed_disparity):
        # Apply a colormap for visualization
        color_map = np.zeros((processed_disparity.shape[0], processed_disparity.shape[1], 3), dtype=np.uint8)
        color_map[:, :, 0] = processed_disparity  # Blue
        color_map[:, :, 1] = processed_disparity  # Green
        color_map[:, :, 2] = 255 - processed_disparity  # Red
        return color_map

    def get_model_input_details(self):
        self.input_details = self.interpreter.get_input_details()
        input_shape = self.input_details[0]['shape']
        self.input_height = input_shape[1]
        self.input_width = input_shape[2]
        self.channels = input_shape[3]

    def get_model_output_details(self):
        self.output_details = self.interpreter.get_output_details()
        output_shape = self.output_details[0]['shape']
        self.output_height = output_shape[1]
        self.output_width = output_shape[2]

    def update_fps(self):
        self.frame_counter += 1
        if time.time() - self.time_last_prediction > 1:
            self.fps = self.frame_counter
            self.frame_counter = 0
            self.time_last_prediction = time.time()
