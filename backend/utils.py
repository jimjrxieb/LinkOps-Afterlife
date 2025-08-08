import os
import shutil
import json
import logging
from cryptography.fernet import Fernet
from datetime import datetime
from typing import Optional, Tuple, List
from fastapi import UploadFile
import mimetypes

logger = logging.getLogger(__name__)

class FileValidator:
    """Validates uploaded files for security and compliance."""
    
    ALLOWED_PHOTO_TYPES = {"image/jpeg", "image/jpg", "image/png"}
    ALLOWED_AUDIO_TYPES = {"audio/wav", "audio/mpeg", "audio/mp3", "audio/x-wav"}
    ALLOWED_TEXT_TYPES = {"text/plain", "text/txt"}
    
    MAX_PHOTO_SIZE = 5 * 1024 * 1024  # 5MB
    MAX_AUDIO_SIZE = 5 * 1024 * 1024  # 5MB
    MAX_TEXT_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_AUDIO_DURATION = 30  # seconds (we'll estimate based on file size)
    
    @staticmethod
    def validate_file_type(file: UploadFile, allowed_types: set, file_category: str) -> bool:
        """Validate file type against allowed types."""
        # Get MIME type from filename
        mime_type, _ = mimetypes.guess_type(file.filename)
        
        # Also check the content type provided by the client
        content_type = file.content_type
        
        # Check both MIME type and content type
        if mime_type not in allowed_types and content_type not in allowed_types:
            logger.warning(f"Invalid {file_category} file type: {mime_type} / {content_type}")
            return False
        
        return True
    
    @staticmethod
    def validate_file_size(file: UploadFile, max_size: int, file_category: str) -> bool:
        """Validate file size."""
        if file.size > max_size:
            logger.warning(f"{file_category} file too large: {file.size} bytes (max: {max_size})")
            return False
        return True
    
    @classmethod
    def validate_photo(cls, photo: UploadFile) -> Tuple[bool, str]:
        """Validate photo file."""
        if not cls.validate_file_type(photo, cls.ALLOWED_PHOTO_TYPES, "photo"):
            return False, "Invalid photo file type. Please upload JPG or PNG files only."
        
        if not cls.validate_file_size(photo, cls.MAX_PHOTO_SIZE, "photo"):
            return False, f"Photo file too large. Maximum size is {cls.MAX_PHOTO_SIZE // 1024 // 1024}MB."
        
        return True, "Photo validation passed"
    
    @classmethod
    def validate_photos(cls, photos: List[UploadFile]) -> Tuple[bool, str]:
        """Validate multiple photo files."""
        if not photos or len(photos) == 0:
            return False, "At least one photo is required."
        
        if len(photos) > 10:  # Limit to 10 photos max
            return False, "Too many photos. Maximum is 10 photos."
        
        for i, photo in enumerate(photos):
            photo_valid, photo_msg = cls.validate_photo(photo)
            if not photo_valid:
                return False, f"Photo {i+1}: {photo_msg}"
        
        return True, f"All {len(photos)} photos validation passed"
    
    @classmethod
    def validate_audio(cls, audio: UploadFile) -> Tuple[bool, str]:
        """Validate audio file."""
        if not cls.validate_file_type(audio, cls.ALLOWED_AUDIO_TYPES, "audio"):
            return False, "Invalid audio file type. Please upload WAV or MP3 files only."
        
        if not cls.validate_file_size(audio, cls.MAX_AUDIO_SIZE, "audio"):
            return False, f"Audio file too large. Maximum size is {cls.MAX_AUDIO_SIZE // 1024 // 1024}MB."
        
        # Estimate duration based on file size (rough estimate)
        estimated_duration = audio.size / (16000 * 2)  # Assuming 16kHz, 16-bit
        if estimated_duration > cls.MAX_AUDIO_DURATION:
            return False, f"Audio file too long. Maximum duration is {cls.MAX_AUDIO_DURATION} seconds."
        
        return True, "Audio validation passed"
    
    @classmethod
    def validate_text(cls, text: UploadFile) -> Tuple[bool, str]:
        """Validate text file."""
        if not cls.validate_file_type(text, cls.ALLOWED_TEXT_TYPES, "text"):
            return False, "Invalid text file type. Please upload TXT files only."
        
        if not cls.validate_file_size(text, cls.MAX_TEXT_SIZE, "text"):
            return False, f"Text file too large. Maximum size is {cls.MAX_TEXT_SIZE // 1024 // 1024}MB."
        
        return True, "Text validation passed"
    
    @classmethod
    def validate_all_files(cls, photos: List[UploadFile], audio: UploadFile, text: UploadFile) -> Tuple[bool, list]:
        """Validate all uploaded files with multiple photos support."""
        errors = []
        
        photos_valid, photos_msg = cls.validate_photos(photos)
        if not photos_valid:
            errors.append(photos_msg)
        
        audio_valid, audio_msg = cls.validate_audio(audio)
        if not audio_valid:
            errors.append(audio_msg)
        
        text_valid, text_msg = cls.validate_text(text)
        if not text_valid:
            errors.append(text_msg)
        
        return len(errors) == 0, errors


class FileEncryption:
    """Handles file encryption and decryption using Fernet symmetric encryption."""
    
    @staticmethod
    def generate_encryption_key(session_dir: str) -> str:
        """Generate and save an encryption key for a session."""
        try:
            os.makedirs(session_dir, exist_ok=True)
            
            key = Fernet.generate_key()
            key_path = os.path.join(session_dir, "encryption_key.key")
            
            with open(key_path, "wb") as key_file:
                key_file.write(key)
            
            # Set restrictive permissions on the key file
            os.chmod(key_path, 0o600)
            
            logger.info(f"Encryption key generated for session: {session_dir}")
            return key_path
            
        except Exception as e:
            logger.error(f"Error generating encryption key: {str(e)}")
            raise
    
    @staticmethod
    def load_encryption_key(key_path: str) -> bytes:
        """Load encryption key from file."""
        try:
            with open(key_path, "rb") as key_file:
                return key_file.read()
        except Exception as e:
            logger.error(f"Error loading encryption key: {str(e)}")
            raise
    
    @staticmethod
    def encrypt_file(file_path: str, key_path: str) -> str:
        """Encrypt a file and return the path to the encrypted file."""
        try:
            # Load encryption key
            key = FileEncryption.load_encryption_key(key_path)
            fernet = Fernet(key)
            
            # Read original file
            with open(file_path, "rb") as file:
                file_data = file.read()
            
            # Encrypt data
            encrypted_data = fernet.encrypt(file_data)
            
            # Save encrypted file
            encrypted_path = file_path + ".enc"
            with open(encrypted_path, "wb") as encrypted_file:
                encrypted_file.write(encrypted_data)
            
            # Remove original file for security
            os.remove(file_path)
            
            logger.info(f"File encrypted: {file_path} -> {encrypted_path}")
            return encrypted_path
            
        except Exception as e:
            logger.error(f"Error encrypting file: {str(e)}")
            raise
    
    @staticmethod
    def decrypt_file(encrypted_path: str, key_path: str, output_path: Optional[str] = None) -> str:
        """Decrypt a file and return the path to the decrypted file."""
        try:
            # Load encryption key
            key = FileEncryption.load_encryption_key(key_path)
            fernet = Fernet(key)
            
            # Read encrypted file
            with open(encrypted_path, "rb") as encrypted_file:
                encrypted_data = encrypted_file.read()
            
            # Decrypt data
            decrypted_data = fernet.decrypt(encrypted_data)
            
            # Determine output path
            if not output_path:
                output_path = encrypted_path.replace(".enc", "")
            
            # Save decrypted file
            with open(output_path, "wb") as decrypted_file:
                decrypted_file.write(decrypted_data)
            
            logger.info(f"File decrypted: {encrypted_path} -> {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error decrypting file: {str(e)}")
            raise
    
    @staticmethod
    def encrypt_session_files(session_dir: str) -> dict:
        """Encrypt all files in a session directory."""
        try:
            # Generate encryption key for this session
            key_path = FileEncryption.generate_encryption_key(session_dir)
            
            encrypted_files = {}
            
            # Find and encrypt all files (except the key file)
            for filename in os.listdir(session_dir):
                file_path = os.path.join(session_dir, filename)
                
                # Skip directories and the encryption key file
                if os.path.isdir(file_path) or filename == "encryption_key.key":
                    continue
                
                # Encrypt the file
                encrypted_path = FileEncryption.encrypt_file(file_path, key_path)
                encrypted_files[filename] = encrypted_path
            
            logger.info(f"All files encrypted in session: {session_dir}")
            return encrypted_files
            
        except Exception as e:
            logger.error(f"Error encrypting session files: {str(e)}")
            raise


class SessionManager:
    """Manages session data and cleanup."""
    
    @staticmethod
    def create_session_metadata(session_dir: str, user_id: int, session_id: str, upload_data: dict) -> str:
        """Create metadata file for a session."""
        try:
            metadata = {
                "session_id": session_id,
                "user_id": user_id,
                "created_at": datetime.now().isoformat(),
                "upload_data": upload_data,
                "processing_status": {
                    "photo_processed": False,
                    "voice_cloned": False,
                    "text_analyzed": False,
                    "conversation_trained": False,
                    "ready_for_interaction": False
                },
                "security": {
                    "files_encrypted": True,
                    "consent_given": False
                },
                "usage": {
                    "interactions_count": 0,
                    "last_interaction": None
                }
            }
            
            metadata_path = os.path.join(session_dir, "session_metadata.json")
            with open(metadata_path, "w") as metadata_file:
                json.dump(metadata, metadata_file, indent=2)
            
            logger.info(f"Session metadata created: {metadata_path}")
            return metadata_path
            
        except Exception as e:
            logger.error(f"Error creating session metadata: {str(e)}")
            raise
    
    @staticmethod
    def update_session_metadata(session_dir: str, updates: dict) -> bool:
        """Update session metadata with new information."""
        try:
            metadata_path = os.path.join(session_dir, "session_metadata.json")
            
            # Load existing metadata
            if os.path.exists(metadata_path):
                with open(metadata_path, "r") as metadata_file:
                    metadata = json.load(metadata_file)
            else:
                metadata = {}
            
            # Apply updates (deep merge)
            def deep_update(d, u):
                for k, v in u.items():
                    if isinstance(v, dict):
                        d[k] = deep_update(d.get(k, {}), v)
                    else:
                        d[k] = v
                return d
            
            metadata = deep_update(metadata, updates)
            metadata["last_updated"] = datetime.now().isoformat()
            
            # Save updated metadata
            with open(metadata_path, "w") as metadata_file:
                json.dump(metadata, metadata_file, indent=2)
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating session metadata: {str(e)}")
            return False
    
    @staticmethod
    def delete_session_data(session_dir: str) -> bool:
        """Securely delete all session data."""
        try:
            if not os.path.exists(session_dir):
                logger.warning(f"Session directory does not exist: {session_dir}")
                return True
            
            # Remove all files and directories
            shutil.rmtree(session_dir)
            
            logger.info(f"Session data deleted: {session_dir}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting session data: {str(e)}")
            return False
    
    @staticmethod
    def get_session_info(session_dir: str) -> Optional[dict]:
        """Get session information from metadata."""
        try:
            metadata_path = os.path.join(session_dir, "session_metadata.json")
            
            if not os.path.exists(metadata_path):
                return None
            
            with open(metadata_path, "r") as metadata_file:
                return json.load(metadata_file)
                
        except Exception as e:
            logger.error(f"Error getting session info: {str(e)}")
            return None


def save_upload_file(upload_file: UploadFile, destination: str) -> str:
    """Save an uploaded file to the specified destination."""
    try:
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        
        with open(destination, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        
        logger.info(f"File saved: {destination}")
        return destination
        
    except Exception as e:
        logger.error(f"Error saving upload file: {str(e)}")
        raise


def generate_secure_filename(original_filename: str, prefix: str = "") -> str:
    """Generate a secure filename with timestamp."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Clean the original filename
    name, ext = os.path.splitext(original_filename)
    clean_name = "".join(c for c in name if c.isalnum() or c in "._-")[:50]
    
    if prefix:
        return f"{prefix}_{timestamp}_{clean_name}{ext}"
    else:
        return f"{timestamp}_{clean_name}{ext}"