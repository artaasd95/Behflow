"""
User models for authentication
"""
from pydantic import BaseModel
from uuid import UUID


class UserBase(BaseModel):
    """Base user model"""
    username: str
    name: str
    lastname: str


class UserRegister(UserBase):
    """User registration model"""
    password: str


class UserLogin(BaseModel):
    """User login model"""
    username: str
    password: str


class User(UserBase):
    """User model with ID"""
    user_id: UUID
    
    class Config:
        from_attributes = True


class LoginResponse(BaseModel):
    """Login response model"""
    user: User
    message: str
