import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("API Key not found in .env file.")

client = genai.Client(api_key=GOOGLE_API_KEY)

def run_grammar_agent(user_text):
    sys_prompt = """
    You are an advanced TOPIK evaluator.
    Check the provided Korean text for spelling and spacing errors.
    Convert the text strictly to the advanced written form (한다/ㄴ다/다).
    Output in JSON format with:
    - "corrected_text": The fully corrected Korean text.
    - "grammar_errors": A list containing "original", "correction", and "reason".
    - "grammar_score": A score out of 10.
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

def run_logic_agent(corrected_text):
    sys_prompt = """
    You are a senior writing professor evaluating a TOPIK II essay.
    Analyze the logical flow and vocabulary of the provided grammatically correct text.
    Output in JSON format with:
    - "logic_score": A score out of 40.
    - "overall_feedback": Overall feedback on logic and depth.
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

def run_topik_pipeline(draft_text):
    grammar_result = run_grammar_agent(draft_text)
    clean_text = grammar_result["corrected_text"]
    logic_result = run_logic_agent(clean_text)
    
    return {
        "original_text": draft_text,
        "grammar": grammar_result,
        "logic": logic_result
    }