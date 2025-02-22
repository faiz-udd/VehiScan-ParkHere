import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';

const ParkingLotView = () => {
    const { id } = useParams();
    const [parkingLot, setParkingLot] = useState(null);
    const [spots, setSpots] = useState([]);
    const [socket, setSocket] = useState(null);

    useEffect(() => {
        // Fetch initial parking lot data
        const fetchParkingLot = async () => {
            try {
                const response = await axios.get(`/api/parking-lots/${id}/`);
                setParkingLot(response.data);
            } catch (error) {
                console.error('Error fetching parking lot:', error);
            }
        };

        fetchParkingLot();

        // Set up WebSocket connection
        const ws = new WebSocket(`ws://${window.location.host}/ws/parking/${id}/`);
        
        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'initial_data') {
                setParkingLot(data.parking_lot);
                setSpots(data.spots);
            } else if (data.type === 'spot_update') {
                updateSpots(data.spots);
            }
        };

        setSocket(ws);

        return () => {
            if (ws) {
                ws.close();
            }
        };
    }, [id]);

    const updateSpots = (updatedSpots) => {
        setSpots(prevSpots => {
            const newSpots = [...prevSpots];
            updatedSpots.forEach(update => {
                const index = newSpots.findIndex(spot => spot.id === update.id);
                if (index !== -1) {
                    newSpots[index] = { ...newSpots[index], ...update };
                }
            });
            return newSpots;
        });
    };

    const handleSpotClick = async (spotId) => {
        try {
            const response = await axios.post('/api/bookings/', {
                parking_spot: spotId,
                start_time: new Date().toISOString(),
                end_time: new Date(Date.now() + 3600000).toISOString(), // 1 hour
            });

            if (response.data) {
                // Redirect to payment page
                window.location.href = `/payment/${response.data.id}`;
            }
        } catch (error) {
            console.error('Error booking spot:', error);
        }
    };

    if (!parkingLot) {
        return <div>Loading...</div>;
    }

    return (
        <div className="parking-lot-view">
            <h1>{parkingLot.name}</h1>
            <div className="parking-info">
                <p>Available Spaces: {parkingLot.available_spaces}</p>
                <p>Hourly Rate: ${parkingLot.hourly_rate}</p>
            </div>
            <div className="parking-grid">
                {spots.map(spot => (
                    <div
                        key={spot.id}
                        className={`parking-spot ${spot.is_occupied ? 'occupied' : 'available'}`}
                        onClick={() => !spot.is_occupied && handleSpotClick(spot.id)}
                    >
                        <span>{spot.spot_number}</span>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ParkingLotView; 