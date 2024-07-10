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