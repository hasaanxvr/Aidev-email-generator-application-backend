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
    
    for file in files:
        file_location = upload_dir / file.filename
        with file_location.open("wb") as f:
            f.write(file.file.read())

    return JSONResponse(content={"info": "Files uploaded successfully"}, status_code=201)


@router.delete("/email/delete")
async def delete_email(email_document_name: str) -> JSONResponse:
    file_path: str = f'db/sample_emails/{email_document_name}'
    
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
        
    return JSONResponse(status_code=200, content={'message': f'Deleted {email_document_name} successfully!'})