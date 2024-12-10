from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserUpdatePassword(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
