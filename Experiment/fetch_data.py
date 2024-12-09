import cv2
import numpy as np
from utils import ARUCO_DICT, aruco_display
import time
import sys

# Load video
video_path = '06.mp4'
cap = cv2.VideoCapture(video_path)

# Define ARUCO dictionary and parameters
arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_5X5_1000)
arucoParams = cv2.aruco.DetectorParameters_create()

# Initialize data storage
frame_positions = []

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    h, w, _ = frame.shape
    width = 1000
    height = int(width*(h/w))
    frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_CUBIC)
    corners, ids, rejected = cv2.aruco.detectMarkers(frame, arucoDict, parameters=arucoParams)
    detected_markers = aruco_display(corners, ids, rejected, frame)
    if ids is not None:
        for i, marker_id in enumerate(ids.flatten()):
            center = np.mean(corners[i][0], axis=0)
            frame_positions.append((marker_id, center))

    cv2.imshow("Image", detected_markers)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

# Save the detected positions for further analysis
np.save('06.npy', frame_positions)
