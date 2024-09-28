
import os
from datetime import datetime

LOG_DIR = "logs"
FOLDER_CHECK_LOG = "last_folder_check.log"

def log_folder_check():
    current_time = datetime.now()
    log_entry = f"Folder check: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    
    log_path = os.path.join(LOG_DIR, FOLDER_CHECK_LOG)
    
    with open(log_path, "w", encoding="utf-8") as log_file:
        log_file.write(log_entry)

def log_message(message, level="INFO"):
    current_date = datetime.now()
    log_filename = f"logs_{current_date.strftime('%d%m%y')}.log"
    timestamp = current_date.strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}"
    
    print(log_entry)
    
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    
    log_path = os.path.join(LOG_DIR, log_filename)
    with open(log_path, "a", encoding="utf-8") as log_file:
        log_file.write(log_entry + "\n")