from datetime import datetime, timedelta
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from . import models, schemas, database

# --- Configuration ---
# IN PRODUCTION: Move these to environment variables!
SECRET_KEY = "your-secret-key-keep-this-safe"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --- Setup ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# --- Helper Functions ---

def verify_password(plain_password, hashed_password):
    """Checks if the entered password matches the stored hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Hashes a password before storing it in the database."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Generates a JWT token for the user."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- Dependency: Get Current User ---

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    """
    Decodes the token to find the user. 
    Use this dependency in routers to protect endpoints.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
        
    user = db.query(models.User).filter(models.User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user