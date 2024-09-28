import subprocess
import time
import win32gui
import win32process
import win32con
import win32com.client
import os
import json
import shutil
import requests
from dotenv import load_dotenv

from logger import log_message, log_folder_check

load_dotenv()
BAZIS_PATH = os.getenv('BAZIS_PATH')

# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_DIR = "results"
CONVERTER_SCRIPT_PATH = "./bazisToVariant.js"

INPUT_DIR = "inputs"
PROCESSING_DIR = "processings"
ERROR_DIR = "errors"

INPUT_MODEL = "model.b3d"
INPUT_DATA = "user_data.json"
SUCCESS_FILE = "project.s123proj"

TIMEOUT = 30


def activate_window(hwnd):
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.SendKeys('%')
    try:
        win32gui.SetForegroundWindow(hwnd)
    except:
        window_title = win32gui.GetWindowText(hwnd)
        shell.AppActivate(window_title)
    time.sleep(0.5)

def send_enter(hwnd):
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.SendKeys('%')  # Alt key
    time.sleep(0.1)
    shell.SendKeys('{ENTER}')



def copy_to_script_dir(source_folder):
    for item in os.listdir(source_folder):
        s = os.path.join(source_folder, item)
        d = os.path.join(SCRIPT_DIR, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)
    log_message(f"Copied all contents from {source_folder} to {SCRIPT_DIR}")

def remove_previous_data():
    for item in os.listdir(SCRIPT_DIR):
        if item not in ['.gitignore']:
            item_path = os.path.join(SCRIPT_DIR, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
            log_message(f"Removed: {item_path}")



def start_bazis():
    return subprocess.Popen([BAZIS_PATH, "--eval", CONVERTER_SCRIPT_PATH])

def find_bazis_window(pid):
    found_hwnd = [None]
    pirate_window = [False]

    def enum_callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            if found_pid == pid:
                title = win32gui.GetWindowText(hwnd)
                log_message(f"Found window with PID {pid}: {title}")
                if 'Подключение к серверу лицензий Базис-Центра' in title:
                    if win32gui.IsIconic(hwnd):
                        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    found_hwnd[0] = hwnd
                    raise StopIteration

                elif 'Открытие "пиратского" файла' in title:
                    pirate_window[0] = True
                    raise StopIteration
                
        return True

    try:
        win32gui.EnumWindows(enum_callback, None)
    except StopIteration:
        pass

    return found_hwnd[0], pirate_window[0]

def process_folder(folder_path):
    remove_previous_data()
    copy_to_script_dir(folder_path)

    bazis_process = start_bazis()
    start_time = time.time()

    while time.time() - start_time < TIMEOUT:
        hwnd, pirate_detected = find_bazis_window(bazis_process.pid)

        if hwnd:
            log_message(f"Window found and ready: {win32gui.GetWindowText(hwnd)}")
            activate_window(hwnd)
            win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
            win32gui.PostMessage(hwnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
            log_message("ENTER sent")

        if pirate_detected:
            log_message("Pirate window detected")
            kill_bazis(bazis_process)
            return False

        if os.path.exists(os.path.join(SCRIPT_DIR, SUCCESS_FILE)):
            log_message(f"Found results: {SUCCESS_FILE}")
            kill_bazis(bazis_process)
            return True

        time.sleep(1)

    log_message('Processing timed out')
    kill_bazis(bazis_process)

    return False


def kill_bazis(bazis_process):
    try:
        bazis_process.terminate()
        bazis_process.wait(timeout = 3)
    except subprocess.TimeoutExpired:
        log_message('Bazis process did not terminate gracefully, forcing...')
        bazis_process.kill()
    
    log_message('Bazis process terminated')

def send_to_dotnet():
    with open(os.path.join(SCRIPT_DIR, INPUT_DATA), "r") as f:
        user_data = json.load(f)
    
    data = {
        "IdCompany": int(user_data["IdCompany"]),
        "IdUser": str(user_data["IdUser"]),
        "ModelName": str(user_data["ModelName"])
    }

    files = []
    for filename in os.listdir(SCRIPT_DIR):
        file_path = os.path.join(SCRIPT_DIR, filename)
        if os.path.isfile(file_path) and filename not in ['.gitignore', INPUT_DATA]:
            files.append(('Files', (filename, open(file_path, 'rb'), 'application/octet-stream')))

    try:
        # response = requests.post("http://localhost:8123/api/Projects/CreateProjectFromBazisService",
        response = requests.post("https://api.system123.ru/api/Projects/CreateProjectFromBazisService",
            data=data,
            files=files
        )

        return response.ok

    except requests.RequestException as e:
        log_message(f"An error occurred while sending to dotnet: {e}")
        return False

    finally:
        for _, file_tuple in files:
            file_tuple[1].close()

def main():
    log_message("Starting main process")
    remove_previous_data()

    while True:
        log_folder_check()
        # log_message('Checking input dir for folders...')

        # we have only one worker so we can use FOR..IN here, otherwise we'd need to pick the oldest folder...
        for folder_name in os.listdir(INPUT_DIR):
            folder_path = os.path.join(INPUT_DIR, folder_name)

            if os.path.isdir(folder_path):
                log_message(f"\n\n\nFound folder to process: {folder_name}")

                # move to processings
                processing_path = os.path.join(PROCESSING_DIR, folder_name)
                shutil.move(folder_path, processing_path)
                log_message(f"Moved folder to processing: {processing_path}")

                if process_folder(processing_path):
                    log_message("Folder processed successfully")

                    # Send to dotnet
                    if send_to_dotnet():
                        log_message("Data sent to .NET successfully")
                        shutil.rmtree(processing_path)
                        log_message(f"Removed processing folder: {processing_path}")
                    else:
                        log_message("Failed to report to .NET, moving to ERRORS", "ERROR")
                        error_path = os.path.join(ERROR_DIR, folder_name)
                        shutil.move(processing_path, error_path)
                        log_message(f"Moved to error folder: {error_path}")
                else:
                    log_message("Failed to process folder, moving to ERRORS", "ERROR")
                    error_path = os.path.join(ERROR_DIR, folder_name)
                    shutil.move(processing_path, error_path)
                    log_message(f"Moved to error folder: {error_path}")

            time.sleep(1)

        time.sleep(10)

if __name__ == "__main__":
    main()