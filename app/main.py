from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routers import document, email
from EmailGenerator import EmailGenerator
from schemas.EmailGenerationRequest import EmailGenerationRequest
from schemas.SignupRequest import SignupRequest
from schemas.LoginRequest import LoginRequest

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development; change this to your frontend's URL in production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Include routers
app.include_router(document.router, prefix='/api', tags=['documents'])
app.include_router(email.router, prefix='/api', tags=['emails'])

@app.get('/')
def welcome_message() -> JSONResponse:
    return JSONResponse(status_code=200, content={'message': 'Welcome to Personalized Email Generator!'})

@app.post('/generate-email')
def generate_email(email_generation_request: EmailGenerationRequest) -> JSONResponse:
    request_data: dict = email_generation_request.dict()
    
    email_generator = EmailGenerator(**request_data)
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
    print(request_data)
    return JSONResponse(status_code=200, content=request_data)
    

@app.post('/login')
def login(login_request: LoginRequest) -> JSONResponse:
    request_data = login_request.dict()
    print(request_data)
    return JSONResponse(status_code=200, content=request_data)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
