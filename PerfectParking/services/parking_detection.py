from ultralytics import YOLO
import cv2
import numpy as np
from django.conf import settings
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from ..models import ParkingSpot, ParkingLot
import logging

logger = logging.getLogger(__name__)

class ParkingDetectionService:
    def __init__(self):
        self.model = YOLO('yolov8n.pt')  # Load YOLO model
        self.channel_layer = get_channel_layer()

    def process_video_feed(self, parking_lot_id, video_feed):
        """Process video feed and detect parking spot occupancy"""
        try:
            parking_lot = ParkingLot.objects.get(id=parking_lot_id)
            spots = ParkingSpot.objects.filter(parking_lot=parking_lot)
            
            # Process frame
            results = self.model(video_feed)
            detections = results[0].boxes.data  # Get detection boxes
            
            updates = []
            for spot in spots:
                is_occupied = self._check_spot_occupancy(
                    detections, 
                    spot.coordinates
                )
                if spot.is_occupied != is_occupied:
                    spot.is_occupied = is_occupied
                    updates.append(spot)
            
            # Bulk update spots
            if updates:
                ParkingSpot.objects.bulk_update(updates, ['is_occupied'])
                self._notify_clients(parking_lot_id, updates)
                
            return True
            
        except Exception as e:
            logger.error(f"Error processing video feed: {str(e)}")
            return False

    def _check_spot_occupancy(self, detections, spot_coords):
        """Check if a parking spot is occupied based on detections"""
        for det in detections:
            if det[5] == 2:  # Class 2 is 'car' in COCO dataset
                if self._calculate_iou(det[:4], spot_coords) > 0.45:
                    return True
        return False

    def _calculate_iou(self, detection, spot_coords):
        """Calculate Intersection over Union"""
        # Convert coordinates to [x1,y1,x2,y2] format
        box1 = detection
        box2 = np.array([
            spot_coords[0], spot_coords[1],
            spot_coords[2], spot_coords[3]
        ])
        
        # Calculate intersection
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])
        
        intersection = max(0, x2 - x1) * max(0, y2 - y1)
        
        # Calculate union
        box1_area = (box1[2] - box1[0]) * (box1[3] - box1[1])
        box2_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union = box1_area + box2_area - intersection
        
        return intersection / union if union > 0 else 0

    def _notify_clients(self, parking_lot_id, updated_spots):
        """Notify connected WebSocket clients about spot updates"""
        async_to_sync(self.channel_layer.group_send)(
            f'parking_lot_{parking_lot_id}',
            {
                'type': 'spot_status_update',
                'spots': [
                    {
                        'id': spot.id,
                        'is_occupied': spot.is_occupied
                    } for spot in updated_spots
                ]
            }
        ) 