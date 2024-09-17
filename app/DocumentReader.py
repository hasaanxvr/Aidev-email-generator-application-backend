import boto3
import tempfile
import logging
from io import BytesIO
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import Docx2txtLoader


class DocumentReader:
    def __init__(self, documents_folder_path):
        """Initializes the DocumentReader with the folder path as in DigitalOcean Spaces.

        Args:
            documents_folder_path (str): The prefix/path in the DigitalOcean space (e.g., 'file-storage/username/company_name/company_documents')
        """
        # Hardcoded DigitalOcean Spaces credentials and configuration
        self.access_key = 'DO004X6LKK4NR9K4WQHP'
        self.secret_key = 'b2h7TrCXohEsfPm0ejmpapqRFIUKtKCPrPLpalOHK4I'
        self.region = 'nyc3'
        self.space_name = 'spaces-bucket-ai-email'

        # Initialize DigitalOcean Spaces client with hardcoded credentials
        self.s3_client = boto3.client(
            's3',
            region_name=self.region,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            endpoint_url=f'https://{self.region}.digitaloceanspaces.com'
        )
        self.path_prefix = documents_folder_path  # This is the path to the folder in Spaces

    def _read_pdf(self, file_content: bytes) -> str:
        """Reads a PDF file from bytes content by writing to a temporary file."""
        # Create a temporary file to save the PDF content
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(file_content)
            temp_pdf_path = temp_pdf.name  # Save the path of the temporary file

        # Now initialize PyPDFLoader with the temporary file path
        pdf_loader = PyPDFLoader(temp_pdf_path)
        pages = pdf_loader.load_and_split()

        # Extract the text from the PDF
        data = ''
        for page in pages:
            data += ' ' + page.page_content

        return data

    def _read_word(self, file_content: bytes) -> str:
        """Reads a Word file from bytes content and returns data as a string."""
        word_loader = Docx2txtLoader(BytesIO(file_content))
        data_raw = word_loader.load()
        data = data_raw[0].page_content

        return data

    def _get_file_from_spaces(self, file_key: str) -> bytes:
        """Fetches a file from DigitalOcean Spaces."""
        try:
            response = self.s3_client.get_object(Bucket=self.space_name, Key=file_key)
            file_content = response['Body'].read()
            return file_content
        except self.s3_client.exceptions.NoSuchKey:
            logging.error(f"Error: The file {file_key} does not exist in the bucket.")
            return None
        except Exception as e:
            logging.error(f"Error fetching the file {file_key}: {str(e)}")
            return None

    def fetch_data_from_selective_documents(self, selected_documents: list[str], username: str) -> list[str]:
        """Fetches data from the documents passed in the argument from DigitalOcean Spaces.

        Args:
            selected_documents (list[str]): List of document names to fetch.
            username (str): The username to construct the file path in the space.

        Returns:
            list[str]: List of document contents as strings.
        """
        document_content = []

        for document_name in selected_documents:
            file_type = document_name.split('.')[-1]
            file_key = f'{self.path_prefix}/{document_name}'
            file_content = self._get_file_from_spaces(file_key)

            if file_content is None:
                logging.error(f"Failed to retrieve document {document_name}")
                continue

            if file_type == 'pdf':
                data = self._read_pdf(file_content)
                document_content.append(data)

            elif file_type == 'docx':
                data = self._read_word(file_content)
                document_content.append(data)

            else:
                logging.error(f'Unsupported file type: {document_name}. Only PDF and DOCX are supported.')

        return document_content

    def fetch_data_from_documents(self) -> list[str]:
        """Reads all documents from a specific folder in DigitalOcean Spaces and returns their content.

        Returns:
            list[str]: List of document contents as strings.
        """
        try:
            response = self.s3_client.list_objects_v2(Bucket=self.space_name, Prefix=self.path_prefix)
            document_names = [item['Key'].split('/')[-1] for item in response.get('Contents', [])]
        except Exception as e:
            logging.error(f"Failed to list documents for {self.path_prefix}: {str(e)}")
            return []

        document_content = []

        for document_name in document_names:
            file_type = document_name.split('.')[-1]
            file_key = f'{self.path_prefix}/{document_name}'
            file_content = self._get_file_from_spaces(file_key)

            if file_content is None:
                logging.error(f"Failed to retrieve document {document_name}")
                continue

            if file_type == 'pdf':
                data = self._read_pdf(file_content)
                document_content.append(data)

            elif file_type == 'docx':
                data = self._read_word(file_content)
                document_content.append(data)

            else:
                logging.error(f'Unsupported file type: {document_name}. Only PDF and DOCX are supported.')

        return document_content
