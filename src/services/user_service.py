from datetime import timedelta
from fastapi.responses import JSONResponse

from src.repository.user_repository import UserRepository
from src.services.hashing_service import PasswordHasher
from src.services.token_service import TokenService
from src.configs.config import Config 
from src.logger_setup import setup_logger

logger = setup_logger(__name__)

class UserService:
    _instance = None

    def __new__(cls, db):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self, db):
        if getattr(self, '__initialized', False):
            return
        self.__initialized = True
        self.db = db
        self.user_repository = UserRepository(db)
        self.token_service = TokenService(db)

    def login(self, email, password):
        """Authenticate user and generate access/refresh tokens."""
        user = self._authenticate_user(email, password)
        if not user:
            return JSONResponse(
                {'message': 'Invalid credentials'}, 
                status_code=401
            )
        
        return self._create_login_response(user)

    def _authenticate_user(self, email, password):
        """Verify user credentials and return user if valid."""
        user = self.user_repository.get_user_by_email(email)
        if user and PasswordHasher.check_password(user['password'], password):
            return user
        return None

    def _create_login_response(self, user):
        """Create response with tokens after successful authentication."""
        tokens = self._generate_tokens(str(user['_id']))
        
        response = JSONResponse({
            "message": "Login successful",
            "access_token": tokens['access_token']
        }, status_code=200)
        
        self._set_refresh_token_cookie(response, tokens['refresh_token'])
        return response

    def _generate_tokens(self, user_id):
        """Generate access and refresh tokens."""
        access_token_expires = timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=Config.REFRESH_TOKEN_EXPIRE_DAYS)
        
        return {
            'access_token': self.token_service.create_access_token(
                user_id, 
                expires_delta=access_token_expires
            ),
            'refresh_token': self.token_service.create_refresh_token(
                user_id, 
                expires_delta=refresh_token_expires
            ),
            'refresh_token_expires': refresh_token_expires
        }

    def _set_refresh_token_cookie(self, response, refresh_token):
        """Set refresh token in HTTP-only cookie."""
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite='lax',
            max_age=Config.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )

    def create_user(self, email, password):
        hashed_password = PasswordHasher.hash_password(password)
        user = self.user_repository.create_user(email, hashed_password)
        if user is None:
            # User already exists or error occurred
            return None
        return user
    
    def get_user_by_id(self, user_id):
        return self.user_repository.get_user_by_id(user_id)

    def validate_user_password(self, user, password):
        return PasswordHasher.check_password(user['password'], password)

    def update_user_password(self, user_id, new_password):
        hashed_password = PasswordHasher.hash_password(new_password)
        return self.user_repository.update_password(user_id, hashed_password)
