# Remote Worker Network Monitoring Tool

This tool monitors various network metrics for remote workers, including connection type, Wi-Fi details, IP information, DNS performance, latency, and speed test results.

## Features

- Connection type detection (Wi-Fi/Ethernet)
- Wi-Fi SSID and signal strength (when available)
- Internal and external IP addresses
- DNS resolution time measurement
- Ping/latency tests to Google, 8.8.8.8, and Cloudflare
- Internet speed test (download/upload)
- Device hostname and system information

## Installation

1. Ensure Python 3.6 or higher is installed on your system
2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the script using Python:
```
python network_monitor.py
```

The script will display real-time network metrics in the console.

## Requirements

See `requirements.txt` for the list of Python package dependencies:
- psutil: For system and network information
- speedtest-cli: For internet speed testing
- wifi: For Wi-Fi network details (optional)

## Note

Some features may require administrative/root privileges to access network information.