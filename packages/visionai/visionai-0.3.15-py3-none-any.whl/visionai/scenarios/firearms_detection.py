from rich import print
import time

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

class Event(str, Enum):
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    CRITICAL = 'CRITICAL'

class FirearmsDetection(Scenario):
    def __init__(self, scenario_name='firearms-detection', camera_name=0, events=None, triton_url=TRITON_HTTP_URL):

        from models.triton_client_yolov5 import yolov5_triton
        self.model = yolov5_triton(triton_url, scenario_name)
        self.f_event =  EventsEngine(use_redis=False)
        super().__init__(scenario_name, camera_name, events, triton_url)


    def start(self, camera_name=0, test = False):
        '''
        Stream processing

        When running a scenario - the caller can specify any specific camera.
        '''

        import cv2
        stream = camera_name

        print(f'Opening capture for {stream}')
        video = cv2.VideoCapture(stream)
        gun_count = 0
        knife_count = 0
        prev = time.time()
        while True:
            # Do processing
            ret, frame = video.read()
            if 'rtsp' in str(stream):
                frame_width = 640
                frame_height = 480
                frame = cv2.resize(frame, (frame_width, frame_height))
            if ret is False:
                LOGGER.error('ERROR: reading from video frame')
                time.sleep(1)
                continue

            # Detect smoke & fire
            results = self.model(frame, size=640)  # batched inference

            det = results.xyxy[0]

            if len(det):
                for *xyxy, conf, cls in reversed(det):
                    if int(cls.item()) == 0:
                        gun_count += 1

                    if int(cls.item()) == 1:
                        knife_count += 1

            if gun_count > 5:
                self.f_event.fire_event(Event.CRITICAL, 'WEBCAM', "arms-detection", 'GUN_DETECTED', {})
            if knife_count > 5:
                self.f_event.fire_event(Event.CRITICAL, 'WEBCAM', "arms-detection", 'KNIFE_DETECTED', {})


            results.print()
            results.show()

            if test == True:
                cur = time.time()
                print(cur-prev)
                if cur-prev >= 10:
                    return "10_SECS_RAN"
            if self.stop_evt.is_set():
                break

def camera_stream():
    snf = FirearmsDetection(scenario_name = 'firearms-detection')
    snf.start(camera_name=0)

if __name__ == '__main__':
    camera_stream()