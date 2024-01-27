import cv2
import numpy as np

# Global variables
edges_buffer = []  # Buffer to store edges from the last 5 frames
previous_frame_gray = None  # Store the previous frame for frame differencing

def matrix_filter(frame):
    global edges_buffer, previous_frame_gray

    # Convert current frame to grayscale
    current_frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Increase contrast
    alpha = 1.5  # Contrast control
    beta = 0  # Brightness control
    adjusted = cv2.convertScaleAbs(current_frame_gray, alpha=alpha, beta=beta)

    # Apply a slight blur
    blurred = cv2.GaussianBlur(adjusted, (3, 3), 0)

    # Perform edge detection

    edges = cv2.Canny(blurred, 25, 75)

    # Frame differencing to detect significant movement
    if previous_frame_gray is not None:
        frame_diff = cv2.absdiff(current_frame_gray, previous_frame_gray)
        _, motion_mask = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)

        # If significant movement is detected, prioritize the current edges
        if np.sum(motion_mask) > 0.01 * motion_mask.size * 255:
            edges_buffer = [edges for _ in range(len(edges_buffer))]


    # Update the previous frame
    previous_frame_gray = current_frame_gray.copy()

    # Add the current edges to the buffer
    edges_buffer.append(edges)
    if len(edges_buffer) > 3:
        edges_buffer.pop(0)

    # Compute the average of the edges in the buffer
    edges_avg = np.mean(edges_buffer, axis=0).astype(np.uint8)

    # Threshold the averaged edges to make them binary
    _, edges_avg_binary = cv2.threshold(edges_avg, 127, 255, cv2.THRESH_BINARY)

    # Set the entire frame to black
    frame[:] = [0, 0, 0]

    # Apply green color only to the averaged edges
    frame[edges_avg_binary == 255] = [0, 255, 0]

    return frame
