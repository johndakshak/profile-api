from pydantic import BaseModel, Field, EmailStr, field_validator
import re

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


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
    
class LoginResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    email: str
    user_id: int