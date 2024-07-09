from fastapi import FastAPI, Response
from routers import document, email

app = FastAPI()
app.include_router(document.router, prefix='/api', tags=['documents'])
app.include_router(email.router, prefix='/api', tags=['emails'])


@app.get('/')
def welcome_message():
    Response(status_code=200, content={'message': 'Welcome to Personalized Email Generator!'})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
