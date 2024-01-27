import cv2
import numpy as np
from collections import deque

class TimeSliceFilter:
    def __init__(self, buffer_size=30):
        # buffer_size determines how many past frames are stored
        self.frame_buffer = deque(maxlen=buffer_size)
        self.buffer_size = buffer_size

    def process_frame(self, frame):
        # Add current frame to the buffer
        self.frame_buffer.appendleft(frame.copy())

        # If buffer isn't full yet, just return the original frame
        if len(self.frame_buffer) < self.buffer_size:
            return frame

        # Create an output frame composed of slices from different time frames
        output_frame = np.zeros_like(frame)
        slice_height = frame.shape[0] // self.buffer_size

        for i in range(self.buffer_size):
            slice_start = i * slice_height
            slice_end = (i + 1) * slice_height if i < self.buffer_size - 1 else frame.shape[0]
            output_frame[slice_start:slice_end, :] = self.frame_buffer[i][slice_start:slice_end, :]

        return output_frame
