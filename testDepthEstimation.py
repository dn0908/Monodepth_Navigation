

import cv2
import numpy as np
import time
from threading import Thread, Lock
from queue import Queue
from MidasDepthEstimation.midasDepthEstimator import midasDepthEstimator

# Initialize depth estimation model
depthEstimator = midasDepthEstimator()

# Variables
frame_queue = Queue(maxsize=10)  # Shared queue for frames
output_lock = Lock()             # Lock for video output operations

# Initialize webcam
camera = cv2.VideoCapture(0)

# Initialize video writer
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out_video = cv2.VideoWriter("output.mp4", fourcc, 1, (640, 240))

def capture_frames():
    """Thread function to capture frames from the webcam."""
    while True:
        ret, frame = camera.read()
        if ret and frame_queue.qsize() < 5:
            frame = cv2.resize(frame, (320, 240))
            if not frame_queue.full():
                frame_queue.put(frame)
        else:
            break

def depth_estimation():
    """Main thread for depth estimation and video writing."""
    start_time = time.perf_counter()
    total_inference_duration = 0

    while time.perf_counter() - start_time < 50:  # Run for 50 seconds
        if not frame_queue.empty():
            # Get a frame from the queue
            img = frame_queue.get()

            # Estimate depth
            inference_start_time = time.perf_counter()
            colorDepth = depthEstimator.estimateDepth(img)
            inference_duration = time.perf_counter() - inference_start_time
            total_inference_duration += inference_duration
            print(f"Inference time: {inference_duration:.4f}s")

            # Ensure depth image is 3-channel
            if len(colorDepth.shape) == 2:  # Grayscale case
                colorDepth = cv2.cvtColor(colorDepth, cv2.COLOR_GRAY2BGR)
            elif len(colorDepth.shape) == 3 and colorDepth.shape[2] == 3:  # Already 3-channel
                pass  # No conversion needed
            else:
                raise ValueError(f"Unexpected colorDepth shape: {colorDepth.shape}")

            # Combine RGB image and depth image
            img_out = np.hstack((img, colorDepth))
            img_out = cv2.resize(img_out, (640, 240))

            # Write the combined image to the output video
            with output_lock:
                out_video.write(img_out)

    print(f"Average inference time: {total_inference_duration / 50:.4f}s")

# Start the threads
capture_thread = Thread(target=capture_frames, daemon=True)
capture_thread.start()

depth_estimation()  # Run depth estimation in the main thread

# Cleanup
camera.release()
out_video.release()
