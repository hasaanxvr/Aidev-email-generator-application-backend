
import logging
import secrets
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt


ALGORITHM = 'HS256'
SECRET_KEY = secrets.token_hex(16)

security = HTTPBearer()

def create_jwt_token(data: dict, expires_delta: int):
    """Generates access token for jwt-based authentication

    Args:
        data (dict): data from the user. 
        expires_delta (int): expirtion delta of the token (in minutes)

    Returns:
        string: JWT Token
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    return encoded_jwt



def decode_jwt_token(access_token) -> dict:
    """Decodes the access token

    Args:
        access_token (str): JWT token

    Returns:
        dict: user data
    """
    try:
        user_data = jwt.decode(token=access_token, key=SECRET_KEY, algorithms=ALGORITHM)
        return user_data
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    return decode_jwt_token(token)
    