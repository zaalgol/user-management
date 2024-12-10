import uuid
from jose import jwt
from datetime import UTC, datetime, timedelta
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordBearer
from starlette.status import HTTP_401_UNAUTHORIZED

from src.configs.config import Config
from src.repository.token_repository import TokenRepository
from src.logger_setup import setup_logger

logger = setup_logger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)

class TokenService:
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
        self.token_repository = TokenRepository(db)

    def create_access_token(self, user_id: str, expires_delta: timedelta = None):
        to_encode = {"sub": user_id, "type": "access"}
        expire = datetime.now(UTC) + (expires_delta or timedelta(minutes=Config.ACCESS_TOKEN_EXPIRE_MINUTES))
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, Config.ACCESS_TOKEN_SECRET_KEY, algorithm=Config.ALGORITHM)
        return encoded_jwt

    def create_refresh_token(self, user_id: str, expires_delta: timedelta = None):
        token_id = str(uuid.uuid4())
        to_encode = {"sub": user_id, "type": "refresh", "jti": token_id}
        expire = datetime.now(UTC) + (expires_delta or timedelta(days=Config.REFRESH_TOKEN_EXPIRE_DAYS))

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, Config.REFRESH_TOKEN_SECRET_KEY, algorithm=Config.ALGORITHM)

        try:
            self.token_repository.save_refresh_token(token_id, user_id, expire)
        except Exception as e:
            logger.error(f"Error saving refresh token for user {user_id}: {e}")
            raise HTTPException(status_code=500, detail="Internal server error")

        return encoded_jwt

    def decode_token(self, token: str, expected_type: str):
        try:
            if expected_type == "access":
                secret_key = Config.ACCESS_TOKEN_SECRET_KEY
            elif expected_type == "refresh":
                secret_key = Config.REFRESH_TOKEN_SECRET_KEY
            else:
                raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid token type")

            payload = jwt.decode(token, secret_key, algorithms=[Config.ALGORITHM])
            user_id: str = payload.get("sub")
            token_type: str = payload.get("type")
            if user_id is None or token_type != expected_type:
                raise HTTPException(
                    status_code=HTTP_401_UNAUTHORIZED,
                    detail="Could not validate credentials",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return payload
        except Exception as e:
            logger.error(f"Token decoding error: {e}")
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    def refresh_access_token(self, refresh_token: str):
        payload = self.decode_token(refresh_token, expected_type="refresh")
        token_id = payload.get("jti")
        user_id = payload.get("sub")
        if not token_id or not user_id:
            logger.warning("Refresh token payload missing jti or sub.")
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        token_record = self.token_repository.get_refresh_token(token_id)
        if not token_record or token_record['user_id'] != user_id:
            logger.warning("Refresh token not found or does not match user.")
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

        # Token rotation
        self.token_repository.delete_refresh_token(token_id)

        new_refresh_token = self.create_refresh_token(user_id)
        access_token = self.create_access_token(user_id)
        return access_token, new_refresh_token

    async def extract_user_id_from_token(self, token: str, expected_type: str = "access"):
        if not token:
            logger.warning("No token provided for user extraction.")
            raise HTTPException(
                status_code=HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
        payload = self.decode_token(token, expected_type=expected_type)
        return payload.get("sub")
