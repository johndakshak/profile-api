from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
from datetime import datetime
import re


class UserCreate(BaseModel):
    name: str = Field(min_length=3, max_length=30)
    email: EmailStr
    password: str

    @field_validator('name', 'password')
    def no_whitespace(cls, v):
        v = v.strip()  
        if not v:
            raise ValueError('must not be empty or whitespace')
        return v
    
    @field_validator("password")
    def validate_password(cls, value):
        if len(value) < 6:
            raise ValueError("Password must be at least 6 characters long")

        has_lower = False
        has_upper = False
        has_digit = False
        has_special = False

        specials = "@$!%*#?&"

        for passwd in value:
            if passwd.islower():
                has_lower = True
            elif passwd.isupper():
                has_upper = True
            elif passwd.isdigit():
                has_digit = True
            elif passwd in specials:
                has_special = True

        if not has_lower:
            raise ValueError("Password must contain a lowercase letter")

        if not has_upper:
            raise ValueError("Password must contain an uppercase letter")

        if not has_digit:
            raise ValueError("Password must contain a number")

        if not has_special:
            raise ValueError("Password must contain a special character (@$!%*#?&)")

        return value

    model_config = {"from_attributes": True}  

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


    model_config = {"from_attributes": True}

class UserProfile(BaseModel):
    id: int
    name: str
    email: str
    img_url: Optional[str]

    model_config = {"from_attributes": True}

class UserUpdate(BaseModel):
    name: Optional[str] = None

    model_config = {"from_attributes": True}
