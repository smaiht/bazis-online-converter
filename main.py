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


BAZIS_PATH = "C:\\BazisOnline\\Bazis.exe"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONVERTER_SCRIPT_PATH = "./bazisToVariant.js"

INPUT_DIR = "inputs"
PROCESSING_DIR = "processings"
ERROR_DIR = "errors"

INPUT_MODEL = "model.b3d"
SUCCESS_FILE = "output.s123proj"

TIMEOUT = 120  # 2 minutes


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
    
def copy_model_to_script_dir(processing_folder):
    source_model = os.path.join(processing_folder, INPUT_MODEL)
    target_model = os.path.join(SCRIPT_DIR, INPUT_MODEL)
    if os.path.exists(source_model):
        shutil.copy2(source_model, target_model)
        print(f"Copied model from {source_model} to {target_model}")
    else:
        raise FileNotFoundError(f"Model file not found in {processing_folder}")

def remove_previous_data():
    model_path = os.path.join(SCRIPT_DIR, INPUT_MODEL)
    if os.path.exists(model_path):
        os.remove(model_path)
        print(f"Removed copied model: {model_path}")

    output_path = os.path.join(SCRIPT_DIR, "output.s123proj")
    if os.path.exists(output_path):
        os.remove(output_path)
        print(f"Removed previous output.s123proj: {output_path}")

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
                print(f"Found window with PID {pid}: {title}")
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
    copy_model_to_script_dir(folder_path)

    bazis_process = start_bazis()
    start_time = time.time()

    while time.time() - start_time < TIMEOUT:
        hwnd, pirate_detected = find_bazis_window(bazis_process.pid)

        if hwnd:
            print(f"Window found and ready: {win32gui.GetWindowText(hwnd)}")
            activate_window(hwnd)
            win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
            win32gui.PostMessage(hwnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
            print("ENTER sent")

        if pirate_detected:
            print("Pirate window detected")
            kill_bazis(bazis_process)
            return "error", "Pirate file detected"

        if os.path.exists(os.path.join(SCRIPT_DIR, SUCCESS_FILE)):
            print("Success file found")
            kill_bazis(bazis_process)
            return "success", "Processing completed successfully"

        time.sleep(2)

    print("Processing timed out")
    kill_bazis(bazis_process)
    return "error", "Processing timed out"


def kill_bazis(bazis_process):
    try:
        bazis_process.terminate()
        bazis_process.wait(timeout = 3)
    except subprocess.TimeoutExpired:
        print("Bazis process did not terminate gracefully, forcing...")
        bazis_process.kill()
    
    print("Bazis process terminated")

def report_bazis_status(status, message, user_data):
    # response = requests.post("API_ENDPOINT", json={
    #     "status": status,
    #     "message": message,
    #     "userData": user_data
    # })
    # return response.ok
    print(f"Reporting status: {status}, message: {message}")
    return True

def main():
    while True:
        print('timestamp | checking input dir for folders...')

        # we have only one worker so we can use FOR..IN here, otherwise we'd need to pick the oldest folder...
        for folder_name in os.listdir(INPUT_DIR):
            folder_path = os.path.join(INPUT_DIR, folder_name)

            if os.path.isdir(folder_path):
                print(f"Processing folder: {folder_name}")

                # move to processings
                processing_path = os.path.join(PROCESSING_DIR, folder_name)
                shutil.move(folder_path, processing_path)

                # with open(os.path.join(processing_path, "user_data.json"), "r") as f:
                #     user_data = json.load(f)
                user_data = 'test'

                status, message = process_folder(processing_path)
                
                # send report
                if report_bazis_status(status, message, user_data):
                    if status == "success":
                        shutil.rmtree(processing_path)
                    else:
                        error_path = os.path.join(ERROR_DIR, folder_name)
                        shutil.move(processing_path, error_path)
                else:
                    print("Failed to report status, moving back to INPUT_DIR")
                    shutil.move(processing_path, folder_path)

        time.sleep(10)

if __name__ == "__main__":
    main()