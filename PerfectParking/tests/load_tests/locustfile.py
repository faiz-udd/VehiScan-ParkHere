from locust import HttpUser, task, between
import random
import json

class ParkingUser(HttpUser):
    wait_time = between(1, 5)
    
    def on_start(self):
        """Login at start"""
        self.login()
        self.token = None
    
    def login(self):
        """Perform login"""
        response = self.client.post("/api/token/", {
            "username": "test_user",
            "password": "test_password"
        })
        
        if response.status_code == 200:
            self.token = response.json()["access"]
            self.client.headers = {'Authorization': f'Bearer {self.token}'}

    @task(3)
    def view_parking_lots(self):
        """Browse parking lots"""
        self.client.get("/api/parking-lots/")

    @task(2)
    def search_parking(self):
        """Search for parking"""
        params = {
            "latitude": random.uniform(40.7, 40.8),
            "longitude": random.uniform(-74.0, -73.9),
            "radius": random.choice([0.5, 1, 2, 5])
        }
        self.client.get("/api/parking-lots/search/", params=params)

    @task(1)
    def create_booking(self):
        """Create a booking"""
        parking_lot_id = random.randint(1, 10)
        data = {
            "parking_lot_id": parking_lot_id,
            "start_time": "2024-03-20T10:00:00Z",
            "duration": random.randint(1, 8)
        }
        self.client.post("/api/bookings/", json=data)

    @task(1)
    def view_profile(self):
        """View user profile"""
        self.client.get("/api/users/profile/")

class AdminUser(ParkingUser):
    @task(2)
    def view_analytics(self):
        """View analytics dashboard"""
        self.client.get("/api/admin/analytics/")

    @task(1)
    def manage_parking_lots(self):
        """Manage parking lots"""
        # Create parking lot
        data = {
            "name": f"Test Parking Lot {random.randint(1, 1000)}",
            "address": "123 Test St",
            "total_spaces": random.randint(50, 200),
            "hourly_rate": random.uniform(5, 20)
        }
        self.client.post("/api/admin/parking-lots/", json=data)

        # Update parking lot
        lot_id = random.randint(1, 10)
        data = {
            "hourly_rate": random.uniform(5, 20)
        }
        self.client.patch(f"/api/admin/parking-lots/{lot_id}/", json=data) 