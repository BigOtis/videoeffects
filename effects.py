import cv2
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np 

# Set up the webcam
cap = cv2.VideoCapture(1)  # Change index as needed

# Function to apply filters
def apply_filter(frame, filter_name):
    if filter_name == "Black and White":
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)  # Convert back to BGR for compatibility
    elif filter_name == "Matrix Effect":
        # Convert to grayscale for edge detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Apply GaussianBlur to reduce image noise in the edge detection input
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        # Optimized Canny edge detection parameters for human faces
        edges = cv2.Canny(blurred, 30, 90)  # Adjust these values as needed for your specific use case
        # Create a mask from the edges
        mask = edges != 0
        # Create a matrix-like effect with green edges on a black background
        frame = np.zeros_like(frame)
        frame[mask] = [0, 255, 0]  # Set edges to green
    return frame

# Function to get frame from the webcam and apply selected filter
def show_frame():
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab a frame")
        return

    frame = cv2.flip(frame, 1)

    # Get selected filter from dropdown and apply
    selected_filter = filter_var.get()
    frame = apply_filter(frame, selected_filter)

    try:
        cvimg = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        img = Image.fromarray(cvimg)
        imgtk = ImageTk.PhotoImage(image=img)
        lmain.imgtk = imgtk  # Keep a reference, prevent garbage collection
        lmain.configure(image=imgtk)
    except cv2.error as e:
        print(f"OpenCV error: {e}")

    lmain.after(10, show_frame)

# Set up the tkinter window
root = tk.Tk()

# Dropdown menu for filter selection
filter_var = tk.StringVar()
filter_var.set("No Filter")  # default value
filter_dropdown = ttk.Combobox(root, textvariable=filter_var, state="readonly")
filter_dropdown['values'] = ("No Filter", "Black and White", "Matrix Effect")
filter_dropdown.pack()

# Display area for the webcam output
lmain = tk.Label(root)
lmain.pack()

show_frame()
root.mainloop()
