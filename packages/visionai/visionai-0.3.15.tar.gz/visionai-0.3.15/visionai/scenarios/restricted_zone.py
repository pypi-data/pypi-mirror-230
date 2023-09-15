from rich import print
import time

import sys
import cv2
import time

from pathlib import Path
FILE = Path(__file__).resolve()
ROOT = FILE.parents[1]  # visionai/visionai directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH

from util.general import LOGGER
from scenarios import Scenario
from config import TRITON_HTTP_URL
from util.track import *

from events.events_engine import EventsEngine
from models.plots import Annotator

from enum import Enum

class Event(str, Enum):
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    CRITICAL = 'CRITICAL'

class RestrictedZone(Scenario):
    alert_time = 10
    line_thickness = 3
    def __init__(self, scenario_name='restricted-zone', camera_name=0, events=None, triton_url=TRITON_HTTP_URL):

        from models.triton_client_yolov5 import yolov5_triton
        self.model = yolov5_triton(triton_url, scenario_name)
        self.f_event =  EventsEngine(use_redis=False)
        self.line_thickness=3
        super().__init__(scenario_name, camera_name, events, triton_url)


    def start(self, camera_name=0, test = False):
        '''
        Stream processing

        When running a scenario - the caller can specify any specific camera.
        '''

        stream = camera_name

        print(f'Opening capture for {stream}')
        video = cv2.VideoCapture(stream)

        prev = time.time()
        person_count = 0
        no_person = 0
        while True:
            is_person = False

            # Do processing
            ret, frame = video.read()
            if 'rtsp' in str(stream):
                frame_width = 640
                frame_height = 480
                frame = cv2.resize(frame, (frame_width, frame_height))
            # fps = video.get(cv2.CAP_PROP_FPS)
            if ret is False:
                LOGGER.error('ERROR: reading from video frame')
                time.sleep(1)
                continue

            # Detect smoke & fire
            results = self.model(frame, size=640)  # batched inference

            det = results.xyxy[0]

            annotator = Annotator(frame, line_width=self.line_thickness)
            if len(det):
                for *xyxy, conf, cls in reversed(det):
                    if int(cls) == 0:
                        annotator.box_label(xyxy, "Person")
                        is_person = True
            
            if is_person ==  True:
                no_person = 0
                person_count += 1
            else:
                no_person += 1
                
            if no_person > 10:
                person_count = 0

            if person_count >= 10:
                self.f_event.fire_event(Event.CRITICAL, 'WEBCAM', "restricted-zone", 'NOT-ALLOWED')

                    
            cv2.imshow('Output', frame)
            key = cv2.waitKey(5)
            if key == 27:
                import sys
                print('Exiting.')
                sys.exit(0)                                     
                        
            results.print()
            if test == True:
                cur = time.time()
                # print(cur-prev)
                if cur-prev >= 10:
                    return "10_SECS_RAN"

            if self.stop_evt.is_set():
                break

def camera_stream():
    snf = RestrictedZone(scenario_name = 'restricted-zone')
    snf.start(camera_name=0)

if __name__ == '__main__':
    camera_stream()