import cv2

# Global variable to store the previous frame's edges
previous_edges = None

def matrix_filter(frame):
    global previous_edges

    # Increase contrast
    alpha = 1.5  # Contrast control
    beta = 0  # Brightness control
    adjusted = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)

    # Apply a slight blur
    blurred = cv2.GaussianBlur(adjusted, (3, 3), 0)

    # Perform edge detection
    edges = cv2.Canny(blurred, 50, 150)

    # Combine current edges with previous edges for smoothing
    if previous_edges is not None:
        # Use a weighted sum to combine current edges with previous ones
        # Adjust the weights to control the amount of smoothing
        edges = cv2.addWeighted(edges, 0.7, previous_edges, 0.3, 0)

    # Update the previous edges
    previous_edges = edges.copy()

    # Apply the edge mask to the original frame
    frame = cv2.bitwise_and(frame, frame, mask=edges)

    # Highlight edges in green
    frame[edges == 255] = [0, 255, 0]

    return frame
