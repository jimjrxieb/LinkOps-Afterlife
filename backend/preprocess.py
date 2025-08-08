import cv2
import numpy as np
from PIL import Image, ImageEnhance
import os
from typing import Tuple, Optional, List
import logging

logger = logging.getLogger(__name__)

def preprocess_photo(photo_path: str, session_dir: str) -> str:
    """
    Preprocess the uploaded photo for avatar generation.
    Args:
        photo_path: Path to the uploaded photo
        session_dir: Directory to save the preprocessed photo
    Returns:
        Path to the preprocessed photo
    """
    # Load image using OpenCV
    img = cv2.imread(photo_path)
    if img is None:
        raise ValueError("Failed to load image")

    # Convert BGR to RGB for PIL processing
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Detect face using Haar Cascade
    face_center, face_size = detect_and_align_face(img)
    
    # Crop and resize based on face detection
    if face_center is not None:
        img_processed = crop_face_region(img, face_center, face_size)
    else:
        # If no face detected, resize the entire image
        img_processed = img
    
    # Resize to 512x512 pixels
    img_resized = cv2.resize(img_processed, (512, 512), interpolation=cv2.INTER_LANCZOS4)
    
    # Convert to PIL for quality enhancement
    pil_img = Image.fromarray(cv2.cvtColor(img_resized, cv2.COLOR_BGR2RGB))
    
    # Enhance image quality
    enhanced_img = enhance_image_quality(pil_img)
    
    # Convert back to OpenCV format
    final_img = cv2.cvtColor(np.array(enhanced_img), cv2.COLOR_RGB2BGR)
    
    # Save preprocessed image
    preprocessed_filename = "preprocessed_photo.jpg"
    preprocessed_path = os.path.join(session_dir, preprocessed_filename)
    
    # Save with high quality
    cv2.imwrite(preprocessed_path, final_img, [cv2.IMWRITE_JPEG_QUALITY, 95])
    
    return preprocessed_path

def detect_and_align_face(img: np.ndarray) -> Tuple[Optional[Tuple[int, int]], Optional[int]]:
    """
    Detect face in the image and return center coordinates and size.
    Returns:
        Tuple of (face_center, face_size) or (None, None) if no face detected
    """
    # Load Haar Cascade classifier for face detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Convert to grayscale for face detection
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Detect faces
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    
    if len(faces) > 0:
        # Use the largest face detected
        largest_face = max(faces, key=lambda f: f[2] * f[3])
        x, y, w, h = largest_face
        
        # Calculate face center
        face_center = (x + w // 2, y + h // 2)
        face_size = max(w, h)
        
        return face_center, face_size
    
    return None, None

def crop_face_region(img: np.ndarray, face_center: Tuple[int, int], face_size: int) -> np.ndarray:
    """
    Crop the image around the detected face with some padding.
    """
    height, width = img.shape[:2]
    center_x, center_y = face_center
    
    # Add padding around the face (1.5x the face size)
    crop_size = int(face_size * 1.8)
    
    # Calculate crop boundaries
    left = max(0, center_x - crop_size // 2)
    right = min(width, center_x + crop_size // 2)
    top = max(0, center_y - crop_size // 2)
    bottom = min(height, center_y + crop_size // 2)
    
    # Crop the image
    cropped = img[top:bottom, left:right]
    
    # If crop is too small, return original image
    if cropped.shape[0] < 100 or cropped.shape[1] < 100:
        return img
    
    return cropped

def enhance_image_quality(pil_img: Image.Image) -> Image.Image:
    """
    Enhance image quality by adjusting brightness, contrast, and sharpness.
    """
    # Enhance contrast
    contrast_enhancer = ImageEnhance.Contrast(pil_img)
    enhanced_img = contrast_enhancer.enhance(1.1)  # Slight contrast boost
    
    # Enhance brightness
    brightness_enhancer = ImageEnhance.Brightness(enhanced_img)
    enhanced_img = brightness_enhancer.enhance(1.05)  # Slight brightness boost
    
    # Enhance sharpness
    sharpness_enhancer = ImageEnhance.Sharpness(enhanced_img)
    enhanced_img = sharpness_enhancer.enhance(1.1)  # Slight sharpness boost
    
    return enhanced_img

def get_image_info(image_path: str) -> dict:
    """
    Get information about the processed image.
    """
    if not os.path.exists(image_path):
        return {}
    
    # Get file size
    file_size = os.path.getsize(image_path)
    
    # Load image to get dimensions
    img = cv2.imread(image_path)
    if img is not None:
        height, width = img.shape[:2]
        return {
            "width": width,
            "height": height,
            "file_size": file_size,
            "format": "JPEG"
        }
    
    return {"file_size": file_size}

def process_multiple_photos(photo_paths: List[str], session_dir: str, method: str = "best_selection") -> str:
    """
    Process multiple photos using AI/ML techniques for enhanced avatar quality.
    
    Args:
        photo_paths: List of paths to uploaded photos
        session_dir: Directory to save the processed photo
        method: Processing method - "best_selection" or "face_averaging"
    
    Returns:
        Path to the final processed photo
    """
    if not photo_paths:
        raise ValueError("No photos provided for processing")
    
    if len(photo_paths) == 1:
        # If only one photo, use standard preprocessing
        return preprocess_photo(photo_paths[0], session_dir)
    
    logger.info(f"Processing {len(photo_paths)} photos using {method} method")
    
    if method == "face_averaging":
        return process_face_averaging(photo_paths, session_dir)
    else:  # best_selection
        return process_best_selection(photo_paths, session_dir)

def process_best_selection(photo_paths: List[str], session_dir: str) -> str:
    """
    Select the best photo based on face quality metrics.
    
    Face quality is determined by:
    - Face detection confidence
    - Image sharpness
    - Face size relative to image
    - Image quality metrics
    """
    best_photo = None
    best_score = -1
    best_path = None
    
    logger.info("Analyzing photos for best selection...")
    
    for i, photo_path in enumerate(photo_paths):
        try:
            # Load image
            img = cv2.imread(photo_path)
            if img is None:
                logger.warning(f"Could not load photo {i+1}: {photo_path}")
                continue
            
            # Calculate quality score
            score = calculate_photo_quality_score(img)
            logger.info(f"Photo {i+1} quality score: {score:.2f}")
            
            if score > best_score:
                best_score = score
                best_photo = img
                best_path = photo_path
                
        except Exception as e:
            logger.error(f"Error processing photo {i+1}: {str(e)}")
            continue
    
    if best_photo is None:
        raise ValueError("No valid photos found for processing")
    
    logger.info(f"Selected best photo with quality score: {best_score:.2f}")
    
    # Process the best photo using standard preprocessing
    return preprocess_photo(best_path, session_dir)

def calculate_photo_quality_score(img: np.ndarray) -> float:
    """
    Calculate a quality score for a photo based on multiple metrics.
    
    Returns:
        Quality score (higher is better)
    """
    score = 0.0
    
    # Face detection score (40% of total score)
    face_score = calculate_face_score(img)
    score += face_score * 0.4
    
    # Sharpness score (30% of total score)
    sharpness_score = calculate_sharpness_score(img)
    score += sharpness_score * 0.3
    
    # Brightness/contrast score (20% of total score)
    lighting_score = calculate_lighting_score(img)
    score += lighting_score * 0.2
    
    # Resolution score (10% of total score)
    resolution_score = calculate_resolution_score(img)
    score += resolution_score * 0.1
    
    return score

def calculate_face_score(img: np.ndarray) -> float:
    """Calculate face detection score."""
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
    )
    
    if len(faces) == 0:
        return 0.0
    
    # Use the largest face
    largest_face = max(faces, key=lambda f: f[2] * f[3])
    x, y, w, h = largest_face
    
    # Score based on face size relative to image
    img_area = img.shape[0] * img.shape[1]
    face_area = w * h
    face_ratio = face_area / img_area
    
    # Optimal face ratio is around 0.1-0.3 of image
    if 0.1 <= face_ratio <= 0.3:
        return 100.0
    elif face_ratio > 0.3:
        return 100.0 - min(50.0, (face_ratio - 0.3) * 200)
    else:
        return face_ratio * 1000  # Boost small faces

def calculate_sharpness_score(img: np.ndarray) -> float:
    """Calculate image sharpness using Laplacian variance."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
    
    # Normalize to 0-100 scale
    return min(100.0, laplacian_var / 10.0)

def calculate_lighting_score(img: np.ndarray) -> float:
    """Calculate lighting quality score."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    mean_brightness = np.mean(gray)
    std_contrast = np.std(gray)
    
    # Optimal brightness is around 100-150
    brightness_score = 100.0 - abs(mean_brightness - 125.0)
    brightness_score = max(0.0, brightness_score)
    
    # Good contrast should have std > 30
    contrast_score = min(100.0, std_contrast * 2.0)
    
    return (brightness_score + contrast_score) / 2.0

def calculate_resolution_score(img: np.ndarray) -> float:
    """Calculate resolution quality score."""
    height, width = img.shape[:2]
    total_pixels = height * width
    
    # Score based on resolution
    if total_pixels >= 1000000:  # 1MP+
        return 100.0
    elif total_pixels >= 500000:  # 0.5MP+
        return 80.0
    elif total_pixels >= 300000:  # 0.3MP+
        return 60.0
    else:
        return 40.0

def process_face_averaging(photo_paths: List[str], session_dir: str) -> str:
    """
    Create an averaged face from multiple photos.
    
    This is a simplified face averaging implementation.
    For production, consider using more sophisticated techniques like:
    - Facial landmark detection
    - Procrustes analysis for alignment
    - Delaunay triangulation for morphing
    """
    logger.info("Processing face averaging...")
    
    valid_faces = []
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Extract and normalize faces from all photos
    for i, photo_path in enumerate(photo_paths):
        try:
            img = cv2.imread(photo_path)
            if img is None:
                continue
                
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
            
            if len(faces) > 0:
                # Use the largest face
                x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
                
                # Extract face region with padding
                padding = int(max(w, h) * 0.3)
                x1 = max(0, x - padding)
                y1 = max(0, y - padding)
                x2 = min(img.shape[1], x + w + padding)
                y2 = min(img.shape[0], y + h + padding)
                
                face_region = img[y1:y2, x1:x2]
                
                # Resize to standard size for averaging
                face_resized = cv2.resize(face_region, (256, 256))
                valid_faces.append(face_resized)
                
                logger.info(f"Extracted face from photo {i+1}")
                
        except Exception as e:
            logger.error(f"Error extracting face from photo {i+1}: {str(e)}")
            continue
    
    if not valid_faces:
        logger.warning("No faces found, falling back to best selection")
        return process_best_selection(photo_paths, session_dir)
    
    if len(valid_faces) == 1:
        logger.info("Only one face found, using standard preprocessing")
        return preprocess_photo(photo_paths[0], session_dir)
    
    # Average the faces
    logger.info(f"Averaging {len(valid_faces)} faces...")
    averaged_face = np.mean(valid_faces, axis=0).astype(np.uint8)
    
    # Resize to final size
    final_face = cv2.resize(averaged_face, (512, 512))
    
    # Enhance the averaged face
    pil_img = Image.fromarray(cv2.cvtColor(final_face, cv2.COLOR_BGR2RGB))
    enhanced_img = enhance_image_quality(pil_img)
    final_img = cv2.cvtColor(np.array(enhanced_img), cv2.COLOR_RGB2BGR)
    
    # Save the averaged face
    averaged_filename = "preprocessed_photo_averaged.jpg"
    averaged_path = os.path.join(session_dir, averaged_filename)
    cv2.imwrite(averaged_path, final_img, [cv2.IMWRITE_JPEG_QUALITY, 95])
    
    logger.info(f"Face averaging completed: {averaged_path}")
    return averaged_path