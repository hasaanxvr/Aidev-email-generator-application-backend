from fastapi import FastAPI, APIRouter
from fastapi import APIRouter


app = FastAPI()

@app.get('/')
def welcome_message():
    return {'message': 'Welcome to Personalized Email Generation Application!', 'version': '0.0.1'}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
