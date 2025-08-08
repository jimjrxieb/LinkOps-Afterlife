import pytest
import os
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

def test_preprocess_photo_success(client, temp_session_dir):
    """Test successful photo preprocessing."""
    session_id = os.path.basename(temp_session_dir)
    
    # Create mock photo file
    photo_path = os.path.join(temp_session_dir, "photo_test.jpg")
    with open(photo_path, "wb") as f:
        f.write(b"mock_photo_data")
    
    with patch("preprocess.preprocess_photo") as mock_preprocess:
        mock_preprocess.return_value = os.path.join(temp_session_dir, "preprocessed_photo.jpg")
        with patch("preprocess.get_image_info") as mock_info:
            mock_info.return_value = {"width": 512, "height": 512, "format": "JPEG"}
            
            response = client.get(f"/preprocess_photo/{session_id}")
            assert response.status_code == 200
            
            data = response.json()
            assert data["message"] == "Photo preprocessed successfully"
            assert data["session_id"] == session_id
            assert "preprocessed_photo_path" in data
            assert "image_info" in data

def test_preprocess_photo_session_not_found(client):
    """Test photo preprocessing with non-existent session."""
    response = client.get("/preprocess_photo/nonexistent_session")
    assert response.status_code == 404
    assert "Session not found" in response.json()["detail"]

def test_preprocess_photo_no_photo(client, temp_session_dir):
    """Test photo preprocessing with no photo file."""
    session_id = os.path.basename(temp_session_dir)
    
    response = client.get(f"/preprocess_photo/{session_id}")
    assert response.status_code == 404
    assert "Photo not found" in response.json()["detail"]

def test_generate_avatar_success(client, temp_session_dir, mock_d_id_api):
    """Test successful avatar generation."""
    session_id = os.path.basename(temp_session_dir)
    
    # Create mock preprocessed photo
    preprocessed_path = os.path.join(temp_session_dir, "preprocessed_photo.jpg")
    with open(preprocessed_path, "wb") as f:
        f.write(b"mock_preprocessed_photo")
    
    with patch("avatar.generate_avatar") as mock_generate:
        mock_generate.return_value = os.path.join(temp_session_dir, "avatar_video.mp4")
        with patch("avatar.get_video_info") as mock_info:
            mock_info.return_value = {"duration": 10, "width": 512, "height": 512}
            with patch("avatar.validate_d_id_api_key") as mock_validate:
                mock_validate.return_value = True
                
                script_text = "Hello, this is a test avatar."
                response = client.post(f"/generate_avatar/{session_id}?script_text={script_text}")
                assert response.status_code == 200
                
                data = response.json()
                assert data["message"] == "Avatar video generated successfully"
                assert data["session_id"] == session_id
                assert data["script_text"] == script_text
                assert "avatar_video_path" in data

def test_generate_avatar_no_api_key(client, temp_session_dir):
    """Test avatar generation without D-ID API key."""
    session_id = os.path.basename(temp_session_dir)
    
    with patch.dict(os.environ, {}, clear=True):  # Clear env vars
        response = client.post(f"/generate_avatar/{session_id}")
        assert response.status_code == 500
        assert "D-ID API key not configured" in response.json()["detail"]

def test_generate_avatar_invalid_api_key(client, temp_session_dir):
    """Test avatar generation with invalid D-ID API key."""
    session_id = os.path.basename(temp_session_dir)
    
    with patch("avatar.validate_d_id_api_key") as mock_validate:
        mock_validate.return_value = False
        
        response = client.post(f"/generate_avatar/{session_id}")
        assert response.status_code == 401
        assert "Invalid D-ID API key" in response.json()["detail"]

def test_generate_avatar_no_preprocessed_photo(client, temp_session_dir):
    """Test avatar generation without preprocessed photo."""
    session_id = os.path.basename(temp_session_dir)
    
    with patch("avatar.validate_d_id_api_key") as mock_validate:
        mock_validate.return_value = True
        
        response = client.post(f"/generate_avatar/{session_id}")
        assert response.status_code == 404
        assert "Preprocessed photo not found" in response.json()["detail"]

def test_clone_voice_success(client, temp_session_dir, mock_elevenlabs_api):
    """Test successful voice cloning."""
    session_id = os.path.basename(temp_session_dir)
    
    # Create mock audio file
    audio_path = os.path.join(temp_session_dir, "audio_test.wav")
    with open(audio_path, "wb") as f:
        f.write(b"mock_audio_data")
    
    with patch("voice.clone_voice") as mock_clone:
        mock_clone.return_value = {
            "voice_id": "mock_voice_id",
            "metadata": {"name": "Test Voice", "category": "generated"},
            "metadata_path": os.path.join(temp_session_dir, "voice_metadata.json")
        }
        with patch("voice.validate_elevenlabs_api_key") as mock_validate:
            mock_validate.return_value = True
            
            response = client.post(f"/clone_voice/{session_id}")
            assert response.status_code == 200
            
            data = response.json()
            assert data["message"] == "Voice cloned successfully"
            assert data["session_id"] == session_id
            assert data["voice_id"] == "mock_voice_id"
            assert "voice_metadata" in data

def test_clone_voice_no_api_key(client, temp_session_dir):
    """Test voice cloning without ElevenLabs API key."""
    session_id = os.path.basename(temp_session_dir)
    
    with patch.dict(os.environ, {}, clear=True):
        response = client.post(f"/clone_voice/{session_id}")
        assert response.status_code == 500
        assert "ElevenLabs API key not configured" in response.json()["detail"]

def test_clone_voice_no_audio_file(client, temp_session_dir):
    """Test voice cloning without audio file."""
    session_id = os.path.basename(temp_session_dir)
    
    with patch("voice.validate_elevenlabs_api_key") as mock_validate:
        mock_validate.return_value = True
        
        response = client.post(f"/clone_voice/{session_id}")
        assert response.status_code == 404
        assert "Audio file not found" in response.json()["detail"]

def test_generate_speech_success(client, temp_session_dir, mock_elevenlabs_api):
    """Test successful speech generation."""
    session_id = os.path.basename(temp_session_dir)
    
    # Create mock voice metadata
    metadata_path = os.path.join(temp_session_dir, "voice_metadata.json")
    metadata = {"voice_id": "mock_voice_id", "name": "Test Voice"}
    with open(metadata_path, "w") as f:
        json.dump(metadata, f)
    
    with patch("voice.generate_speech") as mock_generate:
        mock_generate.return_value = os.path.join(temp_session_dir, "generated_speech.mp3")
        
        text = "Hello, this is generated speech."
        response = client.post(f"/generate_speech/{session_id}?text={text}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Speech generated successfully"
        assert data["session_id"] == session_id
        assert data["voice_id"] == "mock_voice_id"
        assert data["text"] == text

def test_generate_speech_no_voice_metadata(client, temp_session_dir):
    """Test speech generation without voice metadata."""
    session_id = os.path.basename(temp_session_dir)
    
    response = client.post(f"/generate_speech/{session_id}?text=test")
    assert response.status_code == 404
    assert "Voice not cloned yet" in response.json()["detail"]

def test_process_text_success(client, temp_session_dir):
    """Test successful text processing."""
    session_id = os.path.basename(temp_session_dir)
    
    # Create mock text file
    text_path = os.path.join(temp_session_dir, "text_test.txt")
    with open(text_path, "w") as f:
        f.write("This is a test text with personality traits. I am very friendly and outgoing.")
    
    with patch("text_processor.process_text_data") as mock_process:
        processed_path = os.path.join(temp_session_dir, "processed_text.json")
        mock_process.return_value = processed_path
        
        # Mock processed data
        processed_data = {
            "content": {"sentence_count": 2},
            "analysis": {
                "sentiment_analysis": {"dominant_sentiment": "positive"},
                "personality_traits": {"dominant_trait": "extraversion"},
                "conversation_patterns": {"communication_style": "friendly"}
            }
        }
        
        with open(processed_path, "w") as f:
            json.dump(processed_data, f)
        
        response = client.post(f"/process_text/{session_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Text processed successfully"
        assert data["session_id"] == session_id
        assert "analysis_summary" in data
        assert data["analysis_summary"]["dominant_sentiment"] == "positive"

def test_process_text_no_file(client, temp_session_dir):
    """Test text processing without text file."""
    session_id = os.path.basename(temp_session_dir)
    
    response = client.post(f"/process_text/{session_id}")
    assert response.status_code == 404
    assert "Text file not found" in response.json()["detail"]

def test_fine_tune_conversation_success(client, temp_session_dir):
    """Test successful conversation model fine-tuning."""
    session_id = os.path.basename(temp_session_dir)
    
    # Create mock processed text
    processed_path = os.path.join(temp_session_dir, "processed_text.json")
    processed_data = {
        "analysis": {
            "personality_traits": {"dominant_trait": "openness"},
            "sentiment_analysis": {"dominant_sentiment": "positive"}
        }
    }
    with open(processed_path, "w") as f:
        json.dump(processed_data, f)
    
    with patch("conversation.fine_tune_conversation_model") as mock_fine_tune:
        model_data = {
            "model_id": "mock_model_123",
            "metadata": {
                "personality_profile": {"dominant_trait": "openness"},
                "training_data_summary": {"sentences": 100},
                "conversation_config": {"response_parameters": {"temperature": 0.7}}
            },
            "metadata_path": os.path.join(temp_session_dir, "conversation_model.json")
        }
        mock_fine_tune.return_value = model_data
        
        response = client.post(f"/fine_tune_conversation/{session_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Conversational model fine-tuned successfully"
        assert data["session_id"] == session_id
        assert data["model_id"] == "mock_model_123"
        assert "model_metadata" in data

def test_fine_tune_conversation_no_processed_text(client, temp_session_dir):
    """Test conversation fine-tuning without processed text."""
    session_id = os.path.basename(temp_session_dir)
    
    response = client.post(f"/fine_tune_conversation/{session_id}")
    assert response.status_code == 404
    assert "Text not processed yet" in response.json()["detail"]

def test_generate_conversation_response_success(client, temp_session_dir):
    """Test successful conversation response generation."""
    session_id = os.path.basename(temp_session_dir)
    
    # Create mock conversation model
    model_path = os.path.join(temp_session_dir, "conversation_model.json")
    model_config = {
        "model_id": "mock_model_123",
        "personality_profile": {
            "dominant_trait": "openness",
            "communication_style": "friendly"
        }
    }
    with open(model_path, "w") as f:
        json.dump(model_config, f)
    
    with patch("conversation.generate_conversation_response") as mock_generate:
        mock_generate.return_value = "Hello! How are you doing today? I'm excited to chat with you!"
        
        user_input = "Hello, how are you?"
        response = client.post(f"/generate_conversation/{session_id}?user_input={user_input}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["message"] == "Conversation response generated successfully"
        assert data["session_id"] == session_id
        assert data["user_input"] == user_input
        assert "generated_response" in data
        assert "personality_info" in data

def test_generate_conversation_no_model(client, temp_session_dir):
    """Test conversation generation without model."""
    session_id = os.path.basename(temp_session_dir)
    
    response = client.post(f"/generate_conversation/{session_id}?user_input=test")
    assert response.status_code == 404
    assert "Conversation model not found" in response.json()["detail"]

def test_api_key_validation_d_id(client):
    """Test D-ID API key validation endpoint."""
    with patch("avatar.validate_d_id_api_key") as mock_validate:
        mock_validate.return_value = True
        
        response = client.get("/validate_d_id_key")
        assert response.status_code == 200
        
        data = response.json()
        assert data["valid"] is True
        assert "D-ID API key is valid" in data["message"]

def test_api_key_validation_elevenlabs(client):
    """Test ElevenLabs API key validation endpoint."""
    with patch("voice.validate_elevenlabs_api_key") as mock_validate:
        mock_validate.return_value = True
        
        response = client.get("/validate_elevenlabs_key")
        assert response.status_code == 200
        
        data = response.json()
        assert data["valid"] is True
        assert "ElevenLabs API key is valid" in data["message"]

def test_voice_info_success(client, temp_session_dir, mock_elevenlabs_api):
    """Test getting voice info."""
    session_id = os.path.basename(temp_session_dir)
    
    # Create mock voice metadata
    metadata_path = os.path.join(temp_session_dir, "voice_metadata.json")
    metadata = {"voice_id": "mock_voice_id", "name": "Test Voice"}
    with open(metadata_path, "w") as f:
        json.dump(metadata, f)
    
    with patch("voice.get_voice_info") as mock_info:
        mock_info.return_value = {"voice_id": "mock_voice_id", "status": "ready"}
        
        response = client.get(f"/voice_info/{session_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["session_id"] == session_id
        assert "local_metadata" in data
        assert "elevenlabs_info" in data

def test_conversation_model_info_success(client, temp_session_dir):
    """Test getting conversation model info."""
    session_id = os.path.basename(temp_session_dir)
    
    # Create mock model
    model_path = os.path.join(temp_session_dir, "conversation_model.json")
    model_config = {"model_id": "test_model", "version": "1.0"}
    with open(model_path, "w") as f:
        json.dump(model_config, f)
    
    response = client.get(f"/conversation_model_info/{session_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["session_id"] == session_id
    assert data["model_info"]["model_id"] == "test_model"

def test_session_info_endpoint(client, temp_session_dir):
    """Test session info endpoint."""
    session_id = os.path.basename(temp_session_dir)
    
    # Create some files in session
    test_files = ["test1.txt", "test2.jpg", "test3.wav"]
    for filename in test_files:
        file_path = os.path.join(temp_session_dir, filename)
        with open(file_path, "w") as f:
            f.write("test content")
    
    response = client.get(f"/session/{session_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["session_id"] == session_id
    assert "files" in data
    assert data["total_files"] == len(test_files)