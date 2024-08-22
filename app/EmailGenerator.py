import os
import logging
import requests
import json
from DocumentReader import DocumentReader
from langchain_openai import ChatOpenAI
from RetirevalStrategy import LinkedInDataRetrievalStrategy, NameCompanyDataRetrievalStrategy, UserDataRetrievalStrategy



class EmailGenerator:
    def __init__(self,user_prompt: str, selected_documents: list[str], selected_emails: list[str], retrieval_strategy:UserDataRetrievalStrategy, model: str ='gpt-4-turbo', username = ''):
        
        self.user_prompt: str = user_prompt
        self.selected_documents: list[str] = selected_documents
        self.selected_emails: list[str] = selected_emails
        
        # Defining the document reader objects for fetching emails and documents
        self.email_reader = DocumentReader(documents_folder_path=f'file_storage/{username}/sample_emails')
        self.document_reader = DocumentReader(documents_folder_path=f'file_storage/{username}/company_documents')

        self.llm= ChatOpenAI(model=model)
        
        self.open_ai_api_key: str = os.environ.get('OPENAI_API_KEY')
        
        self.username : str = username
        self.data_retrieval_strategy = retrieval_strategy
        
        
    
        
    def generate_email(self) ->str:
        self.linkedin_user_data = self.data_retrieval_strategy.get_user_data()
        
        
        if self.linkedin_user_data is not None:
            sample_emails: list[str] = self.email_reader.fetch_data_from_selective_documents(self.selected_emails, self.username)
            company_documents: list[str] = self.document_reader.fetch_data_from_selective_documents(self.selected_documents, self.username)
            
            
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
            self.user_prompt += self.linkedin_user_data


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
                RETURN THE EMAIL as a JSON STRING having 2 parts. 1. Subject and 2. Body.
                STRICTLY RETURN A JSON STRING THAT CAN BE CONVERTED INTO DICTIONARY in both Python and JS:
                
                SAMPLE RESPONSE:
                {
                    "subject": "this is a sample email subject",
                    "body": "this is a sample body"
                }
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
            
