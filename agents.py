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
    You are a STRICT TOPIK evaluator grading the 'Language Use' (언어 사용) section.
    Check for spelling, spacing, and grammar errors. Convert to 한다/ㄴ다/다 form.
    
    [IMPORTANT] 
    1. The 'corrected_text' must be strictly in Korean.
    2. STICK TO {feedback_lang}: All 'reason' fields in grammar_errors MUST be written in {feedback_lang}. 
    Do not use Korean for explanations unless specifically quoting the text.
    
    CRITICAL SCORING RUBRIC (Max 20):
    - Start at 20. Deduct 1-2 points per basic grammar/spacing error.
    - Deduct 5 points immediately if speech levels (해요/습니다) are mixed.
    - 🚨 ACADEMIC LANGUAGE PENALTY (고급 어휘/문법 제한): TOPIK Q54 strictly requires Level 6 advanced vocabulary (한자어) and complex sentence structures. Even if there are ZERO grammar/spelling mistakes, if the text relies on simple intermediate expressions (e.g., 나쁜 영향을 미친다, 건강에 좋지 않다, 많아지기 때문이다) instead of formal academic structures (e.g., 악영향을 초래한다, 건강을 해칠 우려가 있다, 증가하기 마련이다), you MUST CAP the language_score at 12/20 maximum.
    
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
        You are a merciless senior professor evaluating a COMPLETE TOPIK II Q54 essay based on 'All About TOPIK Writing' criteria.
        {topic_instruction}
        {language_constraint}
        
        [CRITICAL SCORING RUBRIC]
        - Content (Max 15): 🚨 MANDATORY CHECK: Did they explicitly answer EVERY guiding question? 
          🚨 ACADEMIC DEPTH PENALTY (CRITICAL): TOPIK Q54 strictly requires Level 5-6 academic depth (sociological/psychological analysis). If the essay uses basic everyday logic (e.g., "운동하면 기분이 좋다", "돈이 없어서 힘들다", "스트레스 받으면 싸운다"), it is a Level 3/4 essay. You MUST CAP the content_score at a maximum of 8/15.
        - Structure (Max 15): Paragraph cohesion and logical flow.
          🚨 ADVANCED TRANSITION PENALTY: If the essay relies on elementary conjunctions (e.g., 그래서, 그리고, 먼저) instead of advanced cohesive devices, strictly CAP the structure_score at a maximum of 8/15.
        - Use 50-point scale for full essays.
        
        Output in JSON format with:
        - "content_score": A strict score out of 15.
        - "structure_score": A strict score out of 15.
        - "overall_feedback": Harsh, constructive feedback. Explicitly tear down their childish logic if it sounds like a Level 3 essay instead of a Level 6 academic paper. MUST BE IN {feedback_lang}.
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