from pydantic import BaseModel

class FindPersonByNameAndOrg(BaseModel):
    first_name: str
    company: str
    last_name: str
    location: str
    title: str
    
    
class FindPersonByEmail(BaseModel):
    email: str