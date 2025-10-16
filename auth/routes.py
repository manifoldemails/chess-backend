# auth/routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from database import get_session
from models import User
from auth.schemas import UserCreate, UserLogin, Token
from passlib.context import CryptContext
from jose import jwt
import datetime

router = APIRouter(prefix="/auth", tags=["Auth"])

SECRET_KEY = "manifoldchess"  # later store in env variable
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Helper: hash password
def hash_password(password: str) -> str:
    # Ensure password is max 72 bytes for bcrypt <-- otherwise it gives error password >72 bytes
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        raise ValueError("Password is too long for bcrypt (max 72 bytes).")
    return pwd_context.hash(password)


# Helper: verify password
def verify_password(password, hashed):
    return pwd_context.verify(password, hashed)

# Helper: create JWT token
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/signup")
def signup(user: UserCreate, session: Session = Depends(get_session)):
    print("wor")
    # check if email exists
    existing = session.exec(select(User).where(User.email == user.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password)
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return {"message": "User created successfully", "user_id": new_user.id}

@router.post("/login", response_model=Token)
def login(data: UserLogin, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == data.email)).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}
