from elevenlabs import ElevenLabs, Voice
import os
import json
from typing import Dict, Optional
import uuid
from datetime import datetime

def clone_voice(audio_path: str, session_dir: str, elevenlabs_api_key: str, voice_name: Optional[str] = None) -> Dict:
    """
    Clone a voice using ElevenLabs API.
    Args:
        audio_path: Path to the uploaded audio
        session_dir: Directory to save voice metadata
        elevenlabs_api_key: ElevenLabs API key
        voice_name: Optional custom name for the cloned voice
    Returns:
        Dictionary with voice ID and metadata
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    if not voice_name:
        voice_name = f"LinkOps_Voice_{str(uuid.uuid4())[:8]}"
    
    try:
        # Initialize ElevenLabs client
        client = ElevenLabs(api_key=elevenlabs_api_key)
        
        # Read the audio file
        with open(audio_path, "rb") as audio_file:
            audio_data = audio_file.read()
        
        # Clone the voice using ElevenLabs API
        print(f"Cloning voice with name: {voice_name}")
        
        # Create voice clone
        voice = client.clone(
            name=voice_name,
            description=f"Voice cloned for LinkOps-Afterlife session",
            files=[audio_data]
        )
        
        voice_id = voice.voice_id
        
        print(f"Voice cloned successfully with ID: {voice_id}")
        
        # Prepare voice metadata
        voice_metadata = {
            "voice_id": voice_id,
            "voice_name": voice_name,
            "description": f"Voice cloned for LinkOps-Afterlife session",
            "original_audio_path": audio_path,
            "clone_timestamp": datetime.now().isoformat(),
            "audio_file_size": len(audio_data),
            "status": "active"
        }
        
        # Save voice metadata to session directory
        metadata_path = os.path.join(session_dir, "voice_metadata.json")
        with open(metadata_path, "w") as metadata_file:
            json.dump(voice_metadata, metadata_file, indent=2)
        
        print(f"Voice metadata saved to: {metadata_path}")
        
        return {
            "voice_id": voice_id,
            "metadata": voice_metadata,
            "metadata_path": metadata_path
        }
        
    except Exception as e:
        raise Exception(f"Voice cloning failed: {str(e)}")

def generate_speech(text: str, voice_id: str, elevenlabs_api_key: str, session_dir: str) -> str:
    """
    Generate speech using a cloned voice.
    Args:
        text: Text to convert to speech
        voice_id: ElevenLabs voice ID
        elevenlabs_api_key: ElevenLabs API key
        session_dir: Directory to save the generated audio
    Returns:
        Path to the generated audio file
    """
    try:
        # Initialize ElevenLabs client
        client = ElevenLabs(api_key=elevenlabs_api_key)
        
        print(f"Generating speech for voice ID: {voice_id}")
        
        # Generate speech
        audio = client.generate(
            text=text,
            voice=Voice(voice_id=voice_id),
            model="eleven_multilingual_v2"
        )
        
        # Save the generated audio
        audio_filename = f"generated_speech_{str(uuid.uuid4())[:8]}.mp3"
        audio_path = os.path.join(session_dir, audio_filename)
        
        # Write audio data to file
        with open(audio_path, "wb") as audio_file:
            for chunk in audio:
                audio_file.write(chunk)
        
        print(f"Speech generated and saved to: {audio_path}")
        
        return audio_path
        
    except Exception as e:
        raise Exception(f"Speech generation failed: {str(e)}")

def get_voice_info(voice_id: str, elevenlabs_api_key: str) -> Dict:
    """
    Get information about a cloned voice.
    Args:
        voice_id: ElevenLabs voice ID
        elevenlabs_api_key: ElevenLabs API key
    Returns:
        Dictionary with voice information
    """
    try:
        # Initialize ElevenLabs client
        client = ElevenLabs(api_key=elevenlabs_api_key)
        
        # Get voice information
        voice = client.voices.get(voice_id)
        
        return {
            "voice_id": voice.voice_id,
            "name": voice.name,
            "category": voice.category,
            "description": voice.description or "No description available",
            "preview_url": voice.preview_url or None,
            "available_for_tiers": voice.available_for_tiers,
            "high_quality_base_model_ids": voice.high_quality_base_model_ids
        }
        
    except Exception as e:
        return {"error": str(e)}

def delete_voice(voice_id: str, elevenlabs_api_key: str) -> bool:
    """
    Delete a cloned voice from ElevenLabs.
    Args:
        voice_id: ElevenLabs voice ID
        elevenlabs_api_key: ElevenLabs API key
    Returns:
        True if deletion was successful, False otherwise
    """
    try:
        # Initialize ElevenLabs client
        client = ElevenLabs(api_key=elevenlabs_api_key)
        
        # Delete the voice
        client.voices.delete(voice_id)
        
        print(f"Voice {voice_id} deleted successfully")
        return True
        
    except Exception as e:
        print(f"Failed to delete voice {voice_id}: {str(e)}")
        return False

def validate_elevenlabs_api_key(api_key: str) -> bool:
    """
    Validate ElevenLabs API key by making a test request.
    Args:
        api_key: ElevenLabs API key to validate
    Returns:
        True if valid, False otherwise
    """
    try:
        # Initialize ElevenLabs client
        client = ElevenLabs(api_key=api_key)
        
        # Test by getting user information
        user = client.user.get()
        return user is not None
        
    except Exception:
        return False

def list_available_voices(elevenlabs_api_key: str) -> Dict:
    """
    List all available voices in the ElevenLabs account.
    Args:
        elevenlabs_api_key: ElevenLabs API key
    Returns:
        Dictionary with voice listings
    """
    try:
        # Initialize ElevenLabs client
        client = ElevenLabs(api_key=elevenlabs_api_key)
        
        # Get all voices
        voices = client.voices.get_all()
        
        voice_list = []
        for voice in voices.voices:
            voice_list.append({
                "voice_id": voice.voice_id,
                "name": voice.name,
                "category": voice.category,
                "description": voice.description or "No description",
                "preview_url": voice.preview_url
            })
        
        return {
            "voices": voice_list,
            "total_count": len(voice_list)
        }
        
    except Exception as e:
        return {"error": str(e)}