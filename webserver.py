import uvicorn
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
from typing import List
import os
import uuid
import json
import shutil

app = FastAPI()

INPUT_DIR = "inputs"
TEMP_DIR = "temp"

@app.post("/upload_bazis_project/")
async def create_upload_files(files: List[UploadFile] = File(...), user_data: str = Form(...)):
    folder_id = str(uuid.uuid4())
    temp_folder_path = os.path.join(TEMP_DIR, folder_id)
    os.makedirs(temp_folder_path, exist_ok=True)

    try:
        # Parse user_data
        user_data_dict = json.loads(user_data)
        model_name = user_data_dict.get('model_name')
        if not model_name:
            raise ValueError("model_name is required in user_data")

        # Save files
        for file in files:
            file_location = os.path.join(temp_folder_path, file.filename)
            with open(file_location, "wb+") as file_object:
                file_object.write(await file.read())
            
            # Rename the model file
            if file.filename == model_name:
                os.rename(file_location, os.path.join(temp_folder_path, "model.b3d"))

        # Save user_data.json
        user_data_path = os.path.join(temp_folder_path, "user_data.json")
        with open(user_data_path, "w") as user_data_file:
            json.dump(user_data_dict, user_data_file)

        # Move the completed folder to INPUT_DIR
        final_folder_path = os.path.join(INPUT_DIR, folder_id)
        shutil.move(temp_folder_path, final_folder_path)

        return JSONResponse(content={"message": f"Files uploaded successfully to folder {folder_id}"}, status_code=200)

    except Exception as e:
        # Clean up temp folder in case of error
        shutil.rmtree(temp_folder_path, ignore_errors=True)
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8123)