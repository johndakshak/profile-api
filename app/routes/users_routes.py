from fastapi import APIRouter, HTTPException, status, Depends, Form, File, UploadFile
from sqlalchemy.orm import Session
from typing import List
from app.models.user_model import User
from app.database import get_db
from app.middleware.auth import User, get_current_user
from app.middleware.auth import authMiddleware
from app.middleware.auth import JWTBearer
from app.schema.users_schema import UserCreate, UserResponse, UserUpdate, UserProfile
from app.security import hash_password
import os
import aiofiles
from uuid import UUID, uuid4


router = APIRouter(prefix="/user", tags=["Users"])

UPLOAD_DIR = "app/static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/me", response_model=UserProfile)
def get_current_user(current_user: User = Depends(JWTBearer())):
    return current_user

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    
    email_exist = db.query(User).filter(User.email == user.email).first()

    if email_exist:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"email '{user.email}' already exist!"
        )

    hashed_pwd = hash_password(user.password)

    new_user = User(
        name=user.name,
        email=user.email,
        password=hashed_pwd,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

UPLOAD_DIR = "app/static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)
    
@router.patch("/upload_dp", status_code=status.HTTP_201_CREATED, response_model = UserProfile)
async def upload_dp(current_user: User = Depends(authMiddleware), db: Session = Depends(get_db),

    img_url: UploadFile = File(...),
):

    user_id = current_user.id

    user_exist = db.query(User).filter(User.id == user_id).first()

    if not user_exist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User Id: {user_id} not found!"
        )

    MAX_FILE_SIZE = 5 * 1024 * 1024 
    allowed_extens = ["jpeg", "png", "jpg"]
    file_exten = img_url.filename.split(".")[-1].lower()

    if file_exten not in allowed_extens:
        raise HTTPException(status_code=400, detail="Invalid file extension!")

    filename = f"{uuid4()}.{file_exten}"
    file_path = f"{UPLOAD_DIR}/{filename}"

    try:
        content = await img_url.read()

        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File size must not be more than 5MB"
            )

        if user_exist.img_url:
            old_path = f"{UPLOAD_DIR}/{user_exist.img_url}"
            if os.path.exists(old_path):
                os.remove(old_path)

        async with aiofiles.open(file_path, "wb") as out_file:
            await out_file.write(content)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An internal server error occured: {e}"
            )

    user_exist.img_url = filename

    db.commit()
    db.refresh(user_exist)

    return user_exist

@router.patch('/', status_code=status.HTTP_200_OK, response_model=UserUpdate)
def update_user(user_name: UserUpdate, current_user: User = Depends(authMiddleware), db: Session = Depends(get_db)):

    name = db.query(User).filter(User.name == current_user.name).first()

    if not name:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User not found!"
        )
    
    for field, value in user_name.dict(exclude_unset=True).items():
        setattr(name, field, value)

    db.commit()
    db.refresh(name)
    return name
    



