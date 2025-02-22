from celery import shared_task
from .services.parking_detection import ParkingDetectionService
from .models import ParkingLot
import cv2
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_parking_lot_feeds():
    """Process all active parking lot video feeds"""
    detector = ParkingDetectionService()
    
    try:
        active_lots = ParkingLot.objects.filter(
            has_ai_detection=True,
            camera_stream_url__isnull=False
        )
        
        for lot in active_lots:
            # Open video stream
            cap = cv2.VideoCapture(lot.camera_stream_url)
            if not cap.isOpened():
                logger.error(f"Failed to open video stream for parking lot {lot.id}")
                continue
                
            ret, frame = cap.read()
            if ret:
                detector.process_video_feed(lot.id, frame)
            
            cap.release()
            
    except Exception as e:
        logger.error(f"Error processing parking lot feeds: {str(e)}")
        raise

@shared_task
def update_parking_statistics():
    """Update parking lot statistics"""
    try:
        for lot in ParkingLot.objects.all():
            occupied_count = lot.parkingspot_set.filter(is_occupied=True).count()
            total_spaces = lot.parkingspot_set.count()
            
            lot.available_spaces = total_spaces - occupied_count
            lot.occupancy_rate = (occupied_count / total_spaces) * 100 if total_spaces > 0 else 0
            lot.save(update_fields=['available_spaces', 'occupancy_rate'])
            
    except Exception as e:
        logger.error(f"Error updating parking statistics: {str(e)}")
        raise 