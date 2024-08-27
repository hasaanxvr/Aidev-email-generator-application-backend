from pydantic import BaseModel

class BulkEmailGenerationRequest(BaseModel):
    linkedin_url_dict: dict
    user_prompt: str
    selected_documents: list
    selected_emails: list
    company_name: str