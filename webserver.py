import uvicorn
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from typing import List
import os
import uuid
import json
import shutil

from logger import log_message

app = FastAPI()

INPUTS_TO_BAZIS = "inputs_to_bazis"
INPUTS_FROM_BAZIS = "inputs_from_bazis"

TEMP_DIR = "temp"
ERROR_DIR = "errors"
LOG_DIR = "logs"
SUPERUSERS_FILE = "superusers.txt"

app.mount("/logs", StaticFiles(directory=LOG_DIR), name="logs")

@app.get("/view_logs")
async def view_logs():
    log_files = os.listdir(LOG_DIR)
    log_links = [f'<a href="/logs/{file}">{file}</a>' for file in log_files]
    content = "<br>".join(log_links)
    html_content = f"""
    <html>
        <head>
            <title>Log Files</title>
        </head>
        <body>
            <h1>Available Log Files:</h1>
            {content}
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/retry/{id_project}")
async def retry(id_project: str):
    log_message(f"Got request to retry converting project: {id_project}", IdProject=id_project, tg=True)
    error_folder = os.path.join(ERROR_DIR, id_project)
    input_folder = os.path.join(INPUTS_FROM_BAZIS, id_project)
    
    if not os.path.exists(error_folder):
        log_message(f"Project {id_project} not found in ERRORS folder", IdProject=id_project, tg=True)
    
    try:
        shutil.move(error_folder, input_folder)
        log_message(f"Moved project {id_project} from ERRORS to INPUTS for retry")

    except Exception as e:
        log_message(f"Error moving project {id_project}: {str(e)}", level="ERROR")
        return JSONResponse(content={}, status_code=200)

@app.post("/upload_bazis_project/")
async def create_upload_files(files: List[UploadFile] = File(...), user_data: str = Form(...)):
    try:
        log_message("\n\n(from bazis) New request received")

        # Parse user_data
        user_data_dict = json.loads(user_data)
        log_message(f"Received user data: {user_data_dict}")
        
        # Use IdProject from user_data if it exists, otherwise generate a new UUID
        folder_id = user_data_dict.get('IdProject', str(uuid.uuid4()))

        # Ensure IdProject is in user_data_dict
        user_data_dict['IdProject'] = folder_id
        
        temp_folder_path = os.path.join(TEMP_DIR, folder_id)
        os.makedirs(temp_folder_path, exist_ok=True)
        log_message(f"Created folder: {temp_folder_path}")

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

        # Move the completed folder to INPUTS_FROM_BAZIS
        final_folder_path = os.path.join(INPUTS_FROM_BAZIS, folder_id)
        if os.path.exists(final_folder_path):
            shutil.rmtree(final_folder_path)
        shutil.move(temp_folder_path, final_folder_path)
        log_message(f"Moved processed folder to: {final_folder_path}")

        log_message(f"Files uploaded successfully to folder {final_folder_path}")
        return JSONResponse(content={"message": f"Files uploaded successfully to folder {final_folder_path}"}, status_code=200)

    except Exception as e:
        log_message(f"Error processing request: {str(e)}", level="ERROR")
        
        log_message(f"Cleaned up temporary folder: {temp_folder_path}")
        shutil.rmtree(temp_folder_path, ignore_errors=True)
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/convert_to_bazis/")
async def create_upload_files(files: List[UploadFile] = File(...), user_data: str = Form(...)):
    try:
        log_message("\n\n(to bazis) New request received")

        # Parse user_data
        user_data_dict = json.loads(user_data)
        log_message(f"(to bazis) Received user data: {user_data_dict}")
        
        # Get data
        project_filename = user_data_dict.get('ProjectFile')
        if not project_filename:
            raise ValueError("ProjectFile not specified in user_data")
        
        project_id = user_data_dict.get('IdProject')
        if not project_filename:
            raise ValueError("IdProject not specified in user_data")
        
        calculation_id = user_data_dict.get('IdCalculation')
        if not project_filename:
            raise ValueError("IdCalculation not specified in user_data")
        
        # Set folder name
        folder_name = f"{project_id}_{calculation_id}"
        temp_folder_path = os.path.join(TEMP_DIR, folder_name)
        os.makedirs(temp_folder_path, exist_ok=True)
        log_message(f"(to bazis) Created folder: {temp_folder_path}")

        # Flag
        project_file_found = False

        # Save files
        for file in files:
            file_location = os.path.join(temp_folder_path, file.filename)
            with open(file_location, "wb+") as file_object:
                file_object.write(await file.read())
            log_message(f"(to bazis) Saved file: {file.filename}")

            # Rename projectFile to "project.s123proj"
            if file.filename == project_filename:
                new_file_location = os.path.join(temp_folder_path, "project.s123proj")
                log_message(f"(to bazis) Renamed {file.filename} to project.s123proj")
                user_data_dict['ProjectFile'] = "project.s123proj"
                os.rename(file_location, new_file_location)
                project_file_found = True

        if not project_file_found:
            raise Exception('No project file found')

        # Save user_data.json
        user_data_path = os.path.join(temp_folder_path, "user_data.json")
        with open(user_data_path, "w") as user_data_file:
            json.dump(user_data_dict, user_data_file)
        log_message("(to bazis) Saved user_data.json")

        # Move the completed folder to INPUTS_TO_BAZIS
        final_folder_path = os.path.join(INPUTS_TO_BAZIS, folder_name)
        if os.path.exists(final_folder_path):
            shutil.rmtree(final_folder_path)
        shutil.move(temp_folder_path, final_folder_path)
        log_message(f"(to bazis) Moved processed folder to: {final_folder_path}")

        log_message(f"(to bazis) Files uploaded successfully to folder {final_folder_path}")
        return JSONResponse(content={"message": f"(to bazis) Files uploaded successfully to folder {final_folder_path}"}, status_code=200)

    except Exception as e:
        log_message(f"(to bazis) Error processing request: {str(e)}", level="ERROR")
        
        log_message(f"(to bazis) Cleaned up temporary folder: {temp_folder_path}")
        shutil.rmtree(temp_folder_path, ignore_errors=True)
        raise HTTPException(status_code=400, detail=str(e))


# Manage superusers
@app.post("/manage_superusers/")
async def manage_superusers(
    IdUser: str = Form(...),
    Method: str = Form(...)
):
    id_user = IdUser.strip().strip('"\'')
    method = Method.strip().strip('"\'').lower()

    if not os.path.exists(SUPERUSERS_FILE):
        open(SUPERUSERS_FILE, 'w').close()  # Create the file if it doesn't exist

    with open(SUPERUSERS_FILE, "r", encoding='utf-8') as file:
        superusers = file.read().splitlines()

    if method == 'add':
        if id_user.lower() not in (su.lower() for su in superusers):
            superusers.append(id_user)
            with open(SUPERUSERS_FILE, "w", encoding='utf-8') as file:
                file.write("\n".join(superusers) + "\n")

            return JSONResponse(content={"message": f"User {id_user} added to superusers."}, status_code=200)
        
        else:
            return JSONResponse(content={"message": f"User {id_user} is already a superuser."}, status_code=200)

    elif method == 'delete':
        initial_count = len(superusers)
        superusers = [su for su in superusers if su.lower() != id_user.lower()]
        if len(superusers) < initial_count:
            with open(SUPERUSERS_FILE, "w", encoding='utf-8') as file:
                file.write("\n".join(superusers) + "\n")

            return JSONResponse(content={"message": f"User {id_user} removed from superusers."}, status_code=200)
        
        else:
            return JSONResponse(content={"message": f"User {id_user} was not found in superusers."}, status_code=404)

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid method: {method}. Use 'add' or 'delete'."
        )



# ONLY FOR DEBUG #
@app.post("/api/Projects/CreateProjectFromBazisService")
async def create_project_from_bazis_service(
    IdCompany: int = Form(...),
    IdUser: str = Form(...),
    IdProject: str = Form(...),
    ModelName: str = Form(...),
    Files: List[UploadFile] = File(...)
):
    try:
        project_id = str(uuid.uuid4())
        project_folder = os.path.join("FAKEPROJECTTEST", project_id)
        os.makedirs(project_folder, exist_ok=True)

        project_data = {
            "IdCompany": IdCompany,
            "IdUser": IdUser,
            "IdProject": IdProject,
            "ModelName": ModelName
        }

        print(project_data)
        
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