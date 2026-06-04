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

def run_grammar_agent(user_text, feedback_lang="中文"):
    sys_prompt = f"""
    You are a STRICT TOPIK evaluator grading the 'Language Use' section.
    Check for spelling, spacing, and grammar errors. Convert to 한다/ㄴ다/다 form.
    
    [IMPORTANT] 
    1. The 'corrected_text' must be strictly in Korean.
    2. STICK TO {feedback_lang}: All 'reason' fields in grammar_errors MUST be written in {feedback_lang}. 
    Do not use Korean for explanations unless specifically quoting the text.
    
    CRITICAL SCORING RUBRIC (Max 20):
    - Start at 20. Deduct 1-2 points per basic grammar/spacing error.
    - Deduct 5 points immediately if speech levels (해요/습니다) are mixed.
    - 🚨 HOLISTIC PENALTY: If the text relies heavily on elementary vocabulary (e.g., 많이, 먹다, 좋다) or lacks complex sentence structures, CAP the score at 10/20 maximum.
    
    Output in JSON format with:
    - "corrected_text": The fully corrected Korean text.
    - "grammar_errors": A list containing "original", "correction", and "reason".
    - "language_score": The final strict score out of 20.
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

def run_logic_agent(corrected_text, is_full_essay, exam_prompt="", feedback_lang="中文"):
    topic_instruction = f"The exact exam prompt (including specific questions to answer) is: '{exam_prompt}'." if exam_prompt else "No specific exam prompt provided."
    
    language_constraint = f"""
    [STRICT LANGUAGE RULE]
    - You must provide all 'overall_feedback' and 'reason' in 'vocabulary_upgrades' strictly in {feedback_lang}.
    - Even if the input is Korean, your explanation MUST be in {feedback_lang}.
    """

    if is_full_essay:
        sys_prompt = f"""
        You are a strict professor evaluating a COMPLETE TOPIK II Q54 essay based on 'All About TOPIK Writing' criteria[cite: 1].
        {topic_instruction}
        {language_constraint}
        
        [CRITICAL SCORING RUBRIC]
        - Content (Max 15): 🚨 MANDATORY CHECK: Did the writer explicitly answer EVERY specific guiding question provided in the exam prompt? If any question is ignored, heavily penalize the content_score.
        - Structure (Max 15): Paragraph cohesion and logical flow[cite: 1].
        - Use 50-point scale for full essays[cite: 1].
        
        Output in JSON format with:
        - "content_score": A strict score out of 15.
        - "structure_score": A strict score out of 15.
        - "overall_feedback": Harsh, constructive feedback. Explicitly state if they missed answering any specific questions from the prompt.
        - "vocabulary_upgrades": A list containing "original", "advanced", and "reason".
        """
    else:
        sys_prompt = f"""
        You are evaluating a SHORT SNIPPET of a TOPIK II Q54 essay.
        {topic_instruction}
        {language_constraint}
        
        DO NOT provide content_score or structure_score. 
        Focus only on flow, topic relevance (does it answer the specific prompt questions?), and vocabulary.
        
        Output in JSON format with:
        - "overall_feedback": Feedback on paragraph cohesion and relevance to the specific prompt questions.
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


def run_topik_pipeline(draft_text, exam_prompt="", feedback_lang="中文"):
    if not is_valid_korean(draft_text):
        raise ValueError("Input text does not contain enough Korean characters.")
    
    char_count = len(draft_text.strip())
    is_full_essay = char_count >= 400
        
    grammar_result = run_grammar_agent(draft_text, feedback_lang)
    clean_text = grammar_result["corrected_text"]
    
    logic_result = run_logic_agent(clean_text, is_full_essay, exam_prompt, feedback_lang)
    
    return {
        "original_text": draft_text,
        "is_full_essay": is_full_essay,
        "grammar": grammar_result,
        "logic": logic_result
    }