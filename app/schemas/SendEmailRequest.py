from pydantic import BaseModel


class SendEmailRequest(BaseModel):
    sender_email: str
    sender_password: str
    receiver_email: str
    email: str
    subject: str
    