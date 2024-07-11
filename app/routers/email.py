import os
from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pathlib import Path


router = APIRouter()





@router.get('/emails')
def get_documents() -> dict:  
    try:    
        sample_emails = os.listdir('db/sample_emails')
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail='Could not find the sample emails.')

    return JSONResponse(content={'sample_emails': sample_emails}, status_code=200)


@router.post("/emails/upload")
async def upload_documents(files: List[UploadFile] = File(...)) -> JSONResponse:
    upload_dir = Path("db/sample_emails")
    upload_dir.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists
    
    file_names = os.listdir(upload_dir)
    
     # keep track of all the files with the same name that already exist
    files_that_already_exist = []
    # keep track of all the files that were uploaded successfully
    successful_file_uploads = []
    # keep track of all the files that were not uploaded successfully
    unsucessful_file_uploads = []
    
    for file in files:
        
        if file.filename in file_names:
            files_that_already_exist.append(file.filename)
            continue
            
        file_location = upload_dir / file.filename
        
        try:
            with file_location.open("wb") as f:
                f.write(file.file.read())
            successful_file_uploads.append(file.filename)
        except:
            unsucessful_file_uploads.append(file.filename)

    data = {
        'files_that_already_exist': files_that_already_exist,
        'successful_file_uploads': successful_file_uploads,
        'unsucessful_file_uploads': unsucessful_file_uploads
    }
    
    return JSONResponse(content=data, status_code=201)
    
    return JSONResponse(content=data, status_code=201)


@router.delete("/email/delete")
async def delete_email(data: dict) -> JSONResponse:
    file_name = data['file_name']
    file_path: str = f'db/sample_emails/{file_name}'
    
    try:
        os.remove(file_path)
        print(f"File '{file_path}' has been deleted successfully.")
    except FileNotFoundError:
        print(f"File '{file_path}' does not exist.")
        raise HTTPException(status_code=404, detail='File not found')
    except PermissionError:
        print(f"Permission denied: Unable to delete '{file_path}'.")
        raise HTTPException(status_code=500, detail='The server does not have permission to delete the file')
    except Exception as e:
        print(f"An error occurred while deleting the file: {e}")
        raise HTTPException(status_code=500, detail='Internal Server Error')
        
    return JSONResponse(status_code=200, content={'message': f'Deleted {file_name} successfully!'})