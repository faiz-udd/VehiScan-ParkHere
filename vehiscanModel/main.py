"""This module is the main module of the PerfectParkingClient package."""
import argparse
import logging
import yaml
from perfectparking import create_image_from_video, ParkingMonitorData, RestApiUtility
from colors import COLOR_RED
from coordinates_generator import CoordinatesGenerator
from motion_detector import MotionDetector
import requests
from requests.auth import HTTPBasicAuth


def main():
    """Main method of the PerfectParkingClient package.
    """
    logging.basicConfig(level=logging.INFO)

    args = parse_args()

    image_file = args.image_file
    data_file = args.data_file
    start_frame = args.start_frame
    config_filepath = args.config_file

    if image_file is not None:
        create_image_from_video(image_file, args.video_file)
        with open(data_file, "w+") as points:
            generator = CoordinatesGenerator(image_file, points, COLOR_RED)
            generator.generate()
        
            
            

    with open(data_file, "r") as data:
        update_total_spaces_to_backend(data_file, config_filepath)
        parking_spaces:list = yaml.full_load(data)
        parking_monitor_data = ParkingMonitorData(config_filepath)
        detector = MotionDetector(args.video_file, parking_spaces, int(start_frame), parking_monitor_data)
        while True:
            was_stopped = detector.detect_motion()
            if was_stopped:
                break
        

def parse_args():
    """Parses the command line arguments."""
    parser = argparse.ArgumentParser(description='Generates Coordinates File')

    parser.add_argument("--image",
                        dest="image_file",
                        required=False,
                        help="Image file to generate coordinates on")

    parser.add_argument("--video",
                        dest="video_file",
                        required=True,
                        help="Video file to detect motion on")

    parser.add_argument("--data",
                        dest="data_file",
                        required=True,
                        help="Data file to be used with OpenCV")

    parser.add_argument("--start-frame",
                        dest="start_frame",
                        required=False,
                        default=1,
                        help="Starting frame on the video")
    parser.add_argument("--config",
                        dest="config_file",
                        required=False,
                        help="Config file to use"
                        )

    return parser.parse_args()


def update_total_spaces_to_backend(data_file: str, config_filepath: str):
    """
    Counts the number of unique parking spot IDs in the YAML data file and updates the backend
    with the total number of spaces for the ParkingLot corresponding to the monitor.
    """
    import yaml

    # Load parking spaces from YAML
    with open(data_file, "r") as f:
        parking_spaces = yaml.full_load(f)

    # Extract unique IDs from the YAML data
    ids = set()
    for spot in parking_spaces:
        spot_id = spot.get("id") or spot.get("parking_spot_id")
        if spot_id is not None:
            ids.add(spot_id)
    total_spaces = len(ids)

    # Load monitor data
    monitor_data = ParkingMonitorData(config_filepath)

    # You need the ParkingLot ID. Assuming monitor_data has parking_lot_id or similar.
    parking_lot_id = getattr(monitor_data, "id", None)
    if not parking_lot_id:
        print("ParkingLot ID not found in config. Please ensure it is set.")
        return

    # Prepare payload for backend
    payload = {
        "parkingLot.parking_spaces": total_spaces
    }

    # Send PATCH request to backend (partial update)
    url = f"{monitor_data.server_url}/{monitor_data.id}/"
    headers = {
        "Authorization": f"Token {monitor_data.app_token}",
        "Content-Type": "application/json",
    }
    auth = HTTPBasicAuth(monitor_data.app_username, monitor_data.app_password)
    response = requests.patch(url, json=payload, headers=headers, auth=auth)

    if response.ok:
        print(f"Successfully updated total spaces to {total_spaces} for ParkingLot {parking_lot_id}")
    else:
        print(f"Failed to update total spaces: {response.status_code} {response.text}")


if __name__ == '__main__':
    main()
