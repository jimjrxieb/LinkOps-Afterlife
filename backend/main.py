from fastapi import FastAPI, UploadFile, File, HTTPException, Body, Depends, Security
from typing import List
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from preprocess import preprocess_photo, get_image_info, process_multiple_photos
from avatar import generate_avatar, get_video_info, validate_d_id_api_key
from voice import clone_voice, generate_speech, get_voice_info, validate_elevenlabs_api_key, list_available_voices
from text_processor import process_text_data
from conversation import fine_tune_conversation_model, generate_conversation_response
from integration import generate_interactive_response, get_interaction_history, validate_session_requirements
from auth import AuthManager
from utils import FileValidator, FileEncryption, SessionManager, save_upload_file, generate_secure_filename
import os
import shutil
import json
from datetime import datetime
import uuid
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="LinkOps-Afterlife API", description="AI-powered digital afterlife platform")

# Prometheus metrics instrumentation
try:
    from prometheus_fastapi_instrumentator import Instrumentator

    Instrumentator().instrument(app).expose(app, include_in_schema=False)
    logger.info("Prometheus metrics instrumentation enabled at /metrics")
except Exception as _instrumentation_error:  # keep app working if metrics libs not present
    logger.warning("Prometheus metrics not enabled: %s", str(_instrumentation_error))

# Add CORS middleware
origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize security and auth
security = HTTPBearer()
auth_manager = AuthManager()

# Dependency to get current user from JWT token
async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """Dependency to extract and validate user from JWT token."""
    try:
        token = credentials.credentials
        payload = auth_manager.verify_token(token)
        
        if payload is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
        
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@app.get("/ping")
async def ping():
    return {"message": "Server is running", "timestamp": datetime.now().isoformat()}

@app.get("/healthz")
async def healthz():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

# Authentication endpoints
@app.post("/register")
async def register_user(body: dict = Body(...)):
    """Register a new user."""
    try:
        username = body.get("username")
        password = body.get("password")
        email = body.get("email")
        
        if not username or not password:
            raise HTTPException(
                status_code=400,
                detail="Username and password are required"
            )
        
        if len(password) < 8:
            raise HTTPException(
                status_code=400,
                detail="Password must be at least 8 characters long"
            )
        
        user = auth_manager.create_user(username, password, email)
        
        return JSONResponse(
            status_code=201,
            content={
                "message": "User registered successfully",
                "user": {
                    "id": user["id"],
                    "username": user["username"],
                    "email": user["email"]
                }
            }
        )
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")

@app.post("/login")
async def login_user(body: dict = Body(...)):
    """Authenticate user and return JWT token."""
    try:
        username = body.get("username")
        password = body.get("password")
        
        if not username or not password:
            raise HTTPException(
                status_code=400,
                detail="Username and password are required"
            )
        
        user = auth_manager.authenticate_user(username, password)
        
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid username or password"
            )
        
        # Create access token
        token = auth_manager.create_access_token(user)
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Login successful",
                "access_token": token,
                "token_type": "bearer",
                "user": user
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")

@app.post("/consent/{session_id}")
async def submit_consent(
    session_id: str,
    body: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """Submit consent agreement for a session."""
    try:
        consent_data = {
            "terms_agreed": body.get("terms_agreed", False),
            "data_processing_agreed": body.get("data_processing_agreed", False),
            "emotional_impact_acknowledged": body.get("emotional_impact_acknowledged", False),
            "consent_timestamp": datetime.now().isoformat(),
            "user_agent": body.get("user_agent", ""),
            "ip_address": body.get("ip_address", "")
        }
        
        # Validate that all required consents are given
        required_consents = ["terms_agreed", "data_processing_agreed", "emotional_impact_acknowledged"]
        for consent in required_consents:
            if not consent_data.get(consent):
                raise HTTPException(
                    status_code=400,
                    detail=f"Consent required: {consent}"
                )
        
        # Store consent in database
        success = auth_manager.store_consent(
            current_user["id"], 
            session_id, 
            consent_data
        )
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to store consent"
            )
        
        # Update session metadata
        data_dir = "../data/"
        session_dir = os.path.join(data_dir, session_id)
        
        if os.path.exists(session_dir):
            SessionManager.update_session_metadata(session_dir, {
                "security": {"consent_given": True}
            })
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Consent recorded successfully",
                "session_id": session_id,
                "consent_timestamp": consent_data["consent_timestamp"]
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Consent submission error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to submit consent")

@app.delete("/delete_session/{session_id}")
async def delete_session(
    session_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Permanently delete all session data."""
    try:
        data_dir = "../data/"
        session_dir = os.path.join(data_dir, session_id)
        
        # Verify session belongs to current user
        session_info = SessionManager.get_session_info(session_dir)
        if session_info and session_info.get("user_id") != current_user["id"]:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Session does not belong to current user"
            )
        
        # Delete all session data
        success = SessionManager.delete_session_data(session_dir)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to delete session data"
            )
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Session data deleted successfully",
                "session_id": session_id,
                "deleted_at": datetime.now().isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Session deletion error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete session")

@app.post("/upload")
async def upload_files(
    photos: List[UploadFile] = File(...), 
    audio: UploadFile = File(...), 
    text: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    try:
        # Validate all files first
        files_valid, validation_errors = FileValidator.validate_all_files(photos, audio, text)
        if not files_valid:
            raise HTTPException(
                status_code=400,
                detail=f"File validation failed: {'; '.join(validation_errors)}"
            )
        
        # Create data directory if it doesn't exist
        data_dir = "../data/"
        os.makedirs(data_dir, exist_ok=True)
        
        # Generate unique session ID for this upload
        session_id = str(uuid.uuid4())
        session_dir = os.path.join(data_dir, session_id)
        os.makedirs(session_dir, exist_ok=True)
        
        # Create user session record
        auth_manager.create_user_session(current_user["id"], session_id)
        
        # Generate secure filenames for multiple photos
        photo_filenames = []
        photo_paths = []
        for i, photo in enumerate(photos):
            photo_filename = generate_secure_filename(photo.filename, f"photo_{i+1}")
            photo_path = os.path.join(session_dir, photo_filename)
            photo_filenames.append(photo_filename)
            photo_paths.append(photo_path)
            # Save each photo
            save_upload_file(photo, photo_path)
        
        # Generate secure filenames for audio and text
        audio_filename = generate_secure_filename(audio.filename, "audio")
        text_filename = generate_secure_filename(text.filename, "text")
        
        # Define file paths for audio and text
        audio_path = os.path.join(session_dir, audio_filename)
        text_path = os.path.join(session_dir, text_filename)
        
        # Save audio and text files securely
        save_upload_file(audio, audio_path)
        save_upload_file(text, text_path)
        
        # Encrypt all uploaded files
        try:
            encrypted_files = FileEncryption.encrypt_session_files(session_dir)
            logger.info(f"Files encrypted for session: {session_id}")
        except Exception as e:
            logger.error(f"File encryption failed: {str(e)}")
            # Clean up session on encryption failure
            SessionManager.delete_session_data(session_dir)
            raise HTTPException(
                status_code=500,
                detail="File encryption failed. Upload cancelled for security."
            )
        
        # Create session metadata with multiple photos
        photos_metadata = []
        for i, photo in enumerate(photos):
            photos_metadata.append({
                "original_filename": photo.filename,
                "secure_filename": photo_filenames[i],
                "size": photo.size,
                "content_type": photo.content_type
            })
        
        upload_data = {
            "files": {
                "photos": photos_metadata,
                "photo_count": len(photos),
                "audio": {
                    "original_filename": audio.filename,
                    "secure_filename": audio_filename,
                    "size": audio.size,
                    "content_type": audio.content_type
                },
                "text": {
                    "original_filename": text.filename,
                    "secure_filename": text_filename,
                    "size": text.size,
                    "content_type": text.content_type
                }
            },
            "validation_passed": True,
            "encryption_applied": True
        }
        
        SessionManager.create_session_metadata(
            session_dir,
            current_user["id"],
            session_id,
            upload_data
        )
        
        # Return response with session info (no file paths for security)
        photos_processed = []
        for photo in photos:
            photos_processed.append({"filename": photo.filename, "size": photo.size})
        
        return JSONResponse(
            status_code=200,
            content={
                "message": f"Files uploaded and secured successfully ({len(photos)} photos)",
                "session_id": session_id,
                "user_id": current_user["id"],
                "files_processed": {
                    "photos": photos_processed,
                    "photo_count": len(photos),
                    "audio": {"filename": audio.filename, "size": audio.size},
                    "text": {"filename": text.filename, "size": text.size}
                },
                "security": {
                    "files_encrypted": True,
                    "validation_passed": True
                },
                "upload_timestamp": datetime.now().isoformat()
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

@app.post("/fine_tune_bio/{session_id}")
async def submit_bio(
    session_id: str, 
    body: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Submit biographical information for enhanced personality fine-tuning.
    
    Args:
        session_id: Session identifier
        body: Request body containing 'who_am_i' biographical text
        current_user: Authenticated user from JWT token
    """
    try:
        who_am_i = body.get("who_am_i", "").strip()
        
        if not who_am_i:
            raise HTTPException(
                status_code=400,
                detail="Biographical information ('who_am_i') is required"
            )
        
        if len(who_am_i) > 10000:  # Limit bio to 10,000 characters
            raise HTTPException(
                status_code=400,
                detail="Biographical information is too long (maximum 10,000 characters)"
            )
        
        # Verify session exists and belongs to user
        data_dir = "../data/"
        session_dir = os.path.join(data_dir, session_id)
        
        if not os.path.exists(session_dir):
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Verify user owns this session
        session_metadata_path = os.path.join(session_dir, "session_metadata.json")
        if os.path.exists(session_metadata_path):
            with open(session_metadata_path, 'r') as f:
                session_data = json.load(f)
                if session_data.get("user_id") != current_user["id"]:
                    raise HTTPException(status_code=403, detail="Access denied to this session")
        
        # Save biographical information securely
        bio_filename = "who_am_i.txt"
        bio_path = os.path.join(session_dir, bio_filename)
        
        # Write bio to file
        with open(bio_path, 'w', encoding='utf-8') as f:
            f.write(who_am_i)
        
        # Encrypt the bio file
        try:
            FileEncryption.encrypt_file(bio_path, bio_path + ".enc")
            # Remove unencrypted file
            os.remove(bio_path)
            logger.info(f"Bio encrypted and saved for session: {session_id}")
        except Exception as e:
            logger.error(f"Bio encryption failed: {str(e)}")
            # Clean up unencrypted file if it exists
            if os.path.exists(bio_path):
                os.remove(bio_path)
            raise HTTPException(
                status_code=500,
                detail="Bio encryption failed. Bio not saved for security."
            )
        
        # Update session metadata to include bio information
        if os.path.exists(session_metadata_path):
            with open(session_metadata_path, 'r') as f:
                session_data = json.load(f)
            
            session_data.setdefault("bio_info", {})
            session_data["bio_info"] = {
                "bio_provided": True,
                "bio_length": len(who_am_i),
                "bio_timestamp": datetime.now().isoformat(),
                "bio_filename": bio_filename + ".enc"
            }
            
            with open(session_metadata_path, 'w') as f:
                json.dump(session_data, f, indent=2)
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Biographical information saved successfully",
                "session_id": session_id,
                "bio_length": len(who_am_i),
                "bio_encrypted": True,
                "submission_timestamp": datetime.now().isoformat()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bio submission error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Bio submission failed: {str(e)}")

@app.get("/preprocess_photo/{session_id}")
async def preprocess_photo_endpoint(session_id: str, method: str = "best_selection"):
    """
    Preprocess uploaded photos for avatar generation using AI/ML enhancement.
    
    Args:
        session_id: Session identifier
        method: Processing method - "best_selection" or "face_averaging"
    """
    try:
        # Define path to the session directory
        data_dir = "../data/"
        session_dir = os.path.join(data_dir, session_id)
        
        if not os.path.exists(session_dir):
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Find all uploaded photos
        photo_paths = []
        for file in os.listdir(session_dir):
            if file.startswith("photo_"):
                photo_path = os.path.join(session_dir, file)
                if os.path.exists(photo_path):
                    photo_paths.append(photo_path)
        
        if not photo_paths:
            raise HTTPException(status_code=404, detail="No photos found in session")
        
        logger.info(f"Found {len(photo_paths)} photos for processing using {method} method")

        # Process multiple photos using AI/ML enhancement
        if method not in ["best_selection", "face_averaging"]:
            method = "best_selection"  # Default to best selection
            
        preprocessed_path = process_multiple_photos(photo_paths, session_dir, method)
        
        # Get image information
        image_info = get_image_info(preprocessed_path)

        # Return response
        return JSONResponse(
            status_code=200,
            content={
                "message": f"Photos preprocessed successfully using {method} method ({len(photo_paths)} photos)",
                "session_id": session_id,
                "processing_method": method,
                "input_photo_count": len(photo_paths),
                "preprocessed_photo_path": preprocessed_path,
                "image_info": image_info,
                "preprocessing_timestamp": datetime.now().isoformat()
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Photo preprocessing failed: {str(e)}")

@app.get("/session/{session_id}")
async def get_session_info(session_id: str):
    """
    Get information about a session and its files.
    """
    try:
        data_dir = "../data/"
        session_dir = os.path.join(data_dir, session_id)
        
        if not os.path.exists(session_dir):
            raise HTTPException(status_code=404, detail="Session not found")
        
        files = []
        for file in os.listdir(session_dir):
            file_path = os.path.join(session_dir, file)
            file_stat = os.stat(file_path)
            files.append({
                "filename": file,
                "path": file_path,
                "size": file_stat.st_size,
                "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat()
            })
        
        return JSONResponse(
            status_code=200,
            content={
                "session_id": session_id,
                "files": files,
                "total_files": len(files)
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session info: {str(e)}")

@app.post("/generate_avatar/{session_id}")
async def generate_avatar_endpoint(session_id: str, script_text: str = "Hello, I'm your digital avatar"):
    """
    Generate an animated avatar using D-ID API.
    """
    try:
        # Load D-ID API key from environment variable
        d_id_api_key = os.getenv("D_ID_API_KEY")
        if not d_id_api_key:
            raise HTTPException(
                status_code=500, 
                detail="D-ID API key not configured. Please set D_ID_API_KEY environment variable."
            )
        
        # Validate API key
        if not validate_d_id_api_key(d_id_api_key):
            raise HTTPException(
                status_code=401,
                detail="Invalid D-ID API key. Please check your credentials."
            )

        # Define paths
        data_dir = "../data/"
        session_dir = os.path.join(data_dir, session_id)
        
        if not os.path.exists(session_dir):
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Find preprocessed photo
        preprocessed_photo_path = os.path.join(session_dir, "preprocessed_photo.jpg")
        if not os.path.exists(preprocessed_photo_path):
            raise HTTPException(
                status_code=404, 
                detail="Preprocessed photo not found. Please run /preprocess_photo/{session_id} first."
            )

        # Generate avatar video
        avatar_video_path = generate_avatar(
            preprocessed_photo_path, 
            session_dir, 
            d_id_api_key,
            script_text
        )

        # Get video metadata
        video_metadata = get_video_info(avatar_video_path)

        # Return response
        return JSONResponse(
            status_code=200,
            content={
                "message": "Avatar video generated successfully",
                "session_id": session_id,
                "avatar_video_path": avatar_video_path,
                "script_text": script_text,
                "video_metadata": video_metadata,
                "generation_timestamp": datetime.now().isoformat()
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Avatar generation failed: {str(e)}")

@app.get("/validate_d_id_key")
async def validate_d_id_key_endpoint():
    """
    Validate the D-ID API key configuration.
    """
    try:
        d_id_api_key = os.getenv("D_ID_API_KEY")
        if not d_id_api_key:
            return JSONResponse(
                status_code=200,
                content={
                    "valid": False,
                    "message": "D-ID API key not configured",
                    "instructions": "Set environment variable: export D_ID_API_KEY=your_api_key"
                }
            )
        
        is_valid = validate_d_id_api_key(d_id_api_key)
        
        return JSONResponse(
            status_code=200,
            content={
                "valid": is_valid,
                "message": "D-ID API key is valid" if is_valid else "D-ID API key is invalid",
                "key_length": len(d_id_api_key),
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

@app.post("/clone_voice/{session_id}")
async def clone_voice_endpoint(session_id: str, voice_name: str = None):
    """
    Clone a voice using ElevenLabs API.
    """
    try:
        # Load ElevenLabs API key from environment variable
        elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        if not elevenlabs_api_key:
            raise HTTPException(
                status_code=500, 
                detail="ElevenLabs API key not configured. Please set ELEVENLABS_API_KEY environment variable."
            )
        
        # Validate API key
        if not validate_elevenlabs_api_key(elevenlabs_api_key):
            raise HTTPException(
                status_code=401,
                detail="Invalid ElevenLabs API key. Please check your credentials."
            )

        # Define paths
        data_dir = "../data/"
        session_dir = os.path.join(data_dir, session_id)
        
        if not os.path.exists(session_dir):
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Find uploaded audio
        audio_path = None
        for file in os.listdir(session_dir):
            if file.startswith("audio_"):
                audio_path = os.path.join(session_dir, file)
                break
        
        if not audio_path or not os.path.exists(audio_path):
            raise HTTPException(
                status_code=404, 
                detail="Audio file not found in session. Please upload audio first."
            )

        # Clone voice
        voice_data = clone_voice(audio_path, session_dir, elevenlabs_api_key, voice_name)

        # Return response
        return JSONResponse(
            status_code=200,
            content={
                "message": "Voice cloned successfully",
                "session_id": session_id,
                "voice_id": voice_data["voice_id"],
                "voice_metadata": voice_data["metadata"],
                "metadata_path": voice_data["metadata_path"],
                "clone_timestamp": datetime.now().isoformat()
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice cloning failed: {str(e)}")

@app.post("/generate_speech/{session_id}")
async def generate_speech_endpoint(session_id: str, text: str):
    """
    Generate speech using a cloned voice.
    """
    try:
        # Load ElevenLabs API key from environment variable
        elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        if not elevenlabs_api_key:
            raise HTTPException(
                status_code=500, 
                detail="ElevenLabs API key not configured."
            )

        # Define paths
        data_dir = "../data/"
        session_dir = os.path.join(data_dir, session_id)
        
        if not os.path.exists(session_dir):
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Load voice metadata
        metadata_path = os.path.join(session_dir, "voice_metadata.json")
        if not os.path.exists(metadata_path):
            raise HTTPException(
                status_code=404, 
                detail="Voice not cloned yet. Please run /clone_voice/{session_id} first."
            )
        
        with open(metadata_path, "r") as f:
            voice_metadata = json.load(f)
        
        voice_id = voice_metadata.get("voice_id")
        if not voice_id:
            raise HTTPException(status_code=500, detail="Voice ID not found in metadata")

        # Generate speech
        audio_path = generate_speech(text, voice_id, elevenlabs_api_key, session_dir)

        # Get audio file info
        audio_size = os.path.getsize(audio_path) if os.path.exists(audio_path) else 0

        # Return response
        return JSONResponse(
            status_code=200,
            content={
                "message": "Speech generated successfully",
                "session_id": session_id,
                "voice_id": voice_id,
                "text": text,
                "audio_path": audio_path,
                "audio_metadata": {
                    "file_size": audio_size,
                    "format": "MP3"
                },
                "generation_timestamp": datetime.now().isoformat()
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Speech generation failed: {str(e)}")

@app.get("/validate_elevenlabs_key")
async def validate_elevenlabs_key_endpoint():
    """
    Validate the ElevenLabs API key configuration.
    """
    try:
        elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        if not elevenlabs_api_key:
            return JSONResponse(
                status_code=200,
                content={
                    "valid": False,
                    "message": "ElevenLabs API key not configured",
                    "instructions": "Set environment variable: export ELEVENLABS_API_KEY=your_api_key"
                }
            )
        
        is_valid = validate_elevenlabs_api_key(elevenlabs_api_key)
        
        return JSONResponse(
            status_code=200,
            content={
                "valid": is_valid,
                "message": "ElevenLabs API key is valid" if is_valid else "ElevenLabs API key is invalid",
                "key_length": len(elevenlabs_api_key),
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

@app.get("/voice_info/{session_id}")
async def get_voice_info_endpoint(session_id: str):
    """
    Get information about the cloned voice in a session.
    """
    try:
        elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        if not elevenlabs_api_key:
            raise HTTPException(status_code=500, detail="ElevenLabs API key not configured")

        # Define paths
        data_dir = "../data/"
        session_dir = os.path.join(data_dir, session_id)
        metadata_path = os.path.join(session_dir, "voice_metadata.json")
        
        if not os.path.exists(metadata_path):
            raise HTTPException(status_code=404, detail="Voice metadata not found")
        
        # Load local metadata
        with open(metadata_path, "r") as f:
            local_metadata = json.load(f)
        
        voice_id = local_metadata.get("voice_id")
        if not voice_id:
            raise HTTPException(status_code=500, detail="Voice ID not found in metadata")
        
        # Get voice info from ElevenLabs
        voice_info = get_voice_info(voice_id, elevenlabs_api_key)
        
        return JSONResponse(
            status_code=200,
            content={
                "session_id": session_id,
                "local_metadata": local_metadata,
                "elevenlabs_info": voice_info,
                "timestamp": datetime.now().isoformat()
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get voice info: {str(e)}")

@app.post("/process_text/{session_id}")
async def process_text_endpoint(session_id: str):
    """
    Process uploaded text data for personality analysis.
    """
    try:
        # Define paths
        data_dir = "../data/"
        session_dir = os.path.join(data_dir, session_id)
        
        if not os.path.exists(session_dir):
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Find uploaded text file
        text_path = None
        for file in os.listdir(session_dir):
            if file.startswith("text_"):
                text_path = os.path.join(session_dir, file)
                break
        
        if not text_path or not os.path.exists(text_path):
            raise HTTPException(
                status_code=404, 
                detail="Text file not found in session. Please upload text first."
            )

        # Process text data
        processed_text_path = process_text_data(text_path, session_dir)
        
        # Load processed data for response
        with open(processed_text_path, 'r', encoding='utf-8') as f:
            processed_data = json.load(f)

        # Return response
        return JSONResponse(
            status_code=200,
            content={
                "message": "Text processed successfully",
                "session_id": session_id,
                "processed_text_path": processed_text_path,
                "analysis_summary": {
                    "total_sentences": processed_data.get("content", {}).get("sentence_count", 0),
                    "dominant_sentiment": processed_data.get("analysis", {}).get("sentiment_analysis", {}).get("dominant_sentiment", "neutral"),
                    "dominant_personality_trait": processed_data.get("analysis", {}).get("personality_traits", {}).get("dominant_trait", "balanced"),
                    "communication_style": processed_data.get("analysis", {}).get("conversation_patterns", {}).get("communication_style", "balanced")
                },
                "processing_timestamp": datetime.now().isoformat()
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text processing failed: {str(e)}")

@app.post("/fine_tune_conversation/{session_id}")
async def fine_tune_conversation_endpoint(session_id: str, model_type: str = "prompt_based"):
    """
    Fine-tune a conversational model with processed text data.
    """
    try:
        # Define paths
        data_dir = "../data/"
        session_dir = os.path.join(data_dir, session_id)
        
        if not os.path.exists(session_dir):
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Check if text has been processed
        processed_text_path = os.path.join(session_dir, "processed_text.json")
        if not os.path.exists(processed_text_path):
            raise HTTPException(
                status_code=404, 
                detail="Text not processed yet. Please run /process_text/{session_id} first."
            )

        # Fine-tune conversational model
        model_data = fine_tune_conversation_model(processed_text_path, session_dir, model_type)

        # Return response
        return JSONResponse(
            status_code=200,
            content={
                "message": "Conversational model fine-tuned successfully",
                "session_id": session_id,
                "model_id": model_data["model_id"],
                "model_type": model_type,
                "model_metadata": {
                    "personality_profile": model_data["metadata"].get("personality_profile", {}),
                    "training_summary": model_data["metadata"].get("training_data_summary", {}),
                    "model_config": model_data["metadata"].get("conversation_config", {}).get("response_parameters", {})
                },
                "metadata_path": model_data["metadata_path"],
                "fine_tune_timestamp": datetime.now().isoformat()
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversational model fine-tuning failed: {str(e)}")

@app.post("/generate_conversation/{session_id}")
async def generate_conversation_endpoint(session_id: str, user_input: str, context: str = ""):
    """
    Generate a conversation response using the fine-tuned model.
    """
    try:
        # Define paths
        data_dir = "../data/"
        session_dir = os.path.join(data_dir, session_id)
        
        if not os.path.exists(session_dir):
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Load conversation model
        model_path = os.path.join(session_dir, "conversation_model.json")
        if not os.path.exists(model_path):
            raise HTTPException(
                status_code=404, 
                detail="Conversation model not found. Please run /fine_tune_conversation/{session_id} first."
            )
        
        with open(model_path, 'r', encoding='utf-8') as f:
            model_config = json.load(f)

        # Generate response
        response = generate_conversation_response(model_config, user_input, context)

        # Return response
        return JSONResponse(
            status_code=200,
            content={
                "message": "Conversation response generated successfully",
                "session_id": session_id,
                "model_id": model_config.get("model_id", "unknown"),
                "user_input": user_input,
                "generated_response": response,
                "context": context,
                "personality_info": {
                    "dominant_trait": model_config.get("personality_profile", {}).get("dominant_trait", "balanced"),
                    "communication_style": model_config.get("personality_profile", {}).get("communication_style", "balanced")
                },
                "generation_timestamp": datetime.now().isoformat()
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversation generation failed: {str(e)}")

@app.get("/conversation_model_info/{session_id}")
async def get_conversation_model_info_endpoint(session_id: str):
    """
    Get information about the conversation model for a session.
    """
    try:
        # Define paths
        data_dir = "../data/"
        session_dir = os.path.join(data_dir, session_id)
        model_path = os.path.join(session_dir, "conversation_model.json")
        
        if not os.path.exists(model_path):
            raise HTTPException(status_code=404, detail="Conversation model not found")
        
        # Load model configuration
        with open(model_path, 'r', encoding='utf-8') as f:
            model_config = json.load(f)
        
        return JSONResponse(
            status_code=200,
            content={
                "session_id": session_id,
                "model_info": model_config,
                "timestamp": datetime.now().isoformat()
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get conversation model info: {str(e)}")

@app.post("/interact/{session_id}")
async def interact_endpoint(
    session_id: str, 
    body: dict = Body(...),
    current_user: dict = Depends(get_current_user)
):
    """
    Generate a complete interactive video response combining conversation, voice, and avatar.
    """
    try:
        # Extract user input from request body
        user_input = body.get("input")
        if not user_input or not user_input.strip():
            raise HTTPException(status_code=400, detail="Input text is required and cannot be empty")
        
        # Check if session belongs to current user
        data_dir = "../data/"
        session_dir = os.path.join(data_dir, session_id)
        session_info = SessionManager.get_session_info(session_dir)
        
        if not session_info or session_info.get("user_id") != current_user["id"]:
            raise HTTPException(
                status_code=403,
                detail="Access denied: Session does not belong to current user"
            )
        
        # Check if user has given consent
        if not auth_manager.check_consent(current_user["id"], session_id):
            raise HTTPException(
                status_code=403,
                detail="Consent required: Please submit consent form before interacting"
            )
        
        # Check usage limits
        usage_status = auth_manager.check_usage_limits(current_user["id"], session_id)
        if not usage_status["allowed"]:
            raise HTTPException(
                status_code=429,
                detail=f"Daily usage limit exceeded. Limit: {usage_status['limit']}, Used: {usage_status['used']}"
            )

        # Load API keys from environment
        d_id_api_key = os.getenv("D_ID_API_KEY")
        elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        
        if not d_id_api_key:
            raise HTTPException(
                status_code=500, 
                detail="D-ID API key not configured. Please set D_ID_API_KEY environment variable."
            )
        
        if not elevenlabs_api_key:
            raise HTTPException(
                status_code=500, 
                detail="ElevenLabs API key not configured. Please set ELEVENLABS_API_KEY environment variable."
            )

        # Define paths
        data_dir = "../data/"
        session_dir = os.path.join(data_dir, session_id)
        
        if not os.path.exists(session_dir):
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Validate session requirements
        validation_results = validate_session_requirements(session_dir)
        if not validation_results.get("all_requirements_met", False):
            missing_requirements = [
                req for req, details in validation_results.items() 
                if isinstance(details, dict) and details.get("required") and not details.get("exists")
            ]
            raise HTTPException(
                status_code=400, 
                detail=f"Session requirements not met. Missing: {', '.join(missing_requirements)}. "
                       f"Please complete photo preprocessing, voice cloning, and conversation model setup."
            )

        # Generate interactive response
        video_path = generate_interactive_response(
            session_id, user_input, session_dir, d_id_api_key, elevenlabs_api_key
        )
        
        # Increment usage counter
        auth_manager.increment_usage(current_user["id"], session_id)
        
        # Update session metadata
        SessionManager.update_session_metadata(session_dir, {
            "usage": {
                "interactions_count": usage_status["used"] + 1,
                "last_interaction": datetime.now().isoformat()
            }
        })

        # Get video metadata
        video_size = os.path.getsize(video_path) if os.path.exists(video_path) else 0
        video_filename = os.path.basename(video_path)
        
        # Get updated usage status
        updated_usage = auth_manager.check_usage_limits(current_user["id"], session_id)

        # Return response
        return JSONResponse(
            status_code=200,
            content={
                "message": "Interactive response generated successfully",
                "session_id": session_id,
                "user_input": user_input,
                "video_path": video_path,
                "video_filename": video_filename,
                "video_metadata": {
                    "file_size": video_size,
                    "format": "MP4",
                    "duration_estimate": "5-15 seconds"
                },
                "processing_steps": [
                    "conversation_model_response",
                    "voice_synthesis", 
                    "avatar_video_generation",
                    "final_video_assembly"
                ],
                "usage_info": {
                    "remaining_interactions": updated_usage["remaining"],
                    "daily_limit": updated_usage["limit"]
                },
                "generation_timestamp": datetime.now().isoformat()
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Interactive response generation failed: {str(e)}")

@app.get("/interaction_history/{session_id}")
async def get_interaction_history_endpoint(session_id: str):
    """
    Get the interaction history for a session.
    """
    try:
        # Define paths
        data_dir = "../data/"
        session_dir = os.path.join(data_dir, session_id)
        
        if not os.path.exists(session_dir):
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get interaction history
        history = get_interaction_history(session_dir)
        
        return JSONResponse(
            status_code=200,
            content={
                "session_id": session_id,
                "interaction_history": history,
                "timestamp": datetime.now().isoformat()
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get interaction history: {str(e)}")

@app.get("/session_status/{session_id}")
async def get_session_status_endpoint(session_id: str):
    """
    Get the complete status of a session including all components.
    """
    try:
        # Define paths
        data_dir = "../data/"
        session_dir = os.path.join(data_dir, session_id)
        
        if not os.path.exists(session_dir):
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Validate session requirements
        validation_results = validate_session_requirements(session_dir)
        
        # Get interaction history
        history = get_interaction_history(session_dir)
        
        # Get session files info
        session_files = []
        for file in os.listdir(session_dir):
            file_path = os.path.join(session_dir, file)
            if os.path.isfile(file_path):
                file_stat = os.stat(file_path)
                session_files.append({
                    "filename": file,
                    "size": file_stat.st_size,
                    "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                })
        
        return JSONResponse(
            status_code=200,
            content={
                "session_id": session_id,
                "session_requirements": validation_results,
                "interaction_history": history,
                "session_files": session_files,
                "ready_for_interaction": validation_results.get("all_requirements_met", False),
                "timestamp": datetime.now().isoformat()
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get session status: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)