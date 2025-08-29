from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import timedelta

from ..utils.auth_utils import register_user, login_user
from ..utils.security import create_access_token
from ..utils.file_handler import load_json
from ..dependency import get_current_user  # now using HTTPBearer version

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    id: int
    name: str
    phone: str
    password: str
    role: str
    city: str
    municipality: str
    ward: str


class LoginRequest(BaseModel):
    phone: str
    password: str


# ✅ Register endpoint
@auth_router.post("/register")
def register(req: RegisterRequest):
    try:
        new_user = register_user(req.model_dump())
        return {"message": "User registered successfully", "user": new_user}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# ✅ Login endpoint → returns JWT
@auth_router.post("/login")
def login(req: LoginRequest):
    try:
        user = login_user(req.phone, req.password)

        # create JWT token
        access_token = create_access_token(
            data={
                "sub": user["phone"],
                "role": user["role"],
                "id": user["id"]
            },
            expires_delta=timedelta(minutes=60)
        )
        return {"access_token": access_token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


# ✅ Protected route (requires Bearer token)
@auth_router.get("/me")
def read_users_me(current_user: dict = Depends(get_current_user)):
    """
    Test endpoint to validate JWT token.
    Returns the current logged-in user's data from the token.
    """
    return {"current_user": current_user}

# Get all users (for ID generation)
@auth_router.get("/users")
def get_users():
    try:
        users = load_json("users.json")
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
