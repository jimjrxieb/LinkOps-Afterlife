import pytest
import os
import tempfile
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from io import BytesIO

def test_file_validation_photo_valid():
    """Test valid photo file validation."""
    from utils import FileValidator
    
    # Create mock photo file
    mock_file = MagicMock()
    mock_file.filename = "test.jpg"
    mock_file.content_type = "image/jpeg"
    mock_file.size = 1024 * 1024  # 1MB
    
    valid, message = FileValidator.validate_photo(mock_file)
    assert valid is True
    assert "validation passed" in message.lower()

def test_file_validation_photo_invalid_type():
    """Test invalid photo file type validation."""
    from utils import FileValidator
    
    mock_file = MagicMock()
    mock_file.filename = "test.gif"
    mock_file.content_type = "image/gif"
    mock_file.size = 1024 * 1024
    
    valid, message = FileValidator.validate_photo(mock_file)
    assert valid is False
    assert "Invalid photo file type" in message

def test_file_validation_photo_too_large():
    """Test photo file too large validation."""
    from utils import FileValidator
    
    mock_file = MagicMock()
    mock_file.filename = "test.jpg"
    mock_file.content_type = "image/jpeg"
    mock_file.size = 10 * 1024 * 1024  # 10MB - too large
    
    valid, message = FileValidator.validate_photo(mock_file)
    assert valid is False
    assert "too large" in message

def test_file_validation_audio_valid():
    """Test valid audio file validation."""
    from utils import FileValidator
    
    mock_file = MagicMock()
    mock_file.filename = "test.wav"
    mock_file.content_type = "audio/wav"
    mock_file.size = 1024 * 1024  # 1MB
    
    valid, message = FileValidator.validate_audio(mock_file)
    assert valid is True
    assert "validation passed" in message.lower()

def test_file_validation_audio_invalid_type():
    """Test invalid audio file type validation."""
    from utils import FileValidator
    
    mock_file = MagicMock()
    mock_file.filename = "test.flac"
    mock_file.content_type = "audio/flac"
    mock_file.size = 1024 * 1024
    
    valid, message = FileValidator.validate_audio(mock_file)
    assert valid is False
    assert "Invalid audio file type" in message

def test_file_validation_text_valid():
    """Test valid text file validation."""
    from utils import FileValidator
    
    mock_file = MagicMock()
    mock_file.filename = "test.txt"
    mock_file.content_type = "text/plain"
    mock_file.size = 1024  # 1KB
    
    valid, message = FileValidator.validate_text(mock_file)
    assert valid is True
    assert "validation passed" in message.lower()

def test_file_validation_all_files_valid():
    """Test validation of all files together."""
    from utils import FileValidator
    
    # Mock valid files
    photo = MagicMock()
    photo.filename = "test.jpg"
    photo.content_type = "image/jpeg"
    photo.size = 1024 * 1024
    
    audio = MagicMock()
    audio.filename = "test.wav"
    audio.content_type = "audio/wav"
    audio.size = 1024 * 1024
    
    text = MagicMock()
    text.filename = "test.txt"
    text.content_type = "text/plain"
    text.size = 1024
    
    valid, errors = FileValidator.validate_all_files(photo, audio, text)
    assert valid is True
    assert len(errors) == 0

def test_file_validation_all_files_invalid():
    """Test validation with some invalid files."""
    from utils import FileValidator
    
    # Mock files with issues
    photo = MagicMock()
    photo.filename = "test.gif"  # Invalid type
    photo.content_type = "image/gif"
    photo.size = 1024 * 1024
    
    audio = MagicMock()
    audio.filename = "test.wav"
    audio.content_type = "audio/wav"
    audio.size = 10 * 1024 * 1024  # Too large
    
    text = MagicMock()
    text.filename = "test.txt"
    text.content_type = "text/plain"
    text.size = 1024
    
    valid, errors = FileValidator.validate_all_files(photo, audio, text)
    assert valid is False
    assert len(errors) == 2  # Photo type + audio size errors

def test_file_encryption_key_generation(temp_session_dir):
    """Test encryption key generation."""
    from utils import FileEncryption
    
    key_path = FileEncryption.generate_encryption_key(temp_session_dir)
    
    assert os.path.exists(key_path)
    assert key_path.endswith("encryption_key.key")
    
    # Verify key file has content
    with open(key_path, "rb") as f:
        key_data = f.read()
        assert len(key_data) > 0

def test_file_encryption_decrypt_cycle(temp_session_dir):
    """Test file encryption and decryption cycle."""
    from utils import FileEncryption
    
    # Create a test file
    test_file_path = os.path.join(temp_session_dir, "test_file.txt")
    test_content = "This is a test file for encryption."
    with open(test_file_path, "w") as f:
        f.write(test_content)
    
    # Generate encryption key
    key_path = FileEncryption.generate_encryption_key(temp_session_dir)
    
    # Encrypt file
    encrypted_path = FileEncryption.encrypt_file(test_file_path, key_path)
    
    assert os.path.exists(encrypted_path)
    assert encrypted_path.endswith(".enc")
    assert not os.path.exists(test_file_path)  # Original should be deleted
    
    # Decrypt file
    decrypted_path = FileEncryption.decrypt_file(encrypted_path, key_path)
    
    assert os.path.exists(decrypted_path)
    
    # Verify content matches
    with open(decrypted_path, "r") as f:
        decrypted_content = f.read()
        assert decrypted_content == test_content

def test_file_encryption_session_files(temp_session_dir):
    """Test encrypting all files in a session directory."""
    from utils import FileEncryption
    
    # Create multiple test files
    files = ["photo.jpg", "audio.wav", "text.txt"]
    for filename in files:
        file_path = os.path.join(temp_session_dir, filename)
        with open(file_path, "w") as f:
            f.write(f"Content of {filename}")
    
    # Encrypt all session files
    encrypted_files = FileEncryption.encrypt_session_files(temp_session_dir)
    
    assert len(encrypted_files) == len(files)
    
    # Verify all files are encrypted
    for filename in files:
        original_path = os.path.join(temp_session_dir, filename)
        encrypted_path = original_path + ".enc"
        
        assert not os.path.exists(original_path)  # Original deleted
        assert os.path.exists(encrypted_path)  # Encrypted exists
        assert filename in encrypted_files

def test_secure_filename_generation():
    """Test secure filename generation."""
    from utils import generate_secure_filename
    
    # Test with normal filename
    filename = generate_secure_filename("my file.txt", "photo")
    assert filename.startswith("photo_")
    assert filename.endswith(".txt")
    assert "my_file" in filename or "my-file" in filename
    
    # Test without prefix
    filename = generate_secure_filename("test.jpg")
    assert not filename.startswith("photo_")
    assert filename.endswith(".jpg")

def test_upload_endpoint_success(client, auth_headers, sample_files):
    """Test successful file upload endpoint."""
    # Create file-like objects for upload
    with open(sample_files["photo"], "rb") as photo_file:
        with open(sample_files["audio"], "rb") as audio_file:
            with open(sample_files["text"], "rb") as text_file:
                
                files = {
                    "photo": ("test_photo.jpg", photo_file, "image/jpeg"),
                    "audio": ("test_audio.wav", audio_file, "audio/wav"),
                    "text": ("test_text.txt", text_file, "text/plain")
                }
                
                with patch("utils.FileValidator.validate_all_files") as mock_validate:
                    mock_validate.return_value = (True, [])
                    with patch("utils.FileEncryption.encrypt_session_files") as mock_encrypt:
                        mock_encrypt.return_value = {"test": "encrypted"}
                        with patch("auth.AuthManager.create_user_session") as mock_session:
                            mock_session.return_value = True
                            
                            response = client.post("/upload", files=files, headers=auth_headers)
                            assert response.status_code == 200
                            
                            data = response.json()
                            assert data["message"] == "Files uploaded and secured successfully"
                            assert "session_id" in data
                            assert data["security"]["files_encrypted"] is True

def test_upload_endpoint_validation_failure(client, auth_headers, sample_files):
    """Test upload endpoint with validation failure."""
    with open(sample_files["photo"], "rb") as photo_file:
        with open(sample_files["audio"], "rb") as audio_file:
            with open(sample_files["text"], "rb") as text_file:
                
                files = {
                    "photo": ("test_photo.jpg", photo_file, "image/jpeg"),
                    "audio": ("test_audio.wav", audio_file, "audio/wav"),
                    "text": ("test_text.txt", text_file, "text/plain")
                }
                
                with patch("utils.FileValidator.validate_all_files") as mock_validate:
                    mock_validate.return_value = (False, ["Invalid file type"])
                    
                    response = client.post("/upload", files=files, headers=auth_headers)
                    assert response.status_code == 400
                    assert "File validation failed" in response.json()["detail"]

def test_upload_endpoint_encryption_failure(client, auth_headers, sample_files):
    """Test upload endpoint with encryption failure."""
    with open(sample_files["photo"], "rb") as photo_file:
        with open(sample_files["audio"], "rb") as audio_file:
            with open(sample_files["text"], "rb") as text_file:
                
                files = {
                    "photo": ("test_photo.jpg", photo_file, "image/jpeg"),
                    "audio": ("test_audio.wav", audio_file, "audio/wav"),
                    "text": ("test_text.txt", text_file, "text/plain")
                }
                
                with patch("utils.FileValidator.validate_all_files") as mock_validate:
                    mock_validate.return_value = (True, [])
                    with patch("utils.FileEncryption.encrypt_session_files") as mock_encrypt:
                        mock_encrypt.side_effect = Exception("Encryption failed")
                        with patch("utils.SessionManager.delete_session_data") as mock_delete:
                            mock_delete.return_value = True
                            
                            response = client.post("/upload", files=files, headers=auth_headers)
                            assert response.status_code == 500
                            assert "File encryption failed" in response.json()["detail"]

def test_upload_endpoint_unauthorized(client, sample_files):
    """Test upload endpoint without authentication."""
    with open(sample_files["photo"], "rb") as photo_file:
        with open(sample_files["audio"], "rb") as audio_file:
            with open(sample_files["text"], "rb") as text_file:
                
                files = {
                    "photo": ("test_photo.jpg", photo_file, "image/jpeg"),
                    "audio": ("test_audio.wav", audio_file, "audio/wav"),
                    "text": ("test_text.txt", text_file, "text/plain")
                }
                
                response = client.post("/upload", files=files)
                assert response.status_code == 403  # No auth header

def test_save_upload_file(temp_session_dir):
    """Test saving upload file utility."""
    from utils import save_upload_file
    from fastapi import UploadFile
    
    # Create mock upload file
    test_content = b"Test file content"
    upload_file = UploadFile(filename="test.txt", file=BytesIO(test_content))
    
    destination = os.path.join(temp_session_dir, "saved_file.txt")
    
    result = save_upload_file(upload_file, destination)
    
    assert result == destination
    assert os.path.exists(destination)
    
    # Verify content
    with open(destination, "rb") as f:
        saved_content = f.read()
        assert saved_content == test_content

def test_session_manager_create_metadata(temp_session_dir):
    """Test session metadata creation."""
    from utils import SessionManager
    
    user_id = 1
    session_id = "test_session_789"
    upload_data = {
        "files": {
            "photo": {"filename": "test.jpg", "size": 1024},
            "audio": {"filename": "test.wav", "size": 2048},
            "text": {"filename": "test.txt", "size": 512}
        }
    }
    
    metadata_path = SessionManager.create_session_metadata(
        temp_session_dir, user_id, session_id, upload_data
    )
    
    assert os.path.exists(metadata_path)
    assert metadata_path.endswith("session_metadata.json")
    
    # Verify metadata content
    import json
    with open(metadata_path, "r") as f:
        metadata = json.load(f)
        
        assert metadata["session_id"] == session_id
        assert metadata["user_id"] == user_id
        assert metadata["upload_data"] == upload_data
        assert "processing_status" in metadata
        assert "security" in metadata

def test_session_manager_update_metadata(temp_session_dir):
    """Test session metadata updates."""
    from utils import SessionManager
    import json
    
    # Create initial metadata
    metadata_path = os.path.join(temp_session_dir, "session_metadata.json")
    initial_data = {"session_id": "test", "status": "initial"}
    with open(metadata_path, "w") as f:
        json.dump(initial_data, f)
    
    # Update metadata
    updates = {
        "processing_status": {"photo_processed": True},
        "new_field": "new_value"
    }
    
    success = SessionManager.update_session_metadata(temp_session_dir, updates)
    assert success is True
    
    # Verify updates
    with open(metadata_path, "r") as f:
        updated_data = json.load(f)
        
        assert updated_data["session_id"] == "test"  # Original preserved
        assert updated_data["processing_status"]["photo_processed"] is True
        assert updated_data["new_field"] == "new_value"
        assert "last_updated" in updated_data