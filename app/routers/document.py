import os
from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pathlib import Path

router = APIRouter()

@router.get('/documents')
def get_documents() -> dict:  
    try:    
        document_names = os.listdir('db/company_documents')
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail='Could not find the documents.')

    return JSONResponse(content={'document_names': document_names}, status_code=200)


@router.post("/documents/upload")
async def upload_documents(files: List[UploadFile] = File(...)) -> JSONResponse:
    upload_dir = Path("db/company_documents")
    upload_dir.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists
    
    for file in files:
        file_location = upload_dir / file.filename
        with file_location.open("wb") as f:
            f.write(file.file.read())

    return JSONResponse(content={"info": "Files uploaded successfully"}, status_code=201)


@router.delete("/document/delete")
async def delete_document(data: dict) -> JSONResponse:
    file_name = data['file_name']
    file_path: str = f'db/company_documents/{file_name}'
    
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