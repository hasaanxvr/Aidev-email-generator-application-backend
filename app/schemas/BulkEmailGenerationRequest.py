from pydantic import BaseModel

class BulkEmailGenerationRequest(BaseModel):
    linkedin_url_list: list
    user_prompt: str
    selected_documents: list
    selected_emails: list