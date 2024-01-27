import cv2
import numpy as np
import pyaudio

# Initialize PyAudio
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024, input_device_index=1)

# Predefined strong colors: Red, Green, Blue, Cyan, Magenta, Yellow
strong_colors = [
    [255, 0, 0],  # Strong Red
    [0, 255, 0],  # Strong Green
    [0, 0, 255],  # Strong Blue
    [0, 255, 255],  # Cyan
    [255, 0, 255],  # Magenta
    [255, 255, 0],  # Yellow
]

current_color_index = -1  # Start with -1 so the first color selected is at index 0

def generate_strong_color():
    global current_color_index
    current_color_index = (current_color_index + 1) % len(strong_colors)
    return strong_colors[current_color_index]

def get_audio_level():
    data = np.frombuffer(stream.read(1024, exception_on_overflow=False), dtype=np.int16)
    return np.abs(np.max(data) - np.min(data))

def audio_reactive_filter(frame):
    audio_level = get_audio_level()

    threshold = 5000
    if audio_level > threshold:
        current_tint_color = generate_strong_color()
    else:
        current_tint_color = [0, 0, 0]  # Default color when below threshold

    overlay = np.full(frame.shape, current_tint_color, dtype=np.uint8)
    return cv2.addWeighted(overlay, 0.4, frame, 0.6, 0)
