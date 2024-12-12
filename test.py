import win32gui
import win32con
import numpy as np
import math
import json
import win32com.client
import pythoncom
from pprint import pprint
from scipy.spatial.transform import Rotation
import uuid
import re
import time

import subprocess
import math
import subprocess

# def resize_window(hwnd, width, height):
#     left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    
#     win32gui.MoveWindow(hwnd, left, top, width, height, True)
    
#     padding_left = 100 
#     padding_top = 20
#     win32gui.SetWindowPos(hwnd, 0, padding_left, padding_top, 0, 0, win32con.SWP_NOSIZE | win32con.SWP_NOZORDER)

# def list_all_windows():
#     def callback(hwnd, windows):
#         if win32gui.IsWindowVisible(hwnd):
#             title = win32gui.GetWindowText(hwnd)
#             if title:
#                 windows.append((hwnd, title))
#         return True

#     windows = []
#     win32gui.EnumWindows(callback, windows)

#     for window in windows:
#         print(f"HWND: {window[0]}, Title: {window[1]}")

# list_all_windows()

# # resize_window(657996, 768, 1280)

from pro100 import main as convert_pro100 

from dotenv import load_dotenv
import os
import time
import win32com.client
from pprint import pprint

load_dotenv()
# PRO100_PATH = os.getenv('PRO100_PATH')
# pro100_process = subprocess.Popen([PRO100_PATH])

time.sleep(2)

# convert_pro100(pro100_process)





def ungroup_all(project):
    selection = project.selection
    while True:
        found_groups = False
        selection.clear()
        
        for entity in project.Entities:
            if entity.entityClass == 'IGroupEntity':
                selection.add(entity)
                found_groups = True
        
        if not found_groups:
            break
            
        selection.ungroup()

def analyze_panel(entity):
    # Получаем базовые размеры
    base_x = entity.dimensions.x
    base_y = entity.dimensions.y 
    base_z = entity.dimensions.z
    
    # Получаем целевые размеры
    target_width = entity.width
    target_height = entity.length
    target_depth = entity.depth
    
    print(f"\nАнализ детали {entity.name}:")
    print(f"Базовые размеры (x,y,z): {base_x}, {base_y}, {base_z}")
    print(f"Целевые размеры (w,h,d): {target_width}, {target_height}, {target_depth}")
    
    # Определяем какая это ориентация
    if abs(base_x - target_depth) < 0.1 and abs(base_y - target_width) < 0.1 and abs(base_z - target_height) < 0.1:
        print("Это вертикальная панель, повернутая на 90° вокруг Y")
        # entity.rotate(0, 90, 0)
    elif abs(base_x - target_width) < 0.1 and abs(base_y - target_depth) < 0.1 and abs(base_z - target_height) < 0.1:
        print("Это вертикальная панель")
        # entity.rotate(0, 0, 0)
    elif abs(base_x - target_depth) < 0.1 and abs(base_y - target_height) < 0.1 and abs(base_z - target_width) < 0.1:
        print("Это горизонтальная панель, повернутая на 90°")
        # entity.rotate(90, 90, 0)
    # и так далее для всех возможных ориентаций


import math 
RAD_90 = math.pi / 2

class Rot3D:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z



def normalize_panel_rotation(entity):
    base_x = entity.dimensions.x
    base_y = entity.dimensions.y 
    base_z = entity.dimensions.z
    
    target_width = entity.width
    target_height = entity.length
    target_depth = entity.depth

    print(f"Базовые размеры (x,y,z): {base_x}, {base_y}, {base_z}")
    print(f"Целевые размеры (w,h,d): {target_width}, {target_height}, {target_depth}")

    eps = 0.001  # погрешность для сравнения float
    
    if (abs(base_x - target_width) < eps and 
        abs(base_y - target_height) < eps and 
        abs(base_z - target_depth) < eps):
        print("Нормальная панель - не поворачиваем.")
        return Rot3D(
            0,
            0,
            0
        )
        
    if (abs(base_x - target_depth) < eps and 
        abs(base_y - target_height) < eps and 
        abs(base_z - target_width) < eps):
        print("Боковая панель - поворачиваем на 90° вокруг Y")
        return Rot3D(
            0,
            RAD_90,
            0
        )

    if (abs(base_x - target_width) < eps and 
        abs(base_y - target_depth) < eps and 
        abs(base_z - target_height) < eps):
        print("Лежачая панель - поворачиваем на 90° вокруг X")
        return Rot3D(
            RAD_90,
            0,
            0
        )
    
    # Случай 4: (x,y,z) = (l,w,d) - Нормальная панель, но повернута вокруг своей оси на 90
    if (abs(base_x - target_height) < eps and 
        abs(base_y - target_width) < eps and 
        abs(base_z - target_depth) < eps):
        print("Случай 4: (x,y,z) = (l,w,d) - Нормальная панель, но повернута вокруг своей оси на 90")
        return Rot3D(0, 0, RAD_90)

    # Случай 5: (x,y,z) = (l,d,w) - Боковая панель, но повернута вокруг своей оси на 90
    if (abs(base_x - target_height) < eps and 
        abs(base_y - target_depth) < eps and 
        abs(base_z - target_width) < eps):
        print("Случай 5: (x,y,z) = (l,d,w) - Боковая панель, но повернута вокруг своей оси на 90")
        return Rot3D(RAD_90, RAD_90, 0)

    # Случай 6: (x,y,z) = (d,w,l) - Лежачая панель, но повернута вокруг своей оси на 90
    if (abs(base_x - target_depth) < eps and 
        abs(base_y - target_width) < eps and 
        abs(base_z - target_height) < eps):
        print("Случай 6: (x,y,z) = (d,w,l) - Лежачая панель, но повернута вокруг своей оси на 90")
        return Rot3D(RAD_90, 0, RAD_90)
    

    print("ВНИМАНИЕ: Не удалось определить правильный поворот!")
    print("Требуется добавить новый случай в функцию")
    print(f"Базовые размеры (x,y,z): {base_x}, {base_y}, {base_z}")
    print(f"Целевые размеры (w,h,d): {target_width}, {target_height}, {target_depth}")








psto_app = win32com.client.Dispatch("P100.Application")

project = psto_app.Project
ungroup_all(project)

print("Application methods:")
# pprint(dir(psto_app))

print("Project attributes:")
# pprint (dir(project))

        # selection = psto_app.Project.selection
        # print("selection attributes:")
        # # pprint (dir(selection))



# Применяем ко всем панелям
for entity in project.Entities:
    print(f"{entity.name}")
    if hasattr(entity, 'dimensions'):
        # entity.rotate(RAD_90, 0, RAD_90)
        og = entity.rotation
        print(f"og ROT {og.x, og.y, og.z}")

        # original_euler = Rot3D(
        #     entity.rotation.x,
        #     entity.rotation.y,
        #     entity.rotation.z
        # )

        # original_rotation = Rotation.from_euler('yxz', [
        #     -original_euler.y,  # -pitch
        #     original_euler.x,   # roll
        #     -original_euler.z   # -yaw
        # ], degrees=False)  # радианы
        
        # entity.unrotate(
        #     original_euler.x,
        #     original_euler.y,
        #     original_euler.z
        # )

        # base_rotation = normalize_panel_rotation(entity)

        # additional_rotation = Rotation.from_euler('yxz', [
        #     -base_rotation.y,  # -pitch
        #     base_rotation.x,   # roll
        #     -base_rotation.z   # -yaw
        # ], degrees=False)  # радианы


        # final_rotation = original_rotation * additional_rotation
        # quaternion = final_rotation.as_quat()
        
        # # entity.rotate(
        # #     kek.x,
        # #     kek.y,
        # #     kek.z
        # # )


        # og = entity.rotation
        # print(f"ROT {og.x, og.y, og.z}")

        # print("Additional euler angles:", base_rotation.x, base_rotation.y, base_rotation.z)
        # print("Original rotation quaternion:", original_rotation.as_quat())
        # print("Additional rotation quaternion:", additional_rotation.as_quat())

        # print(f"quaternion {quaternion}")
        # # entity.unrotate(og.x, og.y, og.z)
        # # entity.unrotate(RAD_90/5,RAD_90/5,RAD_90/5)





# class Rot3D:
#     def __init__(self, x, y, z):
#         self.x = x
#         self.y = y
#         self.z = z


# for i, entity in enumerate(project.Entities):
#     # pprint (dir(entity.GetTypeInfo))
#     # entity.unrotate(RAD_90/5,RAD_90/5,RAD_90/5)


#     # print(f"\n{'='*50}")
#     # print(f"Panel #{i + 1} - {entity.name}")
#     # print(f"{'='*50}")

    
#     material_name = entity.material.textureName
#     print(material_name)

#     # print(entity.rotation.x)
#     # original_euler = Rot3D(
#     #     entity.rotation.x,
#     #     entity.rotation.y,
#     #     entity.rotation.z
#     # )

#     # original_rotation = Rotation.from_euler('yxz', [
#     #     -original_euler.y,  # -pitch
#     #     original_euler.x,   # roll
#     #     -original_euler.z   # -yaw
#     # ], degrees=False)  # радианы

#     # entity.unrotate(
#     #     original_euler.x,
#     #     original_euler.y,
#     #     original_euler.z
#     # )







    

    # # # Все базовые свойства
    # # base_properties = [
    # #     'name', 'entityClass', 'material', 'comment', 'fileName',
    # #     'locked', 'reportAsPart', 'reportAsUsed', 'reportAsCuted',
    # #     'reportUnits', 'priceName', 'priceID'
    # # ]
    
    # # print("\n--- Basic Properties ---")
    # # for prop in base_properties:
    # #     try:
    # #         value = getattr(entity, prop)
    # #         print(f"{prop}: {value}")
    # #     except Exception as e:
    # #         print(f"{prop}: [Error: {str(e)}]")
    
    

    # # Размерные характеристики
    # print("\nReal dimensions (dimensions object):")
    # print(f"  X: {entity.dimensions.x}")
    # print(f"  Y: {entity.dimensions.y}")
    # print(f"  Z: {entity.dimensions.z}")

    # print("\nProjected dimensions:")
    # print(f"  Width: {entity.width}")
    # print(f"  Length: {entity.length}")
    # print(f"  Depth: {entity.depth}")


    # print("\nRotation:")
    # print(f"  X: {entity.rotation.x}")
    # print(f"  Y: {entity.rotation.y}")
    # print(f"  Z: {entity.rotation.z}")

    # # print("\nCenter:")
    # # print(f"  X: {entity.center.x}")
    # # print(f"  Y: {entity.center.y}")
    # # print(f"  Z: {entity.center.z}")





    
    # og = entity.rotation
    # entity.unrotate(og.x, og.y, og.z)

    
    # normalize_panel_rotation(entity)

    # entity.rotate(og.x, og.y-RAD_90, og.z)
    # entity.rotate(-0.1919862177193704, -0.1919862177193704-RAD_90, -0.7679448708775338)
    

    # if hasattr(entity, 'dimensions'):  # проверяем что это панель
    #     # analyze_panel(entity)



    # if entity.entityClass == 'IGroupEntity':

        #         print("IGroupEntity attributes:")
        #         selection.add(entity)
        #         # pprint (dir(entity))

        # selection.ungroup()



# selection = psto_app.Project.selection



#     # material_name = entity.material.textureName
        # print(1)#.material.textureName)
        # print(entity.entityClass)#.material.textureName)


# # project.loadFromFIle('cheche.sto')
# # test = project.getImage(500, 500)
# # project.saveToFile('cheche.jpg')

# import os
# import time
# import win32com.client
# import win32gui
# import win32ui
# import win32con
# import win32api
# from ctypes import windll, byref, create_string_buffer, c_void_p

# # handle = project.getImage(500, 500)
# # print(f"Handle получен: {handle}")

# print("Получаем handle...")
# handle = project.getImage(500, 500)
# print(f"Handle: {handle} (hex: 0x{handle:X})")

# def check_handle_type(handle):
#     # Список всех типов GDI объектов для проверки
#     gdi_types = {
#         win32con.OBJ_BITMAP: "BITMAP",
#         win32con.OBJ_BRUSH: "BRUSH",
#         win32con.OBJ_DC: "DC",
#         win32con.OBJ_ENHMETADC: "ENHMETADC",
#         win32con.OBJ_ENHMETAFILE: "ENHMETAFILE",
#         win32con.OBJ_FONT: "FONT",
#         win32con.OBJ_MEMDC: "MEMDC",
#         win32con.OBJ_PAL: "PALETTE",
#         win32con.OBJ_PEN: "PEN",
#         win32con.OBJ_REGION: "REGION"
#     }
    
#     print("Проверка типов handle...")
#     for type_id, type_name in gdi_types.items():
#         try:
#             if windll.gdi32.GetObjectType(handle) == type_id:
#                 print(f"✓ Это {type_name} (тип {type_id})")
#                 return type_id
#         except:
#             continue
    
#     print("Handle не является стандартным GDI объектом")
    
#     # Проверяем другие возможные типы
#     try:
#         if windll.user32.IsWindow(handle):
#             print("✓ Это WINDOW handle")
#             return "WINDOW"
#     except:
#         pass
        
#     try:
#         if win32gui.IsWindow(handle):
#             print("✓ Это WINDOW handle (win32gui)")
#             return "WINDOW"
#     except:
#         pass

#     # Пробуем получить информацию о процессе
#     try:
#         process_id = windll.kernel32.GetProcessId(handle)
#         if process_id:
#             print(f"✓ Это handle процесса (PID: {process_id})")
#             return "PROCESS"
#     except:
#         pass
    
#     # Проверяем, может это глобальная память
#     try:
#         size = windll.kernel32.GlobalSize(handle)
#         if size:
#             print(f"✓ Это GLOBAL MEMORY handle (размер: {size} байт)")
#             return "GLOBAL_MEMORY"
#     except:
#         pass
    
#     return None

# # Проверяем тип handle
# handle_type = check_handle_type(handle)

# if handle_type:
#     print(f"\nОбнаружен тип: {handle_type}")
# else:
#     print("\nНе удалось определить тип handle")
    
# # Дополнительная информация
# print("\nДополнительные проверки:")
# try:
#     print(f"GetLastError: {windll.kernel32.GetLastError()}")
# except:
#     pass

# try:
#     print(f"IsValidHandle: {bool(windll.kernel32.CloseHandle(handle))}")
# except:
#     pass