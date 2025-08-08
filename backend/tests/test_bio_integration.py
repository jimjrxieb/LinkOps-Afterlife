import pytest
import json
import os
import tempfile
from unittest.mock import patch
from fastapi.testclient import TestClient
from backend.main import app
from backend.utils import FileEncryption
from backend.text_processor import extract_bio_insights, create_bio_enhanced_prompts, process_text_data
from backend.conversation import generate_bio_enhanced_personality_prompt

# Test client for API testing
client = TestClient(app)

class TestBioIntegration:
    """Test suite for biographical information integration functionality."""
    
    def setup_method(self):
        """Set up test environment before each test."""
        self.test_session_id = "test_session_12345"
        self.test_bio_text = """
        Call me Sis - I'm a barber from NYC with 2 kids named Alex and Mia.
        My mom is Jane and dad is Bob. People say I'm funny and caring but stubborn sometimes.
        I love playing guitar and cooking for my family.
        My brother Sam visits from Chicago every summer.
        I work as a barber and have been cutting hair for 15 years.
        """
        
        # Create a test user token (mock)
        self.test_token = "test_jwt_token_12345"
        self.test_user = {"id": "user_123", "username": "testuser"}
    
    def test_extract_bio_insights(self):
        """Test biographical information extraction from text."""
        insights = extract_bio_insights(self.test_bio_text)
        
        # Test nickname extraction
        assert "Sis" in insights["nicknames"]
        
        # Test family member extraction
        family_members = insights["family_members"]
        assert any("mom: Jane" in member for member in family_members)
        assert any("dad: Bob" in member for member in family_members)
        assert any("child: Alex" in member for member in family_members)
        assert any("child: Mia" in member for member in family_members)
        
        # Test profession extraction
        assert insights["profession"] == "Barber"
        
        # Test location extraction
        assert "Nyc" in insights["locations"]
        
        # Test personality descriptors
        personality = insights["personality_descriptors"]
        assert "Funny" in personality
        assert "Caring" in personality
        
        # Test hobbies/interests
        hobbies = insights["hobbies_interests"]
        assert "Playing Guitar" in hobbies
        assert "Cooking For My Family" in hobbies
    
    def test_create_bio_enhanced_prompts(self):
        """Test creation of bio-enhanced conversation prompts."""
        insights = extract_bio_insights(self.test_bio_text)
        prompts = create_bio_enhanced_prompts(insights)
        
        assert len(prompts) > 0
        
        # Check for nickname prompt
        nickname_prompt = next((p for p in prompts if "Sis" in p), None)
        assert nickname_prompt is not None
        
        # Check for profession prompt  
        profession_prompt = next((p for p in prompts if "barber" in p.lower()), None)
        assert profession_prompt is not None
        
        # Check for family prompt
        family_prompt = next((p for p in prompts if "family" in p.lower()), None)
        assert family_prompt is not None
        
        # Check comprehensive prompt exists
        comprehensive_prompt = next((p for p in prompts if len(p) > 200), None)
        assert comprehensive_prompt is not None
    
    def test_bio_enhanced_personality_prompt(self):
        """Test generation of bio-enhanced personality prompts."""
        personality_scores = {"openness": 0.8, "extraversion": 0.6}
        dominant_trait = "openness"
        communication_style = "enthusiastic"
        bio_insights = extract_bio_insights(self.test_bio_text)
        
        prompt = generate_bio_enhanced_personality_prompt(
            personality_scores, dominant_trait, communication_style, bio_insights
        )
        
        # Check basic personality elements
        assert "creative, curious, and open to new experiences" in prompt
        assert "enthusiastic" in prompt
        
        # Check bio integration
        assert "Sis" in prompt
        assert "barber" in prompt.lower()
        assert "NYC" in prompt or "Nyc" in prompt
        assert "Jane" in prompt
        assert "Alex" in prompt
    
    @patch('backend.main.get_current_user')
    def test_submit_bio_endpoint(self, mock_get_current_user):
        """Test the /fine_tune_bio/{session_id} endpoint."""
        mock_get_current_user.return_value = self.test_user
        
        # Create temporary session directory
        with tempfile.TemporaryDirectory() as temp_dir:
            session_dir = os.path.join(temp_dir, self.test_session_id)
            os.makedirs(session_dir, exist_ok=True)
            
            # Create session metadata
            metadata = {
                "user_id": self.test_user["id"],
                "session_id": self.test_session_id,
                "created_at": "2024-01-01T00:00:00"
            }
            
            with open(os.path.join(session_dir, "session_metadata.json"), 'w') as f:
                json.dump(metadata, f)
            
            # Mock data directory path
            with patch('backend.main.os.path.join') as mock_join:
                mock_join.side_effect = lambda *args: os.path.join(*args) if args[0] != "../data/" else temp_dir
                
                # Test successful bio submission
                response = client.post(
                    f"/fine_tune_bio/{self.test_session_id}",
                    json={"who_am_i": self.test_bio_text},
                    headers={"Authorization": f"Bearer {self.test_token}"}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["message"] == "Biographical information saved successfully"
                assert data["session_id"] == self.test_session_id
                assert data["bio_encrypted"] == True
                assert data["bio_length"] > 0
    
    @patch('backend.main.get_current_user')  
    def test_submit_bio_validation(self, mock_get_current_user):
        """Test bio submission validation."""
        mock_get_current_user.return_value = self.test_user
        
        # Test empty bio
        response = client.post(
            f"/fine_tune_bio/{self.test_session_id}",
            json={"who_am_i": ""},
            headers={"Authorization": f"Bearer {self.test_token}"}
        )
        assert response.status_code == 400
        assert "required" in response.json()["detail"]
        
        # Test bio too long (over 10,000 characters)
        long_bio = "a" * 10001
        response = client.post(
            f"/fine_tune_bio/{self.test_session_id}",
            json={"who_am_i": long_bio},
            headers={"Authorization": f"Bearer {self.test_token}"}
        )
        assert response.status_code == 400
        assert "too long" in response.json()["detail"]
    
    def test_text_processing_with_bio(self):
        """Test text processing with biographical information integration."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test text file
            text_file = os.path.join(temp_dir, "test_text.txt")
            with open(text_file, 'w') as f:
                f.write("I love spending time with my family. Work keeps me busy but I enjoy it.")
            
            # Create test bio file
            bio_file = os.path.join(temp_dir, "who_am_i.txt") 
            with open(bio_file, 'w') as f:
                f.write(self.test_bio_text)
            
            # Process text with bio
            processed_path = process_text_data(text_file, temp_dir, bio_file)
            
            # Verify processed data includes bio
            with open(processed_path, 'r') as f:
                processed_data = json.load(f)
            
            assert processed_data["session_metadata"]["bio_provided"] == True
            assert processed_data["session_metadata"]["bio_characters"] > 0
            assert len(processed_data["content"]["bio_text"]) > 0
            assert len(processed_data["analysis"]["bio_insights"]) > 0
            assert len(processed_data["training_data"]["bio_enhanced_prompts"]) > 0
    
    def test_bio_insights_edge_cases(self):
        """Test bio insights extraction with edge cases."""
        # Test empty bio
        empty_insights = extract_bio_insights("")
        for key, value in empty_insights.items():
            if isinstance(value, list):
                assert len(value) == 0
            else:
                assert value == ""
        
        # Test bio with no extractable information
        minimal_bio = "I exist and that's about it."
        minimal_insights = extract_bio_insights(minimal_bio)
        
        # Should still return structured data but mostly empty
        assert isinstance(minimal_insights, dict)
        assert "nicknames" in minimal_insights
        assert "family_members" in minimal_insights
        
        # Test bio with multiple nicknames
        multi_nickname_bio = "Call me Ace, but friends call me Tommy, and family knows me as T."
        multi_insights = extract_bio_insights(multi_nickname_bio)
        
        nicknames = multi_insights["nicknames"]
        assert "Ace" in nicknames
        assert "Tommy" in nicknames
    
    def test_bio_security(self):
        """Test that bio information is properly encrypted and secured."""
        with tempfile.TemporaryDirectory() as temp_dir:
            bio_file = os.path.join(temp_dir, "test_bio.txt")
            encrypted_file = bio_file + ".enc"
            
            # Write test bio
            with open(bio_file, 'w') as f:
                f.write(self.test_bio_text)
            
            # Test encryption
            FileEncryption.encrypt_file(bio_file, encrypted_file)
            
            # Verify encrypted file exists and original is removed
            assert os.path.exists(encrypted_file)
            
            # Test decryption
            decrypted_content = FileEncryption.decrypt_file(encrypted_file)
            assert self.test_bio_text in decrypted_content
    
    def teardown_method(self):
        """Clean up after each test."""
        # Clean up any temporary files or state
        pass

if __name__ == "__main__":
    pytest.main([__file__])