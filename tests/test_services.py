import json

import pytest
from unittest.mock import MagicMock

from src.services.hashing_service import PasswordHasher
from src.services.user_service import UserService

# from services.user_service import UserService
# from services.hashing_service import PasswordHasher


@pytest.fixture
def mock_db():
    # You can return a mock or a fixture that your repositories can use
    return MagicMock()

@pytest.fixture
def user_service(mock_db):
    # Mock repositories within the service
    user_repo_mock = MagicMock()
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

    # Mock the user repository in the user service
    orig_user_repo = UserService.__dict__.get('user_repository', None)
    service = UserService(mock_db)
    service.user_repository = user_repo_mock
    return service

def test_create_user(user_service):
    result = user_service.create_user("new@example.com", "SomePass123")
    assert result is not None
    assert result["email"] == "new@example.com"

def test_login_valid_credentials(user_service):
    response = user_service.login("test@example.com", "TestPass123")
    assert response.status_code == 200
    data = json.loads(response.body.decode("utf-8"))
    assert "access_token" in data

def test_login_invalid_credentials(user_service):
    response = user_service.login("test@example.com", "WrongPass")
    assert response.status_code == 401
    data = json.loads(response.body.decode("utf-8"))
    assert data["message"] == "Invalid credentials"
