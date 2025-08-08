import json
import os
import uuid
from typing import Dict, List, Optional
from datetime import datetime
import logging
from persona_loader import load_persona, list_available_personas
from persona_models import PersonaConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fine_tune_conversation_model(processed_text_path: str, session_dir: str, model_type: str = "prompt_based") -> Dict:
    """
    Fine-tune a conversational model with processed text data.
    For this implementation, we create a prompt-based system rather than actual fine-tuning
    due to resource constraints. For production, this could be extended to use actual model fine-tuning.
    
    In demo mode, this returns a fixed, compassionate response for showcase purposes.
    
    Args:
        processed_text_path: Path to the processed text JSON
        session_dir: Directory to save model metadata
        model_type: Type of model to use ("prompt_based", "distilgpt2", "claude_api")
    Returns:
        Dictionary with model ID and metadata
    """
    try:
        logger.info(f"Starting conversation model fine-tuning for session: {session_dir}")
        
        # Check if in demo mode
        demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"
        
        if demo_mode:
            logger.info("Demo mode detected - creating fixed response model")
            return create_demo_model(session_dir)
        
        # Load processed text data
        with open(processed_text_path, 'r', encoding='utf-8') as f:
            processed_data = json.load(f)
        
        # Generate unique model ID
        model_id = f"linkops_conversation_{str(uuid.uuid4())[:8]}"
        
        if model_type == "prompt_based":
            model_data = create_prompt_based_model(processed_data, model_id, session_dir)
        elif model_type == "distilgpt2":
            model_data = create_lightweight_fine_tuned_model(processed_data, model_id, session_dir)
        else:
            model_data = create_prompt_based_model(processed_data, model_id, session_dir)
        
        # Save model metadata
        model_metadata_path = os.path.join(session_dir, "conversation_model.json")
        with open(model_metadata_path, 'w', encoding='utf-8') as f:
            json.dump(model_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Conversation model created successfully: {model_id}")
        
        return {
            "model_id": model_id,
            "metadata": model_data,
            "metadata_path": model_metadata_path
        }
        
    except Exception as e:
        logger.error(f"Conversation model fine-tuning failed: {str(e)}")
        raise Exception(f"Conversation model fine-tuning failed: {str(e)}")

def create_prompt_based_model(processed_data: Dict, model_id: str, session_dir: str) -> Dict:
    """
    Create a prompt-based conversational model using processed personality data with bio enhancement.
    This approach uses sophisticated prompt engineering instead of actual model fine-tuning.
    """
    analysis = processed_data.get("analysis", {})
    personality = analysis.get("personality_traits", {})
    conversation_patterns = analysis.get("conversation_patterns", {})
    bio_insights = analysis.get("bio_insights", {})
    
    # Extract key personality characteristics
    personality_scores = personality.get("scores", {})
    dominant_trait = personality.get("dominant_trait", "balanced")
    communication_style = conversation_patterns.get("communication_style", "balanced")
    
    # Create bio-enhanced personality prompt
    personality_prompt = generate_bio_enhanced_personality_prompt(
        personality_scores, dominant_trait, communication_style, bio_insights
    )
    
    # Create conversation examples
    training_examples = processed_data.get("training_data", {}).get("conversation_examples", [])
    example_prompts = create_example_prompts(training_examples[:5])  # Use top 5 examples
    
    # Get bio-enhanced prompts
    bio_enhanced_prompts = processed_data.get("training_data", {}).get("bio_enhanced_prompts", [])
    
    # Create style guidelines
    style_guidelines = generate_style_guidelines(conversation_patterns, analysis.get("sentiment_analysis", {}))
    
    # Compile model configuration
    model_config = {
        "model_id": model_id,
        "model_type": "prompt_based",
        "created_timestamp": datetime.now().isoformat(),
        "session_dir": session_dir,
        "personality_profile": {
            "dominant_trait": dominant_trait,
            "personality_scores": personality_scores,
            "communication_style": communication_style,
            "description": personality.get("description", "Balanced personality")
        },
        "conversation_config": {
            "base_prompt": personality_prompt,
            "style_guidelines": style_guidelines,
            "example_conversations": example_prompts,
            "bio_enhanced_prompts": bio_enhanced_prompts,
            "bio_context": {
                "nicknames": bio_insights.get("nicknames", []),
                "family_members": bio_insights.get("family_members", []),
                "profession": bio_insights.get("profession", ""),
                "locations": bio_insights.get("locations", []),
                "personality_descriptors": bio_insights.get("personality_descriptors", []),
                "hobbies_interests": bio_insights.get("hobbies_interests", []),
                "important_facts": bio_insights.get("important_facts", [])
            },
            "response_parameters": {
                "max_length": determine_response_length(conversation_patterns),
                "temperature": determine_temperature(personality_scores),
                "tone": determine_tone(analysis.get("sentiment_analysis", {})),
                "use_bio_context": bool(bio_insights)
            }
        },
        "training_data_summary": {
            "total_sentences": processed_data.get("content", {}).get("sentence_count", 0),
            "dominant_sentiment": analysis.get("sentiment_analysis", {}).get("dominant_sentiment", "neutral"),
            "language": processed_data.get("session_metadata", {}).get("language", "english")
        }
    }
    
    return model_config

def create_lightweight_fine_tuned_model(processed_data: Dict, model_id: str, session_dir: str) -> Dict:
    """
    Create a lightweight fine-tuned model using DistilGPT-2.
    This is a placeholder for actual fine-tuning implementation.
    In production, this would involve actual model training.
    """
    logger.info("Creating lightweight fine-tuned model (simulation)")
    
    # For now, create a configuration that simulates fine-tuning
    # In production, this would involve actual transformers training
    
    analysis = processed_data.get("analysis", {})
    training_examples = processed_data.get("training_data", {}).get("conversation_examples", [])
    
    # Simulate model training metrics
    simulated_metrics = {
        "training_loss": 2.4 - (len(training_examples) * 0.05),  # Simulated improvement
        "validation_loss": 2.6 - (len(training_examples) * 0.04),
        "perplexity": 12.5 - (len(training_examples) * 0.2),
        "epochs": min(max(len(training_examples) // 5, 1), 10),
        "learning_rate": 5e-5,
        "batch_size": 4
    }
    
    model_config = {
        "model_id": model_id,
        "model_type": "distilgpt2_fine_tuned",
        "created_timestamp": datetime.now().isoformat(),
        "session_dir": session_dir,
        "base_model": "distilgpt2",
        "training_config": {
            "training_examples": len(training_examples),
            "training_metrics": simulated_metrics,
            "fine_tuning_approach": "lightweight",
            "model_size": "117M parameters (DistilGPT-2)"
        },
        "personality_adaptation": {
            "dominant_trait": analysis.get("personality_traits", {}).get("dominant_trait", "balanced"),
            "sentiment_bias": analysis.get("sentiment_analysis", {}).get("dominant_sentiment", "neutral"),
            "communication_style": analysis.get("conversation_patterns", {}).get("communication_style", "balanced")
        },
        "model_path": os.path.join(session_dir, f"{model_id}_model"),  # Where model would be saved
        "tokenizer_path": os.path.join(session_dir, f"{model_id}_tokenizer")
    }
    
    # Create model directory structure (simulation)
    model_dir = os.path.join(session_dir, f"{model_id}_model")
    os.makedirs(model_dir, exist_ok=True)
    
    # Save a placeholder configuration file
    with open(os.path.join(model_dir, "config.json"), 'w') as f:
        json.dump({
            "model_type": "distilgpt2",
            "fine_tuned": True,
            "session_id": model_id,
            "created": datetime.now().isoformat()
        }, f, indent=2)
    
    return model_config

def generate_bio_enhanced_personality_prompt(personality_scores: Dict, dominant_trait: str, communication_style: str, bio_insights: Dict) -> str:
    """Generate a bio-enhanced personality-based prompt for conversation generation."""
    
    trait_descriptions = {
        "extraversion": "outgoing, social, and energetic",
        "agreeableness": "kind, cooperative, and empathetic", 
        "conscientiousness": "organized, responsible, and detail-oriented",
        "neuroticism": "emotionally sensitive and expressive",
        "openness": "creative, curious, and open to new experiences"
    }
    
    style_descriptions = {
        "energetic_brief": "speaks in short, enthusiastic bursts",
        "thoughtful_detailed": "provides comprehensive, well-considered responses",
        "enthusiastic": "expresses excitement and positivity frequently",
        "inquisitive": "asks thoughtful questions and shows genuine curiosity",
        "balanced": "maintains a steady, measured communication approach"
    }
    
    # Start with basic personality prompt
    base_prompt = f"""You are embodying the personality and communication style of someone who is primarily {trait_descriptions.get(dominant_trait, 'balanced')} and {style_descriptions.get(communication_style, 'communicates naturally')}."""
    
    # Enhance with biographical context
    if bio_insights:
        bio_sections = []
        
        # Add nickname context
        if bio_insights.get("nicknames"):
            nicknames = ", ".join(bio_insights["nicknames"][:2])
            bio_sections.append(f"Your loved ones call you {nicknames}")
        
        # Add family context
        if bio_insights.get("family_members"):
            family_members = "; ".join(bio_insights["family_members"][:4])
            bio_sections.append(f"Your family includes {family_members}")
        
        # Add profession context
        if bio_insights.get("profession"):
            bio_sections.append(f"You work as a {bio_insights['profession']}")
        
        # Add location context
        if bio_insights.get("locations"):
            location = bio_insights["locations"][0]
            bio_sections.append(f"You're from {location}")
        
        # Add personality descriptors
        if bio_insights.get("personality_descriptors"):
            descriptors = ", ".join(bio_insights["personality_descriptors"][:3])
            bio_sections.append(f"People describe you as {descriptors}")
        
        # Add hobbies/interests
        if bio_insights.get("hobbies_interests"):
            interests = ", ".join(bio_insights["hobbies_interests"][:3])
            bio_sections.append(f"You enjoy {interests}")
        
        if bio_sections:
            bio_context = ". ".join(bio_sections) + "."
            base_prompt += f"\n\nPersonal Background: {bio_context}"
            
            # Add instruction for using bio context
            base_prompt += "\n\nWhen responding, naturally incorporate these personal details when relevant. Use nicknames when appropriate, reference your family and background organically, and let your profession and interests influence your perspective and advice."
    
    return base_prompt

def generate_personality_prompt(personality_scores: Dict, dominant_trait: str, communication_style: str) -> str:
    """Generate a personality-based prompt for conversation generation (legacy function)."""
    return generate_bio_enhanced_personality_prompt(personality_scores, dominant_trait, communication_style, {})

def create_example_prompts(training_examples: List[Dict]) -> List[Dict]:
    """Create example conversation prompts from training data."""
    example_prompts = []
    
    for i, example in enumerate(training_examples[:5]):
        example_prompts.append({
            "id": i + 1,
            "context": example.get("context", "personal_conversation"),
            "input": example.get("prompt", ""),
            "expected_output": example.get("response", ""),
            "usage": "conversation_style_reference"
        })
    
    return example_prompts

def generate_style_guidelines(conversation_patterns: Dict, sentiment_analysis: Dict) -> Dict:
    """Generate style guidelines based on conversation analysis."""
    
    guidelines = {
        "sentence_length": {
            "preferred_length": conversation_patterns.get("avg_sentence_length", 15),
            "category": conversation_patterns.get("sentence_length_category", "medium"),
            "guideline": f"Aim for {conversation_patterns.get('sentence_length_category', 'medium')} length responses"
        },
        "punctuation_style": {
            "exclamation_frequency": conversation_patterns.get("punctuation_style", {}).get("exclamation_frequency", 0),
            "enthusiasm_level": conversation_patterns.get("punctuation_style", {}).get("enthusiasm_level", "normal"),
            "guideline": "Match the observed punctuation patterns and enthusiasm level"
        },
        "emotional_tone": {
            "dominant_sentiment": sentiment_analysis.get("dominant_sentiment", "neutral"),
            "positive_ratio": sentiment_analysis.get("overall_sentiment", {}).get("positive_ratio", 0.5),
            "guideline": f"Maintain a generally {sentiment_analysis.get('dominant_sentiment', 'neutral')} tone"
        },
        "vocabulary": {
            "common_words": conversation_patterns.get("common_words", [])[:5],
            "guideline": "Use vocabulary patterns consistent with the training examples"
        }
    }
    
    return guidelines

def determine_response_length(conversation_patterns: Dict) -> int:
    """Determine appropriate response length based on patterns."""
    avg_length = conversation_patterns.get("avg_sentence_length", 15)
    
    if avg_length < 8:
        return 50  # Short, concise responses
    elif avg_length < 20:
        return 100  # Medium length responses
    else:
        return 150  # Longer, more detailed responses

def determine_temperature(personality_scores: Dict) -> float:
    """Determine conversation temperature based on personality."""
    openness = personality_scores.get("openness", 0.5)
    extraversion = personality_scores.get("extraversion", 0.5)
    
    # Higher openness and extraversion = more creative/varied responses
    base_temp = 0.7
    personality_adjustment = (openness + extraversion) * 0.2
    
    return min(max(base_temp + personality_adjustment, 0.3), 1.0)

def determine_tone(sentiment_analysis: Dict) -> str:
    """Determine conversational tone based on sentiment analysis."""
    dominant_sentiment = sentiment_analysis.get("dominant_sentiment", "neutral")
    positive_ratio = sentiment_analysis.get("overall_sentiment", {}).get("positive_ratio", 0.5)
    
    if dominant_sentiment == "positive" and positive_ratio > 0.6:
        return "optimistic"
    elif dominant_sentiment == "negative":
        return "thoughtful"
    else:
        return "balanced"

def generate_conversation_response(model_config: Dict, user_input: str, context: str = "") -> str:
    """
    Generate a conversation response using the configured personality model with bio enhancement.
    This function would be used by the API to generate responses.
    """
    conversation_config = model_config.get("conversation_config", {})
    base_prompt = conversation_config.get("base_prompt", "")
    style_guidelines = conversation_config.get("style_guidelines", {})
    bio_context = conversation_config.get("bio_context", {})
    bio_enhanced_prompts = conversation_config.get("bio_enhanced_prompts", [])
    
    # This is a simplified implementation
    # In production, this would interface with a language model
    
    response_config = conversation_config.get("response_parameters", {})
    max_length = response_config.get("max_length", 100)
    tone = response_config.get("tone", "balanced")
    use_bio_context = response_config.get("use_bio_context", False)
    
    # Enhanced response generation with bio context
    personality_trait = model_config.get('personality_profile', {}).get('dominant_trait', 'balanced')
    
    # Build contextual information for response
    response_context = f"[{personality_trait} personality, {tone} tone"
    
    if use_bio_context and bio_context:
        bio_elements = []
        if bio_context.get("nicknames"):
            bio_elements.append(f"nicknames: {', '.join(bio_context['nicknames'][:2])}")
        if bio_context.get("profession"):
            bio_elements.append(f"profession: {bio_context['profession']}")
        if bio_context.get("locations"):
            bio_elements.append(f"from: {bio_context['locations'][0]}")
        
        if bio_elements:
            response_context += f", with bio context: {'; '.join(bio_elements)}"
    
    response_context += f", max {max_length} characters]"
    
    # Placeholder response generation with enhanced context
    # In production, this would use the actual model to generate responses
    # The bio_enhanced_prompts would be used to guide the model's behavior
    simulated_response = f"[Bio-enhanced response based on {response_context}]"
    
    return simulated_response

def validate_model_config(model_config: Dict) -> bool:
    """Validate the model configuration."""
    required_fields = ["model_id", "model_type", "created_timestamp"]


# ====== PERSONA-BASED CONVERSATION SYSTEM ======

PERSONA_SYSTEM_TEMPLATE = """You are {display_name}.

Communication Style:
- Tone: {tone}
- Formality: {register}
- Quirks: {quirks}

Professional Background:
{bio}

Elevator Pitch:
{elevator_pitch}

Key Highlights:
{highlights}

Projects:
{projects}

Certifications: {certs}

Boundaries: 
- Safe topics: {safe_topics}
- Avoid discussing: {avoid_topics}
- If asked about avoided topics, use one of these responses: {refusals}

Guidelines:
- Answer clearly and concisely
- Use step-by-step explanations when giving instructions
- Stay in character and maintain your professional tone
- When appropriate, reference your projects and experience
- If a question matches your pinned Q&A, prefer that answer but expand naturally
"""


def build_persona_system_prompt(persona: PersonaConfig) -> str:
    """
    Build a comprehensive system prompt from a persona configuration.
    
    Args:
        persona: PersonaConfig object with all persona details
        
    Returns:
        str: Formatted system prompt for the conversation model
    """
    # Format projects as bullet points
    projects_text = "\n".join([f"- {name}: {desc}" for name, desc in persona.memory.projects.items()])
    
    return PERSONA_SYSTEM_TEMPLATE.format(
        display_name=persona.display_name,
        tone=persona.style.tone,
        register=persona.style.register,
        quirks="; ".join(persona.style.quirks) if persona.style.quirks else "None specified",
        bio=persona.memory.bio,
        elevator_pitch=persona.memory.elevator_pitch,
        highlights="\\n".join([f"• {h}" for h in persona.memory.highlights]),
        projects=projects_text,
        certs=", ".join(persona.memory.certs) if persona.memory.certs else "None listed",
        safe_topics=", ".join(persona.boundaries.safe_topics),
        avoid_topics=", ".join(persona.boundaries.avoid_topics),
        refusals=" / ".join(persona.boundaries.refusals)
    )


def find_matching_pinned_qa(persona: PersonaConfig, user_input: str) -> Optional[Dict[str, str]]:
    """
    Find a matching pinned Q&A pair for the user input.
    
    Args:
        persona: PersonaConfig with pinned Q&A pairs
        user_input: User's question/input
        
    Returns:
        Dict with 'q' and 'a' keys if match found, None otherwise
    """
    user_input_lower = user_input.lower()
    
    for qa_pair in persona.qa.pinned:
        question_lower = qa_pair["q"].lower()
        
        # Simple keyword matching - could be enhanced with semantic similarity
        if any(word in user_input_lower for word in question_lower.split() if len(word) > 3):
            return qa_pair
    
    return None


def generate_persona_response(persona_id: str, user_input: str, context: str = "") -> Dict[str, str]:
    """
    Generate a conversation response using persona-based prompting.
    
    Args:
        persona_id: ID of the persona to use
        user_input: User's message/question
        context: Additional context for the conversation
        
    Returns:
        Dict with 'answer', 'persona_id', 'tts_voice', and 'matched_qa' keys
    """
    try:
        # Load persona configuration
        persona = load_persona(persona_id)
        
        # Build system prompt
        system_prompt = build_persona_system_prompt(persona)
        
        # Check for matching pinned Q&A
        matched_qa = find_matching_pinned_qa(persona, user_input)
        
        # Build guided response context if we found a match
        guided_context = ""
        if matched_qa:
            guided_context = f"\\nPinned Q&A Reference (expand naturally on this):\\nQ: {matched_qa['q']}\\nA: {matched_qa['a']}\\n"
        
        # For now, return a structured response
        # In production, this would call your LLM with the system prompt
        if matched_qa:
            # Use pinned answer as base, but could be enhanced by LLM
            response = matched_qa["a"]
        else:
            # Generate contextual response based on persona
            response = generate_contextual_response(persona, user_input)
        
        return {
            "answer": response,
            "persona_id": persona_id,
            "persona_name": persona.display_name,
            "tts_voice": persona.tts_voice,
            "matched_qa": matched_qa is not None,
            "system_prompt_preview": system_prompt[:200] + "..." if len(system_prompt) > 200 else system_prompt
        }
        
    except FileNotFoundError:
        logger.error(f"Persona not found: {persona_id}")
        return {
            "answer": f"Sorry, I couldn't find the persona '{persona_id}'. Available personas: {list_available_personas()}",
            "persona_id": persona_id,
            "persona_name": "Unknown",
            "tts_voice": None,
            "matched_qa": False,
            "error": "Persona not found"
        }
    except Exception as e:
        logger.error(f"Error generating persona response: {e}")
        return {
            "answer": f"I'm having trouble processing that request. Error: {str(e)}",
            "persona_id": persona_id,
            "persona_name": "Error",
            "tts_voice": None,
            "matched_qa": False,
            "error": str(e)
        }


def generate_contextual_response(persona: PersonaConfig, user_input: str) -> str:
    """
    Generate a contextual response based on persona characteristics.
    This is a simplified version - in production, this would use an LLM.
    
    Args:
        persona: PersonaConfig object
        user_input: User's input/question
        
    Returns:
        str: Generated response
    """
    user_lower = user_input.lower()
    
    # Check for project-related questions
    for project_name, project_desc in persona.memory.projects.items():
        if project_name.lower() in user_lower:
            return f"Great question about {project_name}! {project_desc}. I built this because I believe in {persona.memory.elevator_pitch.split('.')[0].lower()}."
    
    # Check for skills/certification questions
    if any(cert.lower() in user_lower for cert in persona.memory.certs):
        return f"Yes, I'm certified in {', '.join(persona.memory.certs)}. These certifications are crucial for the work I do in {persona.memory.bio.split('.')[0].lower()}."
    
    # Check for general "about you" questions
    if any(word in user_lower for word in ["who", "about", "tell me", "background"]):
        return f"{persona.memory.elevator_pitch} Some highlights of my work include: {'; '.join(persona.memory.highlights[:2])}."
    
    # Default response with personality
    return f"That's an interesting question! {persona.memory.bio.split('.')[0]}. I'd be happy to discuss how this relates to my work with {', '.join(list(persona.memory.projects.keys())[:2])}."
    
    for field in required_fields:
        if field not in model_config:
            return False
    
    return True