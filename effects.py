import cv2
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np
import pyaudio
from bgblur import blur_background
from matrix_filter import matrix_filter

# Initialize PyAudio
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                frames_per_buffer=1024,
                input_device_index=1)
current_color_index = -1  # Start with -1 so the first color selected is at index 0

# Function to get audio level
def get_audio_level():
    data = np.frombuffer(stream.read(1024, exception_on_overflow=False), dtype=np.int16)
    return np.abs(np.max(data) - np.min(data))

# Predefined strong colors: Red, Green, Blue, Cyan, Magenta, Yellow
strong_colors = [
    [255, 0, 0],  # Strong Red
    [0, 255, 0],  # Strong Green
    [0, 0, 255],  # Strong Blue
    [0, 255, 255],  # Cyan
    [255, 0, 255],  # Magenta
    [255, 255, 0],  # Yellow
]

# Function to select a color from the predefined list
def generate_strong_color():
    global current_color_index
    current_color_index = (current_color_index + 1) % len(strong_colors)
    return strong_colors[current_color_index]

# Global variable to store the current tint color
current_tint_color = [0, 0, 0]

# Set up the webcam
cap = cv2.VideoCapture(1)

# Updated function to apply filters
def apply_filter(frame, filter_name, audio_level):
    global current_tint_color

    if filter_name == "Black and White":
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
    elif filter_name == "Matrix Effect":
        frame = matrix_filter(frame)
    elif filter_name == "Audio Reactive":
        threshold = 5000
        if audio_level > threshold:
            current_tint_color = generate_strong_color()
        overlay = np.full(frame.shape, current_tint_color, dtype=np.uint8)
        cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)
    elif filter_name == "Blur Background":  # Handle the new filter
        frame = blur_background(frame)
    return frame

# Function to get frame from the webcam and apply selected filter
def show_frame():
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab a frame")
        return

    frame = cv2.flip(frame, 1)

    audio_level = get_audio_level()

    selected_filter = filter_var.get()
    frame = apply_filter(frame, selected_filter, audio_level)

    try:
        cvimg = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cvimg)
        imgtk = ImageTk.PhotoImage(image=img)
        lmain.imgtk = imgtk
        lmain.configure(image=imgtk)
    except cv2.error as e:
        print(f"OpenCV error: {e}")

    lmain.after(10, show_frame)

# Set up the tkinter window
root = tk.Tk()

# Dropdown menu for filter selection with the new option
filter_var = tk.StringVar()
filter_var.set("No Filter")
filter_dropdown = ttk.Combobox(root, textvariable=filter_var, state="readonly")
filter_dropdown['values'] = ("No Filter", "Black and White", "Matrix Effect", "Audio Reactive", "Blur Background") 
filter_dropdown.pack()

# Display area for the webcam output
lmain = tk.Label(root)
lmain.pack()

show_frame()
root.mainloop()

# Clean up
cap.release()
stream.stop_stream()
stream.close()
p.terminate()
