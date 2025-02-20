
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




load_dotenv()
BAZIS_PATH = os.getenv('BAZIS_PATH')
BAZIS_PIRATE_PATH = os.getenv('BAZIS_PIRATE_PATH')
PRO100_PATH = os.getenv('PRO100_PATH')

BAZIS_CRACK_FILE_PATH = os.getenv('BAZIS_CRACK_FILE_PATH')
APPDATA_ROAMING_FOLDER_PATH = os.getenv('APPDATA_ROAMING_FOLDER_PATH')
SUPERUSERS_FILE = "superusers.txt"

ENDPOINT = os.getenv('ENDPOINT')

ASSIMP_PATH = os.getenv('ASSIMP_PATH')

# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT_DIR = "results"
CONVERTER_FROM_BAZIS_SCRIPT = "./convertBazisToVariant.js"
CONVERTER_TO_BAZIS_SCRIPT = "./convertVariantToBazis.js"

INPUTS_TO_BAZIS = "inputs_to_bazis"
INPUTS_FROM_BAZIS = "inputs_from_bazis"
INPUTS_FROM_PRO100 = "inputs_from_pro100"

PROCESSING_DIR = "processings"
ERROR_DIR = "errors"

INPUT_MODEL = "model.b3d"
INPUT_PRO100_MODEL = "model.sto"
INPUT_DATA = "user_data.json"
SUCCESS_FILE_S123PROJ = "project.s123proj"
SUCCESS_FILE_TO_BAZIS = "bazis.b3d"
MAIN_ICON = "main_icon.jpg"
ICON_SIZE = 512

TIMEOUT = 240


import os
import pyassimp.helper


# Добавляем путь к папке с assimp.dll в список поиска
ASSIMP_PATH2="C:\\Program Files\\Assimp\\bin\\x64"
assimp_dir = os.path.dirname(ASSIMP_PATH2)
pyassimp.helper.additional_dirs.append(assimp_dir)



import pyassimp
import os

def combine_models():
    try:
        # Загружаем обе модели
        panel_scene = pyassimp.load(os.path.join(SCRIPT_DIR, "panel.obj"))
        butts_scene = pyassimp.load(os.path.join(SCRIPT_DIR, "butts.obj"))

        # Создаем новую сцену
        combined_scene = pyassimp.Scene()
        
        # Создаем корневой узел
        combined_scene.rootnode = pyassimp.Node("root")
        
        # Создаем узлы для панели и кромок
        panel_node = pyassimp.Node("Panel")
        butts_node = pyassimp.Node("Butts")
        
        # Добавляем меши в соответствующие узлы
        panel_node.meshes = panel_scene.meshes
        butts_node.meshes = butts_scene.meshes
        
        # Добавляем узлы в корневой узел
        combined_scene.rootnode.children.append(panel_node)
        combined_scene.rootnode.children.append(butts_node)

        # Экспортируем в FBX
        pyassimp.export(combined_scene, os.path.join(SCRIPT_DIR, "combined.fbx"), 'fbx')
        
        # Освобождаем ресурсы
        pyassimp.release(panel_scene)
        pyassimp.release(butts_scene)
        
        return True
        
    except Exception as e:
        print(f"Error combining models: {str(e)}")
        return False