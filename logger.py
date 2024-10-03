import requests
import os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()


LOG_DIR = "logs"
FOLDER_CHECK_LOG = "last_folder_check.log"
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


def send_tg(input):
    response = requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", json={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": input
    })

def log_folder_check():
    current_time = datetime.now()
    log_entry = f"Folder check: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    
    log_path = os.path.join(LOG_DIR, FOLDER_CHECK_LOG)
    
    with open(log_path, "w", encoding="utf-8") as log_file:
        log_file.write(log_entry)

def log_message(message, level="INFO", IdProject=None, tg=False):
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

    if IdProject:
        # response = requests.post("http://localhost:8123/api/Projects/CreateProjectFromBazisService", # debug
        response = requests.post("https://api.system123.ru/api/Projects/CreateProjectFromBazisService", # prod
            data = {
                "IdProject": str(IdProject),
                "Status": str(level.lower()),
                "Message": str(message)
            }
        )

    if tg or IdProject:
        if IdProject:
            send_tg(f"{log_entry}.\n\nProject: {IdProject}")
        else:
            send_tg(f"{log_entry}")