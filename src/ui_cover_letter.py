import streamlit as st
from src.ai_cover_letter import generate_cover_letter


def show_cover_letter(cleaned_resume, job_description):
    """
    Displays the AI Cover Letter Generator.
    """

    st.header("📄 AI Cover Letter Generator")

    st.info("""
Generate a professional, ATS-friendly cover letter
tailored to your resume and the job description.
""")

    if st.button("📄 Generate Cover Letter", key="generate_cover_letter_button"):
        with st.spinner("🤖 Gemini is writing your cover letter..."):
            try:
                cover_letter = generate_cover_letter(cleaned_resume, job_description)

                st.success("✅ Cover Letter Generated Successfully!")

                st.text_area("Generated Cover Letter", cover_letter, height=500)
            except Exception as e:
                st.error(f"Error: {e}")
