import cv2
import numpy as np
import random

# Global variables
edges_buffer = []  # Buffer to store edges
previous_frame_gray = None  # Store the previous frame for frame differencing
matrix_streams = []  # List to track active matrix streams
frame_count = 0  # Frame counter for consistent number display

def matrix_filter(frame, enable_rain_effect=False):
    global edges_buffer, previous_frame_gray, matrix_streams, frame_count

    # Matrix stream parameters
    max_stream_length = 20  # Maximum length of a stream
    stream_chance = 0.0075    # Chance of a new stream starting
    stream_fall_speed = 1   # Number of pixels the stream falls per frame
    number_change_frequency = 5  # Frequency of number changes within the stream
    min_font_scale = 0.3  # Minimum font scale
    max_font_scale = 0.6  # Maximum font scale

    # Convert current frame to grayscale
    current_frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Increase contrast
    alpha = 1.5
    beta = 0
    adjusted = cv2.convertScaleAbs(current_frame_gray, alpha=alpha, beta=beta)

    # Apply a slight blur
    blurred = cv2.GaussianBlur(adjusted, (3, 3), 0)

    # Perform edge detection
    edges = cv2.Canny(blurred, 25, 75)

    previous_frame_gray = current_frame_gray.copy()
    edges_buffer.append(edges)
    if len(edges_buffer) > 3:
        edges_buffer.pop(0)

    edges_avg = np.mean(edges_buffer, axis=0).astype(np.uint8)
    _, edges_avg_binary = cv2.threshold(edges_avg, 127, 255, cv2.THRESH_BINARY)

    # Set the entire frame to black
    frame[:] = [0, 0, 0]

    # Apply green color only to the averaged edges
    frame[edges_avg_binary == 255] = [0, 255, 0]

    # Matrix rain effect
    if enable_rain_effect:
        # Update existing streams
        new_streams = []
        for x, y, length, numbers, font_scale in matrix_streams:
            if y < frame.shape[0]:
                new_streams.append((x, y + stream_fall_speed, length, numbers, font_scale))  # Move stream down

        matrix_streams = new_streams

        # Start new streams
        for j in range(0, frame.shape[1], 12):
            if random.random() < stream_chance:
                stream_length = random.randint(5, max_stream_length)
                stream_numbers = [str(random.randint(0, 1)) for _ in range(stream_length)]
                stream_font_scale = random.uniform(min_font_scale, max_font_scale)  # Random font scale
                matrix_streams.append((j, 0, stream_length, stream_numbers, stream_font_scale))

        # Draw the streams
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_thickness = 1

        for x, y, length, numbers, font_scale in matrix_streams:
            for i, number in enumerate(numbers):
                if y + i * 12 < frame.shape[0]:
                    text_color = (0, random.randint(100, 255), 0)
                    if frame_count % number_change_frequency == 0:
                        numbers[i] = str(random.randint(0, 1))
                    cv2.putText(frame, number, (x, y + i * 12), font, font_scale, text_color, font_thickness, cv2.LINE_AA)

    frame_count += 1
    return frame
