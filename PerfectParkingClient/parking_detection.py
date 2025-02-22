from ultralytics import YOLO
import cv2
import numpy as np
import requests

class ParkingDetector:
    def __init__(self, model_path='yolov8n.pt'):
        self.model = YOLO(model_path)
        
    def process_frame(self, frame, parking_spots):
        """Process video frame and detect cars in parking spots"""
        results = self.model(frame)
        
        for spot in parking_spots:
            # Check if any detected car overlaps with spot coordinates
            is_occupied = self._check_spot_occupancy(
                results[0].boxes.xyxy.cpu().numpy(),
                spot.coordinates
            )
            
            # Update spot status via API
            self._update_spot_status(spot.id, is_occupied)
    
    def _check_spot_occupancy(self, detections, spot_coords):
        """Check if any detected car overlaps with parking spot"""
        for det in detections:
            if self._calculate_overlap(det, spot_coords) > 0.5:
                return True
        return False
    
    def _calculate_overlap(self, detection, spot_coords):
        """
        Calculate Intersection over Union (IoU) between detection and parking spot
        
        Args:
            detection: numpy array [x1, y1, x2, y2] of detection box
            spot_coords: numpy array [x1, y1, x2, y2] of parking spot
        Returns:
            float: IoU score between 0 and 1
        """
        # Convert inputs to numpy arrays if they aren't already
        detection = np.array(detection)
        spot_coords = np.array(spot_coords)
        
        # Calculate intersection coordinates
        x1 = max(detection[0], spot_coords[0])
        y1 = max(detection[1], spot_coords[1])
        x2 = min(detection[2], spot_coords[2])
        y2 = min(detection[3], spot_coords[3])
        
        # Calculate intersection area
        if x2 < x1 or y2 < y1:
            return 0.0
        intersection_area = (x2 - x1) * (y2 - y1)
        
        # Calculate union area
        detection_area = (detection[2] - detection[0]) * (detection[3] - detection[1])
        spot_area = (spot_coords[2] - spot_coords[0]) * (spot_coords[3] - spot_coords[1])
        union_area = detection_area + spot_area - intersection_area
        
        # Calculate IoU
        if union_area <= 0:
            return 0.0
        return intersection_area / union_area
    
    def _update_spot_status(self, spot_id, is_occupied):
        """Send spot status update to server"""
        try:
            response = requests.post(
                f'http://localhost:8000/api/spots/{spot_id}/update_occupancy/',
                json={'is_occupied': is_occupied}
            )
            return response.status_code == 200
        except requests.exceptions.RequestException as e:
            print(f"Error updating spot status: {str(e)}")
            return False

    def start_detection(self, video_source, parking_spots, interval=1.0):
        """
        Start continuous detection on video source
        
        Args:
            video_source: int or str, camera index or video file path
            parking_spots: list of ParkingSpot objects
            interval: float, seconds between detections
        """
        cap = cv2.VideoCapture(video_source)
        
        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                    
                self.process_frame(frame, parking_spots)
                cv2.waitKey(int(interval * 1000))  # Convert seconds to milliseconds
                
        except Exception as e:
            print(f"Error in detection loop: {str(e)}")
        finally:
            cap.release() 