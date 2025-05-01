# File Location: /tests/comprehensive/conftest.py
"""
Shared Fixtures for Comprehensive Test Suite
---------------------------------------------
This file provides shared pytest fixtures for authentication, user and admin
setup, test data (courses, content), and API clients.
All tests in /tests/comprehensive/ can use these.
"""
import pytest

# Example user credentials for testing
@pytest.fixture(scope="module")
def student_user():
    return {
        "user_id": "test_student",
        "email": "student@example.com",
        "password": "student_pw",
        "role": "student"
    }

@pytest.fixture(scope="module")
def admin_user():
    return {
        "user_id": "test_admin",
        "email": "admin@example.com",
        "password": "admin_pw",
        "role": "admin"
    }

# Example: Auth client factory (simulate login/auth)
@pytest.fixture
def auth_client():
    from app.core.auth.authentication import authenticate_user
    def _auth_client(user):
        # Simulate authentication, returns session/token or raises
        # Create a mock session based on your authentication logic
        return authenticate_user(user['user_id'], user['password'])
    return _auth_client

# Add more fixtures: e.g. course setup, API client, event bus, clean DB/session, etc.