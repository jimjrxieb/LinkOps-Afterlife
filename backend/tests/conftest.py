import pytest
import os
import tempfile
import shutil
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
import jwt
from datetime import datetime, timedelta

# Import the app and auth manager
from main import app
from auth import AuthManager

@pytest.fixture(scope="session")
def test_db():
    """Create a temporary test database."""
    temp_dir = tempfile.mkdtemp()
    test_db_path = os.path.join(temp_dir, "test_users.db")
    
    # Set up test database
    with patch.dict(os.environ, {"DATABASE_PATH": test_db_path}):
        auth_manager = AuthManager(db_path=test_db_path)
        auth_manager.init_db()
        yield test_db_path
    
    # Cleanup
    shutil.rmtree(temp_dir)

@pytest.fixture
def client(test_db):
    """Create a test client with test database."""
    with patch("auth.AuthManager") as mock_auth:
        mock_auth.return_value.db_path = test_db
        with TestClient(app) as test_client:
            yield test_client

@pytest.fixture
def auth_manager(test_db):
    """Create auth manager with test database."""
    return AuthManager(db_path=test_db)

@pytest.fixture
def test_user(auth_manager):
    """Create a test user."""
    user_data = {
        "username": "testuser",
        "password": "testpass123",
        "email": "test@example.com"
    }
    user = auth_manager.create_user(
        user_data["username"], 
        user_data["password"], 
        user_data["email"]
    )
    return {**user, "password": user_data["password"]}

@pytest.fixture
def auth_token(auth_manager, test_user):
    """Create JWT token for test user."""
    token = auth_manager.create_access_token({
        "id": test_user["id"],
        "username": test_user["username"],
        "email": test_user["email"]
    })
    return token

@pytest.fixture
def auth_headers(auth_token):
    """Create authorization headers."""
    return {"Authorization": f"Bearer {auth_token}"}

@pytest.fixture
def temp_session_dir():
    """Create temporary session directory."""
    temp_dir = tempfile.mkdtemp()
    session_id = "test_session_123"
    session_dir = os.path.join(temp_dir, session_id)
    os.makedirs(session_dir, exist_ok=True)
    
    yield session_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)

@pytest.fixture
def mock_d_id_api():
    """Mock D-ID API responses."""
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "mock_video_id",
            "status": "created",
            "result_url": "https://mock-url.com/video.mp4"
        }
        mock_post.return_value = mock_response
        yield mock_post

@pytest.fixture
def mock_elevenlabs_api():
    """Mock ElevenLabs API responses."""
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b"mock_audio_data"
        mock_response.json.return_value = {
            "voice_id": "mock_voice_id",
            "name": "Test Voice"
        }
        mock_post.return_value = mock_response
        yield mock_post

@pytest.fixture
def sample_files():
    """Create sample test files."""
    temp_dir = tempfile.mkdtemp()
    
    # Sample photo (small valid image)
    photo_path = os.path.join(temp_dir, "test_photo.jpg")
    with open(photo_path, "wb") as f:
        f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF')  # Minimal JPEG header
    
    # Sample audio (small valid file)
    audio_path = os.path.join(temp_dir, "test_audio.wav")
    with open(audio_path, "wb") as f:
        f.write(b'RIFF\x24\x00\x00\x00WAVE')  # Minimal WAV header
    
    # Sample text
    text_path = os.path.join(temp_dir, "test_text.txt")
    with open(text_path, "w") as f:
        f.write("Hello, this is a test text file with personality data.")
    
    yield {
        "photo": photo_path,
        "audio": audio_path, 
        "text": text_path
    }
    
    # Cleanup
    shutil.rmtree(temp_dir)

@pytest.fixture(autouse=True)
def mock_env_vars():
    """Mock environment variables for testing."""
    env_vars = {
        "D_ID_API_KEY": "test_d_id_key",
        "ELEVENLABS_API_KEY": "test_elevenlabs_key",
        "SECRET_KEY": "test_secret_key_for_jwt_signing"
    }
    with patch.dict(os.environ, env_vars):
        yield env_vars