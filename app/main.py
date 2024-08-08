import os
import sqlite3
import requests
import json
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routers import document, email
from EmailGenerator import EmailGenerator
from schemas.EmailGenerationRequest import LinkedinURLEmailGenerationRequest, NameEmailGenerationRequest
from schemas.SignupRequest import SignupRequest
from schemas.LoginRequest import LoginRequest
from schemas.FindEmailRequest import FindEmailRequest
from schemas.SendEmailRequest import SendEmailRequest
from config import DATABASE_NAME, FILE_STORAGE_PATH
from db.Database import MongoDatabase
from core.security import create_jwt_token, get_current_user
from RetirevalStrategy import LinkedInDataRetrievalStrategy, NameCompanyDataRetrievalStrategy


db_handler = MongoDatabase()

app = FastAPI()

origins = [
    "http://localhost:3000",  # Your React app's URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(document.router, prefix='/api', tags=['documents'])
app.include_router(email.router, prefix='/api', tags=['emails'])

@app.get('/')
def welcome_message() -> JSONResponse:
    return JSONResponse(status_code=200, content={'message': 'Welcome to Personalized Email Generator!'})



@app.get('/email-history')
def get_email_history(current_user: dict = Depends(get_current_user)) -> JSONResponse:
    username = current_user['username']
    
    email_history = db_handler.fetch_emails(username)
    
    return JSONResponse(status_code=200, content=email_history)



@app.post('/generate-email/name')
def generate_email_name(email_generation_request: NameEmailGenerationRequest, current_user: dict = Depends(get_current_user)) -> JSONResponse:
    
    request_data: dict = email_generation_request.dict()
    username = current_user['username']
    
    retrieval_strategy = NameCompanyDataRetrievalStrategy(request_data['first_name'], request_data['company'], request_data['last_name'], request_data['location'], request_data['title'])
    email_generator = EmailGenerator(request_data['user_prompt'], request_data['selected_documents'], request_data['selected_emails'],retrieval_strategy, username=username)
    email = email_generator.generate_email()
    
    if email == -1:
        raise HTTPException(status_code=505, detail='Could not fetch data of the person from LinkedIn')
    
    
    person_data = email_generator.linkedin_user_data
    person_data = json.loads(person_data)
    
    url = person_data['url']
    person_data = person_data['profile']
    person_data['url'] = url
    
    
        
    data = {
        'linkedinurl': person_data['url'],
        'user_prompt': request_data['user_prompt'],
        'selected_emails': request_data['selected_emails'],
        'selected_documents': request_data['selected_documents'],
        'generated_email': email,
        'username': username,
        'time': datetime.now().isoformat()
    }
    
    
    db_handler.insert_email(data)
    db_handler.insert_person(person_data)
    
    response_data = {
        'message': 'Email Generated Successfully!',
        'generated_email': email,
        'linkedinurl': person_data['url']
    }
    
    
    print(response_data)
    return JSONResponse(status_code=200, content=response_data)
    
    

@app.post('/generate-email/linkedinurl')
def generate_email(email_generation_request: LinkedinURLEmailGenerationRequest, current_user: dict = Depends(get_current_user)) -> JSONResponse:
    request_data: dict = email_generation_request.dict()
    
    username = current_user['username']
    
    retrieval_strategy = LinkedInDataRetrievalStrategy(request_data['linkedin_url'])
    email_generator = EmailGenerator(request_data['user_prompt'], request_data['selected_documents'], request_data['selected_emails'],retrieval_strategy, username=username)
    email = email_generator.generate_email()
    
    
    if email == -1:
        raise HTTPException(status_code=505, detail='Could not fetch data of the person from LinkedIn')
    
    
    data = {
        'linkedinurl': request_data['linkedin_url'],
        'user_prompt': request_data['user_prompt'],
        'selected_emails': request_data['selected_emails'],
        'selected_documents': request_data['selected_documents'],
        'generated_email': email,
        'username': username,
        'time': datetime.now().isoformat()
    }
    
    
    person_data = email_generator.linkedin_user_data
    person_data = json.loads(person_data)
    person_data['url'] = request_data['linkedin_url']
    
    
    
    db_handler.insert_email(data)
    db_handler.insert_person(person_data)

    
    
    response_data = {
        'message': 'Email Generated Successfully!',
        'generated_email': email,
        'linkedinurl': person_data['url']

    }
    
    print(response_data)
    return JSONResponse(status_code=200, content=response_data)




@app.post('/signup')
def signup(signup_request: SignupRequest) -> JSONResponse:
    request_data = signup_request.dict()
    
    if db_handler.username_exists(request_data['username']):
        raise HTTPException(status_code=409, detail='The username is already taken!')        
    
    
    db_handler.insert_user(request_data['username'],request_data['password'], request_data['first_name'],  request_data['last_name'])
    
    username = request_data['username']
    
    # Make relevant data stores
    os.makedirs(f'{FILE_STORAGE_PATH}/{username}', exist_ok=True)
    os.makedirs(f'{FILE_STORAGE_PATH}/{username}/company_documents', exist_ok=True)
    os.makedirs(f'{FILE_STORAGE_PATH}/{username}/sample_emails', exist_ok=True)
    
    
    return JSONResponse(status_code=200, content=request_data)
    

@app.post('/login')
def login(login_request: LoginRequest) -> JSONResponse:
    request_data = login_request.dict()
    
    if not db_handler.login_valid(request_data['username'], request_data['password']):
        raise HTTPException(status_code=401, detail='INVALID Username or Password!')

    access_token = create_jwt_token(request_data, 3600)

    return_data = {
        'access_token': access_token,
        'message': 'Login successful!',
        'expires_in': 3600
    }
    
    response = JSONResponse(status_code=200, content=return_data)
    
    
    return response


@app.post('/find-email')
def find_email(request_data: FindEmailRequest, current_user: dict = Depends(get_current_user)):

    request_data: dict = request_data.dict() 

    api_key = 'LOkC-q7SjAV8ihl9DC7bCQ'
    headers = {'Authorization': 'Bearer ' + api_key}
    api_endpoint = 'https://nubela.co/proxycurl/api/contact-api/personal-email'
    params = {
        'linkedin_profile_url': request_data['linkedinurl'],
        'email_validation': 'include',    
    }
    
    response = requests.get(api_endpoint, params=params, headers=headers)
    
    if response.status_code == 200:
        response_data = response.json()
        return JSONResponse(content=response_data, status_code=200)
    else:
        return JSONResponse(content={"error": "Failed to fetch email"}, status_code=response.status_code)

    

@app.post('/send-email')
def send_email(request_data: SendEmailRequest, current_user: dict = Depends(get_current_user)):
    request_data = request_data.dict()

    msg = MIMEMultipart()
    msg['From'] = request_data['sender_email']
    msg['To'] = request_data['receiver_email']
    msg['Subject'] = request_data['subject']

    # Attach the email body
    msg.attach(MIMEText(request_data['email'], 'plain'))

    try:
        # Connect to the Gmail SMTP server and send the email
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(request_data['sender_email'], request_data['sender_password'])
        text = msg.as_string()
        server.sendmail(request_data['sender_email'], request_data['receiver_email'], text)
        server.quit()
        return JSONResponse(content={"message": "Email sent successfully!"}, status_code=status.HTTP_200_OK)
    except smtplib.SMTPAuthenticationError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
    except smtplib.SMTPRecipientsRefused:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Recipient email address refused.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to send email. Error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


