from datetime import timedelta
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# Import local modules
from . import models, schemas, auth, database
from .routers import assignments, student

# --- Database Initialization ---
# This automatically creates all tables (users, assignments, etc.) in the database 
# if they don't exist when the app starts.
models.Base.metadata.create_all(bind=database.engine)

# --- App Configuration ---
app = FastAPI(
    title="EduGen AI API",
    description="Backend for EduGen AI: Intelligent Content System",
    version="1.0.0"
)

# --- CORS Middleware ---
# This is CRITICAL for React to talk to FastAPI.
# We allow requests from your frontend (usually running on localhost:5173 or 3000)
origins = [
    "http://localhost:5173", # Vite default
    "http://localhost:3000", # CRA default
    "http://127.0.0.1:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allow all methods (GET, POST, etc.)
    allow_headers=["*"], # Allow all headers
)

# --- Authentication Routes ---

@app.post("/register", response_model=schemas.UserResponse, tags=["Authentication"])
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    """
    Register a new user (Educator or Student).
    """
    # Check if email already exists
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Hash password and save
    hashed_password = auth.get_password_hash(user.password)
    new_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/token", response_model=schemas.Token, tags=["Authentication"])
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(database.get_db)
):
    """
    Login endpoint. Returns a JWT token if credentials are valid.
    Form fields: username (email), password.
    """
    # 1. Find user
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    
    # 2. Verify password
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 3. Create Token
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=schemas.UserResponse, tags=["Authentication"])
async def read_users_me(current_user: models.User = Depends(auth.get_current_user)):
    """
    Get details of the currently logged-in user.
    """
    return current_user

# --- Include Specific Routers ---
# This keeps main.py clean by offloading logic to dedicated files.
app.include_router(assignments.router, prefix="/assignments", tags=["Assignments"])
app.include_router(student.router, prefix="/student", tags=["Student Portal"])

# --- Health Check ---
@app.get("/")
def read_root():
    return {
        "status": "online", 
        "message": "EduGen AI Backend is running. Visit /docs for API documentation."
    }