from pydantic import BaseModel


class FindEmailRequest(BaseModel):
    linkedinurl: str