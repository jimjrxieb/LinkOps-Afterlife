"""
Full pipeline integration tests for LinkOps-Afterlife.
Tests the complete user journey from registration to interaction and deletion.
"""

import pytest
import os
import tempfile
import json
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import time

def test_complete_user_journey_success(client, test_db, mock_d_id_api, mock_elevenlabs_api, sample_files):
    """Test the complete user journey from registration to deletion."""
    
    # Step 1: User Registration
    user_data = {
        "username": f"integration_user_{int(time.time())}",
        "password": "securepass123",
        "email": "integration@test.com"
    }
    
    response = client.post("/register", json=user_data)
    assert response.status_code == 201
    
    # Step 2: User Login
    login_response = client.post("/login", json={
        "username": user_data["username"],
        "password": user_data["password"]
    })
    assert login_response.status_code == 200
    
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    user_id = login_response.json()["user"]["id"]
    
    # Step 3: File Upload with Security Validation
    with patch("utils.FileValidator.validate_all_files") as mock_validate:
        mock_validate.return_value = (True, [])
        
        with patch("utils.FileEncryption.encrypt_session_files") as mock_encrypt:
            mock_encrypt.return_value = {"photo": "encrypted", "audio": "encrypted", "text": "encrypted"}
            
            with patch("auth.AuthManager.create_user_session") as mock_session:
                mock_session.return_value = True
                
                # Create file-like objects for upload
                with open(sample_files["photo"], "rb") as photo_file:
                    with open(sample_files["audio"], "rb") as audio_file:
                        with open(sample_files["text"], "rb") as text_file:
                            
                            files = {
                                "photo": ("test_photo.jpg", photo_file, "image/jpeg"),
                                "audio": ("test_audio.wav", audio_file, "audio/wav"),
                                "text": ("test_text.txt", text_file, "text/plain")
                            }
                            
                            upload_response = client.post("/upload", files=files, headers=headers)
                            assert upload_response.status_code == 200
                            
                            session_id = upload_response.json()["session_id"]
                            assert upload_response.json()["security"]["files_encrypted"] is True
    
    # Step 4: Consent Submission
    consent_data = {
        "terms_agreed": True,
        "data_processing_agreed": True,
        "emotional_impact_acknowledged": True,
        "user_agent": "test-agent",
        "ip_address": "127.0.0.1"
    }
    
    with patch("auth.AuthManager.store_consent") as mock_store_consent:
        mock_store_consent.return_value = True
        with patch("utils.SessionManager.update_session_metadata") as mock_update:
            mock_update.return_value = True
            with patch("os.path.exists") as mock_exists:
                mock_exists.return_value = True
                
                consent_response = client.post(f"/consent/{session_id}", json=consent_data, headers=headers)
                assert consent_response.status_code == 200
    
    # Step 5: Photo Preprocessing
    with patch("preprocess.preprocess_photo") as mock_preprocess:
        mock_preprocess.return_value = f"/mock/session/{session_id}/preprocessed_photo.jpg"
        with patch("preprocess.get_image_info") as mock_image_info:
            mock_image_info.return_value = {"width": 512, "height": 512, "format": "JPEG"}
            with patch("os.listdir") as mock_listdir:
                mock_listdir.return_value = ["photo_test.jpg"]
                with patch("os.path.exists") as mock_exists:
                    mock_exists.return_value = True
                    
                    preprocess_response = client.get(f"/preprocess_photo/{session_id}")
                    assert preprocess_response.status_code == 200
    
    # Step 6: Voice Cloning
    with patch("voice.clone_voice") as mock_clone:
        mock_clone.return_value = {
            "voice_id": "integration_voice_id",
            "metadata": {"name": "Integration Voice", "category": "generated"},
            "metadata_path": f"/mock/session/{session_id}/voice_metadata.json"
        }
        with patch("voice.validate_elevenlabs_api_key") as mock_validate_key:
            mock_validate_key.return_value = True
            with patch("os.listdir") as mock_listdir:
                mock_listdir.return_value = ["audio_test.wav"]
                with patch("os.path.exists") as mock_exists:
                    mock_exists.return_value = True
                    
                    voice_response = client.post(f"/clone_voice/{session_id}")
                    assert voice_response.status_code == 200
                    assert voice_response.json()["voice_id"] == "integration_voice_id"
    
    # Step 7: Text Processing
    with patch("text_processor.process_text_data") as mock_process_text:
        processed_path = f"/mock/session/{session_id}/processed_text.json"
        mock_process_text.return_value = processed_path
        
        processed_data = {
            "content": {"sentence_count": 5},
            "analysis": {
                "sentiment_analysis": {"dominant_sentiment": "positive"},
                "personality_traits": {"dominant_trait": "extraversion"},
                "conversation_patterns": {"communication_style": "friendly"}
            }
        }
        
        with patch("builtins.open", MagicMock()) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = json.dumps(processed_data)
            with patch("os.listdir") as mock_listdir:
                mock_listdir.return_value = ["text_test.txt"]
                with patch("os.path.exists") as mock_exists:
                    mock_exists.return_value = True
                    
                    text_response = client.post(f"/process_text/{session_id}")
                    assert text_response.status_code == 200
                    assert text_response.json()["analysis_summary"]["dominant_sentiment"] == "positive"
    
    # Step 8: Conversation Model Fine-tuning
    with patch("conversation.fine_tune_conversation_model") as mock_fine_tune:
        model_data = {
            "model_id": "integration_model_123",
            "metadata": {
                "personality_profile": {"dominant_trait": "extraversion"},
                "training_data_summary": {"sentences": 100},
                "conversation_config": {"response_parameters": {"temperature": 0.7}}
            },
            "metadata_path": f"/mock/session/{session_id}/conversation_model.json"
        }
        mock_fine_tune.return_value = model_data
        
        with patch("os.path.exists") as mock_exists:
            mock_exists.return_value = True
            
            fine_tune_response = client.post(f"/fine_tune_conversation/{session_id}")
            assert fine_tune_response.status_code == 200
            assert fine_tune_response.json()["model_id"] == "integration_model_123"
    
    # Step 9: Full Interactive Response
    with patch("utils.SessionManager.get_session_info") as mock_session_info:
        mock_session_info.return_value = {"user_id": user_id, "session_id": session_id}
        
        with patch("auth.AuthManager.check_consent") as mock_check_consent:
            mock_check_consent.return_value = True
            
            with patch("auth.AuthManager.check_usage_limits") as mock_check_limits:
                mock_check_limits.return_value = {"allowed": True, "remaining": 9, "limit": 10, "used": 1}
                
                with patch("integration.validate_session_requirements") as mock_validate_req:
                    mock_validate_req.return_value = {"all_requirements_met": True}
                    
                    with patch("integration.generate_interactive_response") as mock_generate:
                        video_path = f"/mock/session/{session_id}/response_video.mp4"
                        mock_generate.return_value = video_path
                        
                        with patch("os.path.getsize") as mock_getsize:
                            mock_getsize.return_value = 1024 * 1024  # 1MB
                            
                            with patch("auth.AuthManager.increment_usage") as mock_increment:
                                mock_increment.return_value = True
                                
                                interaction_data = {"input": "Hello, how are you today?"}
                                interaction_response = client.post(
                                    f"/interact/{session_id}", 
                                    json=interaction_data, 
                                    headers=headers
                                )
                                
                                assert interaction_response.status_code == 200
                                response_data = interaction_response.json()
                                assert response_data["message"] == "Interactive response generated successfully"
                                assert response_data["user_input"] == "Hello, how are you today?"
                                assert "video_path" in response_data
                                assert "usage_info" in response_data
    
    # Step 10: Session Status Verification
    with patch("integration.validate_session_requirements") as mock_validate_status:
        mock_validate_status.return_value = {"all_requirements_met": True}
        with patch("integration.get_interaction_history") as mock_history:
            mock_history.return_value = [
                {
                    "timestamp": "2024-01-01T10:00:00",
                    "user_input": "Hello, how are you today?",
                    "response": "I'm doing well, thank you!",
                    "video_path": video_path
                }
            ]
            with patch("os.listdir") as mock_listdir:
                mock_listdir.return_value = ["photo.jpg", "audio.wav", "text.txt", "metadata.json"]
                with patch("os.path.isfile") as mock_isfile:
                    mock_isfile.return_value = True
                    with patch("os.stat") as mock_stat:
                        mock_stat.return_value.st_size = 1024
                        mock_stat.return_value.st_mtime = time.time()
                        
                        status_response = client.get(f"/session_status/{session_id}")
                        assert status_response.status_code == 200
                        
                        status_data = status_response.json()
                        assert status_data["ready_for_interaction"] is True
                        assert len(status_data["interaction_history"]) == 1
                        assert len(status_data["session_files"]) == 4
    
    # Step 11: Session Deletion (Data Privacy)
    with patch("utils.SessionManager.get_session_info") as mock_session_info:
        mock_session_info.return_value = {"user_id": user_id, "session_id": session_id}
        
        with patch("utils.SessionManager.delete_session_data") as mock_delete:
            mock_delete.return_value = True
            
            delete_response = client.delete(f"/delete_session/{session_id}", headers=headers)
            assert delete_response.status_code == 200
            
            delete_data = delete_response.json()
            assert delete_data["message"] == "Session data deleted successfully"
            assert delete_data["session_id"] == session_id


def test_pipeline_with_security_failures(client, test_db, sample_files):
    """Test pipeline behavior with various security failures."""
    
    # Create and login user
    user_data = {"username": f"security_test_{int(time.time())}", "password": "testpass123"}
    client.post("/register", json=user_data)
    
    login_response = client.post("/login", json=user_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: File validation failure
    with patch("utils.FileValidator.validate_all_files") as mock_validate:
        mock_validate.return_value = (False, ["Invalid file type", "File too large"])
        
        with open(sample_files["photo"], "rb") as photo_file:
            with open(sample_files["audio"], "rb") as audio_file:
                with open(sample_files["text"], "rb") as text_file:
                    
                    files = {
                        "photo": ("test.jpg", photo_file, "image/jpeg"),
                        "audio": ("test.wav", audio_file, "audio/wav"),
                        "text": ("test.txt", text_file, "text/plain")
                    }
                    
                    response = client.post("/upload", files=files, headers=headers)
                    assert response.status_code == 400
                    assert "File validation failed" in response.json()["detail"]
    
    # Test 2: Encryption failure during upload
    with patch("utils.FileValidator.validate_all_files") as mock_validate:
        mock_validate.return_value = (True, [])
        
        with patch("utils.FileEncryption.encrypt_session_files") as mock_encrypt:
            mock_encrypt.side_effect = Exception("Encryption failed")
            
            with patch("utils.SessionManager.delete_session_data") as mock_delete:
                mock_delete.return_value = True
                
                with open(sample_files["photo"], "rb") as photo_file:
                    with open(sample_files["audio"], "rb") as audio_file:
                        with open(sample_files["text"], "rb") as text_file:
                            
                            files = {
                                "photo": ("test.jpg", photo_file, "image/jpeg"),
                                "audio": ("test.wav", audio_file, "audio/wav"),
                                "text": ("test.txt", text_file, "text/plain")
                            }
                            
                            response = client.post("/upload", files=files, headers=headers)
                            assert response.status_code == 500
                            assert "File encryption failed" in response.json()["detail"]


def test_pipeline_with_consent_requirements(client, test_db, sample_files):
    """Test that consent requirements are properly enforced throughout pipeline."""
    
    # Create user and upload files
    user_data = {"username": f"consent_test_{int(time.time())}", "password": "testpass123"}
    client.post("/register", json=user_data)
    
    login_response = client.post("/login", json=user_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    user_id = login_response.json()["user"]["id"]
    
    # Upload files successfully
    with patch("utils.FileValidator.validate_all_files") as mock_validate:
        mock_validate.return_value = (True, [])
        with patch("utils.FileEncryption.encrypt_session_files") as mock_encrypt:
            mock_encrypt.return_value = {"encrypted": "files"}
            with patch("auth.AuthManager.create_user_session") as mock_session:
                mock_session.return_value = True
                
                with open(sample_files["photo"], "rb") as photo_file:
                    with open(sample_files["audio"], "rb") as audio_file:
                        with open(sample_files["text"], "rb") as text_file:
                            
                            files = {
                                "photo": ("test.jpg", photo_file, "image/jpeg"),
                                "audio": ("test.wav", audio_file, "audio/wav"),
                                "text": ("test.txt", text_file, "text/plain")
                            }
                            
                            upload_response = client.post("/upload", files=files, headers=headers)
                            session_id = upload_response.json()["session_id"]
    
    # Test interaction without consent - should fail
    with patch("utils.SessionManager.get_session_info") as mock_session_info:
        mock_session_info.return_value = {"user_id": user_id, "session_id": session_id}
        
        with patch("auth.AuthManager.check_consent") as mock_consent:
            mock_consent.return_value = False  # No consent given
            
            response = client.post(f"/interact/{session_id}", json={"input": "Hello"}, headers=headers)
            assert response.status_code == 403
            assert "Consent required" in response.json()["detail"]
    
    # Give consent
    consent_data = {
        "terms_agreed": True,
        "data_processing_agreed": True,
        "emotional_impact_acknowledged": True
    }
    
    with patch("auth.AuthManager.store_consent") as mock_store:
        mock_store.return_value = True
        with patch("utils.SessionManager.update_session_metadata") as mock_update:
            mock_update.return_value = True
            with patch("os.path.exists") as mock_exists:
                mock_exists.return_value = True
                
                consent_response = client.post(f"/consent/{session_id}", json=consent_data, headers=headers)
                assert consent_response.status_code == 200
    
    # Now interaction should work (with proper mocking)
    with patch("utils.SessionManager.get_session_info") as mock_session_info:
        mock_session_info.return_value = {"user_id": user_id, "session_id": session_id}
        
        with patch("auth.AuthManager.check_consent") as mock_consent:
            mock_consent.return_value = True  # Consent given
            
            with patch("auth.AuthManager.check_usage_limits") as mock_limits:
                mock_limits.return_value = {"allowed": True, "remaining": 10, "limit": 10, "used": 0}
                
                with patch("integration.validate_session_requirements") as mock_validate:
                    mock_validate.return_value = {"all_requirements_met": True}
                    
                    with patch("integration.generate_interactive_response") as mock_generate:
                        mock_generate.return_value = "/mock/video.mp4"
                        
                        with patch("auth.AuthManager.increment_usage") as mock_increment:
                            mock_increment.return_value = True
                            
                            response = client.post(f"/interact/{session_id}", json={"input": "Hello"}, headers=headers)
                            assert response.status_code == 200


def test_pipeline_usage_limits_enforcement(client, test_db, sample_files):
    """Test that daily usage limits are properly enforced."""
    
    # Setup user and session
    user_data = {"username": f"usage_test_{int(time.time())}", "password": "testpass123"}
    client.post("/register", json=user_data)
    
    login_response = client.post("/login", json=user_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    user_id = login_response.json()["user"]["id"]
    
    # Create session with consent
    session_id = "test_session_usage"
    
    # Mock successful usage limit check initially
    with patch("utils.SessionManager.get_session_info") as mock_session_info:
        mock_session_info.return_value = {"user_id": user_id, "session_id": session_id}
        
        with patch("auth.AuthManager.check_consent") as mock_consent:
            mock_consent.return_value = True
            
            # Test 1: Allow interaction within limits
            with patch("auth.AuthManager.check_usage_limits") as mock_limits:
                mock_limits.return_value = {"allowed": True, "remaining": 5, "limit": 10, "used": 5}
                
                with patch("integration.validate_session_requirements") as mock_validate:
                    mock_validate.return_value = {"all_requirements_met": True}
                    
                    with patch("integration.generate_interactive_response") as mock_generate:
                        mock_generate.return_value = "/mock/video.mp4"
                        
                        with patch("auth.AuthManager.increment_usage") as mock_increment:
                            mock_increment.return_value = True
                            
                            response = client.post(f"/interact/{session_id}", json={"input": "Hello"}, headers=headers)
                            assert response.status_code == 200
            
            # Test 2: Block interaction when limit exceeded
            with patch("auth.AuthManager.check_usage_limits") as mock_limits:
                mock_limits.return_value = {"allowed": False, "remaining": 0, "limit": 10, "used": 10}
                
                response = client.post(f"/interact/{session_id}", json={"input": "Hello"}, headers=headers)
                assert response.status_code == 429
                assert "Daily usage limit exceeded" in response.json()["detail"]


def test_pipeline_error_recovery(client, test_db, mock_d_id_api, mock_elevenlabs_api, sample_files):
    """Test pipeline behavior during various error conditions and recovery."""
    
    # Setup user
    user_data = {"username": f"error_test_{int(time.time())}", "password": "testpass123"}
    client.post("/register", json=user_data)
    
    login_response = client.post("/login", json=user_data)
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test 1: API key validation failure
    with patch("avatar.validate_d_id_api_key") as mock_validate:
        mock_validate.return_value = False
        
        response = client.post("/generate_avatar/test_session")
        assert response.status_code == 401
        assert "Invalid D-ID API key" in response.json()["detail"]
    
    # Test 2: Missing session files
    response = client.get("/preprocess_photo/nonexistent_session")
    assert response.status_code == 404
    assert "Session not found" in response.json()["detail"]
    
    # Test 3: Processing failure with cleanup
    with patch("preprocess.preprocess_photo") as mock_preprocess:
        mock_preprocess.side_effect = Exception("Processing failed")
        
        with patch("os.path.exists") as mock_exists:
            mock_exists.return_value = True
            with patch("os.listdir") as mock_listdir:
                mock_listdir.return_value = ["photo_test.jpg"]
                
                response = client.get("/preprocess_photo/test_session")
                assert response.status_code == 500
                assert "preprocessing failed" in response.json()["detail"]


def test_unauthorized_access_attempts(client, test_db):
    """Test that unauthorized access attempts are properly blocked."""
    
    # Test 1: Access protected endpoint without token
    response = client.post("/consent/test_session", json={"terms_agreed": True})
    assert response.status_code == 403
    
    # Test 2: Access with invalid token
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.post("/consent/test_session", json={"terms_agreed": True}, headers=headers)
    assert response.status_code == 401
    
    # Test 3: Access other user's session
    user1_data = {"username": f"user1_{int(time.time())}", "password": "testpass123"}
    user2_data = {"username": f"user2_{int(time.time())}", "password": "testpass123"}
    
    client.post("/register", json=user1_data)
    client.post("/register", json=user2_data)
    
    user1_login = client.post("/login", json=user1_data)
    user2_login = client.post("/login", json=user2_data)
    
    user1_token = user1_login.json()["access_token"]
    user2_token = user2_login.json()["access_token"]
    user2_id = user2_login.json()["user"]["id"]
    
    # User1 tries to delete User2's session
    with patch("utils.SessionManager.get_session_info") as mock_session_info:
        mock_session_info.return_value = {"user_id": user2_id, "session_id": "user2_session"}
        
        headers = {"Authorization": f"Bearer {user1_token}"}
        response = client.delete("/delete_session/user2_session", headers=headers)
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]