import os
import json
import re
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("API Key not found in .env file.")

client = genai.Client(api_key=GOOGLE_API_KEY)

def is_valid_korean(text, min_ratio=0.3):
    if not text or not text.strip():
        return False
    total_chars = len(text.strip())
    korean_chars = len(re.findall(r'[\uac00-\ud7a3]', text))
    return (korean_chars / total_chars) >= min_ratio

def run_grammar_agent(user_text):
    sys_prompt = """
    You are an advanced TOPIK evaluator grading the 'Language Use' section.
    Check the provided Korean text for spelling, spacing, and grammar errors.
    Convert the text strictly to the advanced written form (한다/ㄴ다/다).
    Output in JSON format with:
    - "corrected_text": The fully corrected Korean text.
    - "grammar_errors": A list containing "original", "correction", and "reason".
    - "language_score": A score out of 20.
    """
    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=user_text,
        config=types.GenerateContentConfig(
            system_instruction=sys_prompt,
            response_mime_type="application/json",
            temperature=0.2,
        )
    )
    return json.loads(response.text)

def run_logic_agent(corrected_text, is_full_essay, essay_topic=""):
    topic_instruction = f"The essay topic is: '{essay_topic}'." if essay_topic else "No specific topic provided; evaluate general logical flow."
    
    if is_full_essay:
        sys_prompt = f"""
        You are a STRICT senior professor evaluating a COMPLETE TOPIK II Question 54 essay.
        {topic_instruction}
        
        CRITICAL SCORING RULES:
        1. Content (Max 15): Does it deeply address the topic? If it completely misses the provided topic, CAP at 3/15.
        2. Structure (Max 15): MUST have a clear Introduction, Body, and Conclusion.
        3. 🚨 ANTI-CHEAT: If the essay relies on semantic repetition to meet length, CAP structure_score at 3/15 and content_score at 4/15.
        
        Output in JSON format with:
        - "content_score": A strict score out of 15.
        - "structure_score": A strict score out of 15.
        - "overall_feedback": Harsh, constructive feedback on depth, topic fulfillment, and logic.
        - "vocabulary_upgrades": A list containing "original", "advanced", and "reason".
        """
    else:
        sys_prompt = f"""
        You are evaluating a SHORT SNIPPET of a TOPIK II Q54 essay.
        {topic_instruction}
        DO NOT provide content_score or structure_score. Focus only on flow, topic relevance, and vocabulary.
        Output in JSON format with:
        - "overall_feedback": Feedback on paragraph cohesion and relevance to the topic.
        - "vocabulary_upgrades": A list containing "original", "advanced", and "reason".
        """
        
    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=corrected_text,
        config=types.GenerateContentConfig(
            system_instruction=sys_prompt,
            response_mime_type="application/json",
            temperature=0.5,
        )
    )
    return json.loads(response.text)

def run_topik_pipeline(draft_text, essay_topic=""):
    if not is_valid_korean(draft_text):
        raise ValueError("Input text does not contain enough Korean characters.")
    
    char_count = len(draft_text.strip())
    is_full_essay = char_count >= 400
        
    grammar_result = run_grammar_agent(draft_text)
    clean_text = grammar_result["corrected_text"]
    logic_result = run_logic_agent(clean_text, is_full_essay, essay_topic)
    
    return {
        "original_text": draft_text,
        "is_full_essay": is_full_essay,
        "grammar": grammar_result,
        "logic": logic_result
    }