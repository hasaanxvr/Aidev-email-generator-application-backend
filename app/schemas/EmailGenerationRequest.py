from pydantic import BaseModel


class EmailGenerationRequest(BaseModel):
    linkedin_url: str
    user_prompt: str
    selected_emails:  list
    selected_documents:  list
    