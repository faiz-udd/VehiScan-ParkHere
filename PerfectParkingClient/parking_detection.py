from ultralytics import YOLO
import cv2
import numpy as np
import requests
from shapely.geometry import Point, Polygon
from typing import List, Dict, Any, Tuple

class ParkingDetector:
    def __init__(self, model_path: str = 'yolov8n.pt'):
        """Initialize parking detector with YOLO model"""
        try:
            self.model = YOLO(model_path)
            self.frame_buffer: Dict[int, List[bool]] = {}
        except Exception as e:
            print(f"Error initializing YOLO model: {str(e)}")
            raise

    def process_frame(self, frame: np.ndarray, parking_spots: List[Dict[str, Any]]) -> np.ndarray:
        """Process video frame and detect cars in parking spots"""
        if frame is None or frame.size == 0:
            raise ValueError("Invalid frame input")

        frame = self._correct_perspective(frame)
        results = self.model(frame, classes=[2])  # Only detect cars (class 2)
        
        for spot in parking_spots:
            is_occupied = self._check_spot_occupation(results, spot)
            self._update_spot_buffer(spot, is_occupied)
        
        self._draw_parking_spots(frame, parking_spots)
        return frame

    def _check_spot_occupation(self, results, spot: Dict[str, Any]) -> bool:
        """Check if a parking spot is occupied"""
        for result in results:
            for box in result.boxes:
                centroid = self._get_centroid(box.xyxy[0])
                if spot["polygon"].contains(Point(centroid)):
                    return True
        return False

    def _update_spot_buffer(self, spot: Dict[str, Any], is_occupied: bool) -> None:
        """Update spot buffer and status"""
        spot_id = spot["id"]
        if spot_id not in self.frame_buffer:
            self.frame_buffer[spot_id] = [spot["is_occupied"]] * 3
        
        self.frame_buffer[spot_id].append(is_occupied)
        self.frame_buffer[spot_id].pop(0)
        
        if self.frame_buffer[spot_id].count(is_occupied) >= 2:
            if spot["is_occupied"] != is_occupied:
                spot["is_occupied"] = is_occupied
                self._update_spot_status(spot_id, is_occupied)

    def _get_centroid(self, bbox):
        """Calculate the centroid of a bounding box"""
        x1, y1, x2, y2 = bbox
        return ((x1 + x2) / 2, (y1 + y2) / 2)

    def _correct_perspective(self, frame: np.ndarray) -> np.ndarray:
        """Correct the perspective of the frame"""
        if frame is None or frame.size == 0:
            return frame

        try:
            height, width = frame.shape[:2]
            
            # Dynamic margins based on frame size
            margin_x = int(width * 0.1)
            margin_y = int(height * 0.1)
            
            src_points = np.float32([
                [margin_x, margin_y],
                [width - margin_x, margin_y],
                [width - margin_x, height - margin_y],
                [margin_x, height - margin_y]
            ])
            
            dst_points = np.float32([
                [0, 0],
                [width, 0],
                [width, height],
                [0, height]
            ])
            
            matrix = cv2.getPerspectiveTransform(src_points, dst_points)
            return cv2.warpPerspective(
                frame, matrix, (width, height),
                flags=cv2.INTER_LINEAR,
                borderMode=cv2.BORDER_REPLICATE
            )
        except Exception as e:
            print(f"Perspective correction failed: {str(e)}")
            return frame

    def _draw_parking_spots(self, frame: np.ndarray, parking_spots: List[Dict[str, Any]]) -> None:
        """Draw parking space outlines on the frame"""
        if frame is None:
            return

        for spot in parking_spots:
            try:
                coords = np.array(spot["coordinates"], dtype=np.int32).reshape((-1, 1, 2))
                color = (0, 255, 0) if not spot["is_occupied"] else (0, 0, 255)  # Green if free, Red if occupied
                cv2.polylines(frame, [coords], isClosed=True, color=color, thickness=2)
                
                # Add spot ID
                centroid = coords.mean(axis=0)[0]
                cv2.putText(frame, str(spot["id"]), tuple(centroid.astype(int)),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            except Exception as e:
                print(f"Error drawing spot {spot.get('id', 'unknown')}: {str(e)}")

    def start_detection(self, video_source: str, parking_spots: List[Dict[str, Any]], interval: float = 1.0) -> None:
        """Start continuous detection on video source"""
        cap = cv2.VideoCapture(video_source)
        if not cap.isOpened():
            raise ValueError(f"Could not open video source: {video_source}")

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                processed_frame = self.process_frame(frame, parking_spots)
                cv2.imshow("Parking Detection", processed_frame)
                
                if cv2.waitKey(int(interval * 1000)) & 0xFF == ord('q'):
                    break
                
        except Exception as e:
            print(f"Detection error: {str(e)}")
        finally:
            cap.release()
            cv2.destroyAllWindows()