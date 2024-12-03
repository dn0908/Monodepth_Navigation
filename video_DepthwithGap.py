import cv2
import numpy as np
import time
from pathlib import Path
from params import *
from MidasDepthEstimation.midasDepthEstimator import midasDepthEstimator

# Initialize depth estimation model
depthEstimator = midasDepthEstimator()

# variables
input_video_frame_nr = 0
start_time = time.perf_counter()
total_inference_duration = 0

# open input video (file)
cap = cv2.VideoCapture(str(VIDEO_FILE))

try:
    while cap.isOpened():
        ret, img = cap.read()

        input_fps = cap.get(cv2.CAP_PROP_FPS)
        input_video_frame_height, input_video_frame_width = img.shape[:2]

        target_fps = input_fps / ADVANCE_FRAMES
        target_frame_height = int(input_video_frame_height * SCALE_OUTPUT)
        target_frame_width = int(input_video_frame_width * SCALE_OUTPUT)

        num_frames = int(NUM_SECONDS * input_fps)
        total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT) if num_frames == 0 else num_frames


        result_video_path2 = output_directory / f"{Path(VIDEO_FILE).stem}_binary_withGapt.mp4"
        # Create a result video.
        out_video = cv2.VideoWriter(
            str(result_video_path),
            FOURCC,
            target_fps,
            (target_frame_width * 3, target_frame_height),
        )

        if not ret:
            cap.release()
            break
        if input_video_frame_nr >= total_frames:
            break

        inference_start_time = time.perf_counter()

        # Estimate depth
        colorDepth = depthEstimator.estimateDepth(img)

        inference_stop_time = time.perf_counter()
        inference_duration = inference_stop_time - inference_start_time
        print("Inference time : ", inference_duration, "s")
        total_inference_duration += inference_duration

        # Resize the image and the result to a target frame shape.
        result_frame = cv2.resize(result_frame, (target_frame_width, target_frame_height))
        image = cv2.resize(image, (target_frame_width, target_frame_height))

        normalized_depth = cv2.normalize(result_frame, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        binary_map = cv2.cvtColor(binary_map, cv2.COLOR_BGR2GRAY)
        gaps = detect_gaps(binary_map)
        result_with_gaps = visualize_gaps(result_frame, gaps)

        # Put the image and the result side by side.
        stacked_frame = np.hstack((image, result_frame, result_with_gaps))
        # Save a frame to the video.
        out_video.write(stacked_frame)

        input_video_frame_nr = input_video_frame_nr + ADVANCE_FRAMES
        cap.set(1, input_video_frame_nr)


except KeyboardInterrupt:
    print("Processing interrupted.")
finally:
    processed_frames = num_frames // ADVANCE_FRAMES
    out_video.release()
    cap.release()
    end_time = time.perf_counter()
    duration = end_time - start_time

    print(
        f"Processed {processed_frames} frames in {duration:.2f} seconds. "
        f"Total FPS (including video processing): {processed_frames/duration:.2f}."
        f"Inference FPS: {processed_frames/total_inference_duration:.2f} "
    )
    print(f"Monodepth Video saved to '{str(result_video_path)}'.")