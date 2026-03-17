# ✅ CORRECT app/routers/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter()

@router.post('/register', response_model=UserOut, status_code=201)
def register(body: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail='Email already registered')
    if len(body.password) < 8:
        raise HTTPException(status_code=400, detail='Password must be at least 8 characters')
    
    user = User(
        email=body.email,
        password_hash=hash_password(body.password),
        full_name=body.full_name,
        role=body.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post('/login')
def login(body: dict, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body['email']).first()
    if not user or not verify_password(body['password'], user.password_hash):
        raise HTTPException(status_code=401, detail='Invalid email or password')
    token = create_access_token(user.id, user.role)
    return {'access_token': token, 'token_type': 'bearer', 'role': user.role}