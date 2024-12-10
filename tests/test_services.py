import json
import pytest
from unittest.mock import MagicMock, AsyncMock

from src.services.hashing_service import PasswordHasher
from src.services.user_service import UserService

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def user_service(mock_db):
    user_repo_mock = AsyncMock()
    user_repo_mock.get_user_by_email.return_value = {
        "_id": "dummy_id",
        "email": "test@example.com",
        "password": PasswordHasher.hash_password("TestPass123")
    }
    user_repo_mock.create_user.return_value = {
        "_id": "new_user_id",
        "email": "new@example.com",
        "password": "hashed_pass"
    }

    service = UserService(mock_db)
    service.user_repository = user_repo_mock
    return service

@pytest.mark.asyncio
async def test_create_user(user_service):
    result = await user_service.create_user("new@example.com", "SomePass123")
    assert result is not None
    assert result["email"] == "new@example.com"

@pytest.mark.asyncio
async def test_login_valid_credentials(user_service):
    response = await user_service.login("test@example.com", "TestPass123")
    assert response.status_code == 200
    data = json.loads(response.body.decode("utf-8"))
    assert "access_token" in data

@pytest.mark.asyncio
async def test_login_invalid_credentials(user_service):
    response = await user_service.login("test@example.com", "WrongPass")
    assert response.status_code == 401
    data = json.loads(response.body.decode("utf-8"))
    assert data["message"] == "Invalid credentials"
