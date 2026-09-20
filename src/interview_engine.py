import os
import json
import re
from dotenv import load_dotenv

load_dotenv()

# Optional Gemini import
try:
    import google.generativeai as genai
    GEMINI_KEY = os.getenv("GEMINI_API_KEY")
    if GEMINI_KEY:
        genai.configure(api_key=GEMINI_KEY)
except Exception:
    GEMINI_KEY = None


def extract_candidate_name(resume_text, contact_info=None):
    """Extract candidate name from contact info or top of resume."""
    if contact_info and contact_info.get("email"):
        email = contact_info["email"]
        name_part = email.split("@")[0]
        name_part = re.sub(r"[0-9._-]+", " ", name_part).strip().title()
        if len(name_part) >= 3 and not any(char.isdigit() for char in name_part):
            lines = [line.strip() for line in resume_text.splitlines() if line.strip()]
            if lines and len(lines[0]) < 40 and not any(k in lines[0].lower() for k in ["resume", "curriculum", "email", "phone"]):
                return lines[0].title()
            return name_part
            
    lines = [line.strip() for line in resume_text.splitlines() if line.strip()]
    for line in lines[:3]:
        if len(line) < 40 and not any(k in line.lower() for k in ["resume", "curriculum", "email", "phone", "http", "@"]):
            clean_name = re.sub(r"[^a-zA-Z\s]", "", line).strip()
            if len(clean_name.split()) in [2, 3]:
                return clean_name.title()
                
    return "Candidate"


def parse_projects_list(projects_text, detected_skills):
    """Parse projects into structured list."""
    if not projects_text or len(projects_text.strip()) < 5:
        return []
    lines = [l.strip() for l in projects_text.splitlines() if l.strip()]
    projects = []
    current_proj = None
    
    for line in lines:
        clean_line = line.lstrip("•*-–1234567890. ").strip()
        if not clean_line:
            continue
            
        is_header = False
        if len(clean_line) < 70 and not clean_line.endswith("."):
            is_header = True
            
        if is_header or current_proj is None:
            if current_proj and current_proj.get("name"):
                projects.append(current_proj)
            techs = [s for s in detected_skills if re.search(r'\b' + re.escape(s) + r'\b', clean_line, re.I)]
            proj_name = clean_line.split(":")[0].split("|")[0].split("-")[0].strip()
            current_proj = {
                "name": proj_name if proj_name else "Project",
                "technologies": techs,
                "description": clean_line
            }
        else:
            current_proj["description"] += " " + clean_line
            for s in detected_skills:
                if re.search(r'\b' + re.escape(s) + r'\b', clean_line, re.I) and s not in current_proj["technologies"]:
                    current_proj["technologies"].append(s)
                    
    if current_proj and current_proj.get("name"):
        projects.append(current_proj)
        
    return projects


def parse_experience_list(experience_text):
    """Parse work experience roles into structured list."""
    if not experience_text or len(experience_text.strip()) < 5:
        return []
    lines = [l.strip() for l in experience_text.splitlines() if l.strip()]
    roles = []
    current_role = None
    
    for line in lines:
        clean_line = line.lstrip("•*-–").strip()
        if not clean_line:
            continue
            
        is_header = False
        if len(clean_line) < 80 and any(k in clean_line.lower() for k in ["engineer", "developer", "analyst", "manager", "intern", "lead", "specialist", "consultant", "architect", "|", "at ", "ltd", "inc", "solutions", "tech"]):
            is_header = True
            
        if is_header or current_role is None:
            if current_role and current_role.get("title"):
                roles.append(current_role)
            current_role = {
                "title": clean_line,
                "description": clean_line
            }
        else:
            current_role["description"] += " " + clean_line
            
    if current_role and current_role.get("title"):
        roles.append(current_role)
        
    return roles


def build_evidence_based_suggested_questions(resume_data, target_job="Target Role"):
    """
    Constructs 15-18 high-quality, candidate-specific suggested interview questions.
    Categorized into Resume & Intro, Technical, Projects, Experience, Behavioral, Target Role, and Resume Deep-Dive.
    Includes Priority and 'Based on' indicators.
    """
    cleaned_resume = resume_data.get("cleaned_resume", "")
    contact_info = resume_data.get("contact_info", {})
    detected_skills = resume_data.get("detected_skills", [])
    resume_sections = resume_data.get("resume_sections", {})
    matched_skills = resume_data.get("matched_skills", [])
    missing_skills = resume_data.get("missing_skills", [])
    
    candidate_name = extract_candidate_name(cleaned_resume, contact_info)
    target_job = target_job.strip() if target_job and target_job.strip() else "Target Position"
    
    proj_text = resume_sections.get("projects", "")
    exp_text = resume_sections.get("experience", "")
    edu_text = resume_sections.get("education", "")
    cert_text = resume_sections.get("certifications", "")
    
    projects = parse_projects_list(proj_text, detected_skills)
    roles = parse_experience_list(exp_text)
    
    top_skills = detected_skills[:5] if detected_skills else ["Software Engineering", "Problem Solving"]
    
    questions = []
    q_id = 1
    
    # 1. RESUME & INTRODUCTION (2 Questions)
    questions.append({
        "id": q_id,
        "category": "RESUME & INTRODUCTION",
        "priority": "🔥 HIGH PRIORITY",
        "question": f"Welcome, {candidate_name}. Based on your resume, you are targeting the role of {target_job}. Can you walk me through your technical background and why this role is the right next step for you?",
        "based_on": f"Profile Summary • {target_job}"
    })
    q_id += 1

    questions.append({
        "id": q_id,
        "category": "RESUME & INTRODUCTION",
        "priority": "⭐ IMPORTANT",
        "question": f"Looking at your career path, you have built core skills in {', '.join(top_skills[:3])}. What major milestone or project best demonstrates your growth as a developer?",
        "based_on": f"{', '.join(top_skills[:3])}"
    })
    q_id += 1

    # 2. TECHNICAL QUESTIONS (4-5 Questions)
    for idx, skill in enumerate(top_skills[:4]):
        prio = "🔥 HIGH PRIORITY" if idx < 2 else "⭐ IMPORTANT"
        questions.append({
            "id": q_id,
            "category": "TECHNICAL",
            "priority": prio,
            "question": f"You listed {skill} in your resume. How have you used {skill} in your projects or work experience, and what best practices do you follow when writing code in {skill}?",
            "based_on": skill
        })
        q_id += 1

    if len(top_skills) >= 2:
        questions.append({
            "id": q_id,
            "category": "TECHNICAL",
            "priority": "🔥 HIGH PRIORITY",
            "question": f"You mentioned both {top_skills[0]} and {top_skills[1]} in your resume. Explain how you integrated these two technologies together in an application or architecture.",
            "based_on": f"{top_skills[0]} • {top_skills[1]}"
        })
        q_id += 1

    # 3. PROJECT QUESTIONS (3-4 Questions)
    if projects:
        for proj in projects[:3]:
            tech_str = " • ".join(proj["technologies"]) if proj["technologies"] else top_skills[0]
            questions.append({
                "id": q_id,
                "category": "PROJECTS",
                "priority": "🔥 HIGH PRIORITY",
                "question": f"Your resume highlights the project '{proj['name']}'. What was your specific technical contribution, what tech stack did you use, and what major challenge did you solve?",
                "based_on": f"{proj['name']} ({tech_str})"
            })
            q_id += 1
            
            questions.append({
                "id": q_id,
                "category": "PROJECTS",
                "priority": "⭐ IMPORTANT",
                "question": f"In your project '{proj['name']}', what technical trade-offs did you make during development, and how would you redesign the architecture to handle 10x higher user scale?",
                "based_on": f"{proj['name']} System Scale"
            })
            q_id += 1
    else:
        questions.append({
            "id": q_id,
            "category": "PROJECTS",
            "priority": "⭐ IMPORTANT",
            "question": f"What is the most complex technical project you have built using {top_skills[0]}? Walk me through the architecture and design decisions you made.",
            "based_on": f"Technical Skills ({top_skills[0]})"
        })
        q_id += 1

    # 4. EXPERIENCE QUESTIONS (2-3 Questions if exp exists)
    if roles:
        for role in roles[:2]:
            questions.append({
                "id": q_id,
                "category": "EXPERIENCE",
                "priority": "🔥 HIGH PRIORITY",
                "question": f"During your role as '{role['title']}', what were your primary day-to-day engineering responsibilities, and how did you deliver value to the team?",
                "based_on": role['title']
            })
            q_id += 1
            
            questions.append({
                "id": q_id,
                "category": "EXPERIENCE",
                "priority": "⭐ IMPORTANT",
                "question": f"In your role as '{role['title']}', tell me about a difficult technical issue or bug you encountered in production and how you debugged and fixed it.",
                "based_on": f"{role['title']} • Debugging & Ops"
            })
            q_id += 1
    elif edu_text:
        questions.append({
            "id": q_id,
            "category": "EXPERIENCE",
            "priority": "⭐ IMPORTANT",
            "question": f"Your resume highlights your background in {edu_text.splitlines()[0]}. What key practical assignments or team projects best prepared you for hands-on industry work?",
            "based_on": edu_text.splitlines()[0]
        })
        q_id += 1

    # 5. BEHAVIORAL QUESTIONS (2 Questions)
    questions.append({
        "id": q_id,
        "category": "BEHAVIORAL",
        "priority": "○ GOOD TO PREPARE",
        "question": f"Tell me about a time when you had to learn a new technology or tool quickly under tight deadline pressure. How did you approach the learning curve?",
        "based_on": "Continuous Learning & Agility"
    })
    q_id += 1

    questions.append({
        "id": q_id,
        "category": "BEHAVIORAL",
        "priority": "○ GOOD TO PREPARE",
        "question": f"Describe a project scenario where you had a disagreement over technical architecture or implementation approach with a peer. How did you reach a resolution?",
        "based_on": "Technical Collaboration & Communication"
    })
    q_id += 1

    # 6. TARGET ROLE QUESTIONS (2 Questions)
    questions.append({
        "id": q_id,
        "category": "TARGET ROLE",
        "priority": "🔥 HIGH PRIORITY",
        "question": f"For a professional {target_job} position, what automated testing, CI/CD pipelines, and code quality standards do you typically implement?",
        "based_on": f"Target Role: {target_job}"
    })
    q_id += 1

    if missing_skills:
        questions.append({
            "id": q_id,
            "category": "TARGET ROLE",
            "priority": "⭐ IMPORTANT",
            "question": f"The target position '{target_job}' frequently uses tools like {', '.join(missing_skills[:2])}. How are you building hands-on familiarity with these skills?",
            "based_on": f"Missing Target Skills ({', '.join(missing_skills[:2])})"
        })
        q_id += 1
    else:
        questions.append({
            "id": q_id,
            "category": "TARGET ROLE",
            "priority": "⭐ IMPORTANT",
            "question": f"What security standards and performance optimization techniques do you apply to maintain reliable production applications in {target_job} roles?",
            "based_on": f"Production Security ({target_job})"
        })
        q_id += 1

    # 7. RESUME DEEP-DIVE QUESTIONS (2 Questions)
    questions.append({
        "id": q_id,
        "category": "RESUME DEEP-DIVE",
        "priority": "🔥 HIGH PRIORITY",
        "question": f"Be prepared to defend every claim on your resume. If asked to write code or explain internal mechanics of {top_skills[0]}, what specific topics would you highlight?",
        "based_on": f"Resume Skill Claim ({top_skills[0]})"
    })
    q_id += 1

    if projects:
        questions.append({
            "id": q_id,
            "category": "RESUME DEEP-DIVE",
            "priority": "⭐ IMPORTANT",
            "question": f"If an interviewer asks you to draw the data flow diagram for '{projects[0]['name']}', how would you explain the inputs, database models, and output API response?",
            "based_on": f"Data Flow in {projects[0]['name']}"
        })
        q_id += 1

    return questions


def generate_suggested_interview_questions(resume_data, target_job="Target Position", job_description=""):
    """
    Generates candidate-specific suggested interview questions using Gemini API or Python fallback.
    """
    cleaned_resume = resume_data.get("cleaned_resume", "")
    contact_info = resume_data.get("contact_info", {})
    detected_skills = resume_data.get("detected_skills", [])
    resume_sections = resume_data.get("resume_sections", {})
    target_job = target_job.strip() if target_job else "Target Position"
    
    if GEMINI_KEY:
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            prompt = f"""
You are an expert recruiter and technical interviewer.

Analyze ONLY the candidate information provided below:

CANDIDATE NAME: {extract_candidate_name(cleaned_resume, contact_info)}
TARGET ROLE: {target_job}
JOB DESCRIPTION: {job_description}

ACTUAL RESUME TEXT:
{cleaned_resume}

PARSED SECTIONS:
- Summary: {resume_sections.get('summary', '')}
- Education: {resume_sections.get('education', '')}
- Experience: {resume_sections.get('experience', '')}
- Projects: {resume_sections.get('projects', '')}
- Skills: {', '.join(detected_skills)}

CRITICAL RULES:
1. Generate 15 to 18 specific interview questions referencing ACTUAL project names, skills, and roles from the resume.
2. DO NOT invent fake companies, projects, or credentials.
3. Categorize questions into: RESUME & INTRODUCTION, TECHNICAL, PROJECTS, EXPERIENCE, BEHAVIORAL, TARGET ROLE, RESUME DEEP-DIVE.
4. Assign priority: "🔥 HIGH PRIORITY", "⭐ IMPORTANT", or "○ GOOD TO PREPARE".
5. Provide a "based_on" string showing what part of the resume caused the question to be generated.
6. Output valid JSON strictly matching this array of objects:

[
  {{
    "id": 1,
    "category": "TECHNICAL",
    "priority": "🔥 HIGH PRIORITY",
    "question": "You listed AWS and Docker in your resume...",
    "based_on": "AWS • Docker"
  }}
]
"""
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            data = json.loads(response.text)
            if isinstance(data, list) and len(data) >= 8:
                return data
        except Exception as err:
            print(f"Gemini Question Generation Error: {err}. Using evidence-based Python fallback.")

    return build_evidence_based_suggested_questions(resume_data, target_job)
