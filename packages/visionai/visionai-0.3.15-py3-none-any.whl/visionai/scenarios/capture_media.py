import time
import cv2
import numpy as np
import sys
from pathlib import Path
FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # visionai/visionai directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH

from util.general import LOGGER
from scenarios import Scenario
from config import TRITON_HTTP_URL

from events.events_engine import EventsEngine
from enum import Enum
from models.plots import Annotator
import threading


class Event(str, Enum):
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    CRITICAL = 'CRITICAL'

class CaptureMediaScenario(Scenario):
    line_thickness=3
    def __init__(self, scenario_name = 'occupancy-monitoring', camera_name=0, events=None, triton_url=TRITON_HTTP_URL):

        threading.Thread.__init__(self)

        from models.triton_client_yolov5 import yolov5_triton
        self.model = yolov5_triton(triton_url, scenario_name)
        self.f_event =  EventsEngine(use_redis=False)
        super().__init__(scenario_name, camera_name, events, triton_url)

    def draw_boxes(self, img, bbox, count, total_time, offset=(0, 0)):
        for i, box in enumerate(bbox):
            x1, y1, x2, y2 = [int(i) for i in box]
            x1 += offset[0]
            x2 += offset[0]
            y1 += offset[1]
            y2 += offset[1]
            data = (int((box[0]+box[2])/2),(int((box[1]+box[3])/2)))
            label = f"ID: {str(count)} - Duration: {str(int(total_time))}"

            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
            cv2.rectangle(img, (x1, y1), (x2, y2),(255,191,0), 2)
            cv2.rectangle(img, (x1, y1 - 20), (x1 + w, y1), (255,191,0), -1)
            cv2.putText(img, label, (x1, y1 - 5),cv2.FONT_HERSHEY_SIMPLEX, 0.6, 
            [255, 255, 255], 1)
            cv2.circle(img, data, 3, (255,191,0),-1)
        return img
    
    def create_video(self, filename, framesize):
        out = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*'DIVX'), 10, framesize)
        return out


    def start(self, camera_name=0, test=False):
        '''
        Stream processing

        When running a scenario - the caller can specify any specific camera.
        '''

        stream = camera_name

        print(f'Opening capture for {stream}')
        video = cv2.VideoCapture(stream)
        person_count = 0
        prev = time.time()
        prev_frame = 0
        count = 0
        no_motion = 0
        clip = False
        initiate_clip =  True
        frames = []
        motion = 0
        while True:
            count += 1
            # Do processing
            ret, frame = video.read()
            height, width, _ = frame.shape

            if initiate_clip == True:
                print("initiation New Clip")
                video_file_name = time.strftime("%Y%m%d-%H%M%S") + ".avi"
                out = self.create_video("visionai/media/videos/" + video_file_name, (width, height))
                initiate_clip = False

            if ret is False:
                LOGGER.error('ERROR: reading from video frame')
                time.sleep(1)
                continue

            # Detect smoke & fire
            results = self.model(frame, size=640)  # batched inference

            det = results.xyxy[0]
            annotator = Annotator(frame.copy(), line_width=self.line_thickness)

            if len(det):
              for *xyxy, conf, cls in reversed(det):
                    if int(cls.item()) == 0:
                        person_count += 1
                        annotator.box_label(xyxy, "person")

            if person_count > 5:
                file_name = time.strftime("%Y%m%d-%H%M%S")
                cv2.imwrite("visionai/media/images/person_detected_" + file_name + ".jpg", frame)
                self.f_event.fire_event(Event.WARNING, 'WEBCAM', "Person-Detected", 'PERSON_DETECTED', {})

            if count > 100:
                file_name = time.strftime("%Y%m%d-%H%M%S")
                cv2.imwrite("visionai/media/images/" + file_name + ".jpg", frame)
                count = 0
            
            diff = cv2.absdiff(frame, prev_frame)
            prev_frame = frame
            diff_sum = diff.flatten().sum()

            if diff_sum > 2500000:
                motion += 1
            else:
                no_motion += 1
            
            if motion >= 4:
                frames.append(frame)

            # if diff_sum > 4500000:
            #     print("Adding Frames")
            #     frames.append(frame)
            #     # self.f_event.fire_event(Event.WARNING, 'WEBCAM', "Motion-Detected", 'MOTION_DETECTED', {})
            # else:
            #     no_motion += 1

            print(motion, no_motion)

            if no_motion > 60 and len(frames) > 60:
                print("New Video Created")
                self.f_event.fire_event(Event.WARNING, 'WEBCAM', "Motion-Detected", 'MOTION_DETECTED', {})
                for frame in frames:
                    out.write(frame)
                out.release()
                initiate_clip = True
                no_motion = 0
                frames = []
                motion = 0

            if test == True:
                cur = time.time()
                if cur-prev >= 10:
                    return "10_SECS_RAN"

            cv2.imshow('Output', frame)
            key = cv2.waitKey(5)
            if key == 27:
                import sys
                print('Exiting.')
                sys.exit(0)
            if self.stop_evt.is_set():
                break


def camera_stream():
    snf = CaptureMediaScenario(scenario_name = 'occupancy-monitoring')
    snf.start(camera_name=0)

if __name__ == '__main__':
    camera_stream()