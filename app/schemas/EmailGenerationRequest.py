from pydantic import BaseModel


class LinkedinURLEmailGenerationRequest(BaseModel):
    linkedin_url: str
    user_prompt: str
    selected_emails:  list
    selected_documents:  list
    company_name: str
    
class NameEmailGenerationRequest(BaseModel):
    first_name: str
    company: str
    last_name: str
    location: str
    title: str
    user_prompt: str
    selected_emails: list
    selected_documents: list