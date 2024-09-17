import boto3
from io import BytesIO

# Hardcoded credentials and configuration for DigitalOcean Spaces
ACCESS_KEY = 'DO004X6LKK4NR9K4WQHP'
SECRET_KEY = 'b2h7TrCXohEsfPm0ejmpapqRFIUKtKCPrPLpalOHK4I'
REGION = 'nyc3'
BUCKET_NAME = 'spaces-bucket-ai-email'  # Replace with your actual bucket name

def fetch_file_from_spaces(file_key):
    """Fetches a file from DigitalOcean Spaces and returns its content.

    Args:
        file_key (str): The key (path) of the file in the space.

    Returns:
        bytes: The content of the file as bytes.
    """
    # Initialize the DigitalOcean Spaces client
    s3_client = boto3.client(
        's3',
        region_name=REGION,
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        endpoint_url=f'https://{REGION}.digitaloceanspaces.com'
    )

    try:
        # Fetch the object from the space
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=file_key)
        file_content = response['Body'].read()
        return file_content
    except s3_client.exceptions.NoSuchKey:
        print(f"Error: The file {file_key} does not exist in the bucket.")
        return None
    except Exception as e:
        print(f"Error fetching the file: {str(e)}")
        return None

if __name__ == "__main__":
    # Example usage:
    
    # Replace this with the correct path to your file in DigitalOcean Spaces
    file_key = 'file-storage/shenk/Company-A/sample_emails/Sample Email.pdf'  # Example path

    # Fetch the file from DigitalOcean Spaces
    file_content = fetch_file_from_spaces(file_key)

    if file_content:
        # File content is retrieved successfully
        print(f"File fetched successfully! Size: {len(file_content)} bytes")

        # Optional: If it's a PDF or DOCX, you can write it to a local file
        with open('downloaded_file.pdf', 'wb') as f:
            f.write(file_content)
        print("File has been written to 'downloaded_file.pdf'")
    else:
        print("Failed to fetch the file.")
