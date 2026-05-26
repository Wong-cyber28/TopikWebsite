import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("[系统拦截] 找不到 API Key！请检查 .env 文件是否配置正确。")

client = genai.Client(api_key=GOOGLE_API_KEY)

print("[System] Connecting to Gemini 3.5 Flash engine...")

try:
    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents="안녕하세요 Gemini! 저는 서울대학교 컴퓨터공학부에 지원하는 학생입니다. 짧게 환영 인사를 부탁드립니다."
    )
    print("====================")
    print("[Response Received]:")
    print(response.text)
    
except Exception as e:
    print(f"[Error] Connection failed: {e}")