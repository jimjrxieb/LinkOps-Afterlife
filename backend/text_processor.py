import nltk
import re
import json
import os
from typing import Dict, List, Optional
from datetime import datetime
from transformers import pipeline, AutoTokenizer
from collections import Counter
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download required NLTK data
def download_nltk_data():
    """Download required NLTK data if not already present."""
    try:
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('vader_lexicon', quiet=True)

def process_text_data(text_path: str, session_dir: str, bio_path: Optional[str] = None) -> str:
    """
    Process uploaded text data for personality analysis and conversation modeling.
    Args:
        text_path: Path to the uploaded text file
        session_dir: Directory to save processed text
        bio_path: Optional path to biographical information file
    Returns:
        Path to the processed text JSON
    """
    try:
        # Ensure NLTK data is downloaded
        download_nltk_data()
        
        logger.info(f"Processing text file: {text_path}")
        
        # Read the text file
        with open(text_path, 'r', encoding='utf-8', errors='ignore') as file:
            raw_text = file.read()
        
        if not raw_text.strip():
            raise ValueError("Text file is empty or contains no readable content")
        
        # Read biographical information if provided
        bio_text = ""
        bio_insights = {}
        if bio_path and os.path.exists(bio_path):
            logger.info(f"Loading biographical information from: {bio_path}")
            try:
                with open(bio_path, 'r', encoding='utf-8', errors='ignore') as bio_file:
                    bio_text = bio_file.read().strip()
                
                if bio_text:
                    bio_insights = extract_bio_insights(bio_text)
                    logger.info(f"Extracted bio insights: {list(bio_insights.keys())}")
            except Exception as e:
                logger.warning(f"Could not read bio file: {str(e)}")
        
        # Merge bio with text for enhanced processing
        combined_text = raw_text
        if bio_text:
            # Add bio as context at the beginning
            combined_text = f"[BIOGRAPHICAL CONTEXT]\n{bio_text}\n\n[TEXT CONTENT]\n{raw_text}"
            logger.info(f"Combined text with bio: {len(combined_text)} characters")
        
        # Clean and preprocess text
        cleaned_text = clean_text(combined_text)
        
        # Extract sentences and analyze
        sentences = extract_sentences(cleaned_text)
        
        # Perform sentiment analysis
        sentiment_analysis = analyze_sentiment(sentences)
        
        # Extract personality traits
        personality_traits = extract_personality_traits(sentences, sentiment_analysis)
        
        # Generate conversation patterns
        conversation_patterns = extract_conversation_patterns(sentences)
        
        # Compile processed data with bio integration
        processed_data = {
            "session_metadata": {
                "original_file": text_path,
                "bio_file": bio_path if bio_path and os.path.exists(bio_path) else None,
                "processing_timestamp": datetime.now().isoformat(),
                "total_characters": len(raw_text),
                "bio_characters": len(bio_text) if bio_text else 0,
                "combined_characters": len(combined_text),
                "total_sentences": len(sentences),
                "language": detect_language(cleaned_text),
                "bio_provided": bool(bio_text)
            },
            "content": {
                "raw_text": raw_text[:1000] + "..." if len(raw_text) > 1000 else raw_text,  # Truncate for storage
                "bio_text": bio_text[:500] + "..." if len(bio_text) > 500 else bio_text,  # Store bio excerpt
                "cleaned_text": cleaned_text[:1000] + "..." if len(cleaned_text) > 1000 else cleaned_text,
                "sentences": sentences[:50],  # Store first 50 sentences
                "sentence_count": len(sentences)
            },
            "analysis": {
                "sentiment_analysis": sentiment_analysis,
                "personality_traits": personality_traits,
                "conversation_patterns": conversation_patterns,
                "bio_insights": bio_insights  # Add extracted bio insights
            },
            "training_data": {
                "conversation_examples": prepare_training_examples(sentences, sentiment_analysis),
                "style_indicators": extract_style_indicators(sentences),
                "bio_enhanced_prompts": create_bio_enhanced_prompts(bio_insights) if bio_insights else []
            }
        }
        
        # Save processed data
        processed_path = os.path.join(session_dir, "processed_text.json")
        with open(processed_path, 'w', encoding='utf-8') as f:
            json.dump(processed_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Text processing completed. Results saved to: {processed_path}")
        
        return processed_path
        
    except Exception as e:
        logger.error(f"Text processing failed: {str(e)}")
        raise Exception(f"Text processing failed: {str(e)}")

def clean_text(text: str) -> str:
    """Clean and normalize text data."""
    # Remove excessive whitespace and newlines
    text = re.sub(r'\s+', ' ', text)
    
    # Remove URLs
    text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # Remove email addresses
    text = re.sub(r'\S+@\S+', '', text)
    
    # Remove excessive punctuation
    text = re.sub(r'[.]{3,}', '...', text)
    text = re.sub(r'[!]{2,}', '!', text)
    text = re.sub(r'[?]{2,}', '?', text)
    
    # Remove special characters but keep basic punctuation
    text = re.sub(r'[^\w\s.,!?;:\'"()-]', '', text)
    
    # Fix spacing around punctuation
    text = re.sub(r'\s+([.,!?;:])', r'\\1', text)
    text = re.sub(r'([.,!?;:])\s*', r'\\1 ', text)
    
    return text.strip()

def extract_sentences(text: str) -> List[str]:
    """Extract and clean sentences from text."""
    from nltk.tokenize import sent_tokenize
    
    sentences = sent_tokenize(text)
    
    # Filter and clean sentences
    cleaned_sentences = []
    for sentence in sentences:
        sentence = sentence.strip()
        # Keep sentences that are meaningful (3+ words, not just punctuation)
        if len(sentence.split()) >= 3 and not sentence.replace(' ', '').replace('.', '').replace('!', '').replace('?', '').isdigit():
            cleaned_sentences.append(sentence)
    
    return cleaned_sentences

def analyze_sentiment(sentences: List[str]) -> Dict:
    """Analyze sentiment of sentences using Hugging Face transformers."""
    try:
        # Use a lightweight sentiment analysis model
        sentiment_pipeline = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            return_all_scores=True
        )
        
        # Analyze sentiment for each sentence (limit to avoid memory issues)
        sample_sentences = sentences[:100]  # Analyze first 100 sentences
        
        sentiments = []
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for sentence in sample_sentences:
            try:
                result = sentiment_pipeline(sentence[:512])  # Truncate long sentences
                sentiment_scores = {item['label']: item['score'] for item in result[0]}
                
                # Determine primary sentiment
                primary_sentiment = max(sentiment_scores, key=sentiment_scores.get)
                confidence = sentiment_scores[primary_sentiment]
                
                sentiments.append({
                    "sentence": sentence[:100] + "..." if len(sentence) > 100 else sentence,
                    "sentiment": primary_sentiment,
                    "confidence": confidence,
                    "all_scores": sentiment_scores
                })
                
                # Count sentiments
                if primary_sentiment == "POSITIVE":
                    positive_count += 1
                elif primary_sentiment == "NEGATIVE":
                    negative_count += 1
                else:
                    neutral_count += 1
                    
            except Exception as e:
                logger.warning(f"Sentiment analysis failed for sentence: {e}")
                continue
        
        total_analyzed = len(sentiments)
        
        return {
            "overall_sentiment": {
                "positive_ratio": positive_count / total_analyzed if total_analyzed > 0 else 0,
                "negative_ratio": negative_count / total_analyzed if total_analyzed > 0 else 0,
                "neutral_ratio": neutral_count / total_analyzed if total_analyzed > 0 else 0
            },
            "dominant_sentiment": max(
                [("positive", positive_count), ("negative", negative_count), ("neutral", neutral_count)],
                key=lambda x: x[1]
            )[0],
            "sentence_sentiments": sentiments[:20],  # Store first 20 detailed results
            "total_analyzed": total_analyzed
        }
        
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")
        return {
            "overall_sentiment": {"positive_ratio": 0.5, "negative_ratio": 0.3, "neutral_ratio": 0.2},
            "dominant_sentiment": "neutral",
            "sentence_sentiments": [],
            "total_analyzed": 0,
            "error": str(e)
        }

def extract_personality_traits(sentences: List[str], sentiment_analysis: Dict) -> Dict:
    """Extract personality traits from text and sentiment analysis."""
    text_combined = " ".join(sentences[:50]).lower()  # Analyze first 50 sentences
    
    # Define personality indicators
    personality_indicators = {
        "extraversion": ["party", "social", "outgoing", "talkative", "energetic", "people", "friends"],
        "agreeableness": ["kind", "helpful", "caring", "empathy", "understanding", "support", "love"],
        "conscientiousness": ["organized", "responsible", "reliable", "planned", "careful", "detail"],
        "neuroticism": ["worry", "stress", "anxious", "nervous", "upset", "emotional", "sensitive"],
        "openness": ["creative", "curious", "imagination", "artistic", "innovative", "explore", "new"]
    }
    
    personality_scores = {}
    for trait, indicators in personality_indicators.items():
        score = sum(1 for indicator in indicators if indicator in text_combined)
        personality_scores[trait] = min(score / len(indicators), 1.0)  # Normalize to 0-1
    
    # Incorporate sentiment into personality
    sentiment_data = sentiment_analysis.get("overall_sentiment", {})
    
    # Adjust scores based on sentiment
    if sentiment_data.get("positive_ratio", 0) > 0.6:
        personality_scores["agreeableness"] += 0.2
        personality_scores["extraversion"] += 0.1
    
    if sentiment_data.get("negative_ratio", 0) > 0.6:
        personality_scores["neuroticism"] += 0.3
    
    # Normalize scores to ensure they don't exceed 1.0
    for trait in personality_scores:
        personality_scores[trait] = min(personality_scores[trait], 1.0)
    
    return {
        "scores": personality_scores,
        "dominant_trait": max(personality_scores, key=personality_scores.get),
        "description": generate_personality_description(personality_scores)
    }

def extract_conversation_patterns(sentences: List[str]) -> Dict:
    """Extract conversation patterns and style indicators."""
    # Analyze sentence length patterns
    sentence_lengths = [len(sentence.split()) for sentence in sentences]
    avg_sentence_length = sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0
    
    # Analyze punctuation usage
    text_combined = " ".join(sentences)
    exclamation_count = text_combined.count('!')
    question_count = text_combined.count('?')
    
    # Extract common phrases (2-3 word combinations)
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    
    try:
        stop_words = set(stopwords.words('english'))
        words = [word.lower() for sentence in sentences[:20] for word in word_tokenize(sentence) 
                if word.isalnum() and word.lower() not in stop_words]
        
        # Get common words
        common_words = Counter(words).most_common(10)
    except:
        common_words = []
    
    return {
        "avg_sentence_length": avg_sentence_length,
        "sentence_length_category": (
            "short" if avg_sentence_length < 10 else
            "medium" if avg_sentence_length < 20 else "long"
        ),
        "punctuation_style": {
            "exclamation_frequency": exclamation_count / len(sentences) if sentences else 0,
            "question_frequency": question_count / len(sentences) if sentences else 0,
            "enthusiasm_level": "high" if exclamation_count > len(sentences) * 0.1 else "normal"
        },
        "common_words": [{"word": word, "count": count} for word, count in common_words],
        "communication_style": determine_communication_style(avg_sentence_length, exclamation_count, question_count)
    }

def prepare_training_examples(sentences: List[str], sentiment_analysis: Dict) -> List[Dict]:
    """Prepare training examples for conversation model."""
    training_examples = []
    
    # Create conversation pairs from sentences
    for i in range(min(len(sentences) - 1, 20)):  # Limit to 20 examples
        prompt = sentences[i]
        response = sentences[i + 1] if i + 1 < len(sentences) else ""
        
        if len(prompt.split()) >= 3 and len(response.split()) >= 3:
            training_examples.append({
                "prompt": prompt,
                "response": response,
                "context": "personal_conversation"
            })
    
    return training_examples

def extract_style_indicators(sentences: List[str]) -> Dict:
    """Extract writing/speaking style indicators."""
    text_combined = " ".join(sentences).lower()
    
    # Style indicators
    style_patterns = {
        "formal": ["therefore", "however", "furthermore", "consequently", "nevertheless"],
        "casual": ["yeah", "ok", "cool", "awesome", "totally", "like", "um"],
        "emotional": ["feel", "heart", "love", "hate", "amazing", "terrible", "wonderful"],
        "analytical": ["think", "consider", "analyze", "reason", "logic", "because", "since"]
    }
    
    style_scores = {}
    for style, patterns in style_patterns.items():
        score = sum(1 for pattern in patterns if pattern in text_combined)
        style_scores[style] = score
    
    dominant_style = max(style_scores, key=style_scores.get) if any(style_scores.values()) else "neutral"
    
    return {
        "style_scores": style_scores,
        "dominant_style": dominant_style,
        "style_description": f"Primarily {dominant_style} communication style"
    }

def detect_language(text: str) -> str:
    """Simple language detection (basic implementation)."""
    # Basic language detection - can be enhanced with langdetect library
    common_english_words = ["the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"]
    text_lower = text.lower()
    english_word_count = sum(1 for word in common_english_words if word in text_lower)
    
    return "english" if english_word_count >= 3 else "unknown"

def generate_personality_description(personality_scores: Dict) -> str:
    """Generate a human-readable personality description."""
    dominant_trait = max(personality_scores, key=personality_scores.get)
    score = personality_scores[dominant_trait]
    
    descriptions = {
        "extraversion": f"Shows {'high' if score > 0.6 else 'moderate'} social energy and outgoing nature",
        "agreeableness": f"Demonstrates {'strong' if score > 0.6 else 'moderate'} kindness and cooperation",
        "conscientiousness": f"Displays {'high' if score > 0.6 else 'moderate'} organization and responsibility",
        "neuroticism": f"Shows {'elevated' if score > 0.6 else 'normal'} emotional sensitivity",
        "openness": f"Exhibits {'high' if score > 0.6 else 'moderate'} creativity and curiosity"
    }
    
    return descriptions.get(dominant_trait, "Balanced personality traits")

def determine_communication_style(avg_length: float, exclamations: int, questions: int) -> str:
    """Determine overall communication style."""
    if avg_length < 8 and exclamations > questions:
        return "energetic_brief"
    elif avg_length > 15 and questions > exclamations:
        return "thoughtful_detailed"
    elif exclamations > 5:
        return "enthusiastic"
    elif questions > 5:
        return "inquisitive"
    else:
        return "balanced"

def extract_bio_insights(bio_text: str) -> Dict:
    """
    Extract structured insights from biographical text for personality fine-tuning.
    
    Args:
        bio_text: Raw biographical text input
        
    Returns:
        Dictionary with extracted biographical insights
    """
    insights = {
        "nicknames": [],
        "family_members": [],
        "relationships": [],
        "profession": "",
        "locations": [],
        "personality_descriptors": [],
        "hobbies_interests": [],
        "important_facts": []
    }
    
    bio_lower = bio_text.lower()
    
    # Extract nicknames - look for patterns like "call me X", "nickname is X", "known as X"
    nickname_patterns = [
        r"call me ([a-zA-Z]+)",
        r"nickname is ([a-zA-Z]+)",
        r"known as ([a-zA-Z]+)",
        r"goes by ([a-zA-Z]+)",
        r"called ([a-zA-Z]+)"
    ]
    
    for pattern in nickname_patterns:
        matches = re.findall(pattern, bio_lower)
        insights["nicknames"].extend([match.title() for match in matches])
    
    # Extract family relationships
    family_patterns = [
        r"(?:my|his|her|their)\s+(mom|mother|dad|father|brother|sister|son|daughter|wife|husband|partner)\s+(?:is|was|named?)\s+([a-zA-Z]+)",
        r"(?:mom|mother|dad|father|brother|sister|son|daughter|wife|husband|partner)(?:'s)?\s+name\s+is\s+([a-zA-Z]+)",
        r"(?:kids?|children)\s+(?:are|named?|called?)\s+([a-zA-Z\s,&and]+)"
    ]
    
    for pattern in family_patterns:
        matches = re.findall(pattern, bio_lower)
        for match in matches:
            if isinstance(match, tuple):
                # For patterns that capture relationship and name
                if len(match) == 2:
                    relationship, name = match
                    insights["family_members"].append(f"{relationship}: {name.title()}")
                else:
                    insights["family_members"].append(match[-1].title())  # Take the name part
            else:
                # For children names patterns
                names = re.split(r'[,&]|and', match)
                for name in names:
                    name = name.strip().title()
                    if name:
                        insights["family_members"].append(f"child: {name}")
    
    # Extract profession/job
    job_patterns = [
        r"(?:work|job|profession|career|occupation)\s+(?:as|is)\s+(?:a\s+)?([a-zA-Z\s]+)",
        r"(?:is|was)\s+(?:a\s+)?([a-zA-Z]+)\s+(?:by|for)\s+profession",
        r"(?:barber|teacher|doctor|nurse|engineer|lawyer|chef|mechanic|artist|musician|writer|programmer|manager|director|sales|marketing|retail|construction|plumber|electrician|accountant|dentist|veterinarian)"
    ]
    
    for pattern in job_patterns:
        matches = re.findall(pattern, bio_lower)
        if matches:
            job = matches[0] if isinstance(matches[0], str) else matches[0]
            insights["profession"] = job.strip().title()
            break
    
    # Extract locations
    location_patterns = [
        r"(?:from|lives?|lived|grew up|born)\s+(?:in\s+)?([a-zA-Z\s]+)(?:,|\.|$)",
        r"(?:city|town|state|country)\s+(?:is|was)\s+([a-zA-Z\s]+)"
    ]
    
    for pattern in location_patterns:
        matches = re.findall(pattern, bio_lower)
        insights["locations"].extend([match.strip().title() for match in matches if len(match.strip()) > 2])
    
    # Extract personality descriptors
    personality_words = [
        "funny", "kind", "caring", "loving", "smart", "creative", "artistic", "musical", 
        "athletic", "outgoing", "shy", "quiet", "loud", "energetic", "calm", "patient",
        "stubborn", "generous", "helpful", "organized", "messy", "punctual", "late",
        "optimistic", "pessimistic", "cheerful", "serious", "playful", "responsible"
    ]
    
    for word in personality_words:
        if word in bio_lower:
            insights["personality_descriptors"].append(word.title())
    
    # Extract hobbies and interests
    hobby_patterns = [
        r"(?:hobby|hobbies|likes?|loves?|enjoys?|interests?)\s+(?:are|is|include|including)?\s*([a-zA-Z\s,&and]+)",
        r"(?:plays?|playing)\s+([a-zA-Z\s]+)",
        r"(?:watches?|watching|reads?|reading|listens? to|listening to)\s+([a-zA-Z\s]+)"
    ]
    
    for pattern in hobby_patterns:
        matches = re.findall(pattern, bio_lower)
        for match in matches:
            hobbies = re.split(r'[,&]|and', match)
            for hobby in hobbies:
                hobby = hobby.strip().title()
                if len(hobby) > 2:
                    insights["hobbies_interests"].append(hobby)
    
    # Extract important facts (numbers, ages, years, special mentions)
    fact_patterns = [
        r"(\d+)\s+(?:years? old|kids?|children)",
        r"(?:born|started|married|graduated)\s+(?:in\s+)?(\d{4})",
        r"(has\s+\d+\s+[a-zA-Z]+)",
        r"(moved\s+to\s+[a-zA-Z\s]+)",
        r"(studied\s+[a-zA-Z\s]+)"
    ]
    
    for pattern in fact_patterns:
        matches = re.findall(pattern, bio_text)  # Use original case for facts
        insights["important_facts"].extend(matches)
    
    # Clean up empty lists and duplicates
    for key in insights:
        if isinstance(insights[key], list):
            insights[key] = list(set([item for item in insights[key] if item]))
    
    return insights

def create_bio_enhanced_prompts(bio_insights: Dict) -> List[str]:
    """
    Create conversation prompts enhanced with biographical information.
    
    Args:
        bio_insights: Extracted biographical insights
        
    Returns:
        List of enhanced prompt templates
    """
    prompts = []
    
    # Base personality prompt
    base_prompt = "You are responding as this person. "
    
    # Add nickname context
    if bio_insights.get("nicknames"):
        nickname_prompt = f"Your close friends and family call you {', '.join(bio_insights['nicknames'][:2])}. "
        prompts.append(base_prompt + nickname_prompt + "Respond warmly and familiarly when someone uses your nickname.")
    
    # Add family context
    if bio_insights.get("family_members"):
        family_context = "Your family includes: " + "; ".join(bio_insights["family_members"][:5]) + ". "
        prompts.append(base_prompt + family_context + "Reference your family naturally in conversations when appropriate.")
    
    # Add profession context
    if bio_insights.get("profession"):
        profession_prompt = f"You work as a {bio_insights['profession']}. "
        prompts.append(base_prompt + profession_prompt + "Draw from your professional experience when discussing work or giving advice.")
    
    # Add location context
    if bio_insights.get("locations"):
        location_prompt = f"You're from {bio_insights['locations'][0]}. "
        prompts.append(base_prompt + location_prompt + "Reference your hometown and local knowledge when relevant.")
    
    # Add personality context
    if bio_insights.get("personality_descriptors"):
        personality_prompt = f"Your personality is {', '.join(bio_insights['personality_descriptors'][:3])}. "
        prompts.append(base_prompt + personality_prompt + "Let your personality shine through in your responses.")
    
    # Add interests context
    if bio_insights.get("hobbies_interests"):
        interests_prompt = f"You enjoy {', '.join(bio_insights['hobbies_interests'][:3])}. "
        prompts.append(base_prompt + interests_prompt + "Share your enthusiasm for your interests when the topic comes up.")
    
    # Combined comprehensive prompt
    if any(bio_insights.values()):
        comprehensive_parts = []
        
        if bio_insights.get("nicknames"):
            comprehensive_parts.append(f"called {bio_insights['nicknames'][0]} by loved ones")
        
        if bio_insights.get("profession"):
            comprehensive_parts.append(f"work as a {bio_insights['profession']}")
        
        if bio_insights.get("family_members"):
            family_summary = f"have family including {', '.join(bio_insights['family_members'][:2])}"
            comprehensive_parts.append(family_summary)
        
        if bio_insights.get("locations"):
            comprehensive_parts.append(f"from {bio_insights['locations'][0]}")
        
        if comprehensive_parts:
            comprehensive_prompt = (
                base_prompt + 
                f"You {', '.join(comprehensive_parts)}. " +
                "Respond authentically based on these personal details, using them naturally in conversation to create meaningful, personalized interactions."
            )
            prompts.append(comprehensive_prompt)
    
    return prompts