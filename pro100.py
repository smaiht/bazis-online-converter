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

def new_guid():
    return str(uuid.uuid4())

def normalize(s):
    # Преобразуем в нижний регистр
    s = s.lower()
    # Заменяем все символы кроме букв, цифр на пробелы
    s = re.sub(r'[^a-zа-яё0-9\s]', ' ', s)
    # Заменяем множественные пробелы на один
    s = re.sub(r'\s+', ' ', s)
    # Убираем пробелы в начале и конце
    s = s.strip()
    return s

def find_material(base_name, materials):
    normalized_base = normalize(base_name)
    words = normalized_base.split()
    
    # print(f"Исходное имя материала: {base_name}")
    # print(f"Нормализованное имя: {normalized_base}")
    # print(f"Искомые слова: {words}")
    
    best_match = "2381385d-91bb-47fa-8925-df8d0f2dd0bd"  # default material
    max_matched_words = 1
    
    for name, guid in materials.items():
        normalized_name = normalize(name)
        matched_words = sum(1 for word in words if word in normalized_name)
        
        if matched_words > max_matched_words:
            max_matched_words = matched_words
            best_match = guid
    
    return best_match

def create_material_input(color_name, index, material_guid):
    return {
        "guid": new_guid(),
        "verbose_ru": None,
        "name": f"Цвет {index+1}",
        "type": 7,
        "value": f"s123mat://{material_guid}",
        "settings": {
            "values": "", # "{{MATERIAL_FOLDERS_PLACEHOLDER}}",
            "target": 3,
            "has_none": False,
            "tag": "material",
            "is_interactive": True,
            "event": None,
            "show_in_preview": False,
            "show_in_consult": True
        },
        "is_active": True,
        "is_hidden": False,
        "hint": color_name,
        "order": 0,
        "related": None
    }

def create_get_input_node(input_name, y_position, order):
    return {
        "guid": new_guid(),
        "name": "Получить вход",
        "color": "#7dff63",
        "position": {
            "x": -350,
            "y": y_position
        },
        "method": {
            "name": "GetInputValue",
            "arguments": [{
                "name": "input",
                "value": input_name,
                "type": 20
            }],
            "result": {
                "name": None,
                "value": None,
                "type": 1
            }
        },
        "order": order
    }

def create_set_material_node(component_paths, input_node_guid, y_position, order):
    details_list = []
    for i, path in enumerate(component_paths):
        details_list.append({
            "type": 3,
            "key": chr(65 + i),  # A, B, C, etc.
            "value": path
        })

    return {
        "guid": new_guid(),
        "name": "Задать материал ЛДСП",
        "color": "#fff",
        "position": {
            "x": -50,
            "y": y_position
        },
        "method": {
            "name": "SetLDSPMaterial",
            "arguments": [
                {
                    "name": "components",
                    "value": details_list,
                    "type": 18
                },
                {
                    "name": "material",
                    "value": {
                        "node_guid": input_node_guid,
                        "pair_key": None
                    },
                    "type": 2
                }
            ],
            "result": {
                "name": None,
                "value": None,
                "type": 0
            }
        },
        "order": order
    }

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


def normalize_panel_rotation(entity):
    base_x = entity.dimensions.x
    base_y = entity.dimensions.y 
    base_z = entity.dimensions.z
    
    target_width = entity.width
    target_height = entity.length
    target_depth = entity.depth
    
    # print(f"\nНормализация детали:")
    
    eps = 0.001  # погрешность для сравнения float
    RAD_90 = math.pi / 2
    
    if (abs(base_x - target_width) < eps and 
        abs(base_y - target_height) < eps and 
        abs(base_z - target_depth) < eps):
        print("Нормальная панель - не поворачиваем.")
        # entity.rotate(0, 0, 0)
        return
        
    if (abs(base_x - target_depth) < eps and 
        abs(base_y - target_height) < eps and 
        abs(base_z - target_width) < eps):
        print("Боковая панель - поворачиваем на 90° вокруг Y")
        entity.rotate(0, RAD_90, 0)
        return

    if (abs(base_x - target_width) < eps and 
        abs(base_y - target_depth) < eps and 
        abs(base_z - target_height) < eps):
        print("Лежачая панель - поворачиваем на 90° вокруг X")
        entity.rotate(RAD_90, 0, 0)
        return

    # Случай 4: Повернутая на Z и Y
    if (abs(base_x - target_height) < eps and
        abs(base_y - target_depth) < eps and
        abs(base_z - target_width) < eps):
        print("Повернутая панель - поворачиваем на 90° вокруг Z, затем 90° вокруг Y")
        entity.rotate(0, RAD_90, RAD_90)
        return

    # Случай 5: x->height, y->width, z->depth
    if (abs(base_x - target_height) < eps and
        abs(base_y - target_width) < eps and
        abs(base_z - target_depth) < eps):
        print("Вертикальная развернутая панель - поворачиваем на 90° вокруг Z")
        entity.rotate(0, 0, RAD_90)
        return

    # Случай 6: Поменять x и y местами
    if (abs(base_x - target_height) < eps and
        abs(base_y - target_width) < eps and
        abs(base_z - target_depth) < eps):
        print("Перевернутая панель - поворачиваем на 90° вокруг Z")
        entity.rotate(0, 0, RAD_90)
        return

    print("ВНИМАНИЕ: Не удалось определить правильный поворот!")
    print("Требуется добавить новый случай в функцию")
    print(f"Базовые размеры (x,y,z): {base_x}, {base_y}, {base_z}")
    print(f"Целевые размеры (w,h,d): {target_width}, {target_height}, {target_depth}")
        


def main(pro100_process):
    components = []
    inputs = []
    nodes = []
    materials = {}
    details = {}

    psto_app = win32com.client.Dispatch("P100.Application")
    
    # time.sleep(22)


    try:
        if not psto_app.Visible:
            psto_app.FileOpen()

        project = psto_app.Project

        

        project.loadFromFIle('results/model.sto')

        time.sleep(5)


        ungroup_all(project)

        # Load materials mapping from file
        with open('materials_mapping.json', 'r', encoding='utf-8') as f:
            sys_mats = json.load(f)

        # print("project attributes:")
        # pprint (dir(project))

        # project.getImage(500, 500)


        # Process entities and collect materials
        for i, entity in enumerate(project.Entities):
            normalize_panel_rotation(entity)

            material_name = entity.material.textureName
            # print(material_name)
            
            # Create component
            roll = entity.rotation.x * 180/np.pi
            pitch = entity.rotation.y * 180/np.pi
            yaw = entity.rotation.z * 180/np.pi
            r = Rotation.from_euler('yxz', [-pitch, roll, -yaw], degrees=True)
            quaternion = r.as_quat()

            component = {
                'position': {
                    'x': -entity.center.x * 1000,
                    'y': entity.center.y * 1000,
                    'z': entity.center.z * 1000
                    # 'x': -entity.position.x * 1000,
                    # 'y': entity.position.y * 1000,
                    # 'z': entity.position.z * 1000
                },
                'rotation': {
                    'x': quaternion[0],
                    'y': quaternion[1],
                    'z': quaternion[2],
                    'w': quaternion[3]
                },
                "size": {
                    "x": entity.width * 1000,
                    "y": entity.length * 1000,
                    "z": entity.depth * 1000
                },
                'modifier': {
                    "cut_angle1": 0.0,
                    "cut_angle2": 0.0,
                    "back_material": None,
                    "edges": [{
                        "type": 0, #arrKromok[3],
                        "material": None,
                        "size": {
                            "x": entity.depth * 1000,
                            "y": 1000.0,
                            "z": 0 #arrKromokZ[3]
                        }

                    }, {
                        "type": 0, #arrKromok[2],
                        "material": None,
                        "size": {
                            "x": entity.depth * 1000,
                            "y": 1000.0,
                            "z": 0 #arrKromokZ[2]
                        }

                    }, {
                        "type": 0, #arrKromok[1],
                        "material": None,
                        "size": {
                            "x": entity.depth * 1000,
                            "y": 1000.0,
                            "z": 0 #arrKromokZ[1]
                        }

                    }, {
                        "type": 0, #arrKromok[0],
                        "material": None,
                        "size": {
                            "x": entity.depth * 1000,
                            "y": 1000.0,
                            "z": 0 #arrKromokZ[0]
                        }

                    }],

                    "type": 9
                },
                "material": None,
                "color": None,
                "ignore_bounds": False,
                "bake": None,
                "processings": [],
                "is_active": True,
                "max_texture_size": 512,
                "build_order": i,
                "order": i,
                "user_data": None,
                "positioning_points": [],
                'name': (entity.name or "Деталь") + " " + str(i),
                'path': "Детали",
                'guid': str(uuid.uuid4()),
            }
            
            # Add material handling
            if material_name not in details:
                materials[material_name] = find_material(material_name, sys_mats)
                details[material_name] = []
            
            details[material_name].append(f"{component['path']}/{component['name']}")
            component["material"] = f"s123mat://{materials[material_name]}"
            
            components.append(component)




        # Create material inputs and nodes
        for i, (material_name, material_guid) in enumerate(materials.items()):

            # Create input
            material_input = create_material_input(material_name, i, material_guid)
            inputs.append(material_input)
            # print(material_input)
            
            # Create get input node
            get_input_node = create_get_input_node(material_input["name"], i * 200, i + 1)
            nodes.append(get_input_node)
            # print(get_input_node)
            
            # Create set material node
            set_material_node = create_set_material_node(
                details[material_name],
                get_input_node["guid"],
                i * 200,
                i + 1
            )
            nodes.append(set_material_node)
            # print(set_material_node)


        


        # Create final project structure
        s123project = {
            "virtual_objects": [],
            "type": None,
            "background_color": "",
            "anchor_x": 2,
            "anchor_y": 1,
            "anchor_z": 2,
            "offset": {
                "x": 0.0,
                "y": 0.0,
                "z": 0.0
            },
            "normal": {
                "x": 0.0,
                "y": 0.0,
                "z": 0.0
            },
            "graph": {
                "inputs": inputs,
                "outputs": [],
                "nodes": nodes,
                "related_inputs": {},
                "comments": [],
                "is_active": True,
                "position": {
                    "x": 0.0,
                    "y": 0.0
                },
                "scale": 1.0
            },
            "components": components,
            "connection_points": []
        }

        # Save project
        with open('results/project.s123proj', 'w') as f:
            json.dump(s123project, f, indent=4)

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    finally:
        print('finally')
        try:
            pro100_process.terminate()
            pro100_process.wait(timeout = 3)
        except subprocess.TimeoutExpired:
            print('pro100_process did not terminate gracefully, forcing...')
            pro100_process.kill()
        
        print('pro100_process terminated')

if __name__ == "__main__":
    main()