import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter()





@router.get('/emails')
def get_documents() -> dict:  
    try:    
        sample_emails = os.listdir('db/sample_emails')
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail='Could not find the sample emails.')

    return JSONResponse(content={'sample_emails': sample_emails}, status_code=200)
