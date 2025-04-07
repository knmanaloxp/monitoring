import os
import sys
import shutil
import winreg
import subprocess
import ctypes
import logging
from pathlib import Path

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

def remove_startup_entry():
    try:
        key_path = r'Software\Microsoft\Windows\CurrentVersion\Run'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_ALL_ACCESS) as key:
            try:
                winreg.DeleteValue(key, 'NetworkAgent')
                logging.info('Removed startup registry entry')
            except WindowsError:
                logging.info('No startup registry entry found')
    except Exception as e:
        logging.error(f'Error removing startup entry: {e}')

def kill_running_process():
    try:
        subprocess.run(['taskkill', '/F', '/IM', 'network_agent.exe'], capture_output=True)
        logging.info('Terminated running network agent process')
    except Exception as e:
        logging.error(f'Error terminating process: {e}')

def remove_files():
    # Define paths to clean
    install_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    files_to_remove = [
        'network_agent.exe',
        'network_agent.log',
        'network_monitor.db',
        'config.env'
    ]
    dirs_to_remove = [
        'logs',
        '__pycache__',
        'build',
        'dist'
    ]

    # Remove files
    for file in files_to_remove:
        try:
            file_path = install_dir / file
            if file_path.exists():
                os.remove(file_path)
                logging.info(f'Removed {file}')
        except Exception as e:
            logging.error(f'Error removing {file}: {e}')

    # Remove directories
    for dir_name in dirs_to_remove:
        try:
            dir_path = install_dir / dir_name
            if dir_path.exists():
                shutil.rmtree(dir_path)
                logging.info(f'Removed directory {dir_name}')
        except Exception as e:
            logging.error(f'Error removing directory {dir_name}: {e}')

def main():
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Ensure running as admin
    run_as_admin()

    try:
        # Kill any running instances
        kill_running_process()

        # Remove startup entry
        remove_startup_entry()

        # Remove files and directories
        remove_files()

        # Show completion message
        ctypes.windll.user32.MessageBoxW(0, 
            "Network Agent has been successfully uninstalled.", 
            "Uninstallation Complete", 
            0x40)

    except Exception as e:
        logging.error(f'Uninstallation failed: {e}')
        ctypes.windll.user32.MessageBoxW(0, 
            f"Error during uninstallation: {str(e)}", 
            "Uninstallation Error", 
            0x10)

if __name__ == '__main__':
    main()