"""
Persona configuration loader for the AfterLife avatar system.
Handles loading and caching of persona YAML configurations.
"""
import os
import yaml
import logging
from typing import Dict, List
from persona_models import PersonaConfig

logger = logging.getLogger(__name__)

# Global cache for loaded personas
_PERSONA_CACHE: Dict[str, PersonaConfig] = {}


def load_persona(persona_id: str, base_dir: str = None) -> PersonaConfig:
    """
    Load a persona configuration from YAML file.
    
    Args:
        persona_id: Unique identifier for the persona
        base_dir: Base directory containing persona YAML files
        
    Returns:
        PersonaConfig: Loaded and validated persona configuration
        
    Raises:
        FileNotFoundError: If persona file doesn't exist
        ValidationError: If persona configuration is invalid
    """
    # Return cached persona if available
    if persona_id in _PERSONA_CACHE:
        logger.debug(f"Returning cached persona: {persona_id}")
        return _PERSONA_CACHE[persona_id]
    
    # Determine personas directory
    if base_dir is None:
        base_dir = os.getenv("PERSONA_DIR", "/app/data/personas")
    
    # Construct file path
    persona_file = f"{persona_id}.yaml"
    persona_path = os.path.join(base_dir, persona_file)
    
    # Check if file exists
    if not os.path.exists(persona_path):
        available_personas = list_available_personas(base_dir)
        logger.error(f"Persona file not found: {persona_path}")
        logger.info(f"Available personas: {available_personas}")
        raise FileNotFoundError(f"Persona '{persona_id}' not found. Available: {available_personas}")
    
    try:
        # Load and parse YAML
        with open(persona_path, "r", encoding="utf-8") as f:
            raw_data = yaml.safe_load(f)
        
        # Validate and create PersonaConfig object
        persona = PersonaConfig(**raw_data)
        
        # Cache the persona
        _PERSONA_CACHE[persona_id] = persona
        logger.info(f"Successfully loaded persona: {persona_id}")
        
        return persona
        
    except yaml.YAMLError as e:
        logger.error(f"YAML parsing error for {persona_path}: {e}")
        raise ValueError(f"Invalid YAML format in persona '{persona_id}': {e}")
    except Exception as e:
        logger.error(f"Error loading persona {persona_id}: {e}")
        raise ValueError(f"Failed to load persona '{persona_id}': {e}")


def list_available_personas(base_dir: str = None) -> List[str]:
    """
    List all available persona IDs in the personas directory.
    
    Args:
        base_dir: Base directory containing persona YAML files
        
    Returns:
        List[str]: List of available persona IDs
    """
    if base_dir is None:
        base_dir = os.getenv("PERSONA_DIR", "/app/data/personas")
    
    if not os.path.exists(base_dir):
        logger.warning(f"Personas directory does not exist: {base_dir}")
        return []
    
    personas = []
    for filename in os.listdir(base_dir):
        if filename.endswith(".yaml") or filename.endswith(".yml"):
            persona_id = filename.rsplit(".", 1)[0]  # Remove extension
            personas.append(persona_id)
    
    return sorted(personas)


def reload_persona(persona_id: str, base_dir: str = None) -> PersonaConfig:
    """
    Force reload a persona configuration, bypassing cache.
    
    Args:
        persona_id: Unique identifier for the persona
        base_dir: Base directory containing persona YAML files
        
    Returns:
        PersonaConfig: Reloaded persona configuration
    """
    # Remove from cache if present
    if persona_id in _PERSONA_CACHE:
        del _PERSONA_CACHE[persona_id]
        logger.info(f"Cleared cached persona: {persona_id}")
    
    # Load fresh copy
    return load_persona(persona_id, base_dir)


def get_cached_persona(persona_id: str) -> PersonaConfig:
    """
    Get a persona from cache only, without loading from file.
    
    Args:
        persona_id: Unique identifier for the persona
        
    Returns:
        PersonaConfig: Cached persona configuration
        
    Raises:
        KeyError: If persona is not in cache
    """
    if persona_id not in _PERSONA_CACHE:
        raise KeyError(f"Persona '{persona_id}' not found in cache")
    
    return _PERSONA_CACHE[persona_id]


def clear_persona_cache():
    """Clear all cached personas."""
    global _PERSONA_CACHE
    _PERSONA_CACHE.clear()
    logger.info("Cleared all cached personas")


# Initialize default personas on module import
def _initialize_default_personas():
    """Load default personas if they exist."""
    try:
        base_dir = os.getenv("PERSONA_DIR", "/app/data/personas")
        if os.path.exists(base_dir):
            available = list_available_personas(base_dir)
            logger.info(f"Found {len(available)} persona(s): {available}")
            
            # Auto-load commonly used personas
            default_personas = ["james", "default", "demo"]
            for persona_id in default_personas:
                if persona_id in available:
                    try:
                        load_persona(persona_id)
                        logger.info(f"Pre-loaded default persona: {persona_id}")
                    except Exception as e:
                        logger.warning(f"Failed to pre-load persona {persona_id}: {e}")
    except Exception as e:
        logger.warning(f"Failed to initialize default personas: {e}")


# Initialize on module import
_initialize_default_personas()