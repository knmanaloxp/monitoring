import PyInstaller.__main__
import os
import shutil

# Ensure the build and dist directories are clean
for dir_name in ['build', 'dist']:
    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Define all required hidden imports
hidden_imports = [
    'psutil',
    'speedtest',
    'pywifi',
    'requests',
    'network_monitor',
    'pystray',
    'PIL',
    'PIL._tkinter_finder',
    'win32gui',
    'win32api',
    'win32con'
]

# Define data files to include
data_files = [
    ('system_tray.py', '.'),
    ('network_agent.ico', '.'),
    ('config.env.example', '.'),
    ('logs', 'logs')
]

# Build PyInstaller command
pyinstaller_args = [
    'network_agent.py',
    '--onefile',
    '--name=network_agent',
    '--noconsole',
    '--windowed',
    '--log-level=ERROR',
    '--icon=network_agent.ico',
    '--clean'
]

# Add hidden imports
for hidden_import in hidden_imports:
    pyinstaller_args.extend(['--hidden-import', hidden_import])

# Add data files
for src, dst in data_files:
    if os.path.exists(src):
        pyinstaller_args.extend(['--add-data', f'{src};{dst}'])

# Run PyInstaller
PyInstaller.__main__.run(pyinstaller_args)

# Copy additional files to dist directory
dist_dir = os.path.join('dist')
if not os.path.exists(os.path.join(dist_dir, 'logs')):
    os.makedirs(os.path.join(dist_dir, 'logs'))