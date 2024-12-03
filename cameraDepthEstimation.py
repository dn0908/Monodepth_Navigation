import cv2
import numpy as np
from MidasDepthEstimation.midasDepthEstimator import midasDepthEstimator

# Initialize depth estimation model
depthEstimator = midasDepthEstimator()

# variables
input_video_frame_nr = 0
start_time = time.perf_counter()
total_inference_duration = 0

# Initialize webcam
camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)
# cv2.namedWindow("Depth Image", cv2.WINDOW_NORMAL)

out_video = cv2.VideoWriter(
        "output.mp4",
        cv2.VideoWriter_fourcc(*"mp4v"),
        10,
        (2592 * 3, 1944),
    )

while True:

	# Read frame from the webcam
	ret, img = camera.read()	

    ###################################################################
    inference_start_time = time.perf_counter()
    
	# Estimate depth
	colorDepth = depthEstimator.estimateDepth(img)
    
    inference_stop_time = time.perf_counter()
    inference_duration = inference_stop_time - inference_start_time
    print("Inference time : ", inference_duration, "s")
    total_inference_duration += inference_duration
    ###################################################################

	# Add the depth image over the color image:
	combinedImg = cv2.addWeighted(img,0.7,colorDepth,0.6,0)

	# Join the input image, the estiamted depth and the combined image
	img_out = np.hstack((img, colorDepth, combinedImg))

    out_video.write(img_out)

	# cv2.imshow("Depth Image", img_out)

	# Press key q to stop
	if cv2.waitKey(1) == ord('q'):
		break

camera.release()
# cv2.destroyAllWindows()