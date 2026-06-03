import streamlit as st
from agents import run_topik_pipeline, is_valid_korean

st.set_page_config(page_title="TOPIK AI Evaluator", page_icon="🎓", layout="centered")

st.title("🎓 TOPIK II Essay Evaluator")
st.markdown("Submit your draft. The system automatically adapts to evaluate short snippets or full essays.")

st.divider()

essay_topic = st.text_input("Enter the essay topic or core theme (Optional):", placeholder="e.g., 현대인의 건강 관리")
user_input = st.text_area("Enter your Korean draft here (Minimum 50 characters):", height=200)

if st.button("Evaluate Now", type="primary"):
    char_count = len(user_input.strip())
    
    if char_count == 0:
        st.warning("Please enter some text before evaluating.")
    elif char_count < 50:
        st.warning(f"Your text is too short ({char_count} chars). Please enter at least 50 characters.")
    elif not is_valid_korean(user_input):
        st.error("Invalid Input: Please ensure your text is written in Korean.")
    else:
        with st.spinner("AI Agents are analyzing your text..."):
            try:
                results = run_topik_pipeline(user_input, essay_topic)
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