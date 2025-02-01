import numpy as np
from pprint import pprint

def quaternion_to_rotation_matrix(q):
    x, y, z, w = q
    norm = np.sqrt(x*x + y*y + z*z + w*w)
    if norm == 0:
        return np.eye(3)
    x, y, z, w = x/norm, y/norm, z/norm, w/norm
    return np.array([
        [1 - 2*y*y - 2*z*z,   2*x*y - 2*z*w,     2*x*z + 2*y*w],
        [2*x*y + 2*z*w,       1 - 2*x*x - 2*z*z, 2*y*z - 2*x*w],
        [2*x*z - 2*y*w,       2*y*z + 2*x*w,     1 - 2*x*x - 2*y*y]
    ])

def get_box_faces(component):
    # Получаем позицию, размеры и кватернион
    pos = np.array([
        component["position"]["x"],
        component["position"]["y"],
        component["position"]["z"]
    ], dtype=float)
    
    size = np.array([
        component["size"]["x"],
        component["size"]["y"],
        component["size"]["z"]
    ], dtype=float)
    
    # Полуразмеры по каждой оси
    hx, hy, hz = size[0]/2.0, size[1]/2.0, size[2]/2.0
    
    # Локальные координаты 8 вершин (индексация согласно стандартной схеме)
    v0 = np.array([-hx, -hy, -hz])
    v1 = np.array([ hx, -hy, -hz])
    v2 = np.array([ hx,  hy, -hz])
    v3 = np.array([-hx,  hy, -hz])
    v4 = np.array([-hx, -hy,  hz])
    v5 = np.array([ hx, -hy,  hz])
    v6 = np.array([ hx,  hy,  hz])
    v7 = np.array([-hx,  hy,  hz])
    
    vertices = [v0, v1, v2, v3, v4, v5, v6, v7]
    
    # Применяем вращение (если rotation не единичное) и сдвиг (translation)
    q = component["rotation"]
    quat = [q["x"], q["y"], q["z"], q["w"]]
    R = quaternion_to_rotation_matrix(quat)
    world_vertices = [ pos + R.dot(v) for v in vertices ]
    
    # Определяем грани по индексам вершин.
    faces = {
        "front": [4, 5, 6, 7],
        "back": [0, 1, 2, 3],
        "left": [0, 3, 7, 4],
        "right": [1, 2, 6, 5],
        "top": [3, 2, 6, 7],
        "bottom": [0, 1, 5, 4]
    }
    
    # Собираем координаты для каждой грани
    faces_coords = {}
    for face_name, indices in faces.items():
        faces_coords[face_name] = [world_vertices[i] for i in indices]
    return faces_coords




# # Пример: одна деталь с заданными параметрами
# component = {
#     "position": {
#         "x": 0.0,
#         "y": 0.0,
#         "z": 0.0
#     },
#     "rotation": {
#         "x": 0.09101049,
#         "y": -0.57181,
#         "z": 0.524406433,
#         "w": 0.6242983
#     },
#     "size": {
#         "x": 600.0,
#         "y": 1000.0,
#         "z": 20.0
#     },
# }

# faces_coords = get_box_faces(component)
# print(faces_coords)

# # Выводим координаты каждой из 4-х точек для всех 6 граней
# for face, points in faces_coords.items():
#     print(f"Грань '{face}':")
#     for i, pt in enumerate(points):
#         print(f"  Точка {i+1}: {np.round(pt, 3)}")
#     print()








def compute_plane(face_points, tol=1e-6, decimals=3):
    p0, p1, p2 = face_points[0], face_points[1], face_points[2]
    v1 = p1 - p0
    v2 = p2 - p0
    normal = np.cross(v1, v2)
    norm_val = np.linalg.norm(normal)
    if norm_val < tol:
        normal = np.array([0.0, 0.0, 0.0])
    else:
        normal = normal / norm_val
    # Вычисляем D
    D = -np.dot(normal, p0)
    # Каноническое представление: если первый ненулевой компонент отрицательный, инвертируем
    for comp in normal:
        if abs(comp) > tol:
            if comp < 0:
                normal = -normal
                D = -D
            break
    # Округляем коэффициенты для использования в качестве ключа
    key = (round(normal[0], decimals), round(normal[1], decimals),
           round(normal[2], decimals), round(D, decimals))
    return key

def group_faces_by_plane(components, tol=1e-6, decimals=3):
    plane_dict = {}
    for comp in components:
        comp["faces"] = {}
        faces = get_box_faces(comp)
        for face_name, points in faces.items():

            plane_key = compute_plane(points, tol=tol, decimals=decimals)
            comp["faces"][face_name] = {
                "plane_key": plane_key, 
                "points": points, 
                "closed": False
            }

            if plane_key in plane_dict:
                plane_dict[plane_key].append(points)
            else:
                plane_dict[plane_key] = [points]
    return plane_dict

# Пример массива компонентов (здесь можно добавить больше деталей)
components = [
    {     
              "position": {
        "x": 120.424683,
        "y": -41.7468071,
        "z": -165.400665
      },
      "rotation": {
        "x": 0.3061863,
        "y": 0.1767767,
        "z": 0.176776648,
        "w": 0.918558657
      },
      "size": {
        "x": 500.0,
        "y": 500.0,
        "z": 100.0
      },
    },

    {     
      "position": {
        "x": -119.975929,
        "y": 0.0,
        "z": 101.225952
      },
      "rotation": {
        "x": 0.3061863,
        "y": 0.1767767,
        "z": 0.176776648,
        "w": 0.918558657
      },
      "size": {
        "x": 600.0,
        "y": 800.0,
        "z": 50.0
      },
    }
]

# Группируем грани всех компонентов по плоскостям
planes = group_faces_by_plane(components)

# Выводим полученный объект
print("Группировка граней по плоскостям:")
for plane_key, faces in planes.items():
    print(f"Плоскость {plane_key}:")
    for pts in faces:
        pts_str = ", ".join([str(np.round(pt,3)) for pt in pts])
        print(f"  грань: {pts_str}")
    print()


def check_rectangles_intersection(points1, points2, tolerance=1e-6):
    # Находим нормаль к плоскости
    v1 = points1[1] - points1[0]
    v2 = points1[3] - points1[0]
    normal = np.cross(v1, v2)
    normal = normal / np.linalg.norm(normal)
    
    # Находим два наиболее подходящих базисных вектора для проекции
    # Выбираем те оси, где нормаль имеет наименьшую компоненту
    components = np.abs(normal)
    skip_axis = np.argmax(components)
    axes = [i for i in range(3) if i != skip_axis]
    
    # Проецируем точки обоих прямоугольников на эту плоскость
    def project_points(points):
        return np.array([[p[axes[0]], p[axes[1]]] for p in points])
    
    rect1_2d = project_points(points1)
    rect2_2d = project_points(points2)
    
    # Находим минимальные и максимальные координаты для каждого прямоугольника
    min1 = np.min(rect1_2d, axis=0)
    max1 = np.max(rect1_2d, axis=0)
    min2 = np.min(rect2_2d, axis=0)
    max2 = np.max(rect2_2d, axis=0)
    
    # Проверяем перекрытие по обеим осям
    overlap = (
        max1[0] + tolerance >= min2[0] and
        max2[0] + tolerance >= min1[0] and
        max1[1] + tolerance >= min2[1] and
        max2[1] + tolerance >= min1[1]
    )
    
    return overlap

# Теперь можно модифицировать основной код:
def mark_closed_faces(components, planes):
    for comp in components:
        for face_name, face_data in comp['faces'].items():
            plane_key = face_data['plane_key']
            current_points = face_data['points']
            
            # Проверяем все грани в той же плоскости
            intersections = 0
            for other_points in planes[plane_key]:                    
                if check_rectangles_intersection(current_points, other_points):
                    intersections += 1
                    
            # Если есть хотя бы больше чем одно пересечение, помечаем грань как закрытую
            comp['faces'][face_name]['closed'] = intersections > 1

        # Обновляем edges на основе результатов анализа
        if 'modifier' in comp and 'edges' in comp['modifier']:
            edges = comp['modifier']['edges']
            
            # left face -> edge[0]
            if comp['faces'].get('left', {}).get('closed', False):
                edges[0]['type'] = 2
                edges[0]['size']['z'] = 2
                
            # top face -> edge[1]
            if comp['faces'].get('top', {}).get('closed', False):
                edges[1]['type'] = 2
                edges[1]['size']['z'] = 2
                
            # right face -> edge[2]
            if comp['faces'].get('right', {}).get('closed', False):
                edges[2]['type'] = 2
                edges[2]['size']['z'] = 2
                
            # bottom face -> edge[3]
            if comp['faces'].get('bottom', {}).get('closed', False):
                edges[3]['type'] = 2
                edges[3]['size']['z'] = 2

mark_closed_faces(components, planes)

pprint(components)

def analyze_butts(components):
    planes = group_faces_by_plane(components)
    mark_closed_faces(components, planes)

    return components












