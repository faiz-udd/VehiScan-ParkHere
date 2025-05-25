class ParkingRealtime {
    constructor() {
        this.socket = null;
        this.parkingLots = new Map();
        this.callbacks = new Map();
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
    }

    init() {
        this.connectWebSocket();
        this.setupHeartbeat();
    }

    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/parking/`;
        
        this.socket = new WebSocket(wsUrl);
        
        this.socket.onopen = () => {
            console.log('WebSocket connected');
            this.reconnectAttempts = 0;
            this.emit('connection_status', { status: 'connected' });
        };

        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };

        this.socket.onclose = () => {
            console.log('WebSocket disconnected');
            this.emit('connection_status', { status: 'disconnected' });
            this.attemptReconnect();
        };
    }

    setupHeartbeat() {
        setInterval(() => {
            if (this.socket && this.socket.readyState === WebSocket.OPEN) {
                this.socket.send(JSON.stringify({ type: 'heartbeat' }));
            }
        }, 30000);
    }

    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            setTimeout(() => {
                console.log(`Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
                this.connectWebSocket();
            }, 5000 * this.reconnectAttempts);
        }
    }

    handleMessage(data) {
        switch (data.type) {
            case 'parking_update':
                this.updateParkingLot(data.parking_lot_id, data.data);
                break;
            case 'booking_status':
                this.emit('booking_update', data);
                break;
            case 'notification':
                this.emit('notification', data);
                break;
            case 'price_update':
                this.updatePrice(data.parking_lot_id, data.price);
                break;
        }
    }

    updateParkingLot(id, data) {
        this.parkingLots.set(id, data);
        this.emit('parking_update', { id, data });
    }

    updatePrice(id, price) {
        const lot = this.parkingLots.get(id);
        if (lot) {
            lot.price = price;
            this.emit('price_update', { id, price });
        }
    }

    on(event, callback) {
        if (!this.callbacks.has(event)) {
            this.callbacks.set(event, new Set());
        }
        this.callbacks.get(event).add(callback);
    }

    off(event, callback) {
        if (this.callbacks.has(event)) {
            this.callbacks.get(event).delete(callback);
        }
    }

    emit(event, data) {
        if (this.callbacks.has(event)) {
            this.callbacks.get(event).forEach(callback => callback(data));
        }
    }

    subscribeToParkingLot(parkingLotId) {
        if (this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                type: 'subscribe',
                parking_lot_id: parkingLotId
            }));
        }
    }

    unsubscribeFromParkingLot(parkingLotId) {
        if (this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({
                type: 'unsubscribe',
                parking_lot_id: parkingLotId
            }));
        }
    }
} 