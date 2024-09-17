import os
from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from core.security import get_current_user
from file_storage import DigitalOceanSpacesManager

router = APIRouter()

# Instantiate DigitalOceanSpacesManager
spaces_manager = DigitalOceanSpacesManager(
    key='DO004X6LKK4NR9K4WQHP',
    secret='b2h7TrCXohEsfPm0ejmpapqRFIUKtKCPrPLpalOHK4I',
    region='nyc3',
    bucket_name='spaces-bucket-ai-email'
)

# List emails for a specific company in DigitalOcean Spaces
@router.get('/emails/company/{company_name}')
def get_emails(company_name: str, current_user: dict = Depends(get_current_user)) -> dict:
    try:
        username = current_user['username']
        sample_emails = spaces_manager.list_emails(username, company_name)
        return JSONResponse(content={'sample_emails': sample_emails}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Could not retrieve sample emails: {str(e)}')

# Get a specific document (email) from DigitalOcean Spaces using a pre-signed URL
@router.get('/emails/{company_name}/{email_name}')
def get_document(company_name: str, email_name: str, current_user: dict = Depends(get_current_user)):
    username = current_user['username']
    file_key = f'file-storage/{username}/{company_name}/sample_emails/{email_name}'
    
    try:
        # Log the key to debug if the file path is correct
        print(f"File Key: {file_key}")
        
        # Generate a pre-signed URL for the file
        presigned_url = spaces_manager.client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': spaces_manager.bucket_name,
                'Key': file_key
            },
            ExpiresIn=3600  # URL valid for 1 hour
        )
        return JSONResponse(content={'url': presigned_url}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error accessing the file: {str(e)}")

# Upload documents (emails) to DigitalOcean Spaces
@router.post("/emails/upload/{company_name}")
async def upload_documents(company_name: str, files: List[UploadFile] = File(...), current_user: dict = Depends(get_current_user)) -> JSONResponse:
    username = current_user['username']
    folder_path = f'file-storage/{username}/{company_name}/sample_emails/'
    
    # List existing files in DigitalOcean Spaces
    existing_files = spaces_manager.list_emails(username, company_name)

    files_that_already_exist = []
    successful_file_uploads = []
    unsuccessful_file_uploads = []
    
    for file in files:
        if file.filename in existing_files:
            files_that_already_exist.append(file.filename)
            continue
            
        file_location = folder_path + file.filename
        
        try:
            # Upload the file to DigitalOcean Spaces
            spaces_manager.client.put_object(
                Bucket=spaces_manager.bucket_name,
                Key=file_location,
                Body=file.file.read()
            )
            successful_file_uploads.append(file.filename)
        except Exception as e:
            unsuccessful_file_uploads.append(file.filename)
            print(f"Error uploading {file.filename}: {e}")

    data = {
        'files_that_already_exist': files_that_already_exist,
        'successful_file_uploads': successful_file_uploads,
        'unsuccessful_file_uploads': unsuccessful_file_uploads
    }
    
    if successful_file_uploads and not unsuccessful_file_uploads and not files_that_already_exist:
        message = "Files uploaded successfully."
        status_code = 201
    elif successful_file_uploads and (unsuccessful_file_uploads or files_that_already_exist):
        message = "Some files were uploaded successfully, but others were not (either they already existed or failed to upload)."
        status_code = 207  
    elif not successful_file_uploads and files_that_already_exist:
        message = "No new files uploaded; all files already exist."
        status_code = 409  
    else:
        message = "All uploads failed due to errors."
        status_code = 500  

    response = {
        'message': message,
        'details': data
    }

    return JSONResponse(content=response, status_code=status_code)

# Delete specific emails from DigitalOcean Spaces
@router.delete("/emails/delete/{company_name}")
async def delete_email(company_name: str, data: dict, current_user: dict = Depends(get_current_user)) -> JSONResponse:
    files = data['files']
    username = current_user['username']
    
    for file in files:
        file_key = f'file-storage/{username}/{company_name}/sample_emails/{file}'
        
        try:
            # Delete the file from DigitalOcean Spaces
            spaces_manager.client.delete_object(
                Bucket=spaces_manager.bucket_name,
                Key=file_key
            )
            print(f"File '{file_key}' has been deleted successfully.")
        except Exception as e:
            print(f"Error occurred while deleting the file: {e}")
            raise HTTPException(status_code=500, detail=f"Internal Server Error while deleting {file}")
            
    return JSONResponse(status_code=200, content={'message': 'Deleted all files successfully!'})
