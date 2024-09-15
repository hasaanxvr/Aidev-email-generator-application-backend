import os
from typing import List
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from core.security import get_current_user  # Assuming this function is defined for JWT validation
from file_storage import DigitalOceanSpacesManager

router = APIRouter()

# Instantiate the DigitalOceanSpacesManager
spaces_manager = DigitalOceanSpacesManager(
    key='DO004X6LKK4NR9K4WQHP',
    secret='b2h7TrCXohEsfPm0ejmpapqRFIUKtKCPrPLpalOHK4I',
    region='nyc3',
    bucket_name='spaces-bucket-ai-email'
)

# This returns the name of the documents from DigitalOcean Spaces
@router.get('/documents/company/{company_name}')
def get_documents(company_name: str, current_user: dict = Depends(get_current_user)) -> JSONResponse:
    try:
        username = current_user['username']
        document_names = spaces_manager.list_sample_documents(username, company_name)
        return JSONResponse(content={'document_names': document_names}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not retrieve document names: {str(e)}")

# Download a specific document from DigitalOcean Spaces using a pre-signed URL
@router.get('/documents/{company_name}/{document_name}')
def get_document(company_name: str, document_name: str, current_user: dict = Depends(get_current_user)):
    username = current_user['username']
    file_key = f'file-storage/{username}/{company_name}/company_documents/{document_name}'
    
    try:
        # Generate a pre-signed URL for the document
        presigned_url = spaces_manager.client.generate_presigned_url(
            'get_object',
            Params={'Bucket': spaces_manager.bucket_name, 'Key': file_key},
            ExpiresIn=3600  # URL expires in 1 hour
        )
        return JSONResponse(content={'url': presigned_url}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error accessing the document: {str(e)}")

# Upload documents to DigitalOcean Spaces
@router.post("/documents/upload/{company_name}")
async def upload_documents(company_name: str, files: List[UploadFile] = File(...), current_user: dict = Depends(get_current_user)) -> JSONResponse:
    username = current_user['username']
    folder_path = f'file-storage/{username}/{company_name}/company_documents/'
    
    # List existing files in DigitalOcean Spaces
    existing_files = spaces_manager.list_folders_in_folder(f'{username}/{company_name}/company_documents')

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

# Delete specific documents from DigitalOcean Spaces
@router.delete("/documents/delete/{company_name}")
async def delete_document(company_name: str, data: dict, current_user: dict = Depends(get_current_user)) -> JSONResponse:
    files = data['files']
    username = current_user['username']
    
    for file in files:
        file_key = f'file-storage/{username}/{company_name}/company_documents/{file}'
        
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
        
    return JSONResponse(status_code=200, content={'message': 'Deleted files successfully!'})
