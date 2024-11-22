import numpy as np

def analyze_obj(filename='model_27.obj'):
    vertices = []
    faces = []
    
    # Чтение файла
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('v '):  # вершины
                # Разбираем строку и конвертируем в числа с плавающей точкой
                coords = [float(x) for x in line.strip().split()[1:4]]
                vertices.append(coords)
            elif line.startswith('f '):  # грани
                # Получаем индексы вершин для каждой грани
                # OBJ использует 1-based индексирование
                face = [int(x.split('/')[0]) - 1 for x in line.strip().split()[1:]]
                faces.append(face)
    
    # Конвертируем в numpy массив для удобства вычислений
    vertices = np.array(vertices)
    
    if len(vertices) == 0:
        raise ValueError("Файл не содержит вершин!")
    
    # Вычисляем габариты
    min_coords = np.min(vertices, axis=0)
    max_coords = np.max(vertices, axis=0)
    dimensions = max_coords - min_coords
    
    # Вычисляем центр модели
    center = (max_coords + min_coords) / 2
    
    # Вычисляем диагональ (для масштаба)
    diagonal = np.sqrt(np.sum(dimensions ** 2))
    
    # Формируем отчет
    print(f"\nАнализ файла: {filename}")
    print("\nГабаритные размеры:")
    print(f"X: {dimensions[0]:.6f} (от {min_coords[0]:.6f} до {max_coords[0]:.6f})")
    print(f"Y: {dimensions[1]:.6f} (от {min_coords[1]:.6f} до {max_coords[1]:.6f})")
    print(f"Z: {dimensions[2]:.6f} (от {min_coords[2]:.6f} до {max_coords[2]:.6f})")
    print(f"\nДиагональ: {diagonal:.6f}")
    
    print("\nЦентр модели:")
    print(f"X: {center[0]:.6f}")
    print(f"Y: {center[1]:.6f}")
    print(f"Z: {center[2]:.6f}")
    
    print(f"\nСтатистика:")
    print(f"Количество вершин: {len(vertices)}")
    print(f"Количество граней: {len(faces)}")
    
    return {
        'dimensions': dimensions,
        'center': center,
        'min_coords': min_coords,
        'max_coords': max_coords,
        'diagonal': diagonal,
        'vertex_count': len(vertices),
        'face_count': len(faces)
    }

if __name__ == "__main__":
    try:
        analyze_obj()
    except FileNotFoundError:
        print("Ошибка: Файл 'model.obj' не найден в текущей директории")
    except Exception as e:
        print(f"Ошибка при анализе файла: {str(e)}")