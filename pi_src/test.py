from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap
import sys
import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
import numpy as np
from picamera2 import Picamera2
from utils import SimpleFPS , draw_fps
import argparse
import time


class VideoThreadPiCam(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self.grab_frame = True

    def run(self):
        # capture from web cam
        picam2 = Picamera2()
        # camera_config = picam2.create_still_configuration(main={"size": (640, 480)}, lores={"size": (640, 480)}, display="lores")
        camera_config = picam2.create_video_configuration(main={"size":(640,480),"format":"RGB888"}, raw={"size": (640, 480)})
        picam2.configure(camera_config)
        picam2.start()

        while True:
            if self.grab_frame:
                frame = picam2.capture_array()
                self.change_pixmap_signal.emit(frame)
                self.grab_frame = False
            else:
                time.sleep(0.0001)


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Qt UI")
        self.disply_width = 640
        self.display_height = 480
        # create the label that holds the image
        self.image_label = QLabel(self)
        self.image_label.resize(self.disply_width, self.display_height)

        self.fps_util = SimpleFPS()

        # create the video capture thread
        self.thread = VideoThreadPiCam()
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        # start the thread
        self.thread.start()

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        # cv_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB) 
        display_img = cv_img
        fps, _ = self.fps_util.get_fps()
        draw_fps(display_img, fps)

        qt_img = self.convert_cv_qt(display_img)
        self.image_label.setPixmap(qt_img)
        self.thread.grab_frame = True

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        # rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        rgb_image = cv_img

        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.disply_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)


def run_no_ui():
    # capture from web cam
    picam2 = Picamera2()
    camera_config = picam2.create_video_configuration(main={"size":(640,480),"format":"RGB888"}, raw={"size": (640, 480)})
    picam2.configure(camera_config)
    picam2.start()

    fps_util = SimpleFPS()

    while True:
        frame = picam2.capture_array()

        fps, is_updated = fps_util.get_fps()
        if is_updated:
            print(fps)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--camera_test', action=argparse.BooleanOptionalAction)
    args = parser.parse_args()
    

    if args.camera_test:
        app = QApplication(sys.argv)
        a = App()
        a.show()
        sys.exit(app.exec_())
    else:
        app = QApplication(sys.argv)
        a = App()
        a.show()
        sys.exit(app.exec_())
