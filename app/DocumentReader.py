import os
import logging

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import Docx2txtLoader


class DocumentReader:
    def __init__(self, documents_folder_path = 'documents'):
        
        self.documents_folder_path = documents_folder_path
        
    def _read_pdf(self, file_path: str) -> str:
        """ Reads a pdf file and returns the text as a string

        Args:
            file_path (str): path to the pdf file

        Returns:
            str: _description_
        """
        loader = PyPDFLoader(file_path)
        pages = loader.load_and_split()
        
        data = ''
        for page in pages:
            data += ' ' + page.page_content
            
        return data
    
    def _read_word(self, file_path: str) -> str:
        """Reads a word file and returns data in form of a string

        Args:
            file_path (str): Path to the word (.docx) file

        Returns:
            str: Complete content of the file
        """
        loader = Docx2txtLoader(file_path)
        data_raw = loader.load()
        data = data_raw[0].page_content
        
        return data
    
    
    def fetch_data_from_selective_documents(self, selected_documents) -> list[str]:
        document_names = os.listdir(self.documents_folder_path)
        document_content = []
        
        for document_name in document_names:
            if document_name in selected_documents:
            
                file_type = document_name.split('.')[-1]
                document_path = self.documents_folder_path + '/' + document_name
                
                if file_type == 'pdf':
                    data = self._read_pdf(document_path)
                    document_content.append(data)
                
                elif file_type == 'docx':
                    data = self._read_word(document_path) 
                    document_content.append(data)           
                
                else:
                    logging.exception('Document Type not Supported. Use Word or PDF')

                
        return document_content
    
    
    
    def fetch_data_from_documents(self) -> list[str]:
        
        """Reads all the documents from a specific folder and returns them in the form of a list

        Returns:
            list[str]: [data_from_doc1, data_from_doc2....] 
        """
        
        document_names = os.listdir(self.documents_folder_path)
        document_content = []
        
        for document_name in document_names:
            
            file_type = document_name.split('.')[-1]
            document_path = self.documents_folder_path + '/' + document_name
            
            if file_type == 'pdf':
                data = self._read_pdf(document_path)
                document_content.append(data)
            
            elif file_type == 'docx':
                data = self._read_word(document_path) 
                document_content.append(data)           
            
            else:
                logging.exception('Document Type not Supported. Use Word or PDF')
    
            

        return document_content
    
    
    def fetch_data_from_documents_dict(self, key) -> list[dict]:
        document_names = os.listdir(self.documents_folder_path)
        document_content = []
        
        for document_name in document_names:
            
            file_type = document_name.split('.')[-1]
            document_path = self.documents_folder_path + '/' + document_name
            
            if file_type == 'pdf':
                data = self._read_pdf(document_path)
                data_dict = {}
                data_dict[key] = data
                document_content.append(data_dict)
            
            elif file_type == 'docx':
                data = self._read_word(document_path) 
                data_dict = {}
                data_dict[key] = data
                document_content.append(data_dict)           
            
            else:
                logging.exception('Document Type not Supported. Use Word or PDF')
    
            

        return document_content