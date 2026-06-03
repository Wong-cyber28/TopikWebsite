import streamlit as st
from agents import run_topik_pipeline

st.set_page_config(page_title="TOPIK AI Evaluator", page_icon="🎓", layout="centered")

st.title("🎓 TOPIK II Essay Evaluator")
st.markdown("Submit your writing draft. Our dual-agent AI will correct your grammar and upgrade your vocabulary to the advanced written form.")

st.divider()

user_input = st.text_area("Enter your Korean draft here:", height=150)

if st.button("Evaluate Now", type="primary"):
    if not user_input.strip():
        st.warning("Please enter some text before evaluating.")
    else:
        with st.spinner("AI Agents are analyzing your essay..."):
            try:
                results = run_topik_pipeline(user_input)
                
                st.success("Evaluation Complete!")
                
                st.subheader("📝 Perfected Text (한다/ㄴ다/다)")
                st.info(results["grammar"]["corrected_text"])
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Grammar Score", f"{results['grammar']['grammar_score']} / 10")
                with col2:
                    st.metric("Logic Score", f"{results['logic']['logic_score']} / 40")
                
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