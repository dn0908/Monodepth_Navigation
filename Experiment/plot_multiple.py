import numpy as np
import cv2
import matplotlib.pyplot as plt

# Step 1: Extract marker positions
def extract_marker_positions(frame_positions, marker_ids):
    """
    Extracts positions of specified marker IDs from frame_positions.
    """
    marker_positions = {}
    for marker_id, position in frame_positions:
        if marker_id in marker_ids:
            marker_positions[marker_id] = position
    return marker_positions

# Step 2: Extract pixel positions of corner markers
def extract_corner_positions(corner_positions):
    """
    Extracts pixel positions of the corner markers in clockwise order:
    ID 10 (top-left), 20 (top-right), 30 (bottom-right), 40 (bottom-left).
    """
    corner_order = [10, 20, 30, 40]
    pixel_corners = []
    for marker_id in corner_order:
        if marker_id in corner_positions:
            pixel_corners.append(corner_positions[marker_id])
        else:
            raise ValueError(f"Marker ID {marker_id} not detected in corner positions!")
    return np.array(pixel_corners, dtype=np.float32)

# Step 3: Compute homography matrix
def compute_homography(pixel_corners, ground_size):
    """
    Computes homography matrix for mapping pixel coordinates to ground plane coordinates.
    """
    ground_corners = np.array([
        [0, 0],  # Top-left
        [ground_size[0], 0],  # Top-right
        [ground_size[0], ground_size[1]],  # Bottom-right
        [0, ground_size[1]],  # Bottom-left
    ], dtype=np.float32)
    homography_matrix, _ = cv2.findHomography(pixel_corners, ground_corners)
    return homography_matrix

# Step 4: Transform positions using homography
def transform_positions(homography_matrix, positions):
    positions = np.array(positions, dtype=np.float32).reshape(-1, 1, 2)
    transformed = cv2.perspectiveTransform(positions, homography_matrix)
    return transformed.reshape(-1, 2)

# Step 5: Plot the trajectories
def plot_trajectories(ground_size, robot_trajectories, obstacle_positions, trajectory_colors):
    plt.rcParams["font.family"] = "Times New Roman"
    fig, ax = plt.subplots()
    ax.set_xlim(0, ground_size[0])
    ax.set_ylim(0, ground_size[1])
    ax.set_aspect('equal', adjustable='box')
    ax.invert_yaxis()

    # Draw ground rectangle
    ax.add_patch(plt.Rectangle((0, 0), ground_size[0], ground_size[1], fill=None, edgecolor='yellowgreen', label="Ground"))

    # Plot obstacles
    for obs_id, pos in obstacle_positions.items():
        ax.add_patch(plt.Circle(pos, 5, color='lightcoral', label=f"Obstacle {obs_id}"))
        ax.text(pos[0], pos[1], f"Obstacle {obs_id}", color='black', fontsize=10)

    # Plot robot trajectories
    for idx, (robot_positions, color) in enumerate(zip(robot_trajectories, trajectory_colors)):
        if len(robot_positions) > 0:
            robot_x, robot_y = zip(*robot_positions)
            ax.plot(robot_x, robot_y, label=None, color=color)

    # Customize the plot
    plt.legend(fontsize=8)
    plt.title('Result Trajectory', fontsize=12)
    plt.xlabel('Width (cm)', fontsize=10)
    plt.ylabel('Height (cm)', fontsize=10)
    plt.grid()
    plt.show()

# Step 6: Main script
if __name__ == "__main__":
    # File paths
    files = ['01.npy', '02.npy', '03.npy', '04.npy', '05.npy', '06.npy']  # Add all file names here

    # Known dimensions of the ground plane (cm)
    ground_size = (75.5, 95)  # Width x Height in cm

    # Marker IDs
    corner_ids = [10, 20, 30, 40]
    robot_id = 100
    obstacle_ids = [1, 2, 3]

    # Trajectories and colors
    robot_trajectories = []
    trajectory_colors = ['steelblue', 'steelblue', 'steelblue', 'steelblue', 'steelblue', 'steelblue']  # Colors for each trajectory

    # Process the first file for obstacles and homography
    frame_positions = np.load(files[0], allow_pickle=True)
    corner_positions = extract_marker_positions(frame_positions, corner_ids)
    if len(corner_positions) < 4:
        raise ValueError("Not all four corner markers were detected in the first file!")
    pixel_corners = extract_corner_positions(corner_positions)
    homography_matrix = compute_homography(pixel_corners, ground_size)

    # Process obstacles from the first file
    obstacle_positions = {}
    for marker_id, pixel_position in frame_positions:
        if marker_id in obstacle_ids:
            obstacle_positions[marker_id] = transform_positions(homography_matrix, [pixel_position])[0]

    # Process robot trajectories from all files
    for file in files:
        frame_positions = np.load(file, allow_pickle=True)
        robot_positions = [pixel_position for marker_id, pixel_position in frame_positions if marker_id == robot_id]
        robot_positions = transform_positions(homography_matrix, robot_positions)
        robot_trajectories.append(robot_positions)

    # Plot all trajectories with obstacles
    plot_trajectories(ground_size, robot_trajectories, obstacle_positions, trajectory_colors)
