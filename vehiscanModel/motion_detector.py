import time
import cv2
import numpy as np
from ultralytics import YOLO
from collections import deque
from colors import COLOR_GREEN, COLOR_WHITE, COLOR_BLUE
from drawing_utils import draw_contours
from cv2 import boundingRect, destroyAllWindows, imshow, VideoCapture, drawContours
from typing import Optional
from numpy import ndarray, ndarray as Mat
from perfectparking import ParkingMonitorData, RestApiUtility

SECONDS_TIME_DELAY = 0.002
IOU_THRESHOLD = 0.1  # Minimum overlap to consider occupied
HISTORY_LENGTH = 4     # Frames for temporal filtering
CONFIDENCE_THRESHOLD = 0.6  # YOLO detection confidence

class ParkingSpot:
    def __init__(self, coordinates: ndarray, parking_spot_id: int):
        self.coordinates = coordinates
        self.is_occupied = False
        self.parking_spot_id = parking_spot_id
        self.rect = boundingRect(self.coordinates)
        self.mask = self.create_contours_mask()
        self.history = deque(maxlen=HISTORY_LENGTH)
        self.area = cv2.contourArea(coordinates)

    def create_contours_mask(self) -> ndarray:
        x, y, w, h = self.rect
        mask = np.zeros((h, w), dtype=np.uint8)
        adjusted_coords = self.coordinates - [x, y]
        drawContours(mask, [adjusted_coords], -1, (255,), thickness=cv2.FILLED)
        return mask == 255

    def determine_and_mark_occupancy_from_image(self, frame: Mat, car_boxes: list):
        current_state = False
        spot_poly = self.coordinates.reshape(-1, 1, 2).astype(np.int32)
        
        for box in car_boxes:
            x1, y1, x2, y2 = map(int, box)
            car_poly = np.array([[x1,y1],[x2,y1],[x2,y2],[x1,y2]])
            
            # Calculate precise intersection
            intersection = cv2.intersectConvexConvex(
                spot_poly.astype(np.float32),
                car_poly.astype(np.float32)
            )[0]
            
            if intersection / self.area > IOU_THRESHOLD:
                current_state = True
                break
        
        # Temporal filtering
        self.history.append(current_state)
        self.is_occupied = sum(self.history)/HISTORY_LENGTH > 0.7

    def _rect_overlap(self, rect1: tuple, rect2: tuple) -> bool:
        # Preserved original rectangle check as fallback
        x1, y1, x2, y2 = rect1
        x3, y3, x4, y4 = rect2
        return not (x2 < x3 or x4 < x1 or y2 < y3 or y4 < y1)


class MotionDetector:
    def __init__(self, video, parking_spots_json_dict, start_frame, parking_monitor_data: ParkingMonitorData):
        self.video = video
        self.parking_spots = [
            ParkingSpot(np.array(spot["coordinates"]), spot["id"])
            for spot in parking_spots_json_dict
        ]
        self.start_frame = start_frame
        self.parking_monitor_data = parking_monitor_data
        self.model = YOLO("yolov8x.pt")
        self.class_ids = [2, 5, 7]  # Car, bus, truck

    def detect_motion(self) -> bool:
        video_capture = VideoCapture(self.video)
        free_spaces = 0
        frame_count = 0

        while True:
            is_open, video_frame = video_capture.read()
            if not is_open or video_frame is None:
                break

            # Enhanced preprocessing
            video_frame = self._enhance_contrast(video_frame)
            
            # Optimized YOLO detection
            results = self.model(video_frame, imgsz=640, conf=CONFIDENCE_THRESHOLD)
            car_boxes = []
            for result in results:
                for box in result.boxes:
                    if int(box.cls) in self.class_ids:
                        car_boxes.append(box.xyxy[0].cpu().numpy())

            # Update parking spots
            for spot in self.parking_spots:
                spot.determine_and_mark_occupancy_from_image(video_frame, car_boxes)

            # Visualization
            self._draw_detections(video_frame, car_boxes)
            self.display_image(video_frame)

            # Backend update
            current_free = len(self.parking_spots) - self.count_occupied_parking_spaces()
            if free_spaces != current_free:
                self.on_free_parking_spaces_changed(len(self.parking_spots), current_free)
                free_spaces = current_free

            if cv2.waitKey(1) == ord("q"):
                break
            time.sleep(SECONDS_TIME_DELAY)

        video_capture.release()
        destroyAllWindows()
        return False

    def _enhance_contrast(self, frame: Mat) -> Mat:
        lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
        l_channel, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        lab = cv2.merge([clahe.apply(l_channel), a, b])
        return cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    def _draw_detections(self, frame: Mat, boxes: list):
        pass
        # for box in boxes:
        #     x1, y1, x2, y2 = map(int, box)
        #     cv2.rectangle(frame, (x1, y1), (x2, y2), COLOR_BLUE, 2)

    # Original preserved methods
    def display_image(self, video_frame: Mat):
        for spot in self.parking_spots:
            color = COLOR_BLUE if spot.is_occupied else COLOR_GREEN
            draw_contours(video_frame, spot.coordinates,
                         str(spot.parking_spot_id), COLOR_WHITE, color)
        imshow("Press q to quit", video_frame)

    def count_occupied_parking_spaces(self) -> int:
        return sum(1 for spot in self.parking_spots if spot.is_occupied)

    def on_free_parking_spaces_changed(self, total: int, free: int):
        probability = free / total
        RestApiUtility.update_server_parking_monitor_data(
            self.parking_monitor_data, free, probability)

class CaptureReadError(Exception):
    pass