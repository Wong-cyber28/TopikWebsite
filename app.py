import streamlit as st
from agents import run_topik_pipeline, is_valid_korean
import database
import pandas as pd

UI_TEXT = {
    "中文": {
        "title": "🎓 TOPIK II 写作智能评估",
        "subtitle": "提交您的第 54 题草稿。系统将基于 TOPIK 官方标准进行严格评分。",
        "sidebar_profile": "### 👤 用户档案",
        "nickname": "专属昵称:",
        "disclaimer_title": "⚠️ 免责声明",
        "disclaimer_text": "本系统的评分和高级词汇建议由 AI 生成，仅供备考参考，不能替代真实考官的最终裁定。请结合官方真题进行复习。",
        "prompt_req": "### 📝 1. 考试题目 (必填)",
        "prompt_desc": "请输入大主题和 3 个引导问题，系统将据此检查您是否跑题。",
        "topic": "大主题 (주제):",
        "q1": "问题 1:",
        "q2": "问题 2:",
        "q3": "问题 3:",
        "essay_header": "### ✍️ 2. 你的韩文草稿",
        "essay_placeholder": "在此输入您的作文 (至少 50 字符)...",
        "eval_btn": "🚀 立即评估",
        "fb_lang_label": "🗣️ 选择 AI 点评语言:",
        # --- 下面是新增的 Dashboard 和 Tab 翻译 ---
        "tab_eval": "📝 评估系统",
        "tab_dash": "📊 专属面板",
        "dash_welcome": "## 欢迎回来, {current_user}! 🌟",
        "dash_chart_title": "📈 你的成长曲线",
        "dash_chart_empty": "还没有成绩记录哦。快去左侧写一篇作文，见证你的进步吧！",
        "dash_vocab_title": "📚 专属高级词库",
        "dash_vocab_empty": "你的错题词汇本还是空的。",
        "hist_cols": {"total": "总分", "grammar": "语法", "content": "内容", "structure": "结构"},
        "vocab_cols": ["初级词汇", "高级替换", "教授解析", "记录时间"]
    },
    "English": {
        "title": "🎓 TOPIK II Essay Evaluator",
        "subtitle": "Submit your Q54 draft. Graded strictly on official TOPIK criteria.",
        "sidebar_profile": "### 👤 User Profile",
        "nickname": "Nickname:",
        "disclaimer_title": "⚠️ Disclaimer",
        "disclaimer_text": "Scores and vocabulary suggestions are AI-generated for practice purposes only. They do not replace official TOPIK examiner evaluations.",
        "prompt_req": "### 📝 1. Exam Prompt (Required)",
        "prompt_desc": "Enter the main topic and 3 guiding questions to check for task fulfillment.",
        "topic": "Main Topic (주제):",
        "q1": "Question 1:",
        "q2": "Question 2:",
        "q3": "Question 3:",
        "essay_header": "### ✍️ 2. Your Essay",
        "essay_placeholder": "Enter your Korean draft here (Minimum 50 characters)...",
        "eval_btn": "🚀 Evaluate Now",
        "fb_lang_label": "🗣️ AI Feedback Language:",
        # --- Dashboard and Tab ---
        "tab_eval": "📝 Evaluation",
        "tab_dash": "📊 My Dashboard",
        "dash_welcome": "## Welcome back, {current_user}! 🌟",
        "dash_chart_title": "📈 Your Progress Chart",
        "dash_chart_empty": "No records yet. Write an essay to see your progress!",
        "dash_vocab_title": "📚 My Advanced Vocab Bank",
        "dash_vocab_empty": "Your vocab bank is currently empty.",
        "hist_cols": {"total": "Total Score", "grammar": "Grammar", "content": "Content", "structure": "Structure"},
        "vocab_cols": ["Original", "Advanced", "Reason", "Date"]
    },
    "한국어": {
        "title": "🎓 TOPIK II 쓰기 평가 시스템",
        "subtitle": "54번 답안을 제출하세요. TOPIK 공식 채점 기준에 따라 엄격하게 평가됩니다.",
        "sidebar_profile": "### 👤 사용자 프로필",
        "nickname": "닉네임:",
        "disclaimer_title": "⚠️ 면책 조항",
        "disclaimer_text": "본 시스템의 점수와 어휘 제안은 AI가 생성한 것으로, 학습 참고용입니다. 실제 채점관의 평가를 대신할 수 없습니다.",
        "prompt_req": "### 📝 1. 시험 문제 (필수)",
        "prompt_desc": "내용의 타당성을 검사하기 위해 주제와 3가지 세부 질문을 입력하세요.",
        "topic": "주제:",
        "q1": "질문 1:",
        "q2": "질문 2:",
        "q3": "질문 3:",
        "essay_header": "### ✍️ 2. 작성한 원고",
        "essay_placeholder": "여기에 한국어 원고를 입력하세요 (최소 50자)...",
        "eval_btn": "🚀 평가 시작",
        "fb_lang_label": "🗣️ AI 피드백 언어:",
        # --- Dashboard and Tab ---
        "tab_eval": "📝 평가 시스템",
        "tab_dash": "📊 내 대시보드",
        "dash_welcome": "## 환영합니다, {current_user}님! 🌟",
        "dash_chart_title": "📈 나의 성장 그래프",
        "dash_chart_empty": "아직 평가 기록이 없습니다. 원고를 작성하고 진행 상황을 확인해 보세요!",
        "dash_vocab_title": "📚 나만의 고급 어휘장",
        "dash_vocab_empty": "아직 저장된 어휘가 없습니다.",
        "hist_cols": {"total": "총점", "grammar": "언어(문법)", "content": "내용", "structure": "구성"},
        "vocab_cols": ["기존 어휘", "고급 어휘", "교수님 피드백", "날짜"]
    }
}
st.sidebar.markdown("### 🌐 Interface Language")
ui_lang = st.sidebar.selectbox("网页语言 (Language)", ["中文", "English", "한국어"], label_visibility="collapsed")

# 取出对应语言的字典包（赋值给变量 t，方便下面调用）
t = UI_TEXT[ui_lang]

st.sidebar.divider()

# 侧边栏：用户档案与免责声明
st.sidebar.markdown(t["sidebar_profile"])
current_user = st.sidebar.text_input(t["nickname"], value="SNU_Student")

st.sidebar.divider()
# 使用 st.sidebar.info 渲染一个漂亮的免责声明提示框
st.sidebar.info(f"**{t['disclaimer_title']}**\n\n{t['disclaimer_text']}")

# ==========================================
# 🖥️ 第三步：渲染主界面 (使用变量 t 替换硬编码的文字)
# ==========================================
tab_eval, tab_dashboard = st.tabs(["📝 评估系统 (Evaluation)", "📊 专属面板 (My Dashboard)"])
with tab_eval:
    st.markdown(f"## {t['title']}")
    st.caption(t["subtitle"])
    st.divider()

    st.markdown(t["prompt_req"])
    st.caption(t["prompt_desc"])

    main_topic = st.text_input(t["topic"])
    q1 = st.text_input(t["q1"])
    q2 = st.text_input(t["q2"])
    q3 = st.text_input(t["q3"])

    st.markdown(t["essay_header"])
    user_input = st.text_area(t["essay_placeholder"], height=200, label_visibility="collapsed")
    st.write("") # 增加一点垂直留白

    col_btn, col_lang = st.columns([1, 1])
    
    with col_lang:
        feedback_lang = st.selectbox(t["fb_lang_label"], ["中文", "English", "한국어"])
        
    with col_btn:
        st.write("") # 强行制造一点垂直空隙，让按钮和右边的下拉框对齐
        # 捕捉点击动作，注意这里的按钮文字也是跟着字典翻译走的！
        submit_clicked = st.button(t["eval_btn"], type="primary", use_container_width=True)

    if submit_clicked:
        char_count = len(user_input.strip())

        if not main_topic or not q1 or not q2 or not q3:
            st.warning("🚨 Please fill in the Main Topic and ALL 3 Guiding Questions before evaluating.")
        
        elif char_count == 0:
            st.warning("Please enter some text before evaluating.")
            
        elif char_count < 50:
            st.warning(f"Your text is too short ({char_count} characters). Please enter at least 50 characters.")
            
        elif not is_valid_korean(user_input):
            st.error("Invalid Input: Please ensure your text is written in Korean.")
            
        else:

            combined_prompt = f"Topic: {main_topic}\n- Q1: {q1}\n- Q2: {q2}\n- Q3: {q3}"
            
            with st.spinner("AI Agents are evaluating your essay..."):
                try:
                    results = run_topik_pipeline(user_input, combined_prompt, feedback_lang)

                    scores = {
                        'grammar': results['grammar'].get('language_score', 0),
                        'content': results['logic'].get('content_score', 0),
                        'structure': results['logic'].get('structure_score', 0)
                    }
                    
                    # 2. 提取评语和高级词汇表
                    feedback = results['logic'].get('overall_feedback', '')
                    vocab_list = results['logic'].get('vocabulary_upgrades', [])
                    
                    database.save_evaluation_data(
                        username=current_user,
                        topic=main_topic,
                        original=user_input,
                        corrected=results['grammar']['corrected_text'],
                        scores=scores,
                        feedback=feedback,
                        vocab_list=vocab_list
                    )
                    
                    is_full = results["is_full_essay"]
                    
                    if is_full:
                        lang_score = results['grammar']['language_score']
                        cont_score = results['logic']['content_score']
                        struct_score = results['logic']['structure_score']
                        total_score = lang_score + cont_score + struct_score
                        st.success(f"Full Essay Evaluation Complete! Final Score: {total_score} / 50")
                        
                        st.subheader("📊 Official Scoring Breakdown")
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Language Use", f"{lang_score} / 20")
                        with col2:
                            st.metric("Content", f"{cont_score} / 15")
                        with col3:
                            st.metric("Structure", f"{struct_score} / 15")
                    else:
                        st.info("📌 Snippet Mode: Evaluating language and vocabulary only. Submit 400+ characters for full 50-point rubric.")
                        st.subheader("📊 Language Evaluation")
                        st.metric("Language Use", f"{results['grammar']['language_score']} / 20")

                    st.subheader("📝 Perfected Text (한다/ㄴ다/다)")
                    st.info(results["grammar"]["corrected_text"])
                    
                    st.subheader("💡 Professor's Feedback")
                    st.write(results["logic"]["overall_feedback"])
                    
                    st.subheader("🔍 Grammar Corrections")
                    for error in results["grammar"]["grammar_errors"]:
                        st.write(f"- **{error['original']}** ➡️ **{error['correction']}** ({error['reason']})")
                    
                    st.subheader("🚀 Vocabulary Upgrades")
                    for vocab in results["logic"]["vocabulary_upgrades"]:
                        st.write(f"- **{vocab['original']}** ➡️ **{vocab['advanced']}** ({vocab['reason']})")
                        
                except Exception as e:
                    st.error(f"An error occurred during evaluation: {e}")

with tab_dashboard:
    # 使用 .format() 把用户的名字动态填入翻译好的欢迎语中
    st.markdown(t["dash_welcome"].format(current_user=current_user))

    history_data = database.get_user_history(current_user)
    vocab_data = database.get_user_vocabulary(current_user)
    
    st.subheader(t["dash_chart_title"])
    if history_data:
        # 画图表的数据处理
        df_history = pd.DataFrame(history_data, columns=["Date", "Grammar", "Content", "Structure"])
        df_history["Total Score"] = df_history["Grammar"] + df_history["Content"] + df_history["Structure"]
        df_history.set_index("Date", inplace=True)
        
        # 将内部英文列名重命名为对应语言的表头，这样折线图的图例就会跟着语言变！
        df_history.rename(columns={
            "Total Score": t["hist_cols"]["total"],
            "Grammar": t["hist_cols"]["grammar"],
            "Content": t["hist_cols"]["content"],
            "Structure": t["hist_cols"]["structure"]
        }, inplace=True)
        
        # 使用翻译后的列名来画图
        st.line_chart(df_history[[t["hist_cols"]["total"], t["hist_cols"]["grammar"], t["hist_cols"]["content"], t["hist_cols"]["structure"]]])
    else:
        st.info(t["dash_chart_empty"])
        
    st.divider()
    
    st.subheader(t["dash_vocab_title"])
    if vocab_data:
        # 把词汇表的表头也直接换成字典里的数组
        df_vocab = pd.DataFrame(vocab_data, columns=t["vocab_cols"])
        st.dataframe(df_vocab, use_container_width=True, hide_index=True)
    else:
        st.info(t["dash_vocab_empty"])