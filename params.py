import cv2
from pathlib import Path

# Video
VIDEO_FILE = "/img/241115_recording1.mp4"
NUM_SECONDS = 10
ADVANCE_FRAMES = 2
SCALE_OUTPUT = 0.5
FOURCC = cv2.VideoWriter_fourcc(*"mp4v")
output_directory = Path("output")
output_directory.mkdir(exist_ok=True)
result_video_path = output_directory / f"{Path(VIDEO_FILE).stem}_monodepth.mp4"

# Gap Detection
threshold_value = 100
safety_distance = 100

# Function to detect gaps
def detect_gaps(binary_map):
    height, width = binary_map.shape
    horizontal_line = binary_map[height // 2]  # Define horizontal line at middle
    gaps = []
    current_gap = None

    for i, value in enumerate(horizontal_line):
        if value == 0:  # Free space
            if current_gap is None:
                current_gap = [i, i]
            else:
                current_gap[1] = i
        elif current_gap is not None:
            gaps.append(current_gap)
            current_gap = None

    if current_gap is not None:
        gaps.append(current_gap)

    return gaps

# Function to visualize gaps as rectangles on the depth image
def visualize_gaps(result_image, gaps):
    image_with_rectangles = result_image.copy()
    height, width, _ = image_with_rectangles.shape

    for gap in gaps:
        x1, x2 = gap
        cv2.rectangle(
            image_with_rectangles,
            (x1, height // 2 - 10),  # Top-left corner of rectangle
            (x2, height // 2 + 10),  # Bottom-right corner of rectangle
            (255, 50, 50),  # Color (green)
            2,  # Line thickness
        )
    return image_with_rectangles