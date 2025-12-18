"""
Authentication router - handles user registration and login
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from app.api.models.user import UserRegister, UserLogin, User, LoginResponse
from uuid import uuid4, UUID
from typing import Optional

router = APIRouter(tags=["auth"])

# Simple in-memory storage (for simplicity, not for production)
users_db = {}

# Initialize with a test user
TEST_USER_ID = uuid4()
users_db["test"] = {
    "user_id": TEST_USER_ID,
    "username": "test",
    "password": "test",
    "name": "Test",
    "lastname": "User"
}


@router.post("/register", response_model=User)
async def register(user_data: UserRegister):
    """
    Register a new user
    """
    if user_data.username in users_db:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    user_id = uuid4()
    users_db[user_data.username] = {
        "user_id": user_id,
        "username": user_data.username,
        "password": user_data.password,  # In real app, hash this!
        "name": user_data.name,
        "lastname": user_data.lastname
    }
    
    return User(
        user_id=user_id,
        username=user_data.username,
        name=user_data.name,
        lastname=user_data.lastname
    )


@router.post("/login", response_model=LoginResponse)
async def login(credentials: UserLogin):
    """
    Login user
    """
    user = users_db.get(credentials.username)
    
    if not user or user["password"] != credentials.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return LoginResponse(
        user=User(
            user_id=user["user_id"],
            username=user["username"],
            name=user["name"],
            lastname=user["lastname"]
        ),
        message="Login successful"
    )


# Authentication dependency
async def get_current_user_from_header(x_user_id: Optional[str] = Header(None)) -> User:
    """
    Simple authentication - checks user_id in header
    For simplicity, we're using a header-based auth
    """
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Missing authentication header (x-user-id)")
    
    try:
        user_uuid = UUID(x_user_id)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid user_id format")
    
    # Find user by user_id
    for username, user_data in users_db.items():
        if user_data["user_id"] == user_uuid:
            return User(
                user_id=user_data["user_id"],
                username=user_data["username"],
                name=user_data["name"],
                lastname=user_data["lastname"]
            )
    
    raise HTTPException(status_code=401, detail="User not found")


@router.get("/users/me", response_model=User)
async def get_current_user(user: User = Depends(get_current_user_from_header)):
    """
    Get current authenticated user
    """
    return user
