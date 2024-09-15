import boto3
from botocore.client import Config

class DigitalOceanSpacesManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DigitalOceanSpacesManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, key: str, secret: str, region: str, bucket_name: str):
        # Prevent reinitializing the instance if it already exists
        if not hasattr(self, "initialized"):
            self.DO_SPACES_KEY = key
            self.DO_SPACES_SECRET = secret
            self.DO_SPACES_REGION = region
            self.DO_SPACES_ENDPOINT = f'https://{region}.digitaloceanspaces.com'
            self.bucket_name = bucket_name
            
            # Initialize the S3 session
            self.session = boto3.session.Session()
            self.client = self.session.client(
                's3',
                region_name=self.DO_SPACES_REGION,
                endpoint_url=self.DO_SPACES_ENDPOINT,
                aws_access_key_id=self.DO_SPACES_KEY,
                aws_secret_access_key=self.DO_SPACES_SECRET,
                config=Config(signature_version='s3v4')
            )

            # Mark the instance as initialized to prevent reinitialization
            self.initialized = True

    def create_folder(self, folder_name: str):
        folder_path = f'file-storage/{folder_name}/'
        self.client.put_object(Bucket=self.bucket_name, Key=folder_path)
        print(f"Folder '{folder_path}' created successfully in the Space '{self.bucket_name}'")

    def create_emails_and_documents_folder(self, company_name: str, username: str):
        folder_path = f'file-storage/{username}/{company_name}/'
        self.client.put_object(Bucket=self.bucket_name, Key=folder_path)
        self.client.put_object(Bucket=self.bucket_name, Key=folder_path + 'company_documents/')
        self.client.put_object(Bucket=self.bucket_name, Key=folder_path + 'sample_emails/')
        print(f"Folders for company '{company_name}' and user '{username}' created successfully")
        
    def delete_folder(self, folder_path: str):
        if not folder_path.endswith('/'):
            folder_path += '/'
        continuation_token = None
        while True:
            if continuation_token:
                response = self.client.list_objects_v2(
                    Bucket=self.bucket_name,
                    Prefix=folder_path,
                    ContinuationToken=continuation_token
                )
            else:
                response = self.client.list_objects_v2(Bucket=self.bucket_name, Prefix=folder_path)
            if 'Contents' not in response:
                print(f"No objects found in folder '{folder_path}'.")
                break
            keys = [{'Key': obj['Key']} for obj in response['Contents']]
            delete_response = self.client.delete_objects(Bucket=self.bucket_name, Delete={'Objects': keys})
            print(f"Deleted objects: {delete_response}")
            if response.get('IsTruncated'):
                continuation_token = response.get('NextContinuationToken')
            else:
                break
        print(f"Folder '{folder_path}' and all its contents deleted successfully in the Space '{self.bucket_name}'")

    def list_folders_in_folder(self, parent_folder: str) -> list:
        folder_path = f'file-storage/{parent_folder}/'
        response = self.client.list_objects_v2(Bucket=self.bucket_name, Prefix=folder_path, Delimiter='/')
        folders = []
        if 'CommonPrefixes' in response:
            folders = [prefix['Prefix'] for prefix in response['CommonPrefixes']]
        folder_names = [folder.replace(folder_path, '').strip('/') for folder in folders]
        return folder_names

    def list_emails(self, username: str, company: str) -> list:
        folder_path = f'file-storage/{username}/{company}/sample_emails/'
        response = self.client.list_objects_v2(Bucket=self.bucket_name, Prefix=folder_path)
        email_files = []
        if 'Contents' in response:
            for obj in response['Contents']:
                file_name = obj['Key'].replace(folder_path, '')
                if file_name != '':
                    email_files.append(file_name)
        return email_files
    
    
    
    def list_sample_documents(self, username: str, company: str) -> list:
        folder_path = f'file-storage/{username}/{company}/company_documents/'
        response = self.client.list_objects_v2(Bucket=self.bucket_name, Prefix=folder_path)
        email_files = []
        if 'Contents' in response:
            for obj in response['Contents']:
                file_name = obj['Key'].replace(folder_path, '')
                if file_name != '':
                    email_files.append(file_name)
        return email_files
