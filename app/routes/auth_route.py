from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user_model import User
from app.schema.auth_schema import LoginRequest, LoginResponse
from app.auth.jwt import create_access_token
from app.security import verify_password  

import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=LoginResponse)
def login(login_request: LoginRequest, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == login_request.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Login failed, user does not exist"
        )

    # Correct password check
    password_match = verify_password(login_request.password, user.password)

    if not password_match:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password"
        )

    claims = {
        "sub": str(user.id),
        "email": user.email,
        "user_id": str(user.id)
    }

    access_token = create_access_token(claims)

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        email=user.email,
        user_id=user.id
    )
