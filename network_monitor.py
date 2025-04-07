import psutil
import socket
import subprocess
import platform
import time
import json
from datetime import datetime

try:
    import wifi
    WIFI_AVAILABLE = True
except ImportError:
    WIFI_AVAILABLE = False

def get_connection_info():
    """Get network connection type and details"""
    info = {}
    interfaces = psutil.net_if_stats()
    
    # Find active network interface
    active_interface = None
    for interface, stats in interfaces.items():
        if stats.isup:
            active_interface = interface
            info['connection_type'] = 'Ethernet' if 'Ethernet' in interface else 'Wi-Fi'
            break
    
    # Get Wi-Fi details if available
    if WIFI_AVAILABLE and info.get('connection_type') == 'Wi-Fi':
        try:
            import subprocess
            output = subprocess.check_output(['netsh', 'wlan', 'show', 'interfaces']).decode('utf-8')
            for line in output.split('\n'):
                if 'Signal' in line:
                    signal = int(line.split(':')[1].strip().strip('%'))
                    # Convert percentage to dBm (approximate conversion)
                    dbm = -100 + (signal / 2)  # This gives a range from -100 dBm (0%) to -50 dBm (100%)
                    info['signal_strength'] = f"{int(dbm)} dBm"
                elif 'SSID' in line and not 'BSSID' in line:
                    info['wifi_ssid'] = line.split(':')[1].strip()
        except Exception as e:
            info['wifi_error'] = str(e)
    
    return info

def get_ip_addresses():
    """Get internal and external IP addresses"""
    # Get internal IP
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        internal_ip = s.getsockname()[0]
    except Exception:
        internal_ip = 'N/A'
    finally:
        s.close()
    
    # Get external IP
    try:
        external_ip = socket.gethostbyname(socket.gethostname())
    except Exception:
        external_ip = 'N/A'
    
    return {
        'internal_ip': internal_ip,
        'external_ip': external_ip
    }

def measure_dns_resolution():
    """Measure DNS resolution time"""
    start_time = time.time()
    try:
        socket.gethostbyname('google.com')
        resolution_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        return round(resolution_time, 2)
    except Exception:
        return None

def ping_host(host):
    """Ping a host and return the latency"""
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', host]
    try:
        output = subprocess.check_output(command).decode().strip()
        if platform.system().lower() == 'windows':
            if 'Average' in output:
                return float(output.split('Average = ')[-1].split('ms')[0])
        else:
            if 'time=' in output:
                return float(output.split('time=')[-1].split(' ms')[0])
    except:
        pass
    return None

def run_speed_test():
    """Run internet speed test using speedtest-cli module"""
    try:
        import speedtest
        s = speedtest.Speedtest(secure=True)
        
        # Configure test
        s.get_servers()  # Get server list first
        s.get_best_server()  # Then get best server
        
        # Set acceptable distance (km) for servers
        s.config['distance_threshold'] = 500
        
        # Get download speed with a timeout
        download_speed = s.download(threads=None) / 1_000_000  # Convert to Mbps
        
        # Get upload speed with a timeout
        upload_speed = s.upload(threads=None) / 1_000_000  # Convert to Mbps
        
        return {
            'download': round(download_speed, 2),
            'upload': round(upload_speed, 2)
        }
    except speedtest.ConfigRetrievalError as e:
        return {'error': f'Failed to retrieve speedtest configuration: {str(e)}'}
    except speedtest.NoMatchedServers as e:
        return {'error': f'No matched servers: {str(e)}'}
    except speedtest.SpeedtestBestServerFailure as e:
        return {'error': f'Failed to find best server: {str(e)}'}
    except Exception as e:
        return {'error': str(e)}

def get_device_info():
    """Get device hostname and user information"""
    return {
        'hostname': socket.gethostname(),
        'username': platform.node(),
        'system': platform.system(),
        'version': platform.version()
    }

def monitor_network():
    """Main function to collect all network metrics"""
    print("Starting network monitoring...\n")
    
    # Get connection info
    connection_info = get_connection_info()
    print(f"Connection Type: {connection_info.get('connection_type', 'N/A')}")
    if 'wifi_ssid' in connection_info:
        print(f"Wi-Fi SSID: {connection_info['wifi_ssid']}")
        print(f"Signal Strength: {connection_info['signal_strength']}")
    
    # Get IP addresses
    ip_info = get_ip_addresses()
    print(f"\nInternal IP: {ip_info['internal_ip']}")
    print(f"External IP: {ip_info['external_ip']}")
    
    # Measure DNS resolution
    dns_time = measure_dns_resolution()
    print(f"\nDNS Resolution Time: {dns_time}ms")
    
    # Ping tests
    print("\nPing Tests:")
    hosts = ['google.com', '8.8.8.8', '1.1.1.1']
    for host in hosts:
        latency = ping_host(host)
        print(f"{host}: {latency}ms" if latency else f"{host}: Failed")
    
    # Speed test
    print("\nRunning speed test (this may take a minute)...")
    speed_results = run_speed_test()
    if 'error' not in speed_results:
        print(f"Download Speed: {speed_results['download']} Mbps")
        print(f"Upload Speed: {speed_results['upload']} Mbps")
    else:
        print(f"Speed test error: {speed_results['error']}")
    
    # Device info
    device_info = get_device_info()
    print(f"\nDevice Information:")
    print(f"Hostname: {device_info['hostname']}")
    print(f"Username: {device_info['username']}")
    print(f"System: {device_info['system']} {device_info['version']}")

if __name__ == '__main__':
    monitor_network()