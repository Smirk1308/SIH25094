import datetime
import json
import random
from typing import Dict, List, Optional, Any
import streamlit as st
from langchain_core.messages import HumanMessage, SystemMessage

try:
    import model_router
except ImportError:
    model_router = None

# -----------------------------------------------------------------------------
# Data Definitions
# -----------------------------------------------------------------------------

INTERVIEW_TEMPLATES = {
    "jkssb_junior_assistant": {
        "title": "JKSSB Junior Assistant Mock",
        "description": "Mock interview for the JKSSB Junior Assistant position focusing on general knowledge, English, quant, and computer awareness.",
        "rounds": ["General Knowledge", "English Proficiency", "Quantitative Aptitude", "Computer Awareness"],
        "questions_per_round": 3,
        "time_per_question": 60,
        "scoring_rubric": {
            "accuracy": 40,
            "clarity": 30,
            "completeness": 20,
            "confidence": 10,
        },
        "difficulty": "moderate",
        "target_audience": "Candidates preparing for JKSSB Junior Assistant exams",
    },
    "kas_interview": {
        "title": "KAS Interview Mock",
        "description": "Rigorous mock interview for Kashmir Administrative Service aspirants.",
        "rounds": ["Current Affairs J&K", "Domain Knowledge", "Ethics & Governance", "Personality Assessment"],
        "questions_per_round": 3,
        "time_per_question": 90,
        "scoring_rubric": {
            "accuracy": 30,
            "clarity": 20,
            "completeness": 30,
            "confidence": 20,
        },
        "difficulty": "hard",
        "target_audience": "KAS and other civil services aspirants",
    },
    "engineering_placement": {
        "title": "Engineering Placement Mock",
        "description": "Technical and HR interview for engineering campus placements.",
        "rounds": ["DSA & Problem Solving", "System Design Basics", "HR & Behavioral", "Project Discussion"],
        "questions_per_round": 3,
        "time_per_question": 120,
        "scoring_rubric": {
            "accuracy": 50,
            "clarity": 20,
            "completeness": 20,
            "confidence": 10,
        },
        "difficulty": "hard",
        "target_audience": "Engineering students seeking campus placements",
    },
    "medical_viva": {
        "title": "Medical Viva Mock",
        "description": "Viva voce preparation for medical students.",
        "rounds": ["Anatomy & Physiology", "Clinical Reasoning", "Medical Ethics", "Patient Communication"],
        "questions_per_round": 3,
        "time_per_question": 90,
        "scoring_rubric": {
            "accuracy": 50,
            "clarity": 20,
            "completeness": 20,
            "confidence": 10,
        },
        "difficulty": "hard",
        "target_audience": "Medical students and practitioners",
    },
    "bank_po_interview": {
        "title": "Bank PO Interview Mock",
        "description": "Mock interview for Probationary Officer exams in banking.",
        "rounds": ["Banking & Economy", "General Awareness", "Reasoning", "Customer Service"],
        "questions_per_round": 3,
        "time_per_question": 60,
        "scoring_rubric": {
            "accuracy": 40,
            "clarity": 30,
            "completeness": 20,
            "confidence": 10,
        },
        "difficulty": "moderate",
        "target_audience": "Banking job aspirants",
    }
}

SAMPLE_QUESTIONS = {
    "jkssb_junior_assistant": {
        "General Knowledge": [
            "What is the capital of Jammu and Kashmir?",
            "Can you name the major rivers flowing through J&K?",
            "Who was the last ruling Maharaja of the princely state of Jammu and Kashmir?",
            "What is the significance of Article 370?",
            "Name three major tourist destinations in J&K.",
            "What are the major crops grown in the Kashmir Valley?"
        ],
        "English Proficiency": [
            "Can you explain the difference between 'affect' and 'effect'?",
            "Give an example of a sentence using the passive voice.",
            "What does the idiom 'bite the bullet' mean?",
            "Correct this sentence: 'He don't have no money.'",
            "What is a synonym for 'ubiquitous'?",
            "Construct a sentence using the word 'ephemeral'."
        ],
        "Quantitative Aptitude": [
            "If a train travels 60 km in 1.5 hours, what is its average speed?",
            "What is 15% of 250?",
            "Solve for x: 3x + 5 = 20.",
            "If the price of a shirt is discounted by 20% from Rs. 500, what is the new price?",
            "What is the square root of 144?",
            "A person walks 3 km north, then 4 km east. How far are they from the starting point?"
        ],
        "Computer Awareness": [
            "What does RAM stand for and what is its function?",
            "What is the difference between hardware and software?",
            "Name three popular web browsers.",
            "What is a computer virus?",
            "What is the function of the operating system?",
            "What is the shortcut key for copying text in Windows?"
        ]
    },
    "kas_interview": {
        "Current Affairs J&K": [
            "Discuss the recent initiatives taken for the economic development of J&K.",
            "What are the key challenges in the health sector of J&K currently?",
            "How has the administrative restructuring post-2019 impacted governance?",
            "What is the role of Panchayati Raj Institutions in J&K today?",
            "Discuss the recent infrastructure projects in the Chenab valley.",
            "What are the major environmental concerns in the Dal Lake ecosystem?"
        ],
        "Domain Knowledge": [
            "Explain the basic structure doctrine of the Indian Constitution.",
            "What is the difference between a statutory body and a constitutional body?",
            "Describe the process of budget formulation in a state.",
            "What are the key principles of good governance?",
            "Discuss the role of the District Magistrate in disaster management.",
            "Explain the concept of e-governance with relevant examples."
        ],
        "Ethics & Governance": [
            "How would you handle a situation where a superior asks you to do something unethical?",
            "What is the importance of transparency in public administration?",
            "Discuss a scenario where you faced a moral dilemma and how you resolved it.",
            "What are the ethical implications of using AI in governance?",
            "How do you balance efficiency with equity in public service delivery?",
            "What is the role of empathy in civil services?"
        ],
        "Personality Assessment": [
            "What motivated you to prepare for the civil services?",
            "Describe a time when you failed and what you learned from it.",
            "What are your key strengths and weaknesses?",
            "Where do you see yourself in 10 years?",
            "How do you handle stress and high-pressure situations?",
            "Describe a leadership experience you have had."
        ]
    },
    "engineering_placement": {
        "DSA & Problem Solving": [
            "Explain the concept of a Binary Search Tree and its operations.",
            "What is the time complexity of Quick Sort and why?",
            "How would you detect a cycle in a linked list?",
            "Explain the concept of dynamic programming with an example.",
            "What is a Hash Map and how does it handle collisions?",
            "Describe an algorithm to find the shortest path in a graph."
        ],
        "System Design Basics": [
            "What are the differences between SQL and NoSQL databases?",
            "Explain the concept of load balancing.",
            "How would you design a URL shortening service like bit.ly?",
            "What is caching and what are common caching strategies?",
            "Explain the concepts of vertical and horizontal scaling.",
            "What is a microservices architecture?"
        ],
        "HR & Behavioral": [
            "Tell me about a time you disagreed with a team member. How did you handle it?",
            "What is your greatest professional achievement?",
            "Why do you want to work for our company?",
            "Describe a time you had to learn a new technology quickly.",
            "How do you prioritize tasks when you have multiple deadlines?",
            "What are your salary expectations?"
        ],
        "Project Discussion": [
            "Can you walk me through the architecture of your most recent project?",
            "What was the most challenging technical problem you solved in your project?",
            "How did you test your application?",
            "If you could do this project again, what would you change?",
            "What technologies did you choose and why?",
            "How did you handle version control and collaboration?"
        ]
    },
    "medical_viva": {
         "Anatomy & Physiology": [
            "Describe the blood flow through the human heart.",
            "What are the main functions of the liver?",
            "Explain the process of cellular respiration.",
            "Describe the anatomy of the cranial nerves.",
            "What is the role of the endocrine system?",
            "Explain the mechanism of muscle contraction."
        ],
        "Clinical Reasoning": [
            "A patient presents with acute chest pain. What is your differential diagnosis?",
            "How would you manage a patient with suspected appendicitis?",
            "What are the clinical signs of dehydration in a child?",
            "Describe the steps in performing a basic neurological exam.",
            "How do you interpret an ECG showing ST elevation?",
            "What is the protocol for managing anaphylactic shock?"
        ],
        "Medical Ethics": [
            "Explain the principle of informed consent.",
            "How would you handle a situation where a patient refuses life-saving treatment?",
            "Discuss the ethical considerations in end-of-life care.",
            "What is the importance of patient confidentiality?",
            "How do you address medical errors?",
            "Discuss the ethics of organ donation."
        ],
        "Patient Communication": [
            "How do you deliver bad news to a patient's family?",
            "How would you explain a complex medical procedure to a patient with low health literacy?",
            "Describe your approach to communicating with an angry or non-compliant patient.",
            "How do you ensure cultural competence in patient interactions?",
            "What strategies do you use to build trust with patients?",
            "How do you handle a language barrier during a consultation?"
        ]
    },
    "bank_po_interview": {
         "Banking & Economy": [
            "What is the function of the Reserve Bank of India (RBI)?",
            "Explain the difference between Repo Rate and Reverse Repo Rate.",
            "What is Non-Performing Asset (NPA)?",
            "Discuss the impact of inflation on the economy.",
            "What are the different types of bank accounts?",
            "What is digital banking and its advantages?"
        ],
        "General Awareness": [
            "Who is the current Finance Minister of India?",
            "What are the major components of the Union Budget?",
            "Name three international financial institutions.",
            "What are the current global economic trends?",
            "Discuss a recent important government scheme related to banking.",
            "What is the significance of the G20 summit?"
        ],
        "Reasoning": [
            "Solve this series: 2, 6, 12, 20, ?",
            "If A is the brother of B, and B is the sister of C, how is A related to C?",
            "What comes next in the sequence: A, C, F, J, O, ?",
            "In a certain code, 'BANK' is written as 'CBOF'. How is 'CASH' written in that code?",
            "A clock shows 3:15. What is the angle between the hour and minute hands?",
            "Solve a basic syllogism problem."
        ],
        "Customer Service": [
            "How would you handle an irate customer complaining about an unauthorized transaction?",
            "Why is customer retention important for a bank?",
            "Describe a situation where you went above and beyond for a customer.",
            "How do you explain a new banking product to an elderly customer?",
            "What are the key qualities of a good bank employee?",
            "How do you handle a situation where you don't know the answer to a customer's question?"
        ]
    }
}


# -----------------------------------------------------------------------------
# Core Functions
# -----------------------------------------------------------------------------

def get_all_templates() -> Dict[str, Dict]:
    """
    Returns the complete dictionary of interview templates.
    """
    return INTERVIEW_TEMPLATES

def start_interview(template_id: str, candidate_profile: Optional[Dict] = None) -> Dict:
    """
    Initializes a new interview session state.
    """
    if template_id not in INTERVIEW_TEMPLATES:
        raise ValueError(f"Invalid template_id: {template_id}")

    template = INTERVIEW_TEMPLATES[template_id]
    
    session = {
        "template_id": template_id,
        "template": template,
        "candidate_profile": candidate_profile or {},
        "current_round": 0,
        "current_question": 0,
        "responses": [],
        "status": "in_progress",
        "started_at": datetime.datetime.now().isoformat(),
    }
    return session

def get_next_question(session: Dict) -> Optional[Dict]:
    """
    Returns the next question based on session progress, adapting difficulty based on recent scores.
    """
    if session["status"] != "in_progress":
        return None

    template = session["template"]
    rounds = template["rounds"]
    questions_per_round = template["questions_per_round"]
    
    current_round_idx = session["current_round"]
    current_question_idx = session["current_question"]
    
    if current_round_idx >= len(rounds):
        return None
        
    round_name = rounds[current_round_idx]
    
    # Adaptive difficulty logic
    recent_scores = [r["score_breakdown"]["total_score"] for r in session["responses"][-2:] if "score_breakdown" in r]
    avg_score = sum(recent_scores) / len(recent_scores) if recent_scores else 50
    
    available_questions = SAMPLE_QUESTIONS.get(session["template_id"], {}).get(round_name, [])
    if not available_questions:
        available_questions = ["Could you tell me more about your experience in this area?"]
        
    # Pick question based on difficulty
    if avg_score < 40:
        question_idx = min(current_question_idx, len(available_questions) // 3)
    elif avg_score > 80:
        question_idx = min(current_question_idx + len(available_questions) // 2, len(available_questions) - 1)
    else:
        question_idx = current_question_idx % len(available_questions)
        
    question_text = available_questions[question_idx]

    return {
        "round_name": round_name,
        "round_number": current_round_idx + 1,
        "question_number": current_question_idx + 1,
        "question": question_text,
        "total_questions": questions_per_round,
        "total_rounds": len(rounds)
    }

def evaluate_answer(question: str, answer: str, rubric: Dict, round_name: str) -> Dict:
    """
    Uses Gemini LLM to evaluate the answer against the rubric.
    """
    if not answer or not answer.strip():
        return {
            "scores": {k: 0 for k in rubric.keys()},
            "total_score": 0,
            "max_score": 100,
            "feedback": "No answer provided.",
            "strengths": [],
            "improvements": ["Provide a complete answer."]
        }

    default_result = {
        "scores": {k: int(v * 0.6) for k, v in rubric.items()},
        "total_score": 60,
        "max_score": 100,
        "feedback": "Answer received. (Fallback evaluation used due to LLM error).",
        "strengths": ["Answered the question"],
        "improvements": ["Add more specific details"]
    }

    if model_router is None:
        return default_result
        
    try:
        llm = model_router.get_llm("Evaluate interview answer", 0)
        
        system_prompt = f"""
You are an expert interviewer evaluating a candidate's answer for the '{round_name}' round.
Evaluate the answer based on the following rubric, assigning scores up to the maximum weight for each dimension:
{json.dumps(rubric, indent=2)}

Question: {question}
Answer: {answer}

Provide your evaluation in STRICT JSON format with the following structure:
{{
    "scores": {{
        "accuracy": <int>,
        "clarity": <int>,
        "completeness": <int>,
        "confidence": <int>
    }},
    "feedback": "<string: detailed overall feedback>",
    "strengths": ["<string>", "<string>"],
    "improvements": ["<string>", "<string>"]
}}
"""
        messages = [
            SystemMessage(content="You are a strict JSON-producing assistant."),
            HumanMessage(content=system_prompt)
        ]
        
        response = llm.invoke(messages)
        content = response.content
        
        # Clean up JSON if necessary
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
            
        result = json.loads(content)
        
        # Calculate total
        total = sum(result.get("scores", {}).values())
        result["total_score"] = total
        result["max_score"] = 100
        
        return result
        
    except Exception as e:
        print(f"Error evaluating answer: {e}")
        return default_result

def submit_answer(session: Dict, answer: str) -> Dict:
    """
    Records the answer, evaluates it, and advances the session state.
    """
    if session["status"] != "in_progress":
        return session
        
    q_data = get_next_question(session)
    if not q_data:
        session["status"] = "completed"
        return session

    rubric = session["template"]["scoring_rubric"]
    evaluation = evaluate_answer(q_data["question"], answer, rubric, q_data["round_name"])
    
    response_record = {
        "round": q_data["round_name"],
        "question": q_data["question"],
        "answer": answer,
        "score_breakdown": evaluation,
        "feedback": evaluation.get("feedback", "")
    }
    
    session["responses"].append(response_record)
    
    # Advance state
    session["current_question"] += 1
    if session["current_question"] >= session["template"]["questions_per_round"]:
        session["current_question"] = 0
        session["current_round"] += 1
        
    if session["current_round"] >= len(session["template"]["rounds"]):
        session["status"] = "completed"
        session["completed_at"] = datetime.datetime.now().isoformat()
        
    return session

def generate_interview_report(session: Dict) -> str:
    """
    Generates a comprehensive markdown report based on the session data.
    """
    if not session.get("responses"):
        return "No interview data available to generate a report."
        
    responses = session["responses"]
    total_score = sum(r.get("score_breakdown", {}).get("total_score", 0) for r in responses)
    max_possible = len(responses) * 100
    percentage = (total_score / max_possible) * 100 if max_possible > 0 else 0
    
    # Grade logic
    if percentage >= 90:
        grade = "A"
    elif percentage >= 80:
        grade = "B"
    elif percentage >= 70:
        grade = "C"
    elif percentage >= 60:
        grade = "D"
    else:
        grade = "F"
        
    # Round breakdown
    round_scores = {}
    for r in responses:
        rnd = r["round"]
        score = r.get("score_breakdown", {}).get("total_score", 0)
        if rnd not in round_scores:
            round_scores[rnd] = {"total": 0, "count": 0}
        round_scores[rnd]["total"] += score
        round_scores[rnd]["count"] += 1
        
    round_summary = []
    weak_rounds = []
    for rnd, data in round_scores.items():
        avg = data["total"] / data["count"]
        round_summary.append(f"| {rnd} | {avg:.1f}/100 |")
        if avg < 70:
            weak_rounds.append(rnd)
            
    # Strengths and improvements
    all_strengths = []
    all_improvements = []
    for r in responses:
        all_strengths.extend(r.get("score_breakdown", {}).get("strengths", []))
        all_improvements.extend(r.get("score_breakdown", {}).get("improvements", []))
        
    top_strengths = list(set(all_strengths))[:3]
    top_improvements = list(set(all_improvements))[:3]
    
    report = f"""# Mock Interview Performance Report

## Overall Summary
* **Total Score:** {total_score}/{max_possible} ({percentage:.1f}%)
* **Grade:** {grade}

## Round-by-Round Breakdown
| Round | Average Score |
|-------|---------------|
{chr(10).join(round_summary)}

## Top Strengths
{chr(10).join(f"- {s}" for s in top_strengths) if top_strengths else "- None identified"}

## Areas for Improvement
{chr(10).join(f"- {i}" for i in top_improvements) if top_improvements else "- None identified"}
"""
    if weak_rounds:
        report += "\n## Study Recommendations\n"
        tips = get_improvement_tips(weak_rounds)
        for rnd, tips_list in tips.items():
            report += f"**{rnd}:**\n"
            for tip in tips_list:
                report += f"- {tip}\n"
            report += "\n"
            
    return report

def get_improvement_tips(weak_areas: List[str]) -> Dict[str, List[str]]:
    """
    Returns actionable study tips mapped by weak round name.
    """
    tips_db = {
        "General Knowledge": ["Read daily newspapers.", "Review Lucent's General Knowledge.", "Follow J&K specific news portals."],
        "Quantitative Aptitude": ["Practice daily arithmetic problems.", "Review RS Aggarwal.", "Take timed quizzes."],
        "DSA & Problem Solving": ["Practice on LeetCode/HackerRank daily.", "Review standard algorithms and data structures.", "Do mock whiteboarding sessions."],
        "System Design Basics": ["Read 'Designing Data-Intensive Applications'.", "Study common architectural patterns.", "Watch system design mock interviews on YouTube."],
        "Medical Ethics": ["Review standard medical ethics guidelines.", "Discuss case studies with peers."],
        "English Proficiency": ["Read English literature.", "Practice grammar exercises.", "Listen to English podcasts."]
    }
    
    result = {}
    for area in weak_areas:
        result[area] = tips_db.get(area, [f"Focus on core concepts of {area}.", "Find standard reference materials for this topic.", "Practice more questions in this area."])
    return result

def get_interview_progress(session: Dict) -> Dict:
    """
    Returns the current progress metrics of the interview.
    """
    template = session.get("template", {})
    total_rounds = len(template.get("rounds", []))
    q_per_round = template.get("questions_per_round", 0)
    total_questions = total_rounds * q_per_round
    
    current_round = session.get("current_round", 0)
    current_question = session.get("current_question", 0)
    
    completed_questions = (current_round * q_per_round) + current_question
    
    responses = session.get("responses", [])
    avg_score = sum(r.get("score_breakdown", {}).get("total_score", 0) for r in responses) / len(responses) if responses else 0.0
    
    current_round_name = ""
    if current_round < total_rounds:
        current_round_name = template["rounds"][current_round]
        
    return {
        "completed_questions": completed_questions,
        "total_questions": total_questions,
        "completed_rounds": current_round,
        "total_rounds": total_rounds,
        "avg_score": avg_score,
        "current_round_name": current_round_name
    }
