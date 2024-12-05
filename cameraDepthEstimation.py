import cv2
import numpy as np
import time
from MidasDepthEstimation.midasDepthEstimator import midasDepthEstimator

# Initialize depth estimation model
depthEstimator = midasDepthEstimator()

# variables
input_video_frame_nr = 0
start_time = time.perf_counter()
total_inference_duration = 0

# Initialize webcam
camera = cv2.VideoCapture(0)

# cv2.namedWindow("Depth Image", cv2.WINDOW_NORMAL)
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out_video = cv2.VideoWriter(
        "output.mp4",
        fourcc,
        1,
        (512, 256),
    )
video_start_time = time.perf_counter()

while True:
    if time.perf_counter() - video_start_time >= 50:
        break
    # Read frame from the webcam
    ret, img = camera.read()
    img = cv2.resize(img, (256, 256))
    ###################################################################
    inference_start_time = time.perf_counter()
    # Estimate depth
    colorDepth = depthEstimator.estimateDepth(img)
    inference_stop_time = time.perf_counter()
    inference_duration = inference_stop_time - inference_start_time
    print("Inference time : ", inference_duration, "s")
    total_inference_duration += inference_duration
    # time.sleep(1.5)
    ###################################################################
    # # Add the depth image over the color image:
    combinedImg = cv2.addWeighted(img,0.7,colorDepth,0.6,0)
    # Join the input image, the estiamted depth and the combined image
    #img_out = np.hstack((img, colorDepth, combinedImg))
    img_out = np.hstack((img, colorDepth))
    cv2.resize(img_out, (512, 256))
    out_video.write(img_out)
    # cv2.imshow("Depth Image", img_out)
    # # Press key q to stop
    if cv2.waitKey(1) == ord('q'):
        break

camera.release()
# cv2.destroyAllWindows()
# out_video.release()