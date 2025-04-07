from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import pytz
import network_monitor
import threading
import time

app = Flask(__name__)
CORS(app)

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///network_monitor.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Philippines timezone
ph_tz = pytz.timezone('Asia/Manila')

# Helper function to convert UTC to Philippines time
def to_ph_time(utc_dt):
    if utc_dt:
        return utc_dt.replace(tzinfo=pytz.UTC).astimezone(ph_tz)
    return None

# Database Models
class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(100))
    location = db.Column(db.String(100))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    connection_type = db.Column(db.String(50))
    wifi_ssid = db.Column(db.String(100))
    signal_strength = db.Column(db.String(20))
    internal_ip = db.Column(db.String(50))
    external_ip = db.Column(db.String(50))
    status = db.Column(db.String(20), default='offline')

class NetworkMetrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    dns_resolution_time = db.Column(db.Float)
    download_speed = db.Column(db.Float)
    upload_speed = db.Column(db.Float)
    latency = db.Column(db.Float)

# Create database tables
with app.app_context():
    db.create_all()

# Helper function to update device metrics
def update_device_metrics(device_id):
    while True:
        with app.app_context():
            device = Device.query.get(device_id)
            if device:
                # Get network metrics
                connection_info = network_monitor.get_connection_info()
                ip_info = network_monitor.get_ip_addresses()
                dns_time = network_monitor.measure_dns_resolution()
                speed_results = network_monitor.run_speed_test()
                latency = network_monitor.ping_host('8.8.8.8')

                # Update device info
                device.connection_type = connection_info.get('connection_type', 'N/A')
                device.wifi_ssid = connection_info.get('wifi_ssid')
                device.signal_strength = connection_info.get('signal_strength')
                device.internal_ip = ip_info['internal_ip']
                device.external_ip = ip_info['external_ip']
                device.last_seen = datetime.utcnow()
                device.status = 'online'

                # Store metrics
                metrics = NetworkMetrics(
                    device_id=device_id,
                    dns_resolution_time=dns_time,
                    download_speed=speed_results.get('download') if 'error' not in speed_results else None,
                    upload_speed=speed_results.get('upload') if 'error' not in speed_results else None,
                    latency=latency
                )
                db.session.add(metrics)
                db.session.commit()

        time.sleep(300)  # Update every 5 minutes

# API Routes
@app.route('/api/devices', methods=['GET'])
def get_devices():
    devices = Device.query.all()
    return jsonify([{
        'id': d.id,
        'hostname': d.hostname,
        'username': d.username,
        'location': d.location,
        'last_seen': to_ph_time(d.last_seen).isoformat(),
        'connection_type': d.connection_type,
        'wifi_ssid': d.wifi_ssid,
        'signal_strength': d.signal_strength,
        'status': d.status
    } for d in devices])

@app.route('/api/devices', methods=['POST'])
def register_device():
    data = request.json
    device_info = network_monitor.get_device_info()
    
    # Check if device already exists
    existing_device = Device.query.filter_by(hostname=device_info['hostname']).first()
    if existing_device:
        existing_device.status = 'online'
        existing_device.last_seen = datetime.utcnow()
        db.session.commit()
        return jsonify({'id': existing_device.id, 'message': 'Device updated successfully'})
    
    device = Device(
        hostname=device_info['hostname'],
        username=device_info['username'],
        location=data.get('location', 'Unknown'),
        status='online'
    )
    db.session.add(device)
    db.session.commit()

    # Start monitoring thread for the new device
    thread = threading.Thread(target=update_device_metrics, args=(device.id,))
    thread.daemon = True
    thread.start()

    return jsonify({'id': device.id, 'message': 'Device registered successfully'})

@app.route('/api/devices/<int:device_id>/metrics', methods=['GET', 'POST'])
def device_metrics(device_id):
    if request.method == 'GET':
        timeframe = request.args.get('timeframe', 'hour')
        
        if timeframe == 'hour':
            since = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        elif timeframe == 'day':
            since = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        else:
            since = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            since = since.replace(day=1)

        metrics = NetworkMetrics.query.filter(
            NetworkMetrics.device_id == device_id,
            NetworkMetrics.timestamp >= since
        ).all()

        return jsonify([{
            'timestamp': to_ph_time(m.timestamp).isoformat(),
            'dns_resolution_time': m.dns_resolution_time,
            'download_speed': m.download_speed,
            'upload_speed': m.upload_speed,
            'latency': m.latency
        } for m in metrics])
    
    elif request.method == 'POST':
        data = request.json
        device = Device.query.get(device_id)
        if not device:
            return jsonify({'error': 'Device not found'}), 404

        # Update device info
        connection_info = data.get('connection_info', {})
        ip_addresses = data.get('ip_addresses', {})
        device.connection_type = connection_info.get('connection_type', 'N/A')
        device.wifi_ssid = connection_info.get('wifi_ssid')
        device.signal_strength = connection_info.get('signal_strength')
        device.internal_ip = ip_addresses.get('internal_ip')
        device.external_ip = ip_addresses.get('external_ip')
        device.last_seen = datetime.utcnow()
        device.status = 'online'

        # Store metrics
        speed_test = data.get('speed_test', {})
        metrics = NetworkMetrics(
            device_id=device_id,
            dns_resolution_time=data.get('dns_resolution_time'),
            download_speed=speed_test.get('download'),
            upload_speed=speed_test.get('upload'),
            latency=data.get('ping_results', {}).get('8.8.8.8')
        )
        db.session.add(metrics)
        db.session.commit()

        return jsonify({'message': 'Metrics updated successfully'}), 200

@app.route('/api/devices/<int:device_id>/speedtest', methods=['POST'])
def run_speedtest(device_id):
    device = Device.query.get(device_id)
    if not device:
        return jsonify({'error': 'Device not found'}), 404
    
    # Run speed test
    speed_results = network_monitor.run_speed_test()
    if 'error' not in speed_results:
        metrics = NetworkMetrics(
            device_id=device_id,
            download_speed=speed_results['download'],
            upload_speed=speed_results['upload']
        )
        db.session.add(metrics)
        db.session.commit()
        return jsonify(speed_results)
    return jsonify({'error': speed_results['error']}), 500

@app.route('/api/devices/<int:device_id>', methods=['DELETE'])
def delete_device(device_id):
    device = Device.query.get(device_id)
    if not device:
        return jsonify({'error': 'Device not found'}), 404
    
    # Delete associated metrics
    NetworkMetrics.query.filter_by(device_id=device_id).delete()
    db.session.delete(device)
    db.session.commit()
    return jsonify({'message': 'Device deleted successfully'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)