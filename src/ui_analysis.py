import streamlit as st


def show_analysis(
    resume_text,
    cleaned_resume,
    normalized_resume,
    contact_info,
    detected_skills,
    resume_sections,
):
    """
    Displays the Resume Analysis dashboard.
    """
    st.header("📊 Resume Analysis")

    st.subheader("📄 Resume Extraction")

    st.write(
        f"Successfully extracted **{len(resume_text):,} characters** from your resume."
    )

    with st.expander("👀 View Extracted Resume Text"):
        st.text(cleaned_resume)

    with st.expander("🧠 View NLP-Processed Text"):
        st.text(normalized_resume)
        st.subheader("👤 Candidate Profile")

    col1, col2 = st.columns(2)

    with col1:

        st.write("**📧 Email**")
        st.write(contact_info["email"] or "Not detected")

        st.write("**🔗 LinkedIn**")
        st.write(contact_info["linkedin"] or "Not detected")

    with col2:

        st.write("**📱 Phone**")
        st.write(contact_info["phone"] or "Not detected")

        st.write("**💻 GitHub**")
        st.write(contact_info["github"] or "Not detected")
        st.subheader("🧠 Detected Skills")

    if detected_skills:

        st.write(" • ".join(detected_skills))

    else:

        st.info("No skills were detected.")
        st.subheader("📂 Resume Sections")

    section_col1, section_col2 = st.columns(2)
