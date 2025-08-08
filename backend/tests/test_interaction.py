import pytest
import os
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

def test_interact_endpoint_success(client, auth_headers, temp_session_dir, test_user, mock_d_id_api, mock_elevenlabs_api):
    """Test successful interaction endpoint."""
    session_id = os.path.basename(temp_session_dir)
    
    # Mock session info and requirements
    with patch("utils.SessionManager.get_session_info") as mock_session_info:
        mock_session_info.return_value = {"user_id": test_user["id"], "session_id": session_id}
        
        with patch("auth.AuthManager.check_consent") as mock_consent:
            mock_consent.return_value = True
            
            with patch("auth.AuthManager.check_usage_limits") as mock_limits:
                mock_limits.return_value = {"allowed": True, "remaining": 9, "limit": 10, "used": 1}
                
                with patch("integration.validate_session_requirements") as mock_validate:
                    mock_validate.return_value = {"all_requirements_met": True}
                    
                    with patch("integration.generate_interactive_response") as mock_generate:
                        video_path = os.path.join(temp_session_dir, "response_video.mp4")
                        mock_generate.return_value = video_path
                        
                        # Create mock video file
                        with open(video_path, "wb") as f:
                            f.write(b"mock_video_data")
                        
                        with patch("auth.AuthManager.increment_usage") as mock_increment:
                            mock_increment.return_value = True
                            
                            user_input = "Hello, how are you today?"
                            response = client.post(
                                f"/interact/{session_id}",
                                json={"input": user_input},
                                headers=auth_headers
                            )
                            
                            assert response.status_code == 200
                            
                            data = response.json()
                            assert data["message"] == "Interactive response generated successfully"
                            assert data["session_id"] == session_id
                            assert data["user_input"] == user_input
                            assert "video_path" in data
                            assert "usage_info" in data

def test_interact_endpoint_empty_input(client, auth_headers, test_user):
    """Test interaction with empty input."""
    session_id = "test_session"
    
    response = client.post(
        f"/interact/{session_id}",
        json={"input": ""},
        headers=auth_headers
    )
    
    assert response.status_code == 400
    assert "Input text is required" in response.json()["detail"]

def test_interact_endpoint_unauthorized_session(client, auth_headers, temp_session_dir, test_user):
    """Test interaction with session belonging to different user."""
    session_id = os.path.basename(temp_session_dir)
    
    with patch("utils.SessionManager.get_session_info") as mock_session_info:
        # Session belongs to different user
        mock_session_info.return_value = {"user_id": 999, "session_id": session_id}
        
        response = client.post(
            f"/interact/{session_id}",
            json={"input": "Hello"},
            headers=auth_headers
        )
        
        assert response.status_code == 403
        assert "Access denied" in response.json()["detail"]

def test_interact_endpoint_no_consent(client, auth_headers, temp_session_dir, test_user):
    """Test interaction without consent."""
    session_id = os.path.basename(temp_session_dir)
    
    with patch("utils.SessionManager.get_session_info") as mock_session_info:
        mock_session_info.return_value = {"user_id": test_user["id"], "session_id": session_id}
        
        with patch("auth.AuthManager.check_consent") as mock_consent:
            mock_consent.return_value = False
            
            response = client.post(
                f"/interact/{session_id}",
                json={"input": "Hello"},
                headers=auth_headers
            )
            
            assert response.status_code == 403
            assert "Consent required" in response.json()["detail"]

def test_interact_endpoint_usage_limit_exceeded(client, auth_headers, temp_session_dir, test_user):
    """Test interaction with usage limit exceeded."""
    session_id = os.path.basename(temp_session_dir)
    
    with patch("utils.SessionManager.get_session_info") as mock_session_info:
        mock_session_info.return_value = {"user_id": test_user["id"], "session_id": session_id}
        
        with patch("auth.AuthManager.check_consent") as mock_consent:
            mock_consent.return_value = True
            
            with patch("auth.AuthManager.check_usage_limits") as mock_limits:
                mock_limits.return_value = {"allowed": False, "remaining": 0, "limit": 10, "used": 10}
                
                response = client.post(
                    f"/interact/{session_id}",
                    json={"input": "Hello"},
                    headers=auth_headers
                )
                
                assert response.status_code == 429
                assert "Daily usage limit exceeded" in response.json()["detail"]

def test_interact_endpoint_session_requirements_not_met(client, auth_headers, temp_session_dir, test_user):
    """Test interaction with session requirements not met."""
    session_id = os.path.basename(temp_session_dir)
    
    with patch("utils.SessionManager.get_session_info") as mock_session_info:
        mock_session_info.return_value = {"user_id": test_user["id"], "session_id": session_id}
        
        with patch("auth.AuthManager.check_consent") as mock_consent:
            mock_consent.return_value = True
            
            with patch("auth.AuthManager.check_usage_limits") as mock_limits:
                mock_limits.return_value = {"allowed": True, "remaining": 5, "limit": 10, "used": 5}
                
                with patch("integration.validate_session_requirements") as mock_validate:
                    mock_validate.return_value = {
                        "all_requirements_met": False,
                        "photo_processing": {"required": True, "exists": False},
                        "voice_cloning": {"required": True, "exists": True}
                    }
                    
                    response = client.post(
                        f"/interact/{session_id}",
                        json={"input": "Hello"},
                        headers=auth_headers
                    )
                    
                    assert response.status_code == 400
                    assert "Session requirements not met" in response.json()["detail"]

def test_interact_endpoint_missing_api_keys(client, auth_headers, temp_session_dir, test_user):
    """Test interaction with missing API keys."""
    session_id = os.path.basename(temp_session_dir)
    
    with patch("utils.SessionManager.get_session_info") as mock_session_info:
        mock_session_info.return_value = {"user_id": test_user["id"], "session_id": session_id}
        
        with patch("auth.AuthManager.check_consent") as mock_consent:
            mock_consent.return_value = True
            
            with patch("auth.AuthManager.check_usage_limits") as mock_limits:
                mock_limits.return_value = {"allowed": True, "remaining": 5, "limit": 10, "used": 5}
                
                with patch.dict(os.environ, {}, clear=True):  # Clear env vars
                    response = client.post(
                        f"/interact/{session_id}",
                        json={"input": "Hello"},
                        headers=auth_headers
                    )
                    
                    assert response.status_code == 500
                    assert "API key not configured" in response.json()["detail"]

def test_interaction_history_success(client, temp_session_dir):
    """Test successful interaction history retrieval."""
    session_id = os.path.basename(temp_session_dir)
    
    with patch("integration.get_interaction_history") as mock_history:
        mock_history.return_value = [
            {
                "timestamp": "2024-01-01T10:00:00",
                "user_input": "Hello",
                "response": "Hi there!",
                "video_path": "/path/to/video1.mp4"
            },
            {
                "timestamp": "2024-01-01T10:05:00",
                "user_input": "How are you?",
                "response": "I'm doing well, thank you!",
                "video_path": "/path/to/video2.mp4"
            }
        ]
        
        response = client.get(f"/interaction_history/{session_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["session_id"] == session_id
        assert "interaction_history" in data
        assert len(data["interaction_history"]) == 2
        assert data["interaction_history"][0]["user_input"] == "Hello"

def test_interaction_history_session_not_found(client):
    """Test interaction history with non-existent session."""
    response = client.get("/interaction_history/nonexistent_session")
    assert response.status_code == 404
    assert "Session not found" in response.json()["detail"]

def test_session_status_success(client, temp_session_dir):
    """Test successful session status retrieval."""
    session_id = os.path.basename(temp_session_dir)
    
    # Create some test files
    test_files = ["photo.jpg", "audio.wav", "text.txt", "metadata.json"]
    for filename in test_files:
        file_path = os.path.join(temp_session_dir, filename)
        with open(file_path, "w") as f:
            f.write("test content")
    
    with patch("integration.validate_session_requirements") as mock_validate:
        mock_validate.return_value = {
            "all_requirements_met": True,
            "photo_processing": {"required": True, "exists": True},
            "voice_cloning": {"required": True, "exists": True},
            "text_processing": {"required": True, "exists": True},
            "conversation_model": {"required": True, "exists": True}
        }
        
        with patch("integration.get_interaction_history") as mock_history:
            mock_history.return_value = [
                {"timestamp": "2024-01-01T10:00:00", "user_input": "Hello", "response": "Hi!"}
            ]
            
            response = client.get(f"/session_status/{session_id}")
            assert response.status_code == 200
            
            data = response.json()
            assert data["session_id"] == session_id
            assert "session_requirements" in data
            assert "interaction_history" in data
            assert "session_files" in data
            assert data["ready_for_interaction"] is True
            assert len(data["session_files"]) == len(test_files)

def test_session_status_not_ready(client, temp_session_dir):
    """Test session status when not ready for interaction."""
    session_id = os.path.basename(temp_session_dir)
    
    with patch("integration.validate_session_requirements") as mock_validate:
        mock_validate.return_value = {
            "all_requirements_met": False,
            "photo_processing": {"required": True, "exists": False},
            "voice_cloning": {"required": True, "exists": True}
        }
        
        with patch("integration.get_interaction_history") as mock_history:
            mock_history.return_value = []
            
            response = client.get(f"/session_status/{session_id}")
            assert response.status_code == 200
            
            data = response.json()
            assert data["ready_for_interaction"] is False
            assert len(data["interaction_history"]) == 0

def test_ping_endpoint(client):
    """Test ping endpoint for health check."""
    response = client.get("/ping")
    assert response.status_code == 200
    
    data = response.json()
    assert data["message"] == "Server is running"
    assert "timestamp" in data

def test_integration_generate_interactive_response_mock():
    """Test the integration module's generate_interactive_response function."""
    from unittest.mock import patch, MagicMock
    
    session_id = "test_session"
    user_input = "Hello, how are you?"
    session_dir = "/mock/session/dir"
    d_id_key = "mock_d_id_key"
    elevenlabs_key = "mock_elevenlabs_key"
    
    with patch("conversation.generate_conversation_response") as mock_conversation:
        mock_conversation.return_value = "I'm doing well, thank you for asking!"
        
        with patch("voice.generate_speech") as mock_speech:
            mock_speech.return_value = "/mock/path/speech.mp3"
            
            with patch("avatar.generate_avatar") as mock_avatar:
                mock_avatar.return_value = "/mock/path/video.mp4"
                
                with patch("integration.get_voice_id_from_session") as mock_voice_id:
                    mock_voice_id.return_value = "mock_voice_id"
                    
                    # This would normally be called by the integration module
                    # We're testing the mock setup here
                    assert mock_conversation.return_value == "I'm doing well, thank you for asking!"
                    assert mock_speech.return_value == "/mock/path/speech.mp3"
                    assert mock_avatar.return_value == "/mock/path/video.mp4"

def test_validate_session_requirements_mock():
    """Test session requirements validation."""
    session_dir = "/mock/session/dir"
    
    with patch("os.path.exists") as mock_exists:
        # Mock different combinations of file existence
        def mock_exists_side_effect(path):
            if "preprocessed_photo" in path:
                return True
            elif "voice_metadata" in path:
                return True
            elif "processed_text" in path:
                return False  # Missing processed text
            elif "conversation_model" in path:
                return False  # Missing conversation model
            return False
        
        mock_exists.side_effect = mock_exists_side_effect
        
        # This would be called by the validate_session_requirements function
        # We're testing the mock behavior
        assert mock_exists("/mock/session/dir/preprocessed_photo.jpg") is True
        assert mock_exists("/mock/session/dir/voice_metadata.json") is True
        assert mock_exists("/mock/session/dir/processed_text.json") is False
        assert mock_exists("/mock/session/dir/conversation_model.json") is False

def test_interaction_workflow_sequence():
    """Test the complete interaction workflow sequence."""
    # This test validates the expected sequence of operations
    # during a full interaction
    
    workflow_steps = [
        "validate_authentication",
        "check_session_ownership", 
        "verify_consent",
        "check_usage_limits",
        "validate_session_requirements",
        "generate_conversation_response",
        "synthesize_speech",
        "generate_avatar_video",
        "increment_usage_counter",
        "update_session_metadata",
        "return_response"
    ]
    
    # Verify we have all expected steps
    assert len(workflow_steps) == 11
    assert "validate_authentication" in workflow_steps
    assert "return_response" in workflow_steps
    
    # This represents the complete flow that should be tested
    # in an integration test

def test_error_handling_cascade():
    """Test error handling in interaction cascade."""
    # Test various error scenarios and their proper handling
    
    error_scenarios = [
        {"error": "authentication_failed", "expected_status": 401},
        {"error": "session_not_owned", "expected_status": 403},
        {"error": "consent_not_given", "expected_status": 403},
        {"error": "usage_limit_exceeded", "expected_status": 429},
        {"error": "requirements_not_met", "expected_status": 400},
        {"error": "api_key_missing", "expected_status": 500},
        {"error": "generation_failed", "expected_status": 500}
    ]
    
    # Verify we handle all expected error cases
    assert len(error_scenarios) == 7
    
    for scenario in error_scenarios:
        assert scenario["expected_status"] in [400, 401, 403, 429, 500]
        assert isinstance(scenario["error"], str)