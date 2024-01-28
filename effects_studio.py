import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer
from background import blur_background, greenscreen_background
from matrix_filter import matrix_filter
from face_filter import face_tracking_filter
from audio_filter import audio_reactive_filter
from time_filter import TimeSliceFilter

time_slice_filter = TimeSliceFilter()

class CameraApp(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_filters = []
        self.initUI()
        self.initCamera()

    def initUI(self):
        self.setWindowTitle("Camera Filters")

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.image_label = QLabel(self)
        layout.addWidget(self.image_label)

        # List for selecting multiple filters
        self.filter_list = QListWidget(self)
        self.filter_list.addItems(["Black and White", "Matrix Effect", "Audio Reactive",
                                   "Blur Background", "Green Screen", "Face Tracking",
                                   "Time Slice"])
        self.filter_list.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.filter_list)

        # Buttons for reordering filters
        button_layout = QHBoxLayout()
        self.up_button = QPushButton('Move Up', self)
        self.up_button.clicked.connect(self.moveUp)
        button_layout.addWidget(self.up_button)

        self.down_button = QPushButton('Move Down', self)
        self.down_button.clicked.connect(self.moveDown)
        button_layout.addWidget(self.down_button)

        layout.addLayout(button_layout)

        # Button to apply selected filters
        self.apply_button = QPushButton('Apply Filters', self)
        self.apply_button.clicked.connect(self.applySelectedFilters)
        layout.addWidget(self.apply_button)

    def initCamera(self):
        self.cap = cv2.VideoCapture(1)  # Change to 0 if your webcam index is different
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateFrame)
        self.timer.start(20)

    def applySelectedFilters(self):
        self.selected_filters = [self.filter_list.item(i).text() for i in range(self.filter_list.count()) 
                                 if self.filter_list.item(i).isSelected()]

    def moveUp(self):
        current_row = self.filter_list.currentRow()
        if current_row >= 1:
            self.filter_list.insertItem(current_row - 1, self.filter_list.takeItem(current_row))
            self.filter_list.setCurrentRow(current_row - 1)

    def moveDown(self):
        current_row = self.filter_list.currentRow()
        if current_row < self.filter_list.count() - 1:
            self.filter_list.insertItem(current_row + 1, self.filter_list.takeItem(current_row))
            self.filter_list.setCurrentRow(current_row + 1)

    def updateFrame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            for filter_name in self.selected_filters:
                frame = self.apply_filter(frame, filter_name)

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qimg = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            self.image_label.setPixmap(QPixmap.fromImage(qimg))

    def apply_filter(self, frame, filter_name):
        if filter_name == "Black and White":
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        elif filter_name == "Matrix Effect":
            frame = matrix_filter(frame)
        elif filter_name == "Audio Reactive":
            frame = audio_reactive_filter(frame)
        elif filter_name == "Blur Background":
            frame = blur_background(frame)
        elif filter_name == "Green Screen":
            frame = greenscreen_background(frame)
        elif filter_name == "Face Tracking":
            frame = face_tracking_filter(frame, "images/face_mask.png")
        elif filter_name == "Time Slice":
            frame = time_slice_filter.process_frame(frame)
        return frame
    
    def apply_filters_to_video(self, input_file, output_file, selected_filters):
        # Open the input video file
        cap = cv2.VideoCapture(input_file)
        if not cap.isOpened():
            print(f"Error: Could not open video {input_file}")
            return

        # Get video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Calculate frame numbers for progress updates
        progress_markers = {
            "25%": total_frames * 0.25,
            "50%": total_frames * 0.50,
            "75%": total_frames * 0.75
        }

        # Define the codec and create a VideoWriter object to write the output video
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))

        current_frame = 0  # Current frame counter

        # Process the video frame by frame
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Apply selected filters
            for filter_name in selected_filters:
                frame = self.apply_filter(frame, filter_name)

            # Write the frame to the output video
            out.write(frame)

            # Check for progress
            for progress, frame_number in progress_markers.items():
                if current_frame == int(frame_number):
                    print(f"Processing is {progress} complete.")

            current_frame += 1

        # Release resources
        cap.release()
        out.release()
        print(f"Video processing complete. Output saved as {output_file}")

    def closeEvent(self, event):
        self.cap.release()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CameraApp()
    if len(sys.argv) > 1:  # Command line arguments were provided
        input_video = sys.argv[1]
        output_video = sys.argv[2]
        # Combine all remaining arguments into a single string and split on commas
        filters_to_apply = ' '.join(sys.argv[3:]).split(',')
        ex.apply_filters_to_video(input_video, output_video, filters_to_apply)
    else:  # No command line arguments, launch the GUI
        ex.show()
        sys.exit(app.exec_())