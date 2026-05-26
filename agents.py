import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 1. 唤醒保险箱
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("[系统拦截] 找不到 API Key！请检查 .env 文件。")

client = genai.Client(api_key=GOOGLE_API_KEY)

def run_grammar_agent(user_text):
    """ Agent 1: 基础语法官 (严谨、死板、零容忍) """
    print("[Agent 1] 正在启动基础语法官：清洗文本，修正拼写与口语化...")
    sys_prompt = """
    你是一名严谨的 TOPIK 高级阅卷人。
    请检查用户提交的韩语作文，纠正拼写、空格(띄어쓰기)错误，并确保严格使用高级书面语体（한다/ㄴ다/다体）。绝不允许出现敬语/口语。
    请以 JSON 格式输出，必须包含：
    - "corrected_text": 修改后的完整韩文文本
    - "grammar_errors": 错误列表，包含 "original", "correction", "reason"
    - "grammar_score": 满分10分的语法基础分
    """
    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=user_text,
        config=types.GenerateContentConfig(
            system_instruction=sys_prompt,
            response_mime_type="application/json",
            temperature=0.2, # 温度 0.2：极度严谨，不乱加戏
        )
    )
    return json.loads(response.text)

def run_logic_agent(corrected_text):
    """ Agent 2: 高级逻辑官 (富有洞察力、严苛的词汇大师) """
    print("[Agent 2] 正在启动高级逻辑官：分析论点深度与词汇升级...")
    sys_prompt = """
    你是一名首尔大学的资深韩文写作教授，负责 TOPIK II 54题（大作文）的逻辑与结构评分。
    你接收到的文本已经在语法上被清理过了。请将全部注意力放在：论点是否深刻、逻辑连词是否恰当、是否可以替换为更高级的TOPIK高级词汇。
    请以 JSON 格式输出，必须包含：
    - "logic_score": 满分40分的逻辑与内容分
    - "overall_feedback": 对文章逻辑和深度的整体韩文评价（不少于2句话）
    - "vocabulary_upgrades": 推荐的高级替换词列表，包含 "original" (原普通词), "advanced" (推荐高级词), "reason" (替换理由)
    """
    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=corrected_text,
        config=types.GenerateContentConfig(
            system_instruction=sys_prompt,
            response_mime_type="application/json",
            temperature=0.5, # 温度 0.5：给予AI一定的创造力来构思高级词汇
        )
    )
    return json.loads(response.text)

def run_topik_pipeline(draft_text):
    """ 核心总线：数据流水线 (Pipeline) """
    print("\n========== [流水线启动] ==========")
    
    # 步骤 1：让 Agent 1 处理原始草稿
    grammar_result = run_grammar_agent(draft_text)
    
    # 极其关键的一步：从 Agent 1 的 JSON 里抽出干净的文本
    clean_text = grammar_result["corrected_text"] 
    
    # 步骤 2：把干净的文本喂给 Agent 2
    logic_result = run_logic_agent(clean_text) 
    
    # 步骤 3：生成终极报告
    print("\n========== [终极批改报告] ==========")
    print(f"✨ 你的原始草稿:\n{draft_text}\n")
    print(f"📖 最终完美润色版本:\n{clean_text}\n")
    print(f"💯 综合得分: 语法 {grammar_result['grammar_score']}/10 | 逻辑 {logic_result['logic_score']}/40")
    print(f"📝 教授点评:\n{logic_result['overall_feedback']}\n")
    
    print("💡 词汇升级建议 (The Vocabulary Upgrades):")
    for vocab in logic_result['vocabulary_upgrades']:
        print(f"   [{vocab['original']}] ➡️ [{vocab['advanced']}] ({vocab['reason']})")

# 本地火力测试
if __name__ == "__main__":
    # 这是一篇充满口语、逻辑极其幼稚的测试草稿
    test_draft = "요즘 스마트폰을 많이 씁니다. 그래서 눈이 아파요. 그리고 친구랑 대화를 안 합니다. 스마트폰은 좋지만 나쁜 점도 있어요."
    
    run_topik_pipeline(test_draft)