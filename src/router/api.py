import json
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Header, status, Request
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer

from src.models.user import UserCreate, UserUpdatePassword
from src.services.token_service import TokenService
from src.services.user_service import UserService
from src.logger_setup import setup_logger

logger = setup_logger(__name__)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

def get_db(request: Request):
    return request.app.state.db

def get_user_service(db = Depends(get_db)):
    return UserService(db)

def get_token_service(db = Depends(get_db)):
    return TokenService(db)

@router.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(UTC) }

async def get_current_user_id(
    request: Request,
    authorization: str = Header(None),
    token_service: TokenService = Depends(get_token_service),
):
    token = None
    if authorization:
        scheme, _, param = authorization.partition(' ')
        if scheme.lower() == 'bearer':
            token = param
    if not token:
        token = request.query_params.get('Authorization')
    if not token:
        logger.info("No authentication token found.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return await token_service.extract_user_id_from_token(token)

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

@router.post('/api/login/', status_code=status.HTTP_200_OK)
async def login(request: Request, user_service: UserService = Depends(get_user_service)):
    data = await request.json()
    email = data.get('email')
    password = data.get('password')
    response = await user_service.login(email, password)
    if response.status_code == 200:
        logger.info(f"User {email} logged in successfully.")
    else:
        logger.warning(f"Failed login attempt for {email}.")
    return response

@router.post('/api/refresh_token/', status_code=status.HTTP_200_OK)
async def refresh_token(request: Request, token_service: TokenService = Depends(get_token_service)):
    refresh_token = request.cookies.get('refresh_token')
    if not refresh_token:
        logger.warning("Refresh token missing in cookies.")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Refresh token missing")

    try:
        access_token, new_refresh_token = await token_service.refresh_access_token(refresh_token)
        response = JSONResponse({"access_token": access_token})
        response.set_cookie(key="refresh_token", value=new_refresh_token, httponly=True, secure=True)
        logger.info("Refresh token successfully rotated.")
        return response
    except HTTPException as e:
        logger.error(f"Invalid refresh token: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during token refresh: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server error")

@router.post('/api/register/', status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, user_service: UserService = Depends(get_user_service)):
    user = await user_service.create_user(user_data.email, user_data.password)
    if user is None:
        logger.warning(f"Attempted to register already existing user: {user_data.email}")
        raise HTTPException(status_code=400, detail="User already exists")
    logger.info(f"User {user_data.email} registered successfully.")
    return {"message": "User registered successfully", "user_id": str(user["_id"])}

@router.post('/api/update_password/', status_code=status.HTTP_200_OK)
async def update_password(
    user_data: UserUpdatePassword,
    current_user_id: str = Depends(get_current_user_id),
    user_service: UserService = Depends(get_user_service)
):
    user = await user_service.get_user_by_id(current_user_id)
    if not user:
        logger.warning(f"Attempted password update for non-existing user ID: {current_user_id}")
        raise HTTPException(status_code=404, detail="User not found")

    if not user_service.validate_user_password(user, user_data.current_password):
        logger.warning(f"Incorrect current password for user ID: {current_user_id}")
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    updated = await user_service.update_user_password(current_user_id, user_data.new_password)
    if updated:
        logger.info(f"Password updated successfully for user ID: {current_user_id}")
        return {"message": "Password updated successfully"}
    else:
        logger.error(f"Failed to update password for user ID: {current_user_id}")
        raise HTTPException(status_code=500, detail="Failed to update password")
