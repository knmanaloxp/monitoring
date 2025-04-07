import pystray
from PIL import Image
import os
import sys
import threading
import logging
from io import BytesIO
import win32gui
import win32con

class SystemTrayIcon:
    def __init__(self, agent):
        self.agent = agent
        self.icon = None
        self.status = "Inactive"
        self.hide_console_window()
        
        # Create icon dimensions and colors
        self.icon_size = 64
        self.bg_color = "#4CAF50"
        self.fg_color = "white"
        
    def create_icon(self):
        # Load the ICO file directly
        try:
            if getattr(sys, 'frozen', False):
                # If we're running as a PyInstaller bundle
                base_path = sys._MEIPASS
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            icon_path = os.path.join(base_path, 'network_agent.ico')
            if os.path.exists(icon_path):
                return Image.open(icon_path)
            else:
                logging.error(f"Icon file not found at: {icon_path}")
        except Exception as e:
            logging.error(f"Failed to load icon: {e}")
        
        # Create a fallback icon if loading fails
        img = Image.new('RGBA', (16, 16), (0, 255, 0, 255))
        return img
    
    def create_menu(self):
        return pystray.Menu(
            pystray.MenuItem("Status", lambda: None, enabled=False),
            pystray.MenuItem(lambda: f"Status: {self.status}", None),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", self.stop_agent)
        )
    
    def stop_agent(self):
        try:
            # Properly cleanup system tray resources
            if self.icon:
                self.icon.visible = False
                self.icon.stop()
                self.icon = None
            
            # Stop the agent and its processes
            if self.agent:
                self.agent.stop()
            
            # Ensure all threads are terminated
            for thread in threading.enumerate():
                if thread != threading.current_thread():
                    thread.join(timeout=1.0)
            
            sys.exit(0)
        except Exception as e:
            logging.error(f"Error during cleanup: {e}")
            sys.exit(1)
    
    def update_status(self, status):
        self.status = status
        if self.icon:
            self.icon.update_menu()
    
    def hide_console_window(self):
        try:
            # Find and hide the console window
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                win32gui.ShowWindow(hwnd, win32con.SW_HIDE)
        except Exception as e:
            logging.error(f"Failed to hide console window: {e}")
    
    def run(self):
        self.icon = pystray.Icon(
            "NetworkAgent",
            self.create_icon(),
            "Network Agent",
            self.create_menu()
        )
        
        # Run the icon in a separate thread
        icon_thread = threading.Thread(target=self.icon.run)
        icon_thread.daemon = True
        icon_thread.start()
        
        return self.icon