import os
from subprocess import run
from dotenv import load_dotenv
load_dotenv()

ASSIMP_PATH = os.getenv('ASSIMP_PATH')

def convert_obj_to_fbx(obj_path):
    fbx_path = obj_path.replace('.obj', '.fbx')
    print(f"Converting {obj_path} to {fbx_path}")
    try:
        # run([ASSIMP_PATH, 'export', obj_path, fbx_path, '--help'], check=True)
        run([
            ASSIMP_PATH, 
            'export',
            obj_path, 
            fbx_path,
        ], check=True)
        print(f"Success: {os.path.basename(obj_path)}")
    except Exception as e:
        print(f"Error converting {obj_path}: {str(e)}")

# Папка с OBJ файлами
directory = "results"

for filename in os.listdir(directory):
    if filename.endswith('.obj'):
        obj_path = os.path.join(directory, filename)
        convert_obj_to_fbx(obj_path)