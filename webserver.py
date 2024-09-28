import uvicorn
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import List
import os
import uuid
import json
import shutil

from logger import log_message

app = FastAPI()

INPUT_DIR = "inputs"
TEMP_DIR = "temp"

@app.post("/upload_bazis_project/")
async def create_upload_files(files: List[UploadFile] = File(...), user_data: str = Form(...)):
    log_message("\n\nNew request received")

    folder_id = str(uuid.uuid4())
    temp_folder_path = os.path.join(TEMP_DIR, folder_id)
    os.makedirs(temp_folder_path, exist_ok=True)
    log_message(f"Created temporary folder: {temp_folder_path}")

    try:
        # Parse user_data
        user_data_dict = json.loads(user_data)
        log_message(f"Received user data: {user_data_dict}")

        # Flag to check if we've renamed a .b3d file
        b3d_file_renamed = False

        # Save files
        for file in files:
            file_location = os.path.join(temp_folder_path, file.filename)
            with open(file_location, "wb+") as file_object:
                file_object.write(await file.read())
            log_message(f"Saved file: {file.filename}")

            # Rename the first .b3d file to model.b3d
            if not b3d_file_renamed and file.filename.lower().endswith('.b3d'):
                new_file_location = os.path.join(temp_folder_path, "model.b3d")
                user_data_dict['ModelName'] = file.filename[:-4] # ".b3d" = 4 symbols
                log_message(f"Renamed {file.filename} to model.b3d")
                os.rename(file_location, new_file_location)
                b3d_file_renamed = True

        # Save user_data.json
        user_data_path = os.path.join(temp_folder_path, "user_data.json")
        with open(user_data_path, "w") as user_data_file:
            json.dump(user_data_dict, user_data_file)
        log_message("Saved user_data.json")

        # Move the completed folder to INPUT_DIR
        final_folder_path = os.path.join(INPUT_DIR, folder_id)
        shutil.move(temp_folder_path, final_folder_path)
        log_message(f"Moved processed folder to: {final_folder_path}")

        log_message(f"Files uploaded successfully to folder {final_folder_path}")
        return JSONResponse(content={"message": f"Files uploaded successfully to folder {final_folder_path}"}, status_code=200)

    except Exception as e:
        log_message(f"Error processing request: {str(e)}", level="ERROR")
        
        log_message(f"Cleaned up temporary folder: {temp_folder_path}")
        shutil.rmtree(temp_folder_path, ignore_errors=True)
        raise HTTPException(status_code=400, detail=str(e))





# just for test
@app.post("/api/Projects/CreateProjectFromBazisService")
async def create_project_from_bazis_service(
    IdCompany: int = Form(...),
    IdUser: str = Form(...),
    ModelName: str = Form(...),
    Files: List[UploadFile] = File(...)
):
    try:
        # Создаем уникальную папку для проекта
        project_id = str(uuid.uuid4())
        project_folder = os.path.join("projects123123123123123123", project_id)
        os.makedirs(project_folder, exist_ok=True)

        # Сохраняем данные проекта
        project_data = {
            "IdCompany": IdCompany,
            "IdUser": IdUser,
            "ModelName": ModelName
        }

        print(project_data)
        

        # Сохраняем файлы
        for file in Files:
            file_location = os.path.join(project_folder, file.filename)
            with open(file_location, "wb+") as file_object:
                file_object.write(await file.read())

        return JSONResponse(content={
            "message": "Project created successfully",
            "project_id": project_id
        }, status_code=200)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




if __name__ == "__main__":
    log_message("Starting FastAPI server")
    uvicorn.run(app, host="0.0.0.0", port=8123)