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
BAZIS_PIRATE_PATH = os.getenv('BAZIS_PIRATE_PATH')

BAZIS_CRACK_FILE_PATH = os.getenv('BAZIS_CRACK_FILE_PATH')
APPDATA_ROAMING_FOLDER_PATH = os.getenv('APPDATA_ROAMING_FOLDER_PATH')
SUPERUSERS_FILE = "superusers.txt"

# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_DIR = "results"
CONVERTER_SCRIPT_PATH = "./bazisToVariant.js"

INPUT_DIR = "inputs"
PROCESSING_DIR = "processings"
ERROR_DIR = "errors"

INPUT_MODEL = "model.b3d"
INPUT_DATA = "user_data.json"
SUCCESS_FILE = "project.s123proj"

TIMEOUT = 69



def find_and_kill_codemeter():
    wmi = win32com.client.GetObject("winmgmts:")
    processes = wmi.ExecQuery("SELECT * FROM Win32_Process WHERE Name='CodeMeterCC.exe'")
    
    for process in processes:
        pid = process.ProcessId
        log_message(f"CodeMeterCC.exe found. PID: {pid}")
        os.kill(pid, 9)  # 9 - SIGKILL
        log_message(f"Process with PID {pid} has been terminated")
        return True
    
    log_message("CodeMeterCC.exe not found")
    return False


def is_superuser(user_id):
    if not os.path.exists(SUPERUSERS_FILE):
        return False
    
    with open(SUPERUSERS_FILE, "r", encoding='utf-8') as file:
        superusers = file.read().splitlines()
    
    return user_id.strip().lower() in (su.strip().lower() for su in superusers)

def manage_hasp_ini(enable_crack):
    roaming_hasp_ini = os.path.join(APPDATA_ROAMING_FOLDER_PATH, "Hasp.ini")
    
    if enable_crack:
        if not os.path.exists(roaming_hasp_ini):
            shutil.copy2(BAZIS_CRACK_FILE_PATH, roaming_hasp_ini)
            log_message("Crack has been copied to Roaming folder")
    else:
        if os.path.exists(roaming_hasp_ini):
            os.remove(roaming_hasp_ini)
            log_message("Crack has been removed")
        
    log_message(f"Current state: Hasp.ini {'exists' if os.path.exists(roaming_hasp_ini) else 'does not exist'} in Roaming folder")

def start_bazis(pirate_mode, project_id):
    find_and_kill_codemeter()

    if pirate_mode:
        manage_hasp_ini(True)
        bazis_app = BAZIS_PIRATE_PATH
    else:
        manage_hasp_ini(False)
        bazis_app = BAZIS_PATH

    log_message(f"Using Bazis version: {bazis_app}", IdProject=project_id)
    return subprocess.Popen([bazis_app, "--eval", CONVERTER_SCRIPT_PATH])

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

def kill_bazis(bazis_process):
    try:
        bazis_process.terminate()
        bazis_process.wait(timeout = 3)
    except subprocess.TimeoutExpired:
        log_message('Bazis process did not terminate gracefully, forcing...')
        bazis_process.kill()
    
    log_message('Bazis process terminated')



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



def process_folder(folder_path, pirate_mode, project_id):
    remove_previous_data()
    copy_to_script_dir(folder_path)

    bazis_process = start_bazis(pirate_mode, project_id)
    start_time = time.time()

    while time.time() - start_time < TIMEOUT:
        if not pirate_mode:
            hwnd, pirate_detected = find_bazis_window(bazis_process.pid)
            if hwnd:
                log_message(f"Window found and ready: {win32gui.GetWindowText(hwnd)}")
                activate_window(hwnd)
                win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
                win32gui.PostMessage(hwnd, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
                log_message("Enter key sent (Authorized successfully?)")
                new_hwnd, new_pirate_detected = find_bazis_window(bazis_process.pid)
                log_message(f"Current window: {win32gui.GetWindowText(new_hwnd)}")

            if pirate_detected:
                log_message("Pirate file detected", level="PIRATE", IdProject=project_id)
                kill_bazis(bazis_process)
                return False

        if os.path.exists(os.path.join(SCRIPT_DIR, SUCCESS_FILE)):
            log_message(f"Converted successfully: {SUCCESS_FILE}", IdProject=project_id)
            kill_bazis(bazis_process)
            return True

        time.sleep(1)

    log_message('Processing timed out', level="ERROR", IdProject=project_id, tg=True)
    kill_bazis(bazis_process)

    return False



def insert_material_folders():
    with open(os.path.join(SCRIPT_DIR, INPUT_DATA), "r", encoding='utf-8') as f:
        user_data = json.load(f)

    material_folders = json.dumps(user_data["MaterialFolders"])
    placeholder = '"{{MATERIAL_FOLDERS_PLACEHOLDER}}"'
    
    with open(os.path.join(SCRIPT_DIR, SUCCESS_FILE), "r", encoding='utf-8') as f:
        content = f.read()

    updated_content = content.replace(placeholder, material_folders)

    with open(os.path.join(SCRIPT_DIR, SUCCESS_FILE), 'w', encoding='utf-8') as file:
        file.write(updated_content)


def send_project_to_dotnet():
    with open(os.path.join(SCRIPT_DIR, INPUT_DATA), "r") as f:
        user_data = json.load(f)
    
    data = {
        "IdCompany": int(user_data["IdCompany"]),
        "IdUser": str(user_data["IdUser"]),
        "ModelName": str(user_data["ModelName"]),
        "IdProject": str(user_data["IdProject"]),
        "Status": "success",
        "Message": "success"
    }

    files = []
    for filename in os.listdir(SCRIPT_DIR):
        file_path = os.path.join(SCRIPT_DIR, filename)
        if os.path.isfile(file_path) and filename not in ['.gitignore', INPUT_DATA, INPUT_MODEL]:
            files.append(('Files', (filename, open(file_path, 'rb'), 'application/octet-stream')))

    try:
        # response = requests.post("http://localhost:8123/api/Projects/CreateProjectFromBazisService", # debug
        response = requests.post("https://api.system123.ru/api/Projects/CreateProjectFromBazisService", # prod
            data=data,
            files=files
        )

        if not response.ok:
            log_message(f"Request failed with status code {response.status_code}", 'ERROR')
            log_message(f"Response content: {response.text}", 'ERROR')

        return response.ok

    except requests.RequestException as e:
        log_message(f"An error occurred while sending to dotnet: {e}")
        return False

    finally:
        for _, file_tuple in files:
            file_tuple[1].close()

def main():
    log_message("Starting main process")
    find_and_kill_codemeter()
    remove_previous_data()

    while True:
        log_folder_check()

        # we have only one worker so we can use FOR..IN here, otherwise we'd need to pick the oldest folder...
        for folder_name in os.listdir(INPUT_DIR):
            folder_path = os.path.join(INPUT_DIR, folder_name)

            if os.path.isdir(folder_path):
                log_message(f"\n\n\nFound folder to process: {folder_name}")
                log_message(f"Starting processing project...", IdProject=folder_name)

                # move to processings
                processing_path = os.path.join(PROCESSING_DIR, folder_name)
                shutil.move(folder_path, processing_path)
                log_message(f"Moved folder to processing: {processing_path}")

                # can open pirate files?
                can_open_pirate_files = False
                with open(os.path.join(processing_path, INPUT_DATA), "r") as f:
                    user_data = json.load(f)
                if is_superuser(str(user_data["IdUser"])):
                    can_open_pirate_files = True
                    log_message(f"Pirate mode activated!", IdProject=folder_name)

                if process_folder(processing_path, can_open_pirate_files, folder_name):
                    log_message("Folder processed successfully")

                    insert_material_folders()
                    log_message("Material Folders IDs inserted successfully", IdProject=folder_name)

                    log_message("Trying send to .NET ...")
                    # Send to dotnet
                    if send_project_to_dotnet():
                        log_message("Data sent to .NET successfully", IdProject=folder_name)
                        shutil.rmtree(processing_path)
                        log_message(f"Removed processing folder: {processing_path}")
                    else:
                        log_message("Failed to send to .NET, moving to ERRORS", "ERROR", IdProject=folder_name, tg=True)
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