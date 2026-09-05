import re
import io
from typing import Dict, List, Optional, Any
from pypdf import PdfReader
from langchain_core.messages import HumanMessage, SystemMessage
import model_router

ROLE_KEYWORDS = {
    "Software Developer": ["python", "java", "javascript", "react", "api", "git", "sql", "data structures", "algorithms", "c++", "c#", "node.js", "django", "flask", "docker", "kubernetes", "agile"],
    "Data Analyst": ["sql", "python", "excel", "tableau", "power bi", "statistics", "data analysis", "data visualization", "pandas", "numpy", "r", "machine learning"],
    "Banking (PO/Associate)": ["finance", "accounting", "economics", "customer service", "banking", "analytical skills", "communication", "sales", "operations", "compliance"],
    "Government Services (KAS/UPSC)": ["public administration", "economics", "history", "current affairs", "policy analysis", "geography", "political science", "leadership", "analytical", "writing"],
    "Healthcare/Medical": ["patient care", "clinical", "diagnosis", "anatomy", "physiology", "medical records", "nursing", "public health", "first aid", "cpr"],
    "Teaching": ["pedagogy", "curriculum", "assessment", "classroom", "education", "lesson planning", "instructional design", "mentoring", "communication", "subject matter expertise"],
    "Civil Engineer": ["autocad", "structural engineering", "project management", "construction", "design", "staad", "surveying", "materials"],
    "Marketing/Sales": ["digital marketing", "seo", "sem", "content creation", "social media", "sales", "crm", "b2b", "b2c", "communication", "negotiation"],
    "Tourism Management": ["hospitality", "tour operations", "customer service", "travel management", "event planning", "local geography", "communication", "marketing"],
    "Handicrafts/Artisan": ["craftsmanship", "design", "traditional arts", "pashmina", "papier-mache", "wood carving", "carpet weaving", "sales", "marketing"],
    "Agriculture/Horticulture": ["farming", "crop management", "soil science", "pest control", "irrigation", "agribusiness", "harvesting", "saffron", "apple farming"]
}

ACTION_VERBS = [
    "achieved", "built", "created", "designed", "developed", "implemented", 
    "improved", "increased", "led", "managed", "optimized", "reduced", 
    "analyzed", "collaborated", "conducted", "coordinated", "delivered", 
    "established", "executed", "facilitated", "generated", "initiated", 
    "integrated", "maintained", "negotiated", "organized", "planned", 
    "resolved", "spearheaded", "streamlined", "transformed"
]

def extract_text_from_pdf(pdf_file) -> str:
    """
    Extracts text from a PDF file object or path.
    """
    try:
        if isinstance(pdf_file, str):
            reader = PdfReader(pdf_file)
        else:
            pdf_file.seek(0)
            reader = PdfReader(pdf_file)
            
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return ""

def extract_resume_sections(text: str) -> Dict[str, str]:
    """
    Extracts common resume sections using rule-based header keyword matching.
    """
    sections = {
        "contact_info": "",
        "summary": "",
        "education": "",
        "experience": "",
        "skills": "",
        "projects": "",
        "certifications": "",
        "achievements": "",
        "hobbies": ""
    }
    
    if not text:
        return sections
        
    lines = text.split('\n')
    
    section_mapping = {
        "contact": "contact_info", "personal": "contact_info",
        "objective": "summary", "summary": "summary", "about": "summary", "profile": "summary",
        "education": "education", "academic": "education",
        "experience": "experience", "work": "experience", "internship": "experience", "employment": "experience",
        "skill": "skills", "technical": "skills", "expertise": "skills",
        "project": "projects",
        "certification": "certifications", "course": "certifications", "training": "certifications",
        "achievement": "achievements", "award": "achievements", "honor": "achievements",
        "hobby": "hobbies", "interest": "hobbies", "extracurricular": "hobbies", "activity": "hobbies"
    }
    
    current_section = None
    
    for line in lines:
        cleaned_line = line.strip().lower()
        if not cleaned_line:
            if current_section:
                sections[current_section] += "\n"
            continue
            
        # Check if line is a header (short length, contains keyword)
        is_header = False
        if len(cleaned_line) < 30: # typical header length
            for keyword, section_name in section_mapping.items():
                if keyword in cleaned_line:
                    current_section = section_name
                    is_header = True
                    break
                    
        if not is_header and current_section:
            sections[current_section] += line + "\n"
        elif not is_header and not current_section:
             # Assume top is contact info if no header seen yet
             if len(sections["contact_info"]) < 500:
                sections["contact_info"] += line + "\n"
                
    # Clean up trailing newlines
    for k in sections:
        sections[k] = sections[k].strip()
        
    return sections

def score_resume(sections: Dict[str, str], target_role: str = None) -> Dict:
    """
    Scores the resume on Completeness, Content Quality, Relevance, and Formatting.
    """
    scores = {
        "completeness": 0,
        "content_quality": 0,
        "relevance": 0,
        "formatting": 0,
        "total": 0,
        "max_score": 100,
        "grade": "F",
        "breakdown": {}
    }
    
    # 1. Completeness (25 points)
    key_sections = ["education", "skills", "experience", "projects"]
    found_key_sections = [s for s in key_sections if sections.get(s)]
    completeness_score = min(25, int((len(found_key_sections) / len(key_sections)) * 25))
    if sections.get("contact_info"): completeness_score += 2
    if sections.get("summary"): completeness_score += 2
    scores["completeness"] = min(25, completeness_score)
    
    # 2. Content Quality (25 points)
    total_length = sum(len(content.split()) for content in sections.values())
    quality_score = 10
    if total_length > 200: quality_score += 5
    if total_length > 400: quality_score += 5
    if total_length > 800: quality_score += 5
    
    if len(sections.get("experience", "").split()) > 50: quality_score += 5
    if len(sections.get("projects", "").split()) > 30: quality_score += 5
    scores["content_quality"] = min(25, quality_score)
    
    # 3. Relevance (25 points)
    relevance_score = 15 # default average
    if target_role and target_role in ROLE_KEYWORDS:
        keywords = ROLE_KEYWORDS[target_role]
        combined_text = (sections.get("skills", "") + " " + sections.get("experience", "") + " " + sections.get("projects", "")).lower()
        matched = sum(1 for kw in keywords if kw in combined_text)
        match_ratio = matched / len(keywords) if keywords else 0
        relevance_score = int(match_ratio * 25)
        # boost slightly
        relevance_score = min(25, relevance_score + 5)
    else:
        # If no target role, judge relevance by presence of clear skills
        if len(sections.get("skills", "").split()) > 10: relevance_score = 20
        
    scores["relevance"] = min(25, relevance_score)
    
    # 4. Formatting (25 points)
    fmt_score = 10
    combined_text = " ".join(sections.values()).lower()
    
    # Check for numbers/percentages (quantifiable achievements)
    if re.search(r'\d+%|\d+\s*(?:percent|lakh|crore|k|m)', combined_text):
        fmt_score += 5
        
    # Check for action verbs
    verbs_found = sum(1 for verb in ACTION_VERBS if verb in combined_text)
    if verbs_found > 5: fmt_score += 5
    if verbs_found > 10: fmt_score += 5
    
    scores["formatting"] = min(25, fmt_score)
    
    # Total
    scores["total"] = scores["completeness"] + scores["content_quality"] + scores["relevance"] + scores["formatting"]
    
    if scores["total"] >= 90: scores["grade"] = "A+"
    elif scores["total"] >= 80: scores["grade"] = "A"
    elif scores["total"] >= 70: scores["grade"] = "B"
    elif scores["total"] >= 60: scores["grade"] = "C"
    elif scores["total"] >= 50: scores["grade"] = "D"
    
    scores["breakdown"] = {
        "completeness_msg": f"{scores['completeness']}/25 points. Present key sections: {', '.join(found_key_sections)}.",
        "content_quality_msg": f"{scores['content_quality']}/25 points. Total word count: {total_length}.",
        "relevance_msg": f"{scores['relevance']}/25 points. Based on target role: {target_role or 'General'}.",
        "formatting_msg": f"{scores['formatting']}/25 points. Action verbs found: {verbs_found}."
    }
    
    return scores

def generate_improvement_suggestions(sections: Dict, scores: Dict, target_role: str = None) -> List[str]:
    """
    Generates actionable improvement suggestions based on scores and sections.
    """
    suggestions = []
    
    if not sections.get("summary"):
        suggestions.append("Add a professional summary or objective at the top of your resume.")
    
    if not sections.get("skills"):
        suggestions.append("Include a dedicated 'Skills' section listing your technical and soft skills.")
        
    if not sections.get("projects") and not sections.get("experience"):
        suggestions.append("Add details about projects or work experience to demonstrate practical application of your skills.")
        
    if scores["formatting"] < 15:
        suggestions.append("Use more strong action verbs (e.g., 'achieved', 'developed', 'managed') to start your bullet points.")
        suggestions.append("Include quantifiable achievements (numbers, percentages, metrics) to show your impact.")
        
    if target_role and target_role in ROLE_KEYWORDS:
        keywords = ROLE_KEYWORDS[target_role]
        combined_text = " ".join(sections.values()).lower()
        missing = [kw for kw in keywords if kw not in combined_text]
        if missing:
            suggestions.append(f"To better match the {target_role} role, consider adding relevant keywords if you have experience with them: {', '.join(missing[:5])}.")
            
    if scores["content_quality"] < 15:
        suggestions.append("Expand on your experience and project descriptions. Provide more detail on what you did and the tools used.")
        
    if len(suggestions) < 3:
        suggestions.append("Ensure your resume is tailored to each specific job description you apply for.")
        suggestions.append("Keep formatting clean, consistent, and easy to read for ATS parsers.")
        
    return suggestions

def get_available_target_roles() -> List[str]:
    """Returns a list of roles that have defined keywords."""
    return list(ROLE_KEYWORDS.keys())

def analyze_resume(text: str, target_role: str = None) -> Dict:
    """
    Main analysis orchestrator pipeline.
    """
    if not text:
        return {
            "sections": {},
            "scores": {},
            "suggestions": ["No text could be extracted from the resume."],
            "word_count": 0,
            "detected_skills": [],
            "target_role": target_role
        }
        
    sections = extract_resume_sections(text)
    scores = score_resume(sections, target_role)
    suggestions = generate_improvement_suggestions(sections, scores, target_role)
    
    word_count = len(text.split())
    
    # Simple skill detection
    detected_skills = []
    text_lower = text.lower()
    for role_skills in ROLE_KEYWORDS.values():
        for skill in role_skills:
            if skill in text_lower and skill not in detected_skills:
                detected_skills.append(skill)
                
    return {
        "sections": sections,
        "scores": scores,
        "suggestions": suggestions,
        "word_count": word_count,
        "detected_skills": sorted(detected_skills),
        "target_role": target_role
    }

def get_ai_review(text: str, target_role: str = None) -> str:
    """
    Uses Gemini LLM for a detailed narrative review.
    """
    try:
        llm = model_router.get_llm("review resume", 0)
        sys_msg = SystemMessage(content="You are an expert career counselor and resume reviewer, particularly familiar with the job market in Jammu & Kashmir. Provide constructive, encouraging, and detailed feedback.")
        
        prompt = f"Please review the following resume text. "
        if target_role:
            prompt += f"The candidate is targeting the role of '{target_role}'. "
        prompt += "Focus on strengths, areas for improvement, formatting issues, and how well it fits the target role (if provided). Keep the review under 400 words.\n\nResume Text:\n" + text[:4000]
        
        hum_msg = HumanMessage(content=prompt)
        response = llm.invoke([sys_msg, hum_msg])
        return response.content
    except Exception as e:
        print(f"Error in get_ai_review: {e}")
        return "The AI review is currently unavailable. Please refer to the automated scoring and suggestions provided above."

def compare_to_job_requirements(sections: Dict, job_data: Dict) -> Dict:
    """
    Compares resume sections to job requirements.
    """
    combined_text = " ".join(sections.values()).lower()
    job_skills = job_data.get("skills", [])
    if isinstance(job_skills, str):
        job_skills = [s.strip().lower() for s in job_skills.split(",")]
    else:
        job_skills = [s.lower() for s in job_skills]
        
    overlap = []
    missing = []
    for skill in job_skills:
        if skill in combined_text:
            overlap.append(skill)
        else:
            missing.append(skill)
            
    match_pct = int((len(overlap) / len(job_skills) * 100)) if job_skills else 0
    
    rec = "Strong match for this role."
    if match_pct < 50:
        rec = "Consider gaining more of the required skills before applying."
    elif match_pct < 80:
        rec = "Good match, but addressing missing skills would improve your chances."
        
    return {
        "qualification_match": match_pct > 50,
        "skill_overlap": overlap,
        "missing_skills": missing,
        "match_percentage": match_pct,
        "recommendation": rec
    }

def render_resume_report(analysis: Dict) -> str:
    """
    Generates a comprehensive markdown report.
    """
    scores = analysis.get("scores", {})
    if not scores:
        return "No analysis available."
        
    md = f"# Resume Analysis Report\n\n"
    md += f"## Overall Score: {scores.get('total', 0)}/100 (Grade: {scores.get('grade', 'F')})\n\n"
    
    md += "### Score Breakdown\n"
    md += f"- **Completeness (25):** {scores.get('completeness', 0)} - {scores.get('breakdown', {}).get('completeness_msg', '')}\n"
    md += f"- **Content Quality (25):** {scores.get('content_quality', 0)} - {scores.get('breakdown', {}).get('content_quality_msg', '')}\n"
    md += f"- **Relevance (25):** {scores.get('relevance', 0)} - {scores.get('breakdown', {}).get('relevance_msg', '')}\n"
    md += f"- **Formatting (25):** {scores.get('formatting', 0)} - {scores.get('breakdown', {}).get('formatting_msg', '')}\n\n"
    
    md += "### Key Areas for Improvement\n"
    for suggestion in analysis.get('suggestions', []):
        md += f"- {suggestion}\n"
        
    md += "\n### Detected Skills\n"
    skills = analysis.get('detected_skills', [])
    if skills:
        md += ", ".join(skills) + "\n"
    else:
        md += "No specific technical skills detected.\n"
        
    return md
