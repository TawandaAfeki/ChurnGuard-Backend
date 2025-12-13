from app import models
from app.database import Base
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import database, models, schemas, crud, auth
from fastapi.security import OAuth2PasswordBearer
from jose import jwt


Base.metadata.create_all(bind=database.engine)


app = FastAPI()

# Add CORS middleware - IMPORTANT for connecting to your website
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://tawandaafeki.github.io",  # Your GitHub Pages site
        "http://localhost:3000",  # For local testing
        "http://localhost:5173",  # For local testing (Vite)
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = crud.get_user_by_email(db, email=email)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

# Health check endpoint
@app.get("/")
def read_root():
    return {"status": "ok", "message": "ChurnGuard API is running"}

# Auth
@app.post("/api/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db, user)

@app.post("/api/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, user.email)
    if not db_user or not auth.verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = auth.create_access_token({"sub": db_user.email})
    return {"access_token": token, "token_type": "bearer"}

# Clients
@app.get("/api/clients", response_model=list[schemas.ClientOut])
def read_clients(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.get_clients(db, user_id=current_user.id)

@app.post("/api/clients", response_model=schemas.ClientOut)
def add_client(client: schemas.ClientCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return crud.create_client(db, client, user_id=current_user.id)

# Remove duplicate metadata creation
# from app.database import Base, engine
# Base.metadata.create_all(bind=engine)

import os

def create_admin_user():
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")

    if not admin_email or not admin_password:
        print("Admin env vars not set, skipping admin creation")
        return

    db = database.SessionLocal()
    try:
        existing = crud.get_user_by_email(db, admin_email)
        if existing:
            return

        admin = models.User(
            email=admin_email,
            password_hash=auth.hash_password(admin_password),
            company_id=1  # temporary, safe default
        )
        db.add(admin)
        db.commit()
    finally:
        db.close()


from fastapi import FastAPI

@app.on_event("startup")
def startup_event():
    create_admin_user()