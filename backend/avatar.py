import requests
import os
import time
import base64
from typing import Dict, Optional
import json

def generate_avatar(preprocessed_photo_path: str, session_dir: str, d_id_api_key: str, script_text: str = "Hello, I'm your digital avatar") -> str:
    """
    Generate an animated avatar using D-ID API.
    Args:
        preprocessed_photo_path: Path to the preprocessed photo
        session_dir: Directory to save the avatar video
        d_id_api_key: D-ID API key
        script_text: Text for the avatar to speak
    Returns:
        Path to the generated avatar video
    """
    if not os.path.exists(preprocessed_photo_path):
        raise FileNotFoundError(f"Preprocessed photo not found: {preprocessed_photo_path}")
    
    # D-ID API endpoint for creating talks
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
    
    # Prepare the request payload
    payload = {
        "script": {
            "type": "text",
            "input": script_text,
            "provider": {
                "type": "microsoft",
                "voice_id": "en-US-JennyNeural"
            }
        },
        "source_url": f"data:image/jpeg;base64,{image_base64}",
        "config": {
            "fluent": True,
            "pad_audio": 0.0,
            "stitch": True
        }
    }
    
    try:
        # Send request to D-ID API
        print(f"Sending request to D-ID API...")
        response = requests.post(d_id_url, headers=headers, json=payload)
        
        if response.status_code != 201:
            error_detail = response.json() if response.headers.get('content-type') == 'application/json' else response.text
            raise Exception(f"D-ID API request failed with status {response.status_code}: {error_detail}")
        
        # Get the talk ID from response
        talk_data = response.json()
        talk_id = talk_data.get("id")
        
        if not talk_id:
            raise Exception("No talk ID received from D-ID API")
        
        print(f"Talk created with ID: {talk_id}")
        
        # Poll for completion
        video_url = poll_for_completion(talk_id, d_id_api_key)
        
        # Download the video
        avatar_video_path = download_video(video_url, session_dir)
        
        return avatar_video_path
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error during D-ID API call: {str(e)}")
    except Exception as e:
        raise Exception(f"Avatar generation failed: {str(e)}")

def poll_for_completion(talk_id: str, d_id_api_key: str, max_attempts: int = 30, wait_time: int = 10) -> str:
    """
    Poll D-ID API for talk completion and return video URL.
    Args:
        talk_id: The talk ID to poll
        d_id_api_key: D-ID API key
        max_attempts: Maximum number of polling attempts
        wait_time: Wait time between attempts in seconds
    Returns:
        URL of the generated video
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
            
            print(f"Attempt {attempt + 1}/{max_attempts}: Status = {status}")
            
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
                raise Exception(f"Unknown status: {status}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error while polling: {str(e)}")
    
    raise Exception(f"Avatar generation timed out after {max_attempts * wait_time} seconds")

def download_video(video_url: str, session_dir: str) -> str:
    """
    Download the generated video from D-ID.
    Args:
        video_url: URL of the generated video
        session_dir: Directory to save the video
    Returns:
        Path to the downloaded video file
    """
    try:
        print(f"Downloading video from: {video_url}")
        
        # Download the video
        response = requests.get(video_url, stream=True)
        response.raise_for_status()
        
        # Save the video file
        avatar_video_path = os.path.join(session_dir, "avatar_video.mp4")
        
        with open(avatar_video_path, "wb") as video_file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    video_file.write(chunk)
        
        print(f"Video saved to: {avatar_video_path}")
        return avatar_video_path
        
    except requests.exceptions.RequestException as e:
        raise Exception(f"Failed to download video: {str(e)}")
    except Exception as e:
        raise Exception(f"Error saving video: {str(e)}")

def get_video_info(video_path: str) -> Dict:
    """
    Get information about the generated video.
    Args:
        video_path: Path to the video file
    Returns:
        Dictionary with video metadata
    """
    if not os.path.exists(video_path):
        return {}
    
    try:
        file_size = os.path.getsize(video_path)
        file_stat = os.stat(video_path)
        
        return {
            "file_size": file_size,
            "format": "MP4",
            "created": time.ctime(file_stat.st_ctime),
            "modified": time.ctime(file_stat.st_mtime)
        }
    except Exception as e:
        return {"error": str(e)}

def validate_d_id_api_key(api_key: str) -> bool:
    """
    Validate D-ID API key by making a test request.
    Args:
        api_key: D-ID API key to validate
    Returns:
        True if valid, False otherwise
    """
    try:
        headers = {
            "Authorization": f"Basic {api_key}",
            "Content-Type": "application/json"
        }
        
        # Test endpoint - get credits
        response = requests.get("https://api.d-id.com/credits", headers=headers)
        return response.status_code == 200
        
    except Exception:
        return False