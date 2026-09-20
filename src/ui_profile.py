import streamlit as st


def render_profile(profile):
    st.header("👤 Candidate Profile")

    st.subheader("🧠 Detected Skills")

    skills = profile.get("skills", [])

    if skills:
        cols = st.columns(3)

        for i, skill in enumerate(skills):
            with cols[i % 3]:
                st.success(skill)
    else:
        st.warning("No skills detected.")

    st.subheader("📄 Resume Profile")

    resume_text = profile.get("resume_text", "")

    if resume_text:
        st.text_area("Extracted Resume Content", resume_text, height=250)
