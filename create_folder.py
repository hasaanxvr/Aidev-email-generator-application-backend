import boto3
from botocore.client import Config

# Your DigitalOcean Spaces credentials
DO_SPACES_KEY = 'DO004X6LKK4NR9K4WQHP'
DO_SPACES_SECRET = 'b2h7TrCXohEsfPm0ejmpapqRFIUKtKCPrPLpalOHK4I'
DO_SPACES_REGION = 'nyc3'  # Change to your region if needed
DO_SPACES_ENDPOINT = f'https://{DO_SPACES_REGION}.digitaloceanspaces.com'

# Name of your Space and the folder you want to create
bucket_name = 'spaces-bucket-ai-email'
folder_name = 'file-storage/'

# Create an S3 session using DigitalOcean Spaces credentials
session = boto3.session.Session()
client = session.client(
    's3',
    region_name=DO_SPACES_REGION,
    endpoint_url=DO_SPACES_ENDPOINT,
    aws_access_key_id=DO_SPACES_KEY,
    aws_secret_access_key=DO_SPACES_SECRET,
    config=Config(signature_version='s3v4')
)

# Create the folder by uploading an empty object with the folder's name (ending with a '/')
client.put_object(Bucket=bucket_name, Key=folder_name)

print(f"Folder '{folder_name}' created successfully in the Space '{bucket_name}'")
