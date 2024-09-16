import os
import io
import requests
import json
import smtplib
import pandas as pd
import shutil
from datetime import datetime
from pymongo.errors import PyMongoError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from fastapi import FastAPI, HTTPException, Depends, status, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routers import document, email
from EmailGenerator import EmailGenerator
from schemas.EmailGenerationRequest import LinkedinURLEmailGenerationRequest, NameEmailGenerationRequest
from schemas.SignupRequest import SignupRequest
from schemas.LoginRequest import LoginRequest
from schemas.FindEmailRequest import FindEmailRequest
from schemas.SendEmailRequest import SendEmailRequest
from schemas.FindPerson import FindPersonByNameAndOrg, FindPersonByEmail
from schemas.BulkEmailGenerationRequest import BulkEmailGenerationRequest
from config import DATABASE_NAME, FILE_STORAGE_PATH
from db.Database import MongoDatabase
from core.security import create_jwt_token, get_current_user
from RetirevalStrategy import LinkedInDataRetrievalStrategy, NameCompanyDataRetrievalStrategy, EmailDataRetrievalStrategy
from file_storage import DigitalOceanSpacesManager


db_handler = MongoDatabase()

spaces_manager = DigitalOceanSpacesManager(
    key='DO004X6LKK4NR9K4WQHP',
    secret='b2h7TrCXohEsfPm0ejmpapqRFIUKtKCPrPLpalOHK4I',
    region='nyc3',
    bucket_name='spaces-bucket-ai-email'
)

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


@app.post('/find-person/email')
def find_person_by_email(find_person_request: FindPersonByEmail):
    
    request_data: dict = find_person_request.dict()
    retrieval_handler = EmailDataRetrievalStrategy(request_data['email'])
    
    data: str = retrieval_handler.get_user_data()
    data: dict = json.loads(data)
    
    return_data = {
        'url': data['linkedin_profile_url'],
        'similarity_score': data['similarity_score']
    }

    
    return JSONResponse(content=return_data, status_code=200)


@app.post('/find-person/name-and-org')
def find_person_by_name_and_org(find_person_request: FindPersonByNameAndOrg, current_user: dict = Depends(get_current_user)) -> JSONResponse:
    request_data: dict = find_person_request.dict()

    retrieval_handler = NameCompanyDataRetrievalStrategy(request_data['first_name'], request_data['company'], request_data['last_name'], request_data['location'], request_data['title'], enrich_profile='skip')
    
    data = retrieval_handler.get_user_data()
    data = json.loads(data)
    #data =  {
    #"url": "https://pk.linkedin.com/in/saad-waseem-aab48a210",
    #"name_similarity_score": 1.0,
    #"company_similarity_score": 1.0,
    #"title_similarity_score": 0.7,
    #"location_similarity_score": 0.0
    #}
    
    return JSONResponse(content=data, status_code=200)













@app.post('/generate-email/name')
def generate_email_name(email_generation_request: NameEmailGenerationRequest, current_user: dict = Depends(get_current_user)) -> JSONResponse:
    

    
    request_data: dict = email_generation_request.dict()
    username = current_user['username']
    
    retrieval_strategy = NameCompanyDataRetrievalStrategy(request_data['first_name'], request_data['company'], request_data['last_name'], request_data['location'], request_data['title'])
    
    email_generator = EmailGenerator(request_data['user_prompt'], request_data['selected_documents'], request_data['selected_emails'],retrieval_strategy, username=username, company_name=request_data['company_name'])
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
    email_generator = EmailGenerator(request_data['user_prompt'], request_data['selected_documents'], request_data['selected_emails'],retrieval_strategy, username=username, company_name=request_data['company_name'])
    email = email_generator.generate_email()
    
    email_data = json.loads(email)
    if email == -1:
        raise HTTPException(status_code=505, detail='Could not fetch data of the person from LinkedIn')
    
    
    data = {
        'linkedinurl': request_data['linkedin_url'],
        'user_prompt': request_data['user_prompt'],
        'selected_emails': request_data['selected_emails'],
        'selected_documents': request_data['selected_documents'],
        'email_body': email_data['body'],
        'email_subject':email_data['subject'],
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
        #'linkedinurl': 'https://www.linkedin.com/in/williamhgates'
    }
    
    
    
    print(response_data)
    return JSONResponse(status_code=200, content=response_data)

"""

    email =  
    Subject: Enhance Your Legal Outreach with TROUSSE MEDIA

    Dear Mr. Gates,

    I hope this message finds you well. Given your esteemed role as Co-chair at the Bill & Melinda Gates Foundation and your influential presence across various sectors, I believe there is an exceptional opportunity for us to collaborate that aligns with your visionary commitment to impact.

    TROUSSE MEDIA, the leading legal news platform in Québec, offers an unparalleled gateway to the heart of the legal community, including top attorneys, law firms, and corporate legal teams from organizations like Norton Rose and Fasken Martineau, as well as legal professionals from major corporations such as Bell and Bombardier. With over 156,091 unique visitors monthly, our platform ensures significant exposure and engagement within this niche yet influential group.

    Given your foundation's initiatives that intersect with various legal aspects, leveraging TROUSSE MEDIA could significantly enhance your outreach and engagement with key legal stakeholders. Here’s how we can help:

    1. **Content-Driven Visibility**: Our 'Publicité de Contenu' allows you to present rich, engaging content that highlights the foundation’s initiatives and positions it as a thought leader in the legal facets of philanthropy. Formats range from concise career advice to in-depth interviews and feature reports, providing a tailored approach to suit your strategic communication needs.

    2. **Targeted Advertising**: With a range of advertising options including banners and dedicated web pages, your message stays visible across our platform, consistently reaching well-educated professionals, 57% of whom earn over $100k and are key decision-makers within their organizations.

    3. **Social Media Amplification**: Boost your campaigns through our strong social media presence with over 46,894 followers across platforms like LinkedIn, Facebook, and Twitter, ensuring your message resonates well beyond the immediate readership.

    4. **Customizable Campaigns**: Whether it’s a short-term awareness campaign or a long-term strategic partnership, our flexible advertising solutions like the dedicated page can be tailored to meet your foundation’s specific objectives, ensuring optimal engagement and impact.

    Mr. Gates, collaborating with TROUSSE MEDIA means placing your trust in a partner that is deeply embedded in the Quebec legal community. I would be delighted to discuss how we can tailor our platforms and services to best support the goals of the Bill & Melinda Gates Foundation.

    Please let me know a convenient time for us to discuss this further. I am looking forward to the opportunity of working together to make a meaningful impact.

    Warm regards,

    [Your Name]
    [Your Position]
    TROUSSE MEDIA
    [Contact Information]
    [Website URL]
    
    
    response_data = {
        'message': 'Email Generated Successfully!',
        'generated_email': email,
        #'linkedinurl': person_data['url']
        'linkedinurl': 'https://www.linkedin.com/in/williamhgates'
    }
    """
    
    
@app.post('/login')
def login(login_request: LoginRequest) -> JSONResponse:
    request_data = login_request.dict()
    
    if not db_handler.login_valid(request_data['username'], request_data['password']):
        raise HTTPException(status_code=401, detail='INVALID Username or Password!')

    access_token = create_jwt_token({'username': request_data['username']}, 3600)

    return_data = {
        'access_token': access_token,
        'message': 'Login successful!',
        'expires_in': 3600
    }
    
    response = JSONResponse(status_code=200, content=return_data)
    
    return response



@app.post('/signup')
def signup(signup_request: SignupRequest) -> JSONResponse:
    request_data = signup_request.dict()
    
    if db_handler.username_exists(request_data['username']):
        raise HTTPException(status_code=409, detail='The username is already taken!')        
    
    success = db_handler.insert_user(request_data['username'], request_data['password'], request_data['first_name'], request_data['last_name'])
    
    if not success:
        raise HTTPException(status_code=500, detail="An error occurred during signup.")

    username = request_data['username']
    
    #os.makedirs(f'{FILE_STORAGE_PATH}/{username}', exist_ok=True)
    spaces_manager.create_folder(username)
    
    return JSONResponse(status_code=200, content={"message": "Signup successful!"})


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
    
    #data = {
    #    'emails': ['hasaan1108@gmail.com', 'l191011@lhr.nu.edu.pk' ],
    #    'invalid_emails': ['fakeemail@something.com']
    #}
    
    #return JSONResponse(content=data, status_code=200)

    

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



@app.post('/api/bulk-search/upload')
async def upload_csv(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)) -> JSONResponse:
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        contents = await file.read()  
        df = pd.read_csv(io.StringIO(contents.decode("utf-8")), header=None) 
        
        email_list = df[0].tolist()
        
        unmatched_emails = []
        matched_emails = {}
        
        for email in email_list:
            retrieval_handler = EmailDataRetrievalStrategy(email)
    
            data: str = retrieval_handler.get_user_data()
            data: dict = json.loads(data)
            
            if data['url'] is None:
                unmatched_emails.append(email)
            else:
                matched_emails[email] = data['url']
                
            
        
         #Dummy data
        """
        matched_emails = {
            'example@afs.com': 'https://linkedin.com/in/example',
            'bhenk@shenk.com': 'https://linkedin.com/in/bhenkshenk'
        }
        
        unmatched_emails = [
            'nomatch@example.com',
            'notfound@shenk.com'
        ]
        """
        return JSONResponse(status_code=200, content={
            "detail": "CSV uploaded and processed successfully", 
            "matched": matched_emails,
            "unmatched": unmatched_emails
        })
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="There was an error processing the file")



@app.post('/bulk-email-generation/')
def generate_bulk_emails(request_data: BulkEmailGenerationRequest, current_user: dict = Depends(get_current_user)):
    request_data = request_data.dict()
    
    username = current_user['username']
    
    generated_emails = []
    
    # Iterate through the dictionary of {url: email}
    for url, email in request_data['linkedin_url_dict'].items():
        retrieval_strategy = LinkedInDataRetrievalStrategy(url)
        email_generator = EmailGenerator(
            request_data['user_prompt'], 
            request_data['selected_documents'], 
            request_data['selected_emails'], 
            retrieval_strategy, 
            username=username, 
            company_name=request_data['company_name']
        )

        email_content = email_generator.generate_email()
    
        email_data = json.loads(email_content)
        
        email_entry = {  # Create a dictionary for the current URL
            url: {
                'subject': email_data['subject'],
                'body': email_data['body'],
                'email_address': email  # Use the provided email
            }
        }
        
        generated_emails.append(email_entry)     
    
        
        data = {
            'linkedinurl': url,
            'user_prompt': request_data['user_prompt'],
            'selected_emails': request_data['selected_emails'],
            'selected_documents': request_data['selected_documents'],
            'email_body': email_data['body'],
            'email_subject':email_data['subject'],
            'username': username,
            'time': datetime.now().isoformat()
        }
        
        
        person_data = email_generator.linkedin_user_data
        person_data = json.loads(person_data)
        person_data['url'] = url
        
        db_handler.insert_email(data)
        db_handler.insert_person(person_data)
    
    
    dummy_emails = []
        
    for url, email in request_data['linkedin_url_dict'].items():
    # Simulating email generation process with dummy data
        dummy_email_data = {
            url: {
                'subject': f"Dummy Subject for {url}",
                'body': f"Dear [Name],\n\nThis is a dummy email body generated for {url}.\n\nBest regards,\n{username}",
                'email_address': email  # Use the email provided in the request data
            }
        }
    dummy_emails.append(dummy_email_data)
        
    return JSONResponse(content=generated_emails, status_code=200)



@app.get('/document-info')
def get_all_emails(current_user: dict = Depends(get_current_user)):
    companies = os.listdir('file_storage')
    data = {}
    for company in companies:
        temp_dict = {}
        temp_dict['sample_emails'] = os.listdir(f'file_storage/{company}/company_documents')
        temp_dict['company_documents'] = os.listdir(f'file_storage/{company}/company_documents')
        data[company] = temp_dict
    
    return JSONResponse(status_code=200, content=data) 


@app.get(f'/company-names')
def get_company_names(current_user: dict = Depends(get_current_user)):
    username = current_user['username']

    #companies = os.listdir(f'file_storage/{username}')
    
    companies = spaces_manager.list_folders_in_folder(username)

    data = {'companies': companies}
    
    return JSONResponse(content=data, status_code=200)


from pydantic import BaseModel
class AddCompanyRequest(BaseModel):
    company_name: str

@app.post('/api/companies/add')
def add_company(request: AddCompanyRequest, current_user: dict = Depends(get_current_user)):
    
    username = current_user['username']
    company_name = request.company_name
    
    
    try:
        spaces_manager.create_emails_and_documents_folder(company_name, username)
        return JSONResponse(status_code=200, content={"message": f"Company '{company_name}' added successfully"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating company: {str(e)}")



@app.delete('/api/companies/delete/{company_name}')
def delete_company(company_name: str, current_user: dict = Depends(get_current_user)):
    
    username = current_user['username']
    company_path = f'file-storage/{username}/{company_name}/'  # Ensure trailing slash
    
    try:
        spaces_manager.delete_folder(company_path)
        return JSONResponse(status_code=200, content={"message": f"Company '{company_name}' deleted successfully"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting company: {str(e)}")

    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


