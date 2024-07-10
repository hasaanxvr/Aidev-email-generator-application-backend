import os
import logging
import requests
import json
from DocumentReader import DocumentReader
from langchain_openai import ChatOpenAI

class EmailGenerator:
    def __init__(self, linkedin_url: str, user_prompt: str, selected_documents: list[str], selected_emails: list[str], model: str ='gpt-4-turbo'):
        
        self.linkedin_url: str = linkedin_url
        self.user_prompt: str = user_prompt
        self.selected_documents: list[str] = selected_documents
        self.selected_emails: list[str] = selected_emails
        
        # Defining the document reader objects for fetching emails and documents
        self.email_reader = DocumentReader(documents_folder_path='db/sample_emails')
        self.document_reader = DocumentReader(documents_folder_path='db/company_documents')

        self.llm= ChatOpenAI(model=model)
        
        self.linkedin_api_key: str = os.environ.get('LINKEDIN_API_KEY') 
        self.open_ai_api_key: str = os.environ.get('OPENAI_API_KEY')
        
    
        
        
    def _get_user_data(self):
        
        headers = {'Authorization': 'Bearer ' + self.linkedin_api_key}
        api_endpoint = 'https://nubela.co/proxycurl/api/v2/linkedin'
        
        # Add more parameter options
        NotImplemented
        
        params = {

            'linkedin_profile_url': self.linkedin_url,
        }
        response = requests.get(api_endpoint,
                                params=params,
                                headers=headers)

        if response.status_code != 200:
            return None
        
        data = json.dumps(response.json(), indent=4)
        
        return data
    
    
    def generate_email(self) ->str:
        linkedin_user_data = self._get_user_data()
        if linkedin_user_data is not None:
            sample_emails: list[str] = self.email_reader.fetch_data_from_selective_documents(self.selected_emails)
            company_documents: list[str] = self.document_reader.fetch_data_from_selective_documents(self.selected_emails)
            
            
            # Addition of company information
            self.user_prompt += 'DOCUMENTS CONTAINING USEFUL COMPANY INFORMATION ARE GIVEN BELOW'
            for doc in company_documents:
                self.user_prompt += 'COMPANY DOCUMENT: /n'
                self.user_prompt += doc + '/n /n'
                
                
            # Addition of sample emails
            self.user_prompt += 'SAMPLE EMAILS ARE GIVEN BELOW: /n'
            for email in sample_emails:
                self.user_prompt += 'SAMPLE EMAIL: /n'
                self.user_prompt += email + '/n /n'


            # Addition of linkedin data
            self.user_prompt += 'THE DATA OF THE PERSON YOU ARE TARGETTING IN JSON FORMAT: /n'
            self.user_prompt += linkedin_user_data


            messages = [
            (
                "system",
                """You are a helpful assistant that writes client-capturing personalized emails.
                Write a sales email for the user based on the information they provide you.
                You make use of the additional information provided to you by analyzing it and making cohesive, compelling and attractive.
                Your emails are easy to read, with great hooks and best sales practices. 
                You use the information of the person provided to you and link it to the information from company docs to create a highly personalized email,
                that highlights how the person can use the services/products of the company.
                You make sure to link the product/services of the company to the data of the person.
                """,
            ),
            ("human", f"{self.user_prompt}"),
            ]
            
            try:
                response = self.llm.invoke(messages)
            
                return response.content
            except:
                logging.exception('The LLM from OPENAI was not invoked properly. Please check your internet connection.')
                return -1
        