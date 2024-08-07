import os
import sqlite3
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routers import document, email
from EmailGenerator import EmailGenerator
from schemas.EmailGenerationRequest import LinkedinURLEmailGenerationRequest, NameEmailGenerationRequest
from schemas.SignupRequest import SignupRequest
from schemas.LoginRequest import LoginRequest
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
    
    conn = sqlite3.connect('email-generation.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            SELECT date, linkedinUrl, userPrompt, selectedDocuments, selectedEmails, generatedEmail
            FROM EmailHistory
            WHERE username = ?
        ''', (username,))
        
        rows = cursor.fetchall()
        
        email_history = []
        for row in rows:
            email_history.append({
                'date': row[0],
                'linkedinUrl': row[1],
                'userPrompt': row[2],
                'selectedDocuments': row[3],
                'selectedEmails': row[4],
                'generatedEmail': row[5]
            })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail='Failed to fetch email history from the database') from e
    finally:
        conn.close()
    
    return JSONResponse(status_code=200, content=email_history)



@app.post('/generate-email/name')
def generate_email_name(email_generation_request: NameEmailGenerationRequest, current_user: dict = Depends(get_current_user)) -> JSONResponse:
    
    import pdb
    pdb.set_trace()
    request_data: dict = email_generation_request.dict()
    username = current_user['username']
    
    retrieval_strategy = NameCompanyDataRetrievalStrategy(request_data['first_name'], request_data['company'], request_data['last_name'], request_data['location'], request_data['title'])
    email_generator = EmailGenerator(request_data['user_prompt'], request_data['selected_documents'], request_data['selected_emails'],retrieval_strategy, username=username)
    email = email_generator.generate_email()
    
    if email == -1:
        raise HTTPException(status_code=505, detail='Could not fetch data of the person from LinkedIn')
    
    response_data = {
        'message': 'Email Generated Successfully!',
        'generated_email': email
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
    
    # Write to the database
    conn = sqlite3.connect('email-generation.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO EmailHistory (date, linkedinUrl, userPrompt, selectedDocuments, selectedEmails, generatedEmail, username)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().isoformat(),
            request_data['linkedin_url'],
            request_data['user_prompt'],
            ','.join(request_data['selected_documents']),
            ','.join(request_data['selected_emails']),
            email,
            username
        ))
        
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail='Failed to write to the database') from e
    finally:
        conn.close()
    
    response_data = {
        'message': 'Email Generated Successfully!',
        'generated_email': email
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
