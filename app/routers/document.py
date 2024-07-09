import os
from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get('/documents')
def get_documents() -> dict:  
    try:    
        document_names = os.listdir('db/company_documents')
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail='Could not find the documents.')

    return JSONResponse(content={'document_names': document_names}, status_code=200)


@router.post('/documents/upload/')
async def upload_documents(files: List[UploadFile] = File(...)) -> JSONResponse:
    for file in files:
        file_location = os.path.join('db/documents', file.filename)
        with open(file_location, "wb") as f:
            f.write(file.file.read())
    return JSONResponse(content={"info": "Files uploaded successfully"}, status_code=201)