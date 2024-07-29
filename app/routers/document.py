import os
from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from pathlib import Path
from core.security import get_current_user  # Assuming this function is defined for JWT validation

router = APIRouter()

@router.get('/documents')
def get_documents(current_user: dict = Depends(get_current_user)) -> dict:
    try:
        username = current_user['username']
        document_names = os.listdir(f'file_storage/{username}/company_documents')
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail='Could not find the documents.')

    return JSONResponse(content={'document_names': document_names}, status_code=200)

@router.post("/documents/upload")
async def upload_documents(files: List[UploadFile] = File(...), current_user: dict = Depends(get_current_user)) -> JSONResponse:
    username = current_user['username']
    upload_dir = Path(f"file_storage/{username}/company_documents")
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    file_names = os.listdir(upload_dir)
    
    # keep track of all the files with the same name that already exist
    files_that_already_exist = []
    # keep track of all the files that were uploaded successfully
    successful_file_uploads = []
    # keep track of all the files that were not uploaded successfully
    unsuccessful_file_uploads = []
    
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
            unsuccessful_file_uploads.append(file.filename)

    data = {
        'files_that_already_exist': files_that_already_exist,
        'successful_file_uploads': successful_file_uploads,
        'unsucessful_file_uploads': unsuccessful_file_uploads
    }
    
    if successful_file_uploads and not unsuccessful_file_uploads and not files_that_already_exist:
        message = "Files uploaded successfully."
        status_code = 201
    elif successful_file_uploads and (unsuccessful_file_uploads or files_that_already_exist):
        message = "Some files were uploaded successfully, but others were not (either they already existed or failed to upload)."
        status_code = 207  # Multi-Status for mixed results
    elif not successful_file_uploads and files_that_already_exist:
        message = "No new files uploaded; all files already exist."
        status_code = 409  # Conflict, no new files uploaded
    else:
        message = "All uploads failed due to errors."
        status_code = 500  # Internal Server Error, all uploads failed

    response = {
        'message': message,
        'details': data
    }

    return JSONResponse(content=response, status_code=status_code)

@router.delete("/documents/delete")
async def delete_document(data: dict, current_user: dict = Depends(get_current_user)) -> JSONResponse:
    files = data['files']
    username = current_user['username']
    for file in files:
        file_path: str = f'file_storage/{username}/company_documents/{file}'
        
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
        
    return JSONResponse(status_code=200, content={'message': f'Deleted files successfully!'})
