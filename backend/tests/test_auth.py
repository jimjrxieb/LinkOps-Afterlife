import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import jwt
from datetime import datetime

def test_register_success(client):
    """Test successful user registration."""
    user_data = {
        "username": "newuser",
        "password": "password123",
        "email": "newuser@example.com"
    }
    
    response = client.post("/register", json=user_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["message"] == "User registered successfully"
    assert data["user"]["username"] == user_data["username"]
    assert data["user"]["email"] == user_data["email"]
    assert "id" in data["user"]

def test_register_duplicate_username(client, test_user):
    """Test registration with duplicate username."""
    user_data = {
        "username": test_user["username"],
        "password": "password123",
        "email": "different@example.com"
    }
    
    response = client.post("/register", json=user_data)
    assert response.status_code == 400
    assert "Username already exists" in response.json()["detail"]

def test_register_weak_password(client):
    """Test registration with weak password."""
    user_data = {
        "username": "testuser",
        "password": "weak",  # Too short
        "email": "test@example.com"
    }
    
    response = client.post("/register", json=user_data)
    assert response.status_code == 400
    assert "Password must be at least 8 characters" in response.json()["detail"]

def test_register_missing_fields(client):
    """Test registration with missing required fields."""
    # Missing password
    response = client.post("/register", json={"username": "testuser"})
    assert response.status_code == 400
    assert "Username and password are required" in response.json()["detail"]
    
    # Missing username
    response = client.post("/register", json={"password": "password123"})
    assert response.status_code == 400
    assert "Username and password are required" in response.json()["detail"]

def test_login_success(client, test_user):
    """Test successful login."""
    login_data = {
        "username": test_user["username"],
        "password": test_user["password"]
    }
    
    response = client.post("/login", json=login_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["message"] == "Login successful"
    assert data["token_type"] == "bearer"
    assert "access_token" in data
    assert data["user"]["username"] == test_user["username"]
    
    # Verify JWT token is valid
    token = data["access_token"]
    decoded = jwt.decode(token, "test_secret_key_for_jwt_signing", algorithms=["HS256"])
    assert decoded["username"] == test_user["username"]

def test_login_invalid_credentials(client, test_user):
    """Test login with invalid credentials."""
    # Wrong password
    response = client.post("/login", json={
        "username": test_user["username"],
        "password": "wrongpassword"
    })
    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]
    
    # Wrong username
    response = client.post("/login", json={
        "username": "wronguser",
        "password": test_user["password"]
    })
    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]

def test_login_missing_fields(client):
    """Test login with missing fields."""
    # Missing password
    response = client.post("/login", json={"username": "testuser"})
    assert response.status_code == 400
    assert "Username and password are required" in response.json()["detail"]
    
    # Missing username
    response = client.post("/login", json={"password": "password123"})
    assert response.status_code == 400
    assert "Username and password are required" in response.json()["detail"]

def test_protected_endpoint_with_valid_token(client, auth_headers, temp_session_dir):
    """Test accessing protected endpoint with valid JWT token."""
    session_id = "test_session_123"
    
    # Mock session directory exists
    with patch("os.path.exists") as mock_exists:
        mock_exists.return_value = True
        with patch("utils.SessionManager.get_session_info") as mock_session:
            mock_session.return_value = {"user_id": 1, "session_id": session_id}
            
            response = client.get(f"/session/{session_id}", headers=auth_headers)
            assert response.status_code == 200

def test_protected_endpoint_without_token(client):
    """Test accessing protected endpoint without JWT token."""
    response = client.post("/consent/test_session", json={"terms_agreed": True})
    assert response.status_code == 403  # No Authorization header

def test_protected_endpoint_with_invalid_token(client):
    """Test accessing protected endpoint with invalid JWT token."""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.post("/consent/test_session", json={"terms_agreed": True}, headers=headers)
    assert response.status_code == 401
    assert "Invalid authentication credentials" in response.json()["detail"]

def test_consent_submission_success(client, auth_headers, test_user):
    """Test successful consent submission."""
    session_id = "test_session_123"
    consent_data = {
        "terms_agreed": True,
        "data_processing_agreed": True,
        "emotional_impact_acknowledged": True,
        "user_agent": "test-agent",
        "ip_address": "127.0.0.1"
    }
    
    with patch("auth.AuthManager.store_consent") as mock_store:
        mock_store.return_value = True
        with patch("utils.SessionManager.update_session_metadata") as mock_update:
            mock_update.return_value = True
            with patch("os.path.exists") as mock_exists:
                mock_exists.return_value = True
                
                response = client.post(f"/consent/{session_id}", json=consent_data, headers=auth_headers)
                assert response.status_code == 200
                
                data = response.json()
                assert data["message"] == "Consent recorded successfully"
                assert data["session_id"] == session_id

def test_consent_submission_missing_required(client, auth_headers):
    """Test consent submission with missing required consents."""
    session_id = "test_session_123"
    consent_data = {
        "terms_agreed": True,
        "data_processing_agreed": False,  # Missing required consent
        "emotional_impact_acknowledged": True
    }
    
    response = client.post(f"/consent/{session_id}", json=consent_data, headers=auth_headers)
    assert response.status_code == 400
    assert "Consent required" in response.json()["detail"]

def test_session_deletion_success(client, auth_headers, test_user):
    """Test successful session deletion."""
    session_id = "test_session_123"
    
    with patch("utils.SessionManager.get_session_info") as mock_session:
        mock_session.return_value = {"user_id": test_user["id"], "session_id": session_id}
        with patch("utils.SessionManager.delete_session_data") as mock_delete:
            mock_delete.return_value = True
            
            response = client.delete(f"/delete_session/{session_id}", headers=auth_headers)
            assert response.status_code == 200
            
            data = response.json()
            assert data["message"] == "Session data deleted successfully"
            assert data["session_id"] == session_id

def test_session_deletion_unauthorized(client, auth_headers, test_user):
    """Test session deletion by unauthorized user."""
    session_id = "test_session_123"
    
    with patch("utils.SessionManager.get_session_info") as mock_session:
        # Session belongs to different user
        mock_session.return_value = {"user_id": 999, "session_id": session_id}
        
        response = client.delete(f"/delete_session/{session_id}", headers=auth_headers)
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]

def test_jwt_token_expiry():
    """Test JWT token expiry handling."""
    from auth import AuthManager
    import time
    
    auth_manager = AuthManager()
    
    # Create token with very short expiry
    user_data = {"id": 1, "username": "test"}
    with patch("auth.timedelta") as mock_timedelta:
        mock_timedelta.return_value.total_seconds.return_value = -1  # Expired
        token = auth_manager.create_access_token(user_data)
        
        # Verify token is invalid due to expiry
        decoded = auth_manager.verify_token(token)
        assert decoded is None

def test_password_hashing():
    """Test password hashing functionality."""
    from auth import AuthManager
    
    auth_manager = AuthManager()
    password = "testpassword123"
    
    # Hash password
    hashed = auth_manager.hash_password(password)
    assert hashed != password
    assert len(hashed) > 20  # Bcrypt hash is long
    
    # Verify password
    assert auth_manager.verify_password(password, hashed) is True
    assert auth_manager.verify_password("wrongpassword", hashed) is False

def test_user_session_management(auth_manager, test_user):
    """Test user session creation and management."""
    session_id = "test_session_456"
    
    # Create user session
    success = auth_manager.create_user_session(test_user["id"], session_id)
    assert success is True
    
    # Check usage limits (should be allowed initially)
    limits = auth_manager.check_usage_limits(test_user["id"], session_id)
    assert limits["allowed"] is True
    assert limits["remaining"] > 0
    
    # Increment usage
    success = auth_manager.increment_usage(test_user["id"], session_id)
    assert success is True
    
    # Check limits after increment
    limits = auth_manager.check_usage_limits(test_user["id"], session_id)
    assert limits["used"] >= 1