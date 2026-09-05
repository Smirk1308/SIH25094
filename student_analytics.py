import random
import datetime
from typing import Dict, List, Tuple

# Risk Factor Definitions
RISK_FACTORS = {
    "attendance_below_75": {"weight": 0.25, "label": "Low Attendance (<75%)", "icon": "🗓️"},
    "failing_subjects": {"weight": 0.20, "label": "Failing in 2+ Subjects", "icon": "📚"},
    "family_income_stress": {"weight": 0.15, "label": "Financial Stress (Income <₹2.5L)", "icon": "💸"},
    "remote_district": {"weight": 0.10, "label": "Remote District (Limited Access)", "icon": "🏔️"},
    "first_gen_college": {"weight": 0.10, "label": "First-Generation College Student", "icon": "🎓"},
    "no_scholarship": {"weight": 0.10, "label": "No Active Scholarship", "icon": "💰"},
    "engagement_drop": {"weight": 0.05, "label": "Declining Platform Engagement", "icon": "📉"},
    "missed_deadlines": {"weight": 0.05, "label": "Missed Application Deadlines", "icon": "⏰"},
}

REMOTE_DISTRICTS = [
    "Doda", "Kishtwar", "Ramban", "Reasi", "Poonch", "Rajouri", 
    "Kupwara", "Bandipora", "Ganderbal", "Kulgam", "Shopian"
]

FIRST_NAMES_MALE = ["Aamir", "Bashir", "Danish", "Faisal", "Irfan", "Junaid", "Khalid", "Mohsin", "Owais", "Rayees", "Suhail", "Tariq", "Waseem", "Zahoor", "Rohit", "Vikram", "Aditya", "Deepak", "Rajesh", "Sunil"]
FIRST_NAMES_FEMALE = ["Aasiya", "Bisma", "Deeba", "Farhana", "Huma", "Insha", "Komal", "Mehak", "Nazia", "Rabia", "Saba", "Ulfat", "Zehra", "Priya", "Neha", "Pooja", "Swati", "Anjali"]
LAST_NAMES = ["Bhat", "Dar", "Lone", "Mir", "Rather", "Shah", "Wani", "Malik", "Sofi", "Parray", "Kumar", "Sharma", "Singh", "Gupta", "Jamwal", "Thakur", "Choudhary", "Koul", "Pandit", "Raina"]
DISTRICTS = ["Srinagar", "Jammu", "Anantnag", "Baramulla", "Pulwama", "Kupwara", "Bandipora", "Ganderbal", "Kulgam", "Shopian", "Budgam", "Doda", "Kishtwar", "Ramban", "Rajouri", "Poonch", "Udhampur", "Kathua", "Samba", "Reasi"]
INSTITUTIONS = ["NIT Srinagar", "IUST Awantipora", "GMC Srinagar", "GMC Jammu", "University of Kashmir", "University of Jammu", "SKUAST-K", "MIET Jammu", "GEC Jammu", "SSM Parihaspora", "BGSBU Rajouri", "CUK", "CUJ"]
PROGRAMS = ["B.Tech CSE", "B.Tech ECE", "B.Tech ME", "B.Tech Civil", "MBBS", "BDS", "BAMS", "BSc Nursing", "BA Economics", "BA English", "BCom", "BBA", "BSc Physics", "BSc Chemistry", "LLB", "B.Ed", "BSc Agriculture"]
CATEGORIES = ["OM", "SC", "ST", "OBC", "RBA"]

def get_risk_category(score: float) -> str:
    """
    Returns category string based on score thresholds
    Low (0-30) | Medium (31-55) | High (56-75) | Critical (76-100)
    """
    if score <= 30:
        return "Low"
    elif score <= 55:
        return "Medium"
    elif score <= 75:
        return "High"
    else:
        return "Critical"

def calculate_risk_score(student: Dict) -> Dict:
    """
    Evaluates each risk factor against the student profile.
    """
    total_score = 0.0
    active_risk_factors = []
    protective_factors = []
    
    # 1. Low Attendance (<75%)
    if student["attendance_percent"] < 75.0:
        total_score += RISK_FACTORS["attendance_below_75"]["weight"] * 100
        active_risk_factors.append({
            "factor": "attendance_below_75",
            "label": RISK_FACTORS["attendance_below_75"]["label"],
            "weight": RISK_FACTORS["attendance_below_75"]["weight"],
            "icon": RISK_FACTORS["attendance_below_75"]["icon"]
        })
    else:
        protective_factors.append("Good attendance record")

    # 2. Failing Subjects (2+)
    if student["failing_subjects"] >= 2:
        total_score += RISK_FACTORS["failing_subjects"]["weight"] * 100
        active_risk_factors.append({
            "factor": "failing_subjects",
            "label": RISK_FACTORS["failing_subjects"]["label"],
            "weight": RISK_FACTORS["failing_subjects"]["weight"],
            "icon": RISK_FACTORS["failing_subjects"]["icon"]
        })
    elif student["failing_subjects"] == 0 and student["cgpa"] > 7.5:
        protective_factors.append("Strong academic performance")

    # 3. Financial Stress (Income < 2.5L)
    if student["family_income"] < 250000:
        total_score += RISK_FACTORS["family_income_stress"]["weight"] * 100
        active_risk_factors.append({
            "factor": "family_income_stress",
            "label": RISK_FACTORS["family_income_stress"]["label"],
            "weight": RISK_FACTORS["family_income_stress"]["weight"],
            "icon": RISK_FACTORS["family_income_stress"]["icon"]
        })

    # 4. Remote District
    if student["district"] in REMOTE_DISTRICTS:
        total_score += RISK_FACTORS["remote_district"]["weight"] * 100
        active_risk_factors.append({
            "factor": "remote_district",
            "label": RISK_FACTORS["remote_district"]["label"],
            "weight": RISK_FACTORS["remote_district"]["weight"],
            "icon": RISK_FACTORS["remote_district"]["icon"]
        })

    # 5. First Generation College Student
    if student.get("first_gen_student", False):
        total_score += RISK_FACTORS["first_gen_college"]["weight"] * 100
        active_risk_factors.append({
            "factor": "first_gen_college",
            "label": RISK_FACTORS["first_gen_college"]["label"],
            "weight": RISK_FACTORS["first_gen_college"]["weight"],
            "icon": RISK_FACTORS["first_gen_college"]["icon"]
        })

    # 6. No Scholarship
    if not student.get("has_scholarship", False):
        total_score += RISK_FACTORS["no_scholarship"]["weight"] * 100
        active_risk_factors.append({
            "factor": "no_scholarship",
            "label": RISK_FACTORS["no_scholarship"]["label"],
            "weight": RISK_FACTORS["no_scholarship"]["weight"],
            "icon": RISK_FACTORS["no_scholarship"]["icon"]
        })
    else:
        protective_factors.append("Has active scholarship")

    # 7. Declining Platform Engagement (< 5 logins/month)
    if student.get("platform_logins_30d", 0) < 5:
        total_score += RISK_FACTORS["engagement_drop"]["weight"] * 100
        active_risk_factors.append({
            "factor": "engagement_drop",
            "label": RISK_FACTORS["engagement_drop"]["label"],
            "weight": RISK_FACTORS["engagement_drop"]["weight"],
            "icon": RISK_FACTORS["engagement_drop"]["icon"]
        })

    # 8. Missed Deadlines (1+)
    if student.get("deadlines_missed", 0) >= 1:
        total_score += RISK_FACTORS["missed_deadlines"]["weight"] * 100
        active_risk_factors.append({
            "factor": "missed_deadlines",
            "label": RISK_FACTORS["missed_deadlines"]["label"],
            "weight": RISK_FACTORS["missed_deadlines"]["weight"],
            "icon": RISK_FACTORS["missed_deadlines"]["icon"]
        })

    # Cap at 100
    total_score = min(total_score, 100.0)
    risk_category = get_risk_category(total_score)
    
    color_map = {
        "Low": "🟢",
        "Medium": "🟡",
        "High": "🟠",
        "Critical": "🔴"
    }
    
    return {
        "total_score": round(total_score, 2),
        "risk_category": risk_category,
        "active_risk_factors": active_risk_factors,
        "protective_factors": protective_factors,
        "risk_color": color_map.get(risk_category, "🟢")
    }

def generate_intervention_plan(student: Dict, risk_result: Dict) -> List[Dict]:
    """
    Creates targeted intervention recommendations based on active risk factors.
    """
    plan = []
    
    for factor in risk_result["active_risk_factors"]:
        f_name = factor["factor"]
        
        if f_name == "attendance_below_75":
            plan.append({
                "priority": "High",
                "action": "Schedule weekly check-in with academic mentor",
                "responsible": "Academic Advisor",
                "timeline": "Immediate (Within 3 days)",
                "icon": "👨‍🏫"
            })
        elif f_name == "failing_subjects":
            plan.append({
                "priority": "Critical",
                "action": "Assign peer tutor for weak subjects",
                "responsible": "Department HOD",
                "timeline": "Immediate",
                "icon": "📖"
            })
        elif f_name == "family_income_stress" and not student.get("has_scholarship", False):
            plan.append({
                "priority": "High",
                "action": "Refer to scholarship engine for PMSSS/Post-Matric eligibility",
                "responsible": "Scholarship Cell",
                "timeline": "Within 1 week",
                "icon": "🏦"
            })
        elif f_name == "no_scholarship":
            plan.append({
                "priority": "Medium",
                "action": "Notify student about upcoming scholarship windows",
                "responsible": "System Auto-alert",
                "timeline": "Next cycle",
                "icon": "📢"
            })
        elif f_name == "engagement_drop":
            plan.append({
                "priority": "Low",
                "action": "Send engagement nudge email/SMS",
                "responsible": "Automated System",
                "timeline": "Within 24 hours",
                "icon": "📧"
            })
        elif f_name == "missed_deadlines":
            plan.append({
                "priority": "Medium",
                "action": "Assign counselor to help manage time and application windows",
                "responsible": "Counseling Cell",
                "timeline": "Within 2 weeks",
                "icon": "🕒"
            })
            
    # Default plan if no severe risks
    if not plan and risk_result["risk_category"] == "Low":
        plan.append({
            "priority": "Low",
            "action": "Continue regular monitoring and periodic check-ins",
            "responsible": "System",
            "timeline": "Monthly",
            "icon": "✅"
        })
        
    return plan

def get_cohort_analytics(students: List[Dict]) -> Dict:
    """
    Aggregate analytics across a student cohort.
    """
    total = len(students)
    if total == 0:
        return {}

    risk_dist = {"Low": 0, "Medium": 0, "High": 0, "Critical": 0}
    gender_dist = {"male": 0, "female": 0}
    district_dist = {}
    program_dist = {}
    
    total_attendance = 0.0
    total_cgpa = 0.0
    total_scholarships = 0
    total_risk_score = 0.0
    
    at_risk_students = []
    critical_alerts = []
    
    factor_counts = {}

    for s in students:
        risk = calculate_risk_score(s)
        rcat = risk["risk_category"]
        rscore = risk["total_score"]
        
        risk_dist[rcat] += 1
        
        gender = s.get("gender", "male")
        gender_dist[gender] = gender_dist.get(gender, 0) + 1
        
        dist = s.get("district", "Unknown")
        district_dist[dist] = district_dist.get(dist, 0) + 1
        
        prog = s.get("program", "Unknown")
        program_dist[prog] = program_dist.get(prog, 0) + 1
        
        total_attendance += s.get("attendance_percent", 0.0)
        total_cgpa += s.get("cgpa", 0.0)
        if s.get("has_scholarship", False):
            total_scholarships += 1
            
        total_risk_score += rscore
        
        if rscore > 55:
            at_risk_students.append({"student": s, "risk": risk})
        if rscore > 75:
            critical_alerts.append({"student": s, "risk": risk})
            
        for f in risk["active_risk_factors"]:
            flabel = f["label"]
            factor_counts[flabel] = factor_counts.get(flabel, 0) + 1

    top_risk_factors = sorted(factor_counts.items(), key=lambda x: x[1], reverse=True)

    return {
        "total_students": total,
        "risk_distribution": risk_dist,
        "avg_attendance": round(total_attendance / total, 2),
        "avg_cgpa": round(total_cgpa / total, 2),
        "scholarship_rate": round((total_scholarships / total) * 100, 2),
        "gender_distribution": gender_dist,
        "district_distribution": district_dist,
        "program_distribution": program_dist,
        "at_risk_students": sorted(at_risk_students, key=lambda x: x["risk"]["total_score"], reverse=True),
        "critical_alerts": sorted(critical_alerts, key=lambda x: x["risk"]["total_score"], reverse=True),
        "avg_risk_score": round(total_risk_score / total, 2),
        "top_risk_factors": top_risk_factors
    }

def simulate_demo_cohort(n: int = 50) -> List[Dict]:
    """
    Generates realistic demo student data for hackathon demonstration.
    Ensure realistic distributions.
    """
    random.seed(42)
    cohort = []
    
    for i in range(n):
        gender = "female" if random.random() < 0.4 else "male"
        
        if gender == "male":
            first_name = random.choice(FIRST_NAMES_MALE)
        else:
            first_name = random.choice(FIRST_NAMES_FEMALE)
            
        last_name = random.choice(LAST_NAMES)
        name = f"{first_name} {last_name}"
        
        # Distributions for risk
        r = random.random()
        if r < 0.2: # High/Critical
            att = random.uniform(40, 74)
            fails = random.randint(2, 4)
            inc = random.randint(100000, 240000)
            cgpa = random.uniform(4.0, 6.0)
            sch = False
            logins = random.randint(0, 4)
            missed = random.randint(1, 3)
            dist = random.choice(REMOTE_DISTRICTS)
        elif r < 0.5: # Medium
            att = random.uniform(65, 85)
            fails = random.randint(0, 2)
            inc = random.randint(200000, 400000)
            cgpa = random.uniform(6.0, 7.5)
            sch = random.random() < 0.2
            logins = random.randint(4, 10)
            missed = random.randint(0, 1)
            dist = random.choice(DISTRICTS)
        else: # Low
            att = random.uniform(80, 100)
            fails = 0
            inc = random.randint(300000, 1000000)
            cgpa = random.uniform(7.5, 9.8)
            sch = random.random() < 0.4
            logins = random.randint(10, 30)
            missed = 0
            dist = random.choice(DISTRICTS)
            
        student_id = f"STU{i+1:03d}"
        
        student = {
            "id": student_id,
            "name": name,
            "district": dist,
            "institution": random.choice(INSTITUTIONS),
            "program": random.choice(PROGRAMS),
            "year": random.randint(1, 4),
            "gender": gender,
            "category": random.choice(CATEGORIES),
            "family_income": inc,
            "attendance_percent": round(att, 2),
            "cgpa": round(cgpa, 2),
            "failing_subjects": fails,
            "has_scholarship": sch,
            "scholarship_name": "PMSSS" if sch and random.random() < 0.5 else ("Post-Matric" if sch else ""),
            "first_gen_student": random.random() < 0.3,
            "platform_logins_30d": logins,
            "deadlines_missed": missed,
            "contact_email": f"{first_name.lower()}.{last_name.lower()}@example.com",
            "contact_phone": f"+91 {random.randint(600000000, 999999999)}",
            "enrolled_date": (datetime.datetime.now() - datetime.timedelta(days=random.randint(100, 1000))).isoformat()
        }
        cohort.append(student)
        
    return cohort

def get_student_summary(student: Dict) -> str:
    """
    Returns a formatted markdown summary of a student's profile.
    """
    risk = calculate_risk_score(student)
    plan = generate_intervention_plan(student, risk)
    
    summary = f"### Student Profile: {student.get('name', '')} ({student.get('id', '')})\n\n"
    summary += f"**Program:** {student.get('program', '')} (Year {student.get('year', '')}) at {student.get('institution', '')}\n"
    summary += f"**District:** {student.get('district', '')} | **Category:** {student.get('category', '')}\n"
    summary += f"**CGPA:** {student.get('cgpa', '')} | **Attendance:** {student.get('attendance_percent', '')}%\n"
    has_sch = student.get('has_scholarship', False)
    sch_name = student.get('scholarship_name', '')
    summary += f"**Scholarship:** {'Yes (' + sch_name + ')' if has_sch else 'None'}\n\n"
    
    summary += f"### Risk Assessment: {risk['risk_color']} {risk['risk_category']} (Score: {risk['total_score']})\n\n"
    
    if risk["active_risk_factors"]:
        summary += "**Active Risk Factors:**\n"
        for factor in risk["active_risk_factors"]:
            summary += f"- {factor['icon']} {factor['label']}\n"
    else:
        summary += "No significant risk factors identified.\n"
        
    summary += "\n**Protective Factors:**\n"
    if risk["protective_factors"]:
        for factor in risk["protective_factors"]:
            summary += f"- ✅ {factor}\n"
    else:
        summary += "- None identified.\n"
        
    summary += "\n### Recommended Interventions\n"
    for p in plan:
        summary += f"- **{p['priority']} Priority:** {p['action']} (Resp: {p['responsible']}, Timeline: {p['timeline']})\n"
        
    return summary

def get_priority_alerts(students: List[Dict], min_risk: float = 56) -> List[Dict]:
    """
    Returns students above the risk threshold sorted by risk score descending.
    """
    alerts = []
    for s in students:
        risk = calculate_risk_score(s)
        if risk["total_score"] >= min_risk:
            plan = generate_intervention_plan(s, risk)
            alerts.append({
                "student": s,
                "risk_result": risk,
                "intervention_plan": plan
            })
            
    return sorted(alerts, key=lambda x: x["risk_result"]["total_score"], reverse=True)

def export_cohort_report(analytics: Dict) -> str:
    """
    Generates a comprehensive markdown report of cohort analytics.
    """
    if not analytics:
        return "No data available."
        
    report = "# 📊 Cohort Analytics Report\n\n"
    report += "## Overview\n"
    report += f"- **Total Students:** {analytics.get('total_students', 0)}\n"
    report += f"- **Average Risk Score:** {analytics.get('avg_risk_score', 0)}\n"
    report += f"- **Average Attendance:** {analytics.get('avg_attendance', 0)}%\n"
    report += f"- **Average CGPA:** {analytics.get('avg_cgpa', 0)}\n"
    report += f"- **Scholarship Rate:** {analytics.get('scholarship_rate', 0)}%\n\n"
    
    report += "## Risk Distribution\n"
    dist = analytics.get('risk_distribution', {})
    report += f"- 🔴 Critical: {dist.get('Critical', 0)}\n"
    report += f"- 🟠 High: {dist.get('High', 0)}\n"
    report += f"- 🟡 Medium: {dist.get('Medium', 0)}\n"
    report += f"- 🟢 Low: {dist.get('Low', 0)}\n\n"
    
    report += "## Top Risk Factors\n"
    top_factors = analytics.get('top_risk_factors', [])
    for factor, count in top_factors[:5]:
        report += f"- {factor}: {count} students\n"
        
    report += "\n## Priority Interventions Needed\n"
    at_risk_count = len(analytics.get('at_risk_students', []))
    critical_count = len(analytics.get('critical_alerts', []))
    report += f"Action required for {at_risk_count} at-risk students (High/Critical).\n"
    report += f"Urgent attention needed for {critical_count} critical students.\n\n"
    
    report += "### Recommendations for Institution\n"
    report += "1. **Academic Support:** Organize peer tutoring for common failing subjects.\n"
    report += "2. **Counseling:** Reach out to students with critical risk scores immediately.\n"
    report += "3. **Financial Aid:** Promote scholarship awareness campaigns for low-income unscholarshipped students.\n"
    
    return report

def search_students(students: List[Dict], query: str) -> List[Dict]:
    """
    Search by name, ID, district, program, or institution. Case-insensitive.
    """
    query = query.lower()
    results = []
    
    for s in students:
        name = s.get('name', '').lower()
        sid = s.get('id', '').lower()
        district = s.get('district', '').lower()
        program = s.get('program', '').lower()
        institution = s.get('institution', '').lower()
        
        if (query in name or query in sid or query in district or 
            query in program or query in institution):
            results.append(s)
            
    return results
