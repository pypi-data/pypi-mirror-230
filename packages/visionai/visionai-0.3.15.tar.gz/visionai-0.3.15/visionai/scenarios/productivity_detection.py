from rich import print
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
from enum import Enum

class Event(str, Enum):
    DEBUG = 'DEBUG'
    INFO = 'INFO'
    WARNING = 'WARNING'
    ERROR = 'ERROR'
    CRITICAL = 'CRITICAL'

class ProductivityMonitoring(Scenario):
    alert_time = 10
    def __init__(self, scenario_name, camera_name=0, events=None, triton_url=TRITON_HTTP_URL):
        from models.triton_client_yolov5 import yolov5_triton
        self.model = yolov5_triton(triton_url, scenario_name)
        self.f_event =  EventsEngine(use_redis=False)
        self.line_thickness=3
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

    def start(self, camera_name=0):
        '''
        Stream processing
        When running a scenario - the caller can specify any specific camera.
        '''
        # pickup_region = [(0,0),(600,0),(600,1080),(0,1080)]
        # drop_region = [(1250,0),(1980,0),(1980,1080),(1250,1080)]
        table_region = [(300,0),(340,0),(340,480),(300,480)] # webcam
        stream = camera_name
        object_class = 39 # 0=Person, 39=bottle, 69=cell phone
        event_fire_threshold = 40
        text_font = 0.5
        text_thickness = 1
        shipping_threshold = 30
        print(f'Opening capture for {stream}')
        video = cv2.VideoCapture(stream)
        info_dic = {}
        objects = set()
        sort_max_age = 5
        sort_min_hits = 2
        sort_iou_thresh = 0.2
        sort_tracker = Track(max_age=sort_max_age,
                        min_hits=sort_min_hits,
                        iou_threshold=sort_iou_thresh)
        prev_frame_time = time.time()
        new_frame_time = 0
        last_obj_time = time.time()
        curr_obj_time = 0
        object_ids = set()
        shipping_ev = False
        while True:
            # Do processing
            ret, frame = video.read()
            if 'rtsp' in str(stream):
                frame_width = 640
                frame_height = 480
                frame = cv2.resize(frame, (frame_width, frame_height))
            # draw region in image
            # frame = cv2.polylines(frame, [np.array(table_region).reshape((-1, 1, 2))], True, 0.5, 1)
            # fps = video.get(cv2.CAP_PROP_FPS)
            if ret is False:
                LOGGER.error('ERROR: reading from video frame')
                time.sleep(1)
                continue
            cv2.putText(frame, "Box Count: " + str(len(object_ids)), (0,50) , cv2.FONT_HERSHEY_SIMPLEX, text_font, (0,0,250), text_thickness, cv2.LINE_AA)
            cv2.putText(frame, 'Shipping : '+str(shipping_ev), (0,70) , cv2.FONT_HERSHEY_SIMPLEX, text_font, (0,0,250), text_thickness, cv2.LINE_AA)
            new_frame_time = time.time()
            fps = 1/(new_frame_time-prev_frame_time)
            # total_time += (new_frame_time-prev_frame_time)
            prev_frame_time = new_frame_time
            curr_obj_time = time.time()
            # Detect smoke & fire
            results = self.model(frame, size=640)  # batched inference
            det = results.xyxy[0]
            print("-----------------------------------")
            if len(det):
                dets_to_sort = np.empty((0,6))
                for x1,y1,x2,y2,conf,detclass in det.cpu().detach().numpy():
                    if int(detclass) == object_class: # 0=Person, 39=bottle, 69=cell phone
                        dets_to_sort = np.vstack((dets_to_sort,
                                                np.array([x1, y1, x2, y2,
                                                            conf, detclass])))
                tracked_dets = sort_tracker.update(dets_to_sort)
                if len(tracked_dets)>0:
                    bbox_xyxy = tracked_dets[:,:4][0].tolist()
                    identities = tracked_dets[:, 8]
                    for i in range(len(identities)):
                        id = identities[i]
                        bbox = bbox_xyxy
                        inside_region = cv2.pointPolygonTest(np.array(table_region), (int(bbox_xyxy[0] + (bbox_xyxy[2]-bbox_xyxy[0])/2), int(bbox_xyxy[1] + (bbox_xyxy[3]-bbox_xyxy[1])/2)), False)
                        if inside_region > 0:
                            shipping_ev = True
                            self.draw_boxes(frame, [bbox], str(id), 0)
                            object_ids.add(id)
                            last_obj_time = curr_obj_time
                        cv2.putText(frame, "Box Count: " + str(len(object_ids)), (0,50) , cv2.FONT_HERSHEY_SIMPLEX, text_font, (0,0,250), text_thickness, cv2.LINE_AA)
                        cv2.putText(frame, 'Shipping : '+str(shipping_ev), (0,30) , cv2.FONT_HERSHEY_SIMPLEX, text_font, (0,0,250), text_thickness, cv2.LINE_AA)
                cv2.imshow('Output', frame)
                key = cv2.waitKey(5)
                if key == 27:
                    # import sys
                    print('Exiting.')
                    sys.exit(0)
            if (curr_obj_time - last_obj_time) > event_fire_threshold:
                last_obj_time = curr_obj_time
                print("fire event")
                self.f_event.fire_event(Event.INFO, 'Production', "Production-Monitoring", 'Production-Info', {"Production Status : " : shipping_ev, "Object Count : " : len(object_ids)})
            if (curr_obj_time - last_obj_time) > shipping_threshold: # and shipping_ev == True:
                last_obj_time = curr_obj_time
                shipping_ev = False
            results.print()
            if self.stop_evt.is_set():
                break

def camera_stream():
    snf = ProductivityMonitoring(scenario_name = 'productivity-detection')
    snf.start(camera_name=0)

if __name__ == '__main__':
    camera_stream()