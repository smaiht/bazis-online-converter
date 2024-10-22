import subprocess
import time
import win32gui
import win32process
import win32con
import win32com.client
import win32service
import os
import json
import shutil
import requests

import win32security
import win32api
import ntsecuritycon as con

from PIL import Image
from dotenv import load_dotenv

from logger import log_message, log_folder_check

load_dotenv()
BAZIS_PATH = os.getenv('BAZIS_PATH')
BAZIS_PIRATE_PATH = os.getenv('BAZIS_PIRATE_PATH')

BAZIS_CRACK_FILE_PATH = os.getenv('BAZIS_CRACK_FILE_PATH')
APPDATA_ROAMING_FOLDER_PATH = os.getenv('APPDATA_ROAMING_FOLDER_PATH')
SUPERUSERS_FILE = "superusers.txt"

ENDPOINT = os.getenv('ENDPOINT')

# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_DIR = "results"
CONVERTER_FROM_BAZIS_SCRIPT = "./convertBazisToVariant.js"
CONVERTER_TO_BAZIS_SCRIPT = "./convertVariantToBazis.js"

INPUTS_TO_BAZIS = "inputs_to_bazis"
INPUTS_FROM_BAZIS = "inputs_from_bazis"

PROCESSING_DIR = "processings"
ERROR_DIR = "errors"

INPUT_MODEL = "model.b3d"
INPUT_DATA = "user_data.json"
SUCCESS_FILE_FROM_BAZIS = "project.s123proj"
SUCCESS_FILE_TO_BAZIS = "bazis.b3d"
MAIN_ICON = "main_icon.jpg"
ICON_SIZE = 512


TIMEOUT = 240



def grant_full_control(file_path):
    # Получаем текущего пользователя
    username = win32api.GetUserName()
    
    # Получаем DACL файла
    sd = win32security.GetFileSecurity(file_path, win32security.DACL_SECURITY_INFORMATION)
    dacl = sd.GetSecurityDescriptorDacl()
    
    # Получаем SID текущего пользователя
    user_sid, _, _ = win32security.LookupAccountName("", username)
    
    # Добавляем полный доступ для текущего пользователя
    dacl.AddAccessAllowedAce(win32security.ACL_REVISION, con.FILE_ALL_ACCESS, user_sid)
    
    # Устанавливаем новый DACL
    sd.SetSecurityDescriptorDacl(1, dacl, 0)
    win32security.SetFileSecurity(file_path, win32security.DACL_SECURITY_INFORMATION, sd)

def crop_resize_icon():
    icon_path = os.path.join(SCRIPT_DIR, MAIN_ICON)
    if os.path.exists(icon_path):
        with Image.open(icon_path) as image:
            # crop
            width, height = image.size
            offset = int(abs(width - height) / 2)
            if width > height:
                left, top, right, bottom = offset, 0, width - offset, height
            else:
                left, top, right, bottom = 0, offset, width, height - offset
                
            square_image = image.crop((left, top, right, bottom))

            # resize
            resized_image = square_image.resize((ICON_SIZE, ICON_SIZE), Image.LANCZOS)
            resized_image.save(icon_path)

        log_message(f"Icon resized.")
    else:
        log_message(f"Icon not found")


def resize_window(hwnd, width, height):
    log_message(f"Trying to resize the window.")
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    
    win32gui.MoveWindow(hwnd, left, top, width, height, True)
    
    padding_left = 100 
    padding_top = 20
    win32gui.SetWindowPos(hwnd, 0, padding_left, padding_top, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_NOZORDER)

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
            grant_full_control(roaming_hasp_ini)
            os.remove(roaming_hasp_ini)
            log_message("Crack has been removed")
        
    log_message(f"Current state: Hasp.ini {'exists' if os.path.exists(roaming_hasp_ini) else 'does not exist'} in Roaming folder")

def ensure_window_desktop():
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.lpDesktop = "winsta0\\default"
    return startupinfo

def start_bazis(pirate_mode, project_id, script=CONVERTER_FROM_BAZIS_SCRIPT):
    find_and_kill_codemeter()

    if pirate_mode:
        manage_hasp_ini(True)
        bazis_app = BAZIS_PIRATE_PATH
    else:
        manage_hasp_ini(False)
        bazis_app = BAZIS_PATH

    log_message(f"Using Bazis version: {bazis_app}", IdProject=project_id)
    log_message(f"Using script: {script}")

    if (script == CONVERTER_FROM_BAZIS_SCRIPT):
        return subprocess.Popen([bazis_app, "--eval", script])

    startupinfo = ensure_window_desktop()
    return subprocess.Popen([bazis_app, "--eval", script], 
                          startupinfo=startupinfo,
                          creationflags=win32con.CREATE_NEW_CONSOLE)

def activate_window(hwnd):
    shell = win32com.client.Dispatch("WScript.Shell")
    shell.SendKeys('%')
    try:
        win32gui.SetForegroundWindow(hwnd)
    except:
        window_title = win32gui.GetWindowText(hwnd)
        shell.AppActivate(window_title)
    time.sleep(0.5)

# def send_enter(hwnd):
#     shell = win32com.client.Dispatch("WScript.Shell")
#     shell.SendKeys('%') # Alt key
#     time.sleep(0.1)
#     shell.SendKeys('{ENTER}')

def send_ctrl_s(hwnd):
    # shell = win32com.client.Dispatch("WScript.Shell")
    # shell.SendKeys('%') # Alt key
    # win32gui.SetForegroundWindow(hwnd)
    # time.sleep(0.1)
    # shell.SendKeys('^s')
    if win32gui.IsWindow(hwnd) and win32gui.IsWindowVisible(hwnd):
        log_message(f"Window for saving found and ready: {win32gui.GetWindowText(hwnd)}")
        activate_window(hwnd)
        # Отправляем Ctrl
        win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, win32con.VK_CONTROL, 0)
        # Отправляем S
        win32gui.PostMessage(hwnd, win32con.WM_KEYDOWN, ord('S'), 0)
        win32gui.PostMessage(hwnd, win32con.WM_KEYUP, ord('S'), 0)
        # Отпускаем Ctrl
        win32gui.PostMessage(hwnd, win32con.WM_KEYUP, win32con.VK_CONTROL, 0)
        log_message("Ctrl+S sent to window")

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
    license_window = [None]
    pirate_window = [None]
    error_window = [None]
    main_window = [None]

    def enum_callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
            _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
            if found_pid == pid:
                title = win32gui.GetWindowText(hwnd)
                log_message(f"Found window with PID {pid}: {title}")

                if 'Подключение к серверу лицензий Базис-Центра' in title or 'Connection to Bazis-Center license server' in title:
                    if win32gui.IsIconic(hwnd):
                        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    license_window[0] = hwnd
                    raise StopIteration

                elif 'Открытие "пиратского" файла' in title or 'Pirate file opening' in title:
                    pirate_window[0] = hwnd
                    raise StopIteration

                elif 'Ошибка' in title or 'Error' in title:
                    error_window[0] = hwnd
                    raise StopIteration

                elif 'БАЗИС' in title or 'BAZIS' in title:
                    main_window[0] = hwnd
                    raise StopIteration
                
        return True

    try:
        win32gui.EnumWindows(enum_callback, None)
    except StopIteration:
        pass

    return license_window[0], pirate_window[0], error_window[0], main_window[0]



def process_folder(folder_path, pirate_mode, project_id):
    remove_previous_data()
    copy_to_script_dir(folder_path)

    bazis_process = start_bazis(pirate_mode, project_id)
    start_time = time.time()

    while time.time() - start_time < TIMEOUT:
        license_window, pirate_detected, error_window, main_window = find_bazis_window(bazis_process.pid)
        
        if not pirate_mode:
            if license_window:
                log_message(f"Window found and ready: {win32gui.GetWindowText(license_window)}")
                activate_window(license_window)
                win32gui.PostMessage(license_window, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
                win32gui.PostMessage(license_window, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
                log_message("Enter key sent (Authorized successfully?)")
                # new_license_window, new_pirate_detected, new_error_window, new_main_window = find_bazis_window(bazis_process.pid)
                # log_message(f"Current window: {win32gui.GetWindowText(new_license_window)}")

            if pirate_detected:
                log_message("Pirate file detected", level="PIRATE", IdProject=project_id)
                kill_bazis(bazis_process)
                return False
            
        if error_window:
            log_message("Error reading file", level="ERROR", IdProject=project_id, tg=True)
            kill_bazis(bazis_process)
            return False

        if os.path.exists(os.path.join(SCRIPT_DIR, SUCCESS_FILE_FROM_BAZIS)):
            log_message(f"Converted successfully: {SUCCESS_FILE_FROM_BAZIS}", IdProject=project_id)
            kill_bazis(bazis_process)
            crop_resize_icon()
            return True

        time.sleep(1)

    log_message('Processing timed out', level="ERROR", IdProject=project_id, tg=True)
    kill_bazis(bazis_process)

    return False


def process_folder_to_bazis(folder_path, id_project, id_calculation):
    remove_previous_data()
    copy_to_script_dir(folder_path)

    log_message('(to bazis) Start')
    bazis_process = start_bazis(False, id_project, CONVERTER_TO_BAZIS_SCRIPT)
    start_time = time.time()

    while time.time() - start_time < TIMEOUT:
        license_window, pirate_detected, error_window, main_window = find_bazis_window(bazis_process.pid)
        if license_window:
            log_message(f"Window found and ready: {win32gui.GetWindowText(license_window)}")
            activate_window(license_window)
            win32gui.PostMessage(license_window, win32con.WM_KEYDOWN, win32con.VK_RETURN, 0)
            win32gui.PostMessage(license_window, win32con.WM_KEYUP, win32con.VK_RETURN, 0)
            log_message("Enter key sent (Authorized successfully?)")
            # new_license_window, new_pirate_detected, new_error_window, new_main_window = find_bazis_window(bazis_process.pid)
            # log_message(f"Current window: {win32gui.GetWindowText(new_license_window)}")

        if error_window:
            log_message("Error reading file", level="ERROR", IdProject=id_project)
            kill_bazis(bazis_process)
            return False
            
        if os.path.exists(os.path.join(SCRIPT_DIR, 'flag-to-ctrl-s.json')):
            log_message(f"Model recreated in Bazis successfully, trying to save...", IdProject=id_project)
            
            bazis_file_path = os.path.join(SCRIPT_DIR, "bazis-base-model.b3d")
            initial_mod_time = os.path.getmtime(bazis_file_path)
            log_message(f"initial_mod_time: {initial_mod_time}")

            new_license_window, new_pirate_detected, new_error_window, new_main_window = find_bazis_window(bazis_process.pid)
            if new_main_window:
                log_message(f"Main Bazis Window found: {win32gui.GetWindowText(new_main_window)}")
                # send_ctrl_s(new_main_window)







                save_bazis_file_with_desktop(new_main_window)
                time.sleep(1)






                
                shell = win32com.client.Dispatch("WScript.Shell")
                
                activate_window(new_main_window)
                time.sleep(1)
                
                # Отправляем Ctrl+S через SendKeys
                shell.SendKeys('^s')
                log_message("shell Ctrl+S sent to Bazis window")
                time.sleep(1)

                time.sleep(0.2)


    
                # Получаем scan code для 'S'
                scan_code = win32api.MapVirtualKey(ord('S'), 0)
                
                # Зажимаем Ctrl
                win32gui.PostMessage(new_main_window, win32con.WM_KEYDOWN, win32con.VK_CONTROL, 0)
                time.sleep(0.1)
                
                # Нажимаем S с правильным scan code
                lparam = (scan_code << 16) | 1
                win32gui.PostMessage(new_main_window, win32con.WM_KEYDOWN, ord('S'), lparam)
                time.sleep(0.1)
                win32gui.PostMessage(new_main_window, win32con.WM_KEYUP, ord('S'), lparam | 0xC0000000)
                
                time.sleep(0.1)
                win32gui.PostMessage(new_main_window, win32con.WM_KEYUP, win32con.VK_CONTROL, 0)

                log_message("postmessage Ctrl+S sent to Bazis window")
                time.sleep(1)


                save_bazis_file(new_main_window)
                log_message("Стандартный ID для команды Save в Windows sent to Bazis window")
                time.sleep(1)

                save_bazis_file2(new_main_window)
                log_message("keyboard lib команды Save sent to Bazis window")
                time.sleep(1)

                save_bazis_file3(new_main_window)
                log_message("SendInput команды Save sent to Bazis window")
                time.sleep(1)
                
                
                new_mod_time = os.path.getmtime(bazis_file_path)
                log_message(f"new_mod_time: {new_mod_time} > initial_mod_time: {new_mod_time > initial_mod_time}")

                if new_mod_time > initial_mod_time:
                    log_message(f"File successfully saved. Modification time changed from {initial_mod_time} to {new_mod_time}", IdProject=id_project)
                    # Remove temporary files and rename to success bazis file
                    os.remove(os.path.join(SCRIPT_DIR, 'flag-to-ctrl-s.json'))
                    new_bazis_file_path = os.path.join(SCRIPT_DIR, SUCCESS_FILE_TO_BAZIS)
                    os.rename(bazis_file_path, new_bazis_file_path)
            
        if os.path.exists(os.path.join(SCRIPT_DIR, SUCCESS_FILE_TO_BAZIS)):
            log_message(f"Converted successfully: {SUCCESS_FILE_TO_BAZIS}", IdProject=id_project)
            kill_bazis(bazis_process)
            return True

        time.sleep(1)

    log_message('(to bazis) Processing timed out', level="ERROR", IdProject=id_project, tg=True)
    kill_bazis(bazis_process)

    return False


def save_bazis_file_with_desktop(hwnd):
    log_message("Starting save operation with separate process...")
    
    try:
        # Создаем временный скрипт для сохранения
        save_script = """
import win32gui
import win32con
import time
import sys

def save_file(hwnd):
    # WM_COMMAND метод
    WM_COMMAND = 0x0111
    ID_FILE_SAVE = 0xE103
    win32gui.PostMessage(int(hwnd), WM_COMMAND, ID_FILE_SAVE, 0)
    
    # Keyboard метод
    win32gui.PostMessage(int(hwnd), win32con.WM_KEYDOWN, win32con.VK_CONTROL, 0)
    time.sleep(0.1)
    win32gui.PostMessage(int(hwnd), win32con.WM_KEYDOWN, ord('S'), 0)
    time.sleep(0.1)
    win32gui.PostMessage(int(hwnd), win32con.WM_KEYUP, ord('S'), 0)
    win32gui.PostMessage(int(hwnd), win32con.WM_KEYUP, win32con.VK_CONTROL, 0)

if __name__ == '__main__':
    save_file(sys.argv[1])
"""
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(save_script)
            temp_script = f.name

        # Создаем процесс с новым рабочим столом
        si = subprocess.STARTUPINFO()
        si.lpDesktop = "winsta0\\default"
        
        process = subprocess.Popen(
            ['python', temp_script, str(hwnd)],
            startupinfo=si,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        # Ждем завершения процесса
        process.wait(timeout=5)
        
        # Удаляем временный файл
        os.unlink(temp_script)
        
        log_message("Save command sent via separate process")
        return True

    except Exception as e:
        log_message(f"Error in save_bazis_file_with_desktop: {str(e)}")
        return False





def save_bazis_file(hwnd):
    # Константы для команды Save
    WM_COMMAND = 0x0111
    ID_FILE_SAVE = 0xE103  # Стандартный ID для команды Save в Windows

    log_message(f"Trying to save file through WM_COMMAND...")
    try:
        # Отправляем команду Save напрямую окну
        win32gui.PostMessage(hwnd, WM_COMMAND, ID_FILE_SAVE, 0)
        log_message("Save command sent successfully")
        return True
    except Exception as e:
        log_message(f"Error sending save command: {str(e)}")
        return False

def save_bazis_file2(hwnd):
    try:
        import keyboard
        log_message("Trying to save using keyboard library...")
        
        # Активируем окно более мягким способом
        shell = win32com.client.Dispatch("WScript.Shell")
        window_title = win32gui.GetWindowText(hwnd)
        shell.AppActivate(window_title)
        time.sleep(0.5)

        # Эмулируем нажатие Ctrl+S
        keyboard.press('ctrl')
        time.sleep(0.1)
        keyboard.press('s')
        time.sleep(0.1)
        keyboard.release('s')
        time.sleep(0.1)
        keyboard.release('ctrl')
        
        log_message("Keyboard save command sent")
        
    except Exception as e:
        log_message(f"Error in keyboard save: {str(e)}")
        
        # Запасной вариант - через WM_COMMAND
        try:
            WM_COMMAND = 0x0111
            ID_FILE_SAVE = 0xE103
            win32gui.PostMessage(hwnd, WM_COMMAND, ID_FILE_SAVE, 0)
            log_message("Backup save command sent via WM_COMMAND")
        except Exception as e2:
            log_message(f"Error in backup save: {str(e2)}")

def save_bazis_file3(hwnd):
    import ctypes
    from ctypes import wintypes
    
    # Определяем структуры для SendInput
    KEYEVENTF_KEYUP = 0x0002
    INPUT_KEYBOARD = 1

    PUL = ctypes.POINTER(ctypes.c_ulong)
    class KeyBdInput(ctypes.Structure):
        _fields_ = [("wVk", ctypes.c_ushort),
                   ("wScan", ctypes.c_ushort),
                   ("dwFlags", ctypes.c_ulong),
                   ("time", ctypes.c_ulong),
                   ("dwExtraInfo", PUL)]

    class HardwareInput(ctypes.Structure):
        _fields_ = [("uMsg", ctypes.c_ulong),
                   ("wParamL", ctypes.c_short),
                   ("wParamH", ctypes.c_ushort)]

    class MouseInput(ctypes.Structure):
        _fields_ = [("dx", ctypes.c_long),
                   ("dy", ctypes.c_long),
                   ("mouseData", ctypes.c_ulong),
                   ("dwFlags", ctypes.c_ulong),
                   ("time",ctypes.c_ulong),
                   ("dwExtraInfo", PUL)]

    class Input_I(ctypes.Union):
        _fields_ = [("ki", KeyBdInput),
                   ("mi", MouseInput),
                   ("hi", HardwareInput)]

    class Input(ctypes.Structure):
        _fields_ = [("type", ctypes.c_ulong),
                   ("ii", Input_I)]

    def press_key(hexKeyCode):
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.ki = KeyBdInput(hexKeyCode, 0x48, 0, 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(1), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    def release_key(hexKeyCode):
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        ii_.ki = KeyBdInput(hexKeyCode, 0x48, KEYEVENTF_KEYUP, 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(1), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    # Активируем окно
    shell = win32com.client.Dispatch("WScript.Shell")
    window_title = win32gui.GetWindowText(hwnd)
    shell.AppActivate(window_title)
    time.sleep(0.5)

    try:
        # Нажимаем Ctrl
        press_key(0x11)  # VK_CONTROL
        time.sleep(0.1)
        # Нажимаем S
        press_key(0x53)  # VK_S
        time.sleep(0.1)
        # Отпускаем S
        release_key(0x53)
        time.sleep(0.1)
        # Отпускаем Ctrl
        release_key(0x11)
        
        log_message("SendInput save command sent")
    except Exception as e:
        log_message(f"Error in SendInput save: {str(e)}")


def insert_material_folders():
    with open(os.path.join(SCRIPT_DIR, INPUT_DATA), "r", encoding='utf-8') as f:
        user_data = json.load(f)

    material_folders = json.dumps(user_data["MaterialFolders"])
    placeholder = '"{{MATERIAL_FOLDERS_PLACEHOLDER}}"'
    
    with open(os.path.join(SCRIPT_DIR, SUCCESS_FILE_FROM_BAZIS), "r", encoding='utf-8') as f:
        content = f.read()

    updated_content = content.replace(placeholder, material_folders)

    with open(os.path.join(SCRIPT_DIR, SUCCESS_FILE_FROM_BAZIS), 'w', encoding='utf-8') as file:
        file.write(updated_content)


def send_project_to_dotnet(from_bazis = True):
    with open(os.path.join(SCRIPT_DIR, INPUT_DATA), "r") as f:
        user_data = json.load(f)
    
    data = {
        "IdCompany": int(user_data["IdCompany"]),
        "IdUser": str(user_data["IdUser"]),
        "IdProject": str(user_data["IdProject"]),
        "Status": "success",
        "Message": "success"
    }

    files = []

    if from_bazis:
        data["ModelName"] = str(user_data["ModelName"])

        for filename in os.listdir(SCRIPT_DIR):
            file_path = os.path.join(SCRIPT_DIR, filename)
            if os.path.isfile(file_path) and filename not in ['.gitignore', INPUT_DATA, INPUT_MODEL]:
                files.append(('Files', (filename, open(file_path, 'rb'), 'application/octet-stream')))

    else:
        data["Status"] = 'file-bazis'
        data["IdCalculation"] = str(user_data["IdCalculation"])

        for filename in os.listdir(SCRIPT_DIR):
            file_path = os.path.join(SCRIPT_DIR, filename)
            if os.path.isfile(file_path) and filename == SUCCESS_FILE_TO_BAZIS:
                files.append(('Files', (filename, open(file_path, 'rb'), 'application/octet-stream')))


    try:
        response = requests.post(ENDPOINT, 
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
        
        # Check FROM BAZIS
        for folder_name in os.listdir(INPUTS_FROM_BAZIS):
            folder_path = os.path.join(INPUTS_FROM_BAZIS, folder_name)

            if os.path.isdir(folder_path):
                log_message(f"\n\n\n(from bazis) Found folder to process: {folder_name}")
                log_message(f"Starting processing project...", IdProject=folder_name)

                # move to processings
                processing_path = os.path.join(PROCESSING_DIR, folder_name)
                if os.path.exists(processing_path):
                    shutil.rmtree(processing_path)
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
                        if os.path.exists(error_path):
                            shutil.rmtree(error_path)
                        shutil.move(processing_path, error_path)
                        log_message(f"Moved to error folder: {error_path}")
                else:
                    log_message("Failed to process folder, moving to ERRORS", "ERROR")
                    error_path = os.path.join(ERROR_DIR, folder_name)
                    if os.path.exists(error_path):
                        shutil.rmtree(error_path)
                    shutil.move(processing_path, error_path)
                    log_message(f"Moved to error folder: {error_path}")

            time.sleep(1)
        

        # Check TO BAZIS
        for folder_name in os.listdir(INPUTS_TO_BAZIS):
            folder_path = os.path.join(INPUTS_TO_BAZIS, folder_name)

            if os.path.isdir(folder_path):
                log_message(f"\n\n\n(to bazis) Found folder to process: {folder_name}")
                
                id_project, id_calculation = folder_name.split('_')
                log_message(f"Starting processing project...", IdProject=id_project)

                processing_path = os.path.join(PROCESSING_DIR, folder_name)
                # move to processings
                if os.path.exists(processing_path):
                    shutil.rmtree(processing_path)
                shutil.move(folder_path, processing_path)
                log_message(f"Moved folder to processing: {processing_path}")

                # copy base-bazis-model to processings
                shutil.copy2("bazis-base-model.b3d", os.path.join(processing_path, "bazis-base-model.b3d"))
                log_message("bazis-base-model has been copied to processings folder")

                if process_folder_to_bazis(processing_path, id_project, id_calculation):
                    log_message("Folder processed successfully")

                    log_message("(to bazis) Trying send to .NET ...")
                    # Send to dotnet
                    if send_project_to_dotnet(from_bazis=False):
                        log_message("Data sent to .NET successfully", IdProject=id_project)
                        shutil.rmtree(processing_path)
                        log_message(f"Removed processing folder: {processing_path}")
                    else:
                        log_message("(to bazis) Failed to send to .NET, moving to ERRORS", "ERROR", IdProject=id_project, tg=True)
                        error_path = os.path.join(ERROR_DIR, folder_name)
                        if os.path.exists(error_path):
                            shutil.rmtree(error_path)
                        shutil.move(processing_path, error_path)
                        log_message(f"Moved to error folder: {error_path}")
                else:
                    log_message("Failed to process folder, moving to ERRORS", "ERROR")
                    error_path = os.path.join(ERROR_DIR, folder_name)
                    if os.path.exists(error_path):
                        shutil.rmtree(error_path)
                    shutil.move(processing_path, error_path)
                    log_message(f"Moved to error folder: {error_path}")




            time.sleep(1)

        time.sleep(10)

if __name__ == "__main__":
    main()
