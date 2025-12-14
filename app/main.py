from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt

from . import database, models, schemas, crud, auth

# --------------------
# App initialization
# --------------------
app = FastAPI()

# --------------------
# CORS
# --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://tawandaafeki.github.io",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------
# Auth
# --------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

# --------------------
# Database dependency
# --------------------
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --------------------
# Current user dependency
# --------------------
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    try:
        payload = jwt.decode(
            token,
            auth.SECRET_KEY,
            algorithms=[auth.ALGORITHM],
        )
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = crud.get_user_by_email(db, email=email)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return user

    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")

# --------------------
# Health check
# --------------------
@app.get("/")
def read_root():
    return {
        "status": "ok",
        "message": "ChurnGuard API is running",
    }

# --------------------
# Auth endpoints
# --------------------
@app.post("/api/register", response_model=schemas.UserOut)
def register(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
):
    existing = crud.get_user_by_email(db, user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    return crud.create_user(db, user)


@app.post("/api/login")
def login(
    user: schemas.UserLogin,
    db: Session = Depends(get_db),
):
    db_user = crud.get_user_by_email(db, user.email)

    if not db_user or not auth.verify_password(
        user.password, db_user.password_hash
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = auth.create_access_token(
        {"sub": db_user.email}
    )

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": db_user.id,
            "full_name": db_user.full_name,
            "email": db_user.email,
            "company_id": db_user.company_id,
        },
    }


# --------------------
# Clients (user-scoped)
# --------------------
@app.get(
    "/api/clients",
    response_model=list[schemas.ClientOut],
)
def read_clients(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return crud.get_clients(
        db,
        user_id=current_user.id,
    )


@app.post(
    "/api/clients",
    response_model=schemas.ClientOut,
)
def add_client(
    client: schemas.ClientCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return crud.create_client(
        db,
        client,
        user_id=current_user.id,
    )

@app.get("/api/me")
def read_me(
    current_user: models.User = Depends(get_current_user),
):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "company_id": current_user.company_id,
    }


@app.get("/api/alerts", response_model=list[schemas.AlertOut])
def get_alerts(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return crud.get_active_alerts_for_user(db, current_user.id)

@app.get("/api/customers/dashboard", response_model=list[schemas.CustomerDashboardOut])
def customers_dashboard(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return crud.get_customers_dashboard(db, current_user.company_id)

@app.get("/api/dashboard/churn-trend")
def churn_trend(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return crud.get_churn_trend(db, current_user.company_id)
