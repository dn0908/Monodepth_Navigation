import cv2
import numpy as np
import time
from threading import Thread, Lock
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
from MidasDepthEstimation.midasDepthEstimator import midasDepthEstimator

# Initialize depth estimation model
depthEstimator = midasDepthEstimator()

# Variables
frame_queue = Queue(maxsize=10)  # Shared queue for frames
output_lock = Lock()             # Lock for video output operations
BATCH_SIZE = 4                   # Number of frames to process in a batch

# Initialize webcam
camera = cv2.VideoCapture(0)

# Initialize video writer
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out_video = cv2.VideoWriter("output.mp4", fourcc, 1, (640, 240))

def capture_frames():
    """Thread function to capture frames from the webcam."""
    while True:
        ret, frame = camera.read()
        if ret:
            frame = cv2.resize(frame, (256, 256))  # Reduced resolution for faster processing
            if not frame_queue.full():
                frame_queue.put(frame)
        else:
            break

def process_batch(batch_frames):
    """Process a batch of frames."""
    # Prepare the batch for inference
    batch_input = np.array([depthEstimator.prepareInputForInference(frame) for frame in batch_frames])
    
    # Perform batch inference
    raw_outputs = depthEstimator.inference(batch_input)
    
    # Post-process each output in the batch
    results = []
    for raw_output, frame in zip(raw_outputs, batch_frames):
        processed_depth = depthEstimator.processRawDisparity(raw_output, frame.shape[:2])
        colorDepth = depthEstimator.drawDepth(processed_depth)
        results.append(colorDepth)
    return results

def depth_estimation():
    """Main thread for depth estimation and video writing."""
    start_time = time.perf_counter()
    total_inference_duration = 0
    frame_batch = []  # To store frames for batching

    with ThreadPoolExecutor(max_workers=2) as executor:  # Use two threads for parallel inference
        while time.perf_counter() - start_time < 50:  # Run for 50 seconds
            if not frame_queue.empty():
                # Get a frame from the queue
                frame = frame_queue.get()
                frame_batch.append(frame)

                # When batch is full, process it
                if len(frame_batch) == BATCH_SIZE:
                    inference_start_time = time.perf_counter()
                    
                    # Submit batch for processing
                    future = executor.submit(process_batch, frame_batch)
                    colorDepths = future.result()
                    
                    inference_duration = time.perf_counter() - inference_start_time
                    total_inference_duration += inference_duration
                    print(f"Batch inference time: {inference_duration:.4f}s")

                    # Combine RGB image and depth image for each frame in the batch
                    for img, colorDepth in zip(frame_batch, colorDepths):
                        if len(colorDepth.shape) == 2:  # Grayscale case
                            colorDepth = cv2.cvtColor(colorDepth, cv2.COLOR_GRAY2BGR)
                        
                        img_out = np.hstack((img, colorDepth))
                        img_out = cv2.resize(img_out, (640, 240))
                        
                        # Write the combined image to the output video
                        with output_lock:
                            out_video.write(img_out)

                    # Clear the batch
                    frame_batch = []

    print(f"Average inference time per batch: {total_inference_duration / (50 // BATCH_SIZE):.4f}s")

# Start the threads
capture_thread = Thread(target=capture_frames, daemon=True)
capture_thread.start()

depth_estimation()  # Run depth estimation in the main thread

# Cleanup
camera.release()
out_video.release()
