# /backend/engines/llm_engine.py
import os, time

def generate_stream(prompt: str, max_new_tokens=256, temperature=0.7):
    # Sprint 1 stub: simulate streaming response
    response = f"Based on the provided context, I can answer your question about: {prompt[:50]}..." + \
               "\n\nThis is a demo response from the local LLM engine. " + \
               "In Sprint 2, this will be replaced with actual Phi-2 model inference."
    
    words = response.split()
    for word in words:
        yield word + " "
        time.sleep(0.05)  # Simulate streaming delay