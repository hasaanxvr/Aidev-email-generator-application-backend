import logging
from app.file_storage import DigitalOceanSpacesManager

spaces_manager = DigitalOceanSpacesManager(
    key='DO004X6LKK4NR9K4WQHP',
    secret='b2h7TrCXohEsfPm0ejmpapqRFIUKtKCPrPLpalOHK4I',
    region='nyc3',
    bucket_name='spaces-bucket-ai-email'
)


try:
    # Correct the file key: remove leading space and trailing slash
    file_key = 'file-storage/shenk/Company-A/company_documents/Portfolio.pdf'
    
    # Generate a presigned URL with the correct key
    presigned_url = spaces_manager.client.generate_presigned_url(
        'get_object',
        Params={'Bucket': spaces_manager.bucket_name, 'Key': file_key},
        ExpiresIn=3600  # URL expires in 1 hour
    )
    
    logging.info(f"Generated presigned URL: {presigned_url}")
    print(presigned_url)

except Exception as e:
    logging.error(f"Error generating presigned URL: {e}")


