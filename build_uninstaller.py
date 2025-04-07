import PyInstaller.__main__
import os

PyInstaller.__main__.run([
    'uninstall_agent.py',
    '--onefile',
    '--name=uninstall_network_agent',
    '--uac-admin',  # Request admin privileges
    '--hidden-import=winreg',
    '--hidden-import=ctypes',
    '--noconsole',
    '--windowed',  # Ensures no console window appears
    '--log-level=ERROR',
    '--icon=network_agent.ico'
])