import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load API key
load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")


def generate_cover_letter(resume_text, job_description):
    """
    Generates a professional cover letter using Gemini.
    """

    prompt = f"""
You are an expert career coach.

Using the resume and job description below, write a professional ATS-friendly cover letter.

Resume:
{resume_text}

Job Description:
{job_description}

Requirements:
- Professional tone
- 300-400 words
- Mention relevant skills
- Mention why the candidate fits the role
- End politely
- Return ONLY the cover letter.
"""

    response = model.generate_content(prompt)

    return response.text
