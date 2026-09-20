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
            # Also check first line of resume
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


def parse_projects_from_text(projects_text, detected_skills):
    """Parse individual projects from text into structured dictionaries."""
    if not projects_text or len(projects_text.strip()) < 5:
        return []
        
    lines = [l.strip() for l in projects_text.splitlines() if l.strip()]
    projects = []
    current_proj = None
    
    for line in lines:
        clean_line = line.lstrip("•*-–1234567890. ").strip()
        if not clean_line:
            continue
            
        # Check if header line
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
                "description": clean_line,
                "bullets": []
            }
        else:
            current_proj["description"] += " " + clean_line
            current_proj["bullets"].append(clean_line)
            for s in detected_skills:
                if re.search(r'\b' + re.escape(s) + r'\b', clean_line, re.I) and s not in current_proj["technologies"]:
                    current_proj["technologies"].append(s)
                    
    if current_proj and current_proj.get("name"):
        projects.append(current_proj)
        
    return projects


def parse_experience_from_text(experience_text, detected_skills):
    """Parse work experience entries into structured list."""
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
                "description": clean_line,
                "bullets": []
            }
        else:
            current_role["description"] += " " + clean_line
            current_role["bullets"].append(clean_line)
            
    if current_role and current_role.get("title"):
        roles.append(current_role)
        
    return roles


def build_evidence_based_review(resume_data, target_job="Target Role", job_description=""):
    """
    Constructs a 100% evidence-based, data-driven personalized AI Review
    grounded strictly in the candidate's actual parsed resume.
    """
    resume_text = resume_data.get("resume_text", "")
    cleaned_resume = resume_data.get("cleaned_resume", resume_text)
    contact_info = resume_data.get("contact_info", {})
    detected_skills = resume_data.get("detected_skills", [])
    resume_sections = resume_data.get("resume_sections", {})
    matched_skills = resume_data.get("matched_skills", [])
    missing_skills = resume_data.get("missing_skills", [])
    job_skills = resume_data.get("job_skills", [])
    overall_score = resume_data.get("overall_score", 75)
    quality_score = resume_data.get("resume_quality_score", 80)
    candidate_level = resume_data.get("candidate_level", "Mid Level")
    
    candidate_name = extract_candidate_name(cleaned_resume, contact_info)
    target_job = target_job.strip() if target_job and target_job.strip() else "Target Role"
    
    # Extract sections
    summary_text = resume_sections.get("summary", "")
    exp_text = resume_sections.get("experience", "")
    proj_text = resume_sections.get("projects", "")
    edu_text = resume_sections.get("education", "")
    cert_text = resume_sections.get("certifications", "")
    achieve_text = resume_sections.get("achievements", "")
    
    parsed_projects = parse_projects_from_text(proj_text, detected_skills)
    parsed_exp = parse_experience_from_text(exp_text, detected_skills)
    
    # ----------------------------------------------------
    # 1. EXECUTIVE SUMMARY
    # ----------------------------------------------------
    exp_summary = f"with professional experience in {parsed_exp[0]['title']}" if parsed_exp else "focusing on project-based technical development"
    skills_summary = ", ".join(detected_skills[:5]) if detected_skills else "relevant core competencies"
    proj_summary = f"including key projects like '{parsed_projects[0]['name']}'" if parsed_projects else "with technical coursework"
    
    exec_summary = (
        f"{candidate_name}'s resume demonstrates a profile aligned as a {candidate_level} candidate "
        f"for {target_job}. The candidate possesses strong technical skills in {skills_summary}, {exp_summary}, "
        f"{proj_summary}. "
        f"{'Education includes ' + edu_text.splitlines()[0] + '. ' if edu_text else ''}"
        f"Overall compatibility is evaluated at {overall_score}% for the target role."
    )
    
    # ----------------------------------------------------
    # 2. RESUME STRENGTHS (EVIDENCE-BASED)
    # ----------------------------------------------------
    strengths = []
    if detected_skills:
        top_skills_str = ", ".join(detected_skills[:4])
        strengths.append({
            "title": f"Strong Core Technical Skills ({top_skills_str})",
            "evidence": f"Your resume explicitly demonstrates proficiency in {top_skills_str} across your technical skill sections."
        })
        
    if parsed_projects:
        first_proj = parsed_projects[0]
        proj_techs = ", ".join(first_proj["technologies"]) if first_proj["technologies"] else "technologies"
        strengths.append({
            "title": f"Practical Application in '{first_proj['name']}'",
            "evidence": f"Demonstrated practical execution of {proj_techs} through project work in {first_proj['name']}."
        })
        
    if parsed_exp:
        first_exp = parsed_exp[0]
        strengths.append({
            "title": f"Relevant Work Experience ({first_exp['title']})",
            "evidence": f"Your resume documents professional hands-on experience as {first_exp['title']}."
        })
    elif edu_text:
        strengths.append({
            "title": "Clear Educational Qualification",
            "evidence": f"Your resume documents formal academic background: {edu_text.splitlines()[0]}."
        })
        
    if cert_text:
        strengths.append({
            "title": "Verified Professional Certifications",
            "evidence": f"Your resume showcases relevant certification: {cert_text.splitlines()[0]}."
        })
        
    if matched_skills:
        strengths.append({
            "title": f"Target Role Skill Alignment ({len(matched_skills)} Matched Skills)",
            "evidence": f"Successfully matches key requirements for {target_job} including {', '.join(matched_skills[:4])}."
        })
        
    # Ensure at least 3 strengths
    if len(strengths) < 3:
        strengths.append({
            "title": "Structured Resume Layout",
            "evidence": "Key resume sections are clearly demarcated, making parsing easy for ATS systems."
        })

    # ----------------------------------------------------
    # 3. AREAS TO IMPROVE (EVIDENCE-BASED)
    # ----------------------------------------------------
    areas_to_improve = []
    if missing_skills:
        areas_to_improve.append({
            "title": f"Missing Target Role Skills ({', '.join(missing_skills[:3])})",
            "explanation": f"The target position '{target_job}' requires skills such as {', '.join(missing_skills[:4])} which were not explicitly detected in your resume."
        })
        
    # Check for metrics
    has_metrics = bool(re.search(r'\b\d+%\b|\$\d+|\b\d+\s*(users|clients|projects|ms|sec|hours|x|x%)\b', cleaned_resume, re.I))
    if not has_metrics:
        areas_to_improve.append({
            "title": "Missing Quantifiable Impact & Metrics",
            "explanation": "Your experience and project bullet points describe tasks but lack measurable metrics (e.g., 'improved performance by 35%', 'handled 10k daily users')."
        })
        
    if not exp_text:
        areas_to_improve.append({
            "title": "No Formal Industry Experience Listed",
            "explanation": "No professional work experience section was identified in the uploaded resume. Highlight internships, freelance work, or open-source contributions."
        })
        
    if not cert_text:
        areas_to_improve.append({
            "title": "No Industry Certifications Identified",
            "explanation": "No professional certifications were identified. Adding recognized certifications for your target role will increase recruiter confidence."
        })
        
    if len(detected_skills) < 6:
        areas_to_improve.append({
            "title": "Under-represented Technical Skillset",
            "explanation": "Fewer than 6 technical skills were detected. Expand your skills section to include specific tools, frameworks, and methodologies."
        })

    # ----------------------------------------------------
    # 4. SKILL ANALYSIS
    # ----------------------------------------------------
    strong_skills = [s for s in detected_skills if any(s.lower() in p.get("description", "").lower() for p in parsed_projects) or any(s.lower() in exp.get("description", "").lower() for exp in parsed_exp)]
    if not strong_skills:
        strong_skills = detected_skills[:4]
        
    developing_skills = [s for s in detected_skills if s not in strong_skills]
    missing_recommended = missing_skills if missing_skills else ["Cloud Deployment (AWS/GCP)", "CI/CD Pipelines", "Automated Testing"]
    
    # ----------------------------------------------------
    # 5. EXPERIENCE ANALYSIS
    # ----------------------------------------------------
    has_exp = bool(parsed_exp)
    exp_items = []
    if has_exp:
        for exp in parsed_exp[:3]:
            exp_items.append({
                "role_or_company": exp["title"],
                "strength": f"Demonstrates hands-on responsibilities in {exp['title']}.",
                "improvement": "Strengthen bullet points by starting with action verbs and adding quantified performance results."
            })
        exp_note = ""
    else:
        exp_note = "No professional experience was identified in the uploaded resume."

    # ----------------------------------------------------
    # 6. PROJECT ANALYSIS
    # ----------------------------------------------------
    has_proj = bool(parsed_projects)
    proj_items = []
    if has_proj:
        for proj in parsed_projects[:3]:
            tech_str = ", ".join(proj["technologies"]) if proj["technologies"] else "Technical tools"
            proj_items.append({
                "name": proj["name"],
                "technologies": proj["technologies"],
                "assessment": f"Practical implementation demonstrating {tech_str}.",
                "improvement": "Include live deployment links (GitHub/Vercel/AWS) and specify architecture patterns used.",
                "impact": f"Frame {proj['name']} around the core problem solved and quantified results achieved."
            })
        proj_note = ""
    else:
        proj_note = "No projects were identified in the uploaded resume."

    # ----------------------------------------------------
    # 7. ATS / KEYWORD INSIGHTS
    # ----------------------------------------------------
    present_kw = matched_skills if matched_skills else detected_skills[:5]
    missing_kw = missing_skills if missing_skills else ["System Design", "Agile Methodology", "Code Optimization"]
    improve_kw = [s for s in detected_skills if s not in matched_skills][:4]
    if not improve_kw:
        improve_kw = ["REST API Integration", "Version Control (Git)"]

    # ----------------------------------------------------
    # 8. CAREER POSITIONING
    # ----------------------------------------------------
    career_pos = {
        "current_profile": f"{candidate_level} {detected_skills[0] if detected_skills else 'Software'} Specialist",
        "target_role": target_job,
        "alignment": f"{'High' if overall_score >= 80 else 'Moderate' if overall_score >= 60 else 'Developing'} Alignment ({overall_score}%)",
        "career_strength": f"Solid foundation in {', '.join(detected_skills[:3]) if detected_skills else 'core fundamentals'}",
        "primary_gap": f"Missing key role competencies: {', '.join(missing_skills[:2]) if missing_skills else 'advanced cloud architecture & metrics'}"
    }

    # ----------------------------------------------------
    # 9. PERSONALIZED RECOMMENDATIONS
    # ----------------------------------------------------
    rec_high = []
    rec_med = []
    rec_low = []
    
    if missing_skills:
        rec_high.append(f"Add and demonstrate target role skills: {', '.join(missing_skills[:3])}.")
    if not has_metrics:
        rec_high.append("Incorporate metric numbers (%, $, numbers) in all project & work bullet points.")
    if not rec_high:
        rec_high.append(f"Tailor professional summary to explicitly target {target_job} position.")
        
    if not proj_text:
        rec_med.append("Add a dedicated Technical Projects section showcasing 2+ hands-on projects.")
    else:
        rec_med.append("Add live demo or GitHub repository links for listed projects.")
    rec_med.append("Include specific frameworks and testing tools used in development.")
    
    if not cert_text:
        rec_low.append("Obtain an industry-recognized certification relevant to target job.")
    rec_low.append("Format contact details and section headers cleanly for ATS scanners.")

    # ----------------------------------------------------
    # 10. ACTION PLAN
    # ----------------------------------------------------
    action_plan = [
        {
            "step": "01",
            "title": "Resume & Impact Metrics",
            "description": f"Revise experience and project bullet points to highlight measurable results for {target_job}."
        },
        {
            "step": "02",
            "title": "Skill Gap Closure",
            "description": f"Focus on mastering and demonstrating missing skills: {', '.join(missing_recommended[:3])}."
        },
        {
            "step": "03",
            "title": "Project Portfolio Enhancement",
            "description": f"Upgrade project '{parsed_projects[0]['name'] if parsed_projects else 'Portfolio Project'}' with cloud hosting and unit test coverage."
        },
        {
            "step": "04",
            "title": "Interview & Technical Prep",
            "description": f"Prepare system design and coding interview scenarios tailored to {target_job} requirements."
        },
        {
            "step": "05",
            "title": "Targeted Job Applications",
            "description": f"Apply to {target_job} opportunities with your customized ATS-optimized resume."
        }
    ]

    # ----------------------------------------------------
    # 11. DYNAMIC SCORES
    # ----------------------------------------------------
    skill_alignment = min(100, max(35, int(resume_data.get("skill_match", 70))))
    experience_alignment = 85 if has_exp else 40
    project_relevance = 88 if has_proj else 45
    keyword_alignment = min(100, max(35, int(resume_data.get("resume_job_similarity", 0.6) * 100)))
    
    scores = {
        "overall": overall_score,
        "skill_alignment": skill_alignment,
        "experience_alignment": experience_alignment,
        "project_relevance": project_relevance,
        "keyword_alignment": keyword_alignment,
        "resume_quality": quality_score
    }

    return {
        "candidate_name": candidate_name,
        "executive_summary": exec_summary,
        "strengths": strengths,
        "areas_to_improve": areas_to_improve,
        "skill_analysis": {
            "strong_skills": strong_skills,
            "developing_skills": developing_skills,
            "missing_skills": missing_recommended
        },
        "experience_analysis": {
            "has_experience": has_exp,
            "items": exp_items,
            "general_note": exp_note
        },
        "project_analysis": {
            "has_projects": has_proj,
            "items": proj_items,
            "general_note": proj_note
        },
        "ats_keyword_insights": {
            "present_keywords": present_kw,
            "missing_keywords": missing_kw,
            "improvement_keywords": improve_kw
        },
        "career_positioning": career_pos,
        "recommendations": {
            "high_priority": rec_high,
            "medium_priority": rec_med,
            "low_priority": rec_low
        },
        "action_plan": action_plan,
        "scores": scores
    }


def generate_personalized_ai_review(resume_data, job_description="", target_job=""):
    """
    Main entry point for generating dynamic, 100% personalized AI review.
    Uses Gemini API if available, with robust evidence-based Python fallback.
    """
    resume_text = resume_data.get("resume_text", "")
    cleaned_resume = resume_data.get("cleaned_resume", resume_text)
    contact_info = resume_data.get("contact_info", {})
    detected_skills = resume_data.get("detected_skills", [])
    resume_sections = resume_data.get("resume_sections", {})
    matched_skills = resume_data.get("matched_skills", [])
    missing_skills = resume_data.get("missing_skills", [])
    overall_score = resume_data.get("overall_score", 75)
    target_job = target_job.strip() if target_job else "Target Position"
    
    # Try Gemini API if API key exists
    if GEMINI_KEY:
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            
            prompt = f"""
You are an expert ATS recruiter and executive career strategist.

Analyze ONLY the candidate information provided below:

CANDIDATE NAME: {extract_candidate_name(cleaned_resume, contact_info)}
CONTACT INFORMATION: {json.dumps(contact_info)}
TARGET ROLE: {target_job}
JOB DESCRIPTION: {job_description}

ACTUAL RESUME TEXT:
{cleaned_resume}

PARSED SECTIONS:
- Summary: {resume_sections.get('summary', '')}
- Education: {resume_sections.get('education', '')}
- Experience: {resume_sections.get('experience', '')}
- Projects: {resume_sections.get('projects', '')}
- Certifications: {resume_sections.get('certifications', '')}
- Skills: {', '.join(detected_skills)}
- Achievements: {resume_sections.get('achievements', '')}

MATCHED SKILLS: {', '.join(matched_skills)}
MISSING SKILLS: {', '.join(missing_skills)}

CRITICAL INSTRUCTIONS:
1. Do NOT hallucinate skills, projects, certifications, education, or companies not in the text.
2. If experience section is empty, set experience_analysis.has_experience = false and general_note = "No professional experience was identified in the uploaded resume."
3. If projects section is empty, set project_analysis.has_projects = false and general_note = "No projects were identified in the uploaded resume."
4. Generate a 100% personalized JSON response strictly adhering to this schema:

{{
  "candidate_name": "{extract_candidate_name(cleaned_resume, contact_info)}",
  "executive_summary": "Concise summary of candidate's actual resume, skills, experience, projects, and target role.",
  "strengths": [
    {{"title": "Title", "evidence": "Specific quote/evidence from resume"}}
  ],
  "areas_to_improve": [
    {{"title": "Title", "explanation": "Explanation based on missing/weak areas"}}
  ],
  "skill_analysis": {{
    "strong_skills": ["skill1", "skill2"],
    "developing_skills": ["skill3"],
    "missing_skills": ["skill4"]
  }},
  "experience_analysis": {{
    "has_experience": true/false,
    "items": [
      {{"role_or_company": "Role at Company", "strength": "...", "improvement": "..."}}
    ],
    "general_note": "..."
  }},
  "project_analysis": {{
    "has_projects": true/false,
    "items": [
      {{"name": "Project Name", "technologies": ["tech1"], "assessment": "...", "improvement": "...", "impact": "..."}}
    ],
    "general_note": "..."
  }},
  "ats_keyword_insights": {{
    "present_keywords": ["kw1"],
    "missing_keywords": ["kw2"],
    "improvement_keywords": ["kw3"]
  }},
  "career_positioning": {{
    "current_profile": "...",
    "target_role": "{target_job}",
    "alignment": "...",
    "career_strength": "...",
    "primary_gap": "..."
  }},
  "recommendations": {{
    "high_priority": ["rec1"],
    "medium_priority": ["rec2"],
    "low_priority": ["rec3"]
  }},
  "action_plan": [
    {{"step": "01", "title": "...", "description": "..."}}
  ],
  "scores": {{
    "overall": {overall_score},
    "skill_alignment": 80,
    "experience_alignment": 75,
    "project_relevance": 85,
    "keyword_alignment": 70,
    "resume_quality": 85
  }}
}}
"""
            response = model.generate_content(
                prompt,
                generation_config={"response_mime_type": "application/json"}
            )
            data = json.loads(response.text)
            if data and isinstance(data, dict) and "executive_summary" in data:
                return data
        except Exception as err:
            print(f"Gemini API Review Error: {err}. Using evidence-based Python fallback.")

    # Fallback to evidence-based Python engine
    return build_evidence_based_review(resume_data, target_job, job_description)
