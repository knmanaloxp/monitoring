import time
import json
import logging
import requests
import os
import sys
import win32gui
import win32con
from datetime import datetime
from network_monitor import (
    get_connection_info,
    get_ip_addresses,
    measure_dns_resolution,
    ping_host,
    run_speed_test,
    get_device_info
)
from system_tray import SystemTrayIcon

# Get cloud configuration from environment variables
CLOUD_ENDPOINT = os.getenv('CLOUD_ENDPOINT', 'https://network-monitor-api.example.com/api')
API_KEY = os.getenv('API_KEY', '')  # Required for authentication

# Configure logging to file only, no console output
if not os.path.exists('logs'):
    os.makedirs('logs')

log_file = os.path.join('logs', 'network_agent.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='a', encoding='utf-8')
    ]
)

# Hide console window
hwnd = win32gui.GetForegroundWindow()
win32gui.ShowWindow(hwnd, win32con.SW_HIDE)

# Properly handle stdout/stderr to prevent console window
class NullWriter:
    def write(self, data):
        pass
    def flush(self):
        pass

# Always redirect output to prevent console window
sys.stdout = NullWriter()
sys.stderr = NullWriter()

class NetworkAgent:
    def __init__(self, cloud_endpoint=CLOUD_ENDPOINT, interval=300):
        self.cloud_endpoint = cloud_endpoint
        self.interval = interval  # Default 5 minutes
        self.device_info = get_device_info()
        self.buffer = []
        self.max_buffer_size = 100
        self.running = True
        self.tray_icon = SystemTrayIcon(self)
        self.tray_icon.run()
        # Register device with server
        self.register_device()

    def collect_metrics(self):
        """Collect all network metrics"""
        try:
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'device_info': self.device_info,
                'connection_info': get_connection_info(),
                'ip_addresses': get_ip_addresses(),
                'dns_resolution_time': measure_dns_resolution(),
                'ping_results': {}
            }

            # Collect ping metrics
            for host in ['google.com', '8.8.8.8', '1.1.1.1']:
                metrics['ping_results'][host] = ping_host(host)

            # Run speed test every hour (controlled by parameter)
            if datetime.now().minute < 5:  # Run in first 5 minutes of every hour
                metrics['speed_test'] = run_speed_test()

            return metrics
        except Exception as e:
            logging.error(f"Error collecting metrics: {str(e)}")
            return None

    def register_device(self):
        """Register device with the server"""
        try:
            response = requests.post(
                self.cloud_endpoint,
                json={'location': 'Local'},
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            response.raise_for_status()
            self.device_id = response.json()['id']
            logging.info(f"Device registered successfully with ID: {self.device_id}")
            if hasattr(self, 'tray_icon'):
                self.tray_icon.update_status('Active')
            return True
        except requests.exceptions.RequestException as e:
            logging.error(f"Error registering device: {str(e)}")
            if hasattr(self, 'tray_icon'):
                self.tray_icon.update_status('Error')
            return False

    def send_to_cloud(self, metrics):
        """Send metrics to cloud endpoint"""
        try:
            headers = {
                'Content-Type': 'application/json',
                'User-Agent': f'NetworkAgent/{self.device_info["hostname"]}',
                'Authorization': f'Bearer {API_KEY}'
            }
            response = requests.post(
                f"{self.cloud_endpoint}/{self.device_id}/metrics",
                json=metrics,
                headers=headers,
                timeout=10
            )
            response.raise_for_status()
            return True
        except requests.exceptions.RequestException as e:
            logging.error(f"Error sending data to cloud: {str(e)}")
            return False

    def buffer_metrics(self, metrics):
        """Buffer metrics when cloud connection fails"""
        if len(self.buffer) < self.max_buffer_size:
            self.buffer.append(metrics)
            logging.info(f"Metrics buffered. Buffer size: {len(self.buffer)}")
        else:
            logging.warning("Buffer full, dropping oldest metrics")
            self.buffer.pop(0)
            self.buffer.append(metrics)

    def send_buffered_metrics(self):
        """Attempt to send buffered metrics"""
        if not self.buffer:
            return

        logging.info(f"Attempting to send {len(self.buffer)} buffered metrics")
        successful_sends = []

        for metrics in self.buffer:
            if self.send_to_cloud(metrics):
                successful_sends.append(metrics)

        # Remove successfully sent metrics from buffer
        for metrics in successful_sends:
            self.buffer.remove(metrics)

    def stop(self):
        """Stop the network agent and cleanup"""
        self.running = False
        logging.info("Stopping Network Agent...")

    def run(self):
        """Main loop for the agent"""
        logging.info(f"Starting Network Agent for device: {self.device_info['hostname']}")

        while self.running:
            try:
                # Collect metrics
                metrics = self.collect_metrics()
                if metrics:
                    # Try to send any buffered metrics first
                    self.send_buffered_metrics()

                    # Try to send current metrics
                    if not self.send_to_cloud(metrics):
                        self.buffer_metrics(metrics)

                # Wait for next collection interval
                time.sleep(self.interval)

            except Exception as e:
                logging.error(f"Error in main loop: {str(e)}")
                time.sleep(60)  # Wait a minute before retrying

if __name__ == '__main__':
    agent = NetworkAgent()
    try:
        agent.run()
    finally:
        if hasattr(agent, 'tray_icon') and agent.tray_icon:
            agent.tray_icon.stop_agent()