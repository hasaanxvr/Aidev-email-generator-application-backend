import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routers import document, email
from EmailGenerator import EmailGenerator
from schemas.EmailGenerationRequest import EmailGenerationRequest
from schemas.SignupRequest import SignupRequest
from schemas.LoginRequest import LoginRequest
from config import DATABASE_NAME, FILE_STORAGE_PATH
from db.utils import username_exists, insert_user, login_valid
from core.security import create_jwt_token, get_current_user


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

@app.post('/generate-email')
def generate_email(email_generation_request: EmailGenerationRequest, current_user: dict = Depends(get_current_user)) -> JSONResponse:
    request_data: dict = email_generation_request.dict()
    
    username = current_user['username']
    
    email_generator = EmailGenerator(**request_data, username=username)
    email = email_generator.generate_email()
    
    if email == -1:
        raise HTTPException(status_code=505, detail='Could not fetch data of the person from LinkedIn')
    
    response_data = {
        'message': 'Email Generated Successfully!',
        'generated_email': email
    }
    
    print(response_data)
    return JSONResponse(status_code=200, content=response_data)


@app.post('/signup')
def signup(signup_request: SignupRequest) -> JSONResponse:
    request_data = signup_request.dict()
    
    if username_exists(DATABASE_NAME, request_data['username']):
        raise HTTPException(status_code=409, detail='The username is already taken!')        
    
    
    insert_user(DATABASE_NAME, request_data['username'],request_data['password'], request_data['first_name'],  request_data['last_name'])
    
    username = request_data['username']
    
    # Make relevant data stores
    os.makedirs(f'{FILE_STORAGE_PATH}/{username}', exist_ok=True)
    os.makedirs(f'{FILE_STORAGE_PATH}/{username}/company_documents', exist_ok=True)
    os.makedirs(f'{FILE_STORAGE_PATH}/{username}/sample_emails', exist_ok=True)
    
    
    return JSONResponse(status_code=200, content=request_data)
    

@app.post('/login')
def login(login_request: LoginRequest) -> JSONResponse:
    request_data = login_request.dict()
    
    if not login_valid(DATABASE_NAME, request_data['username'], request_data['password']):
        raise HTTPException(status_code=401, detail='INVALID Username or Password!')

    access_token = create_jwt_token(request_data, 600)

    return_data = {
        'access_token': access_token,
        'message': 'Login successful!',
        'expires_in': 600
    }
    
    response = JSONResponse(status_code=200, content=return_data)
    
    
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
