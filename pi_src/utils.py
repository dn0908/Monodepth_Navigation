import cv2
import time


class SimpleFPS:
    def __init__(self):
        self.start_time = time.time()
        self.display_time_sec = 1  # update fps display
        self.fps = 0
        self.frame_counter = 0
        self.is_fps_updated = False

    def get_fps(self):
        elapsed = time.time() - self.start_time
        self.frame_counter += 1
        is_fps_updated = False

        if elapsed > self.display_time_sec:
            self.fps = self.frame_counter / elapsed
            self.frame_counter = 0
            self.start_time = time.time()
            is_fps_updated = True

        return int(self.fps), is_fps_updated


def draw_fps(img, fps):
    ##font = cv2.FONT_HERSHEY_SIMPLEX
    #font = cv2.FONT_HERSHEY_SIMPLEX
    ## putting the FPS count on the frame
    #cv2.putText(img, str(fps), (7, 70), font, 3, (100, 255, 0), 3, cv2.LINE_AA)
    print(fps)
