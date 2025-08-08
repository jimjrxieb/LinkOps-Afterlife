import os
import json
import uuid
import time
import base64
from datetime import datetime
from typing import Dict, Optional
import logging

# Import existing modules
from elevenlabs import ElevenLabs, Voice
import requests
# Import moviepy conditionally for optional video processing
try:
    from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    
from conversation import generate_conversation_response

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_interactive_response(session_id: str, user_input: str, session_dir: str, 
                                d_id_api_key: str, elevenlabs_api_key: str) -> str:
    """
    Generate a complete interactive video response combining conversation model, voice cloning, and avatar.
    
    Args:
        session_id: Session ID for file lookup
        user_input: User text input
        session_dir: Directory containing session files
        d_id_api_key: D-ID API key
        elevenlabs_api_key: ElevenLabs API key
    Returns:
        Path to the generated interactive video
    """
    try:
        logger.info(f"Starting interactive response generation for session: {session_id}")
        logger.info(f"User input: {user_input}")
        
        # Step 1: Generate conversation response using fine-tuned model
        conversation_response = generate_conversation_response_from_model(session_dir, user_input)
        logger.info(f"Generated conversation response: {conversation_response}")
        
        # Step 2: Convert response to speech using cloned voice
        speech_audio_path = generate_speech_from_response(
            conversation_response, session_dir, elevenlabs_api_key
        )
        logger.info(f"Generated speech audio: {speech_audio_path}")
        
        # Step 3: Generate D-ID avatar video with the speech audio
        avatar_video_path = generate_avatar_video_with_audio(
            speech_audio_path, session_dir, d_id_api_key, conversation_response
        )
        logger.info(f"Generated avatar video: {avatar_video_path}")
        
        # Step 4: Create final interactive response video
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_video_path = os.path.join(session_dir, f"interactive_response_{timestamp}.mp4")
        
        # For now, the D-ID video is already synced, so we just rename it
        # In more complex scenarios, we might need additional processing with moviepy
        os.rename(avatar_video_path, final_video_path)
        
        # Step 5: Save interaction metadata
        save_interaction_metadata(session_dir, user_input, conversation_response, final_video_path)
        
        logger.info(f"Interactive response completed: {final_video_path}")
        return final_video_path
        
    except Exception as e:
        logger.error(f"Interactive response generation failed: {str(e)}")
        raise Exception(f"Interactive response generation failed: {str(e)}")

def generate_conversation_response_from_model(session_dir: str, user_input: str) -> str:
    """
    Generate a conversation response using the fine-tuned model.
    """
    try:
        # Load conversation model configuration
        model_path = os.path.join(session_dir, "conversation_model.json")
        if not os.path.exists(model_path):
            # Fallback to a generic response if no model is available
            logger.warning("No conversation model found, using fallback response")
            return generate_fallback_response(user_input)
        
        with open(model_path, 'r', encoding='utf-8') as f:
            model_config = json.load(f)
        
        # Generate response using the conversation model
        response = generate_conversation_response(model_config, user_input, "interactive_chat")
        
        # If response is too generic (from placeholder implementation), enhance it
        if response.startswith("[Generated response"):
            response = enhance_placeholder_response(model_config, user_input)
        
        return response
        
    except Exception as e:
        logger.error(f"Conversation response generation failed: {str(e)}")
        return generate_fallback_response(user_input)

def enhance_placeholder_response(model_config: Dict, user_input: str) -> str:
    """
    Enhance placeholder responses with personality-driven content.
    """
    personality_profile = model_config.get("personality_profile", {})
    dominant_trait = personality_profile.get("dominant_trait", "balanced")
    communication_style = personality_profile.get("communication_style", "balanced")
    
    # Create personality-aware responses
    responses_by_trait = {
        "extraversion": [
            "That's such an interesting question! I love talking about this kind of thing.",
            "Oh, I'm so glad you asked! I was just thinking about that recently.",
            "You know what? I have so many thoughts on this topic!"
        ],
        "agreeableness": [
            "I really appreciate you asking about that. It means a lot to share this with you.",
            "Thank you for bringing that up. I think it's important we talk about these things.",
            "I'm so grateful we can have conversations like this together."
        ],
        "conscientiousness": [
            "Let me think carefully about that question before I respond.",
            "That's a thoughtful question that deserves a considered answer.",
            "I want to make sure I give you the most accurate response I can."
        ],
        "neuroticism": [
            "That question really touches something deep in me.",
            "I feel quite emotional thinking about that topic.",
            "That brings up some complex feelings for me."
        ],
        "openness": [
            "What a fascinating question! I love exploring new ideas like this.",
            "That opens up so many interesting possibilities to consider.",
            "I'm always excited to dive into creative topics like this."
        ]
    }
    
    # Select appropriate response based on personality
    trait_responses = responses_by_trait.get(dominant_trait, [
        "That's an interesting point you've raised.",
        "I appreciate you asking about that.",
        "Let me share my thoughts on that with you."
    ])
    
    import random
    base_response = random.choice(trait_responses)
    
    # Add communication style flavor
    if communication_style == "enthusiastic":
        base_response += " I'm really excited to talk about this!"
    elif communication_style == "thoughtful_detailed":
        base_response += " There are several aspects to consider here."
    elif communication_style == "energetic_brief":
        base_response = base_response.replace(".", "!")
    
    return base_response

def generate_fallback_response(user_input: str) -> str:
    """
    Generate a fallback response when no conversation model is available.
    """
    fallback_responses = [
        "That's a thoughtful question. I appreciate you sharing that with me.",
        "Thank you for reaching out. That means a lot to me.",
        "I'm glad we can have this conversation together.",
        "That's something I've been thinking about too.",
        "I appreciate you taking the time to ask about that."
    ]
    
    import random
    return random.choice(fallback_responses)

def generate_speech_from_response(response_text: str, session_dir: str, elevenlabs_api_key: str) -> str:
    """
    Convert the conversation response to speech using the cloned voice.
    """
    try:
        # Load voice metadata
        voice_metadata_path = os.path.join(session_dir, "voice_metadata.json")
        if not os.path.exists(voice_metadata_path):
            raise Exception("Voice metadata not found. Please clone voice first.")
        
        with open(voice_metadata_path, 'r') as f:
            voice_metadata = json.load(f)
        
        voice_id = voice_metadata.get("voice_id")
        if not voice_id:
            raise Exception("Voice ID not found in metadata")
        
        # Initialize ElevenLabs client
        client = ElevenLabs(api_key=elevenlabs_api_key)
        
        logger.info(f"Generating speech for voice ID: {voice_id}")
        
        # Generate speech
        audio = client.generate(
            text=response_text,
            voice=Voice(voice_id=voice_id),
            model="eleven_multilingual_v2"
        )
        
        # Save the generated audio
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        audio_filename = f"response_speech_{timestamp}.mp3"
        audio_path = os.path.join(session_dir, audio_filename)
        
        # Write audio data to file
        with open(audio_path, "wb") as audio_file:
            for chunk in audio:
                audio_file.write(chunk)
        
        logger.info(f"Speech generated and saved to: {audio_path}")
        return audio_path
        
    except Exception as e:
        logger.error(f"Speech generation failed: {str(e)}")
        raise Exception(f"Speech generation failed: {str(e)}")

def generate_avatar_video_with_audio(audio_path: str, session_dir: str, d_id_api_key: str, text_content: str) -> str:
    """
    Generate D-ID avatar video with custom audio for lip-syncing.
    """
    try:
        # Find preprocessed photo
        preprocessed_photo_path = os.path.join(session_dir, "preprocessed_photo.jpg")
        if not os.path.exists(preprocessed_photo_path):
            raise Exception("Preprocessed photo not found. Please preprocess photo first.")
        
        # D-ID API endpoint for creating talks with custom audio
        d_id_url = "https://api.d-id.com/talks"
        
        # Prepare headers
        headers = {
            "Authorization": f"Basic {d_id_api_key}",
            "Content-Type": "application/json"
        }
        
        # Read and encode the image file
        with open(preprocessed_photo_path, "rb") as image_file:
            image_data = image_file.read()
            image_base64 = base64.b64encode(image_data).decode("utf-8")
        
        # Read and encode the audio file
        with open(audio_path, "rb") as audio_file:
            audio_data = audio_file.read()
            audio_base64 = base64.b64encode(audio_data).decode("utf-8")
        
        # Prepare the request payload with custom audio
        payload = {
            "script": {
                "type": "audio",
                "audio_url": f"data:audio/mp3;base64,{audio_base64}",
                "subtitles": "false"
            },
            "source_url": f"data:image/jpeg;base64,{image_base64}",
            "config": {
                "fluent": True,
                "pad_audio": 0.0,
                "stitch": True,
                "result_format": "mp4"
            }
        }
        
        logger.info("Sending request to D-ID API with custom audio...")
        
        # Send request to D-ID API
        response = requests.post(d_id_url, headers=headers, json=payload)
        
        if response.status_code != 201:
            error_detail = response.json() if response.headers.get('content-type') == 'application/json' else response.text
            raise Exception(f"D-ID API request failed with status {response.status_code}: {error_detail}")
        
        # Get the talk ID from response
        talk_data = response.json()
        talk_id = talk_data.get("id")
        
        if not talk_id:
            raise Exception("No talk ID received from D-ID API")
        
        logger.info(f"D-ID talk created with ID: {talk_id}")
        
        # Poll for completion
        video_url = poll_for_d_id_completion(talk_id, d_id_api_key)
        
        # Download the video
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_filename = f"avatar_response_{timestamp}.mp4"
        avatar_video_path = download_d_id_video(video_url, session_dir, video_filename)
        
        return avatar_video_path
        
    except Exception as e:
        logger.error(f"Avatar video generation failed: {str(e)}")
        raise Exception(f"Avatar video generation failed: {str(e)}")

def poll_for_d_id_completion(talk_id: str, d_id_api_key: str, max_attempts: int = 30, wait_time: int = 10) -> str:
    """
    Poll D-ID API for talk completion and return video URL.
    """
    get_url = f"https://api.d-id.com/talks/{talk_id}"
    headers = {
        "Authorization": f"Basic {d_id_api_key}",
        "Content-Type": "application/json"
    }
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(get_url, headers=headers)
            
            if response.status_code != 200:
                raise Exception(f"Failed to get talk status: {response.status_code}")
            
            talk_status = response.json()
            status = talk_status.get("status")
            
            logger.info(f"D-ID poll attempt {attempt + 1}/{max_attempts}: Status = {status}")
            
            if status == "done":
                video_url = talk_status.get("result_url")
                if not video_url:
                    raise Exception("No video URL in completed talk")
                return video_url
            elif status == "error":
                error_msg = talk_status.get("error", {}).get("description", "Unknown error")
                raise Exception(f"D-ID processing failed: {error_msg}")
            elif status in ["created", "started"]:
                # Still processing, wait and try again
                time.sleep(wait_time)
                continue
            else:
                raise Exception(f"Unknown D-ID status: {status}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error while polling D-ID: {str(e)}")
    
    raise Exception(f"D-ID avatar generation timed out after {max_attempts * wait_time} seconds")

def download_d_id_video(video_url: str, session_dir: str, filename: str) -> str:
    """
    Download the generated video from D-ID.
    """
    try:
        logger.info(f"Downloading D-ID video from: {video_url}")
        
        # Download the video
        response = requests.get(video_url, stream=True)
        response.raise_for_status()
        
        # Save the video file
        video_path = os.path.join(session_dir, filename)
        
        with open(video_path, "wb") as video_file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    video_file.write(chunk)
        
        logger.info(f"D-ID video saved to: {video_path}")
        return video_path
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to download D-ID video: {str(e)}")
    except Exception as e:
        raise Exception(f"Error saving D-ID video: {str(e)}")

def save_interaction_metadata(session_dir: str, user_input: str, response_text: str, video_path: str):
    """
    Save metadata about the interaction for future reference.
    """
    try:
        metadata = {
            "interaction_timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "generated_response": response_text,
            "video_path": video_path,
            "video_file_size": os.path.getsize(video_path) if os.path.exists(video_path) else 0,
            "processing_steps": [
                "conversation_model_response",
                "voice_synthesis",
                "avatar_video_generation",
                "final_video_assembly"
            ]
        }
        
        # Save to interactions log
        interactions_log_path = os.path.join(session_dir, "interactions_log.json")
        
        # Load existing log or create new one
        if os.path.exists(interactions_log_path):
            with open(interactions_log_path, 'r', encoding='utf-8') as f:
                interactions_log = json.load(f)
        else:
            interactions_log = {"interactions": []}
        
        # Add new interaction
        interactions_log["interactions"].append(metadata)
        interactions_log["total_interactions"] = len(interactions_log["interactions"])
        interactions_log["last_updated"] = datetime.now().isoformat()
        
        # Save updated log
        with open(interactions_log_path, 'w', encoding='utf-8') as f:
            json.dump(interactions_log, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Interaction metadata saved to: {interactions_log_path}")
        
    except Exception as e:
        logger.warning(f"Failed to save interaction metadata: {str(e)}")

def get_interaction_history(session_dir: str) -> Dict:
    """
    Get the interaction history for a session.
    """
    try:
        interactions_log_path = os.path.join(session_dir, "interactions_log.json")
        
        if not os.path.exists(interactions_log_path):
            return {"interactions": [], "total_interactions": 0}
        
        with open(interactions_log_path, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    except Exception as e:
        logger.error(f"Failed to get interaction history: {str(e)}")
        return {"interactions": [], "total_interactions": 0, "error": str(e)}

def validate_session_requirements(session_dir: str) -> Dict:
    """
    Validate that all required components are available for interaction.
    """
    requirements = {
        "preprocessed_photo": os.path.join(session_dir, "preprocessed_photo.jpg"),
        "voice_metadata": os.path.join(session_dir, "voice_metadata.json"),
        "conversation_model": os.path.join(session_dir, "conversation_model.json")
    }
    
    validation_results = {}
    all_requirements_met = True
    
    for requirement, path in requirements.items():
        exists = os.path.exists(path)
        validation_results[requirement] = {
            "path": path,
            "exists": exists,
            "required": True
        }
        if not exists:
            all_requirements_met = False
    
    validation_results["all_requirements_met"] = all_requirements_met
    validation_results["validation_timestamp"] = datetime.now().isoformat()
    
    return validation_results