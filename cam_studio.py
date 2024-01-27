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

    def closeEvent(self, event):
        self.cap.release()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CameraApp()
    ex.show()
    sys.exit(app.exec_())
