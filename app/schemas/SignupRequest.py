from pydantic import BaseModel


class SignupRequest(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    
