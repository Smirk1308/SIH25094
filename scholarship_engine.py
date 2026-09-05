import datetime
from typing import Dict, List, Optional, Any

SCHOLARSHIPS = [
    {
        "id": "pmsss",
        "name": "PM Special Scholarship Scheme (PMSSS)",
        "provider": "AICTE / MoE",
        "portal_url": "https://www.aicte-india.org/bureaus/jk",
        "eligibility": {
            "domicile": "J&K",
            "class_12_min_percent": 0,
            "family_income_max": 800000,
            "streams": ["All"],
            "categories": ["All"],
            "gender": "all",
            "disability": False,
            "min_age": 0,
            "max_age": 0,
        },
        "benefits": {
            "tuition_support": "Up to ₹1.25L (Eng) / ₹3L (Medical) / ₹30k (General)",
            "maintenance_allowance": "₹1,00,000/year DBT",
            "other_benefits": "Hostel and Book allowance included in maintenance",
            "duration": "Full course duration",
        },
        "deadlines": {
            "application_open": "May",
            "application_close": "July",
        },
        "documents_required": [
            "Domicile Certificate", "Class 12th Marksheet", "Income Certificate", 
            "Aadhaar Card", "Bank Passbook", "Caste Certificate (if applicable)"
        ],
        "slots": 5000,
        "category": "scholarship",
        "priority_for_jk": True,
    },
    {
        "id": "post_matric_nsp",
        "name": "Post-Matric Scholarship for Minorities (NSP)",
        "provider": "Ministry of Minority Affairs",
        "portal_url": "https://scholarships.gov.in/",
        "eligibility": {
            "domicile": "India",
            "class_12_min_percent": 50,
            "family_income_max": 250000,
            "streams": ["All"],
            "categories": ["Minority"],
            "gender": "all",
            "disability": False,
            "min_age": 0,
            "max_age": 0,
        },
        "benefits": {
            "tuition_support": "Actual fee or up to ₹10,000/year",
            "maintenance_allowance": "₹1200/month (Hosteller), ₹550/month (Day Scholar)",
            "other_benefits": "None",
            "duration": "Duration of the course",
        },
        "deadlines": {
            "application_open": "August",
            "application_close": "October",
        },
        "documents_required": [
            "Previous Year Marksheet", "Income Certificate", "Minority Certificate / Self Declaration", 
            "Aadhaar Card", "Bank Passbook", "Fee Receipt"
        ],
        "slots": 0,
        "category": "scholarship",
        "priority_for_jk": False,
    },
    {
        "id": "samarthan_jk",
        "name": "SAMARTHAN Scheme for Orphans/PwD",
        "provider": "J&K Higher Education Dept",
        "portal_url": "https://jkeducation.gov.in/",
        "eligibility": {
            "domicile": "J&K",
            "class_12_min_percent": 0,
            "family_income_max": 0,
            "streams": ["All"],
            "categories": ["All"],
            "gender": "all",
            "disability": True,
            "min_age": 0,
            "max_age": 0,
        },
        "benefits": {
            "tuition_support": "Full fee waiver",
            "maintenance_allowance": "Monthly stipend",
            "other_benefits": "Free boarding/lodging in state hostels",
            "duration": "Full course duration",
        },
        "deadlines": {
            "application_open": "July",
            "application_close": "September",
        },
        "documents_required": [
            "Domicile Certificate", "Disability Certificate / Orphan Certificate", 
            "Previous Year Marksheet", "Aadhaar Card", "Bank Passbook"
        ],
        "slots": 0,
        "category": "scholarship",
        "priority_for_jk": True,
    },
    {
        "id": "jk_mcm",
        "name": "J&K Merit-cum-Means Scholarship",
        "provider": "Department of Social Welfare, J&K",
        "portal_url": "https://jk.gov.in/jammukashmir/",
        "eligibility": {
            "domicile": "J&K",
            "class_12_min_percent": 60,
            "family_income_max": 250000,
            "streams": ["All"],
            "categories": ["All"],
            "gender": "all",
            "disability": False,
            "min_age": 0,
            "max_age": 0,
        },
        "benefits": {
            "tuition_support": "Up to ₹30,000/year",
            "maintenance_allowance": "₹10,000/year",
            "other_benefits": "None",
            "duration": "Annual renewal",
        },
        "deadlines": {
            "application_open": "September",
            "application_close": "November",
        },
        "documents_required": [
            "Domicile Certificate", "Income Certificate", "Previous Year Marksheet", 
            "Aadhaar Card", "Bank Passbook"
        ],
        "slots": 0,
        "category": "scholarship",
        "priority_for_jk": True,
    },
    {
        "id": "pms_tribal",
        "name": "Post Matric Scholarship for ST Students",
        "provider": "Ministry of Tribal Affairs",
        "portal_url": "https://tribal.nic.in/Scholarships.aspx",
        "eligibility": {
            "domicile": "India",
            "class_12_min_percent": 0,
            "family_income_max": 250000,
            "streams": ["All"],
            "categories": ["ST"],
            "gender": "all",
            "disability": False,
            "min_age": 0,
            "max_age": 0,
        },
        "benefits": {
            "tuition_support": "Full tuition fee reimbursement",
            "maintenance_allowance": "₹1200/month (Hosteller)",
            "other_benefits": "Study tour charges, thesis typing charges",
            "duration": "Full course duration",
        },
        "deadlines": {
            "application_open": "August",
            "application_close": "October",
        },
        "documents_required": [
            "ST Certificate", "Income Certificate", "Previous Year Marksheet", 
            "Aadhaar Card", "Bank Passbook", "Fee Receipt"
        ],
        "slots": 0,
        "category": "scholarship",
        "priority_for_jk": True,
    },
    {
        "id": "inspire",
        "name": "INSPIRE Scholarship for Higher Education (SHE)",
        "provider": "Department of Science & Technology (DST)",
        "portal_url": "https://online-inspire.gov.in/",
        "eligibility": {
            "domicile": "India",
            "class_12_min_percent": 90,
            "family_income_max": 0,
            "streams": ["PCM", "PCB"],
            "categories": ["All"],
            "gender": "all",
            "disability": False,
            "min_age": 17,
            "max_age": 22,
        },
        "benefits": {
            "tuition_support": "₹60,000/year in cash",
            "maintenance_allowance": "None",
            "other_benefits": "Summertime attachment fee of ₹20,000/year",
            "duration": "Maximum 5 years (B.Sc/M.Sc)",
        },
        "deadlines": {
            "application_open": "September",
            "application_close": "December",
        },
        "documents_required": [
            "Class 12th Marksheet", "Endorsement Certificate from Principal/Director", 
            "Aadhaar Card", "Bank Passbook"
        ],
        "slots": 10000,
        "category": "scholarship",
        "priority_for_jk": False,
    },
    {
        "id": "csss",
        "name": "Central Sector Scheme of Scholarships (CSSS)",
        "provider": "MoE / MHRD",
        "portal_url": "https://scholarships.gov.in/",
        "eligibility": {
            "domicile": "India",
            "class_12_min_percent": 80,
            "family_income_max": 450000,
            "streams": ["All"],
            "categories": ["All"],
            "gender": "all",
            "disability": False,
            "min_age": 18,
            "max_age": 25,
        },
        "benefits": {
            "tuition_support": "None",
            "maintenance_allowance": "₹12,000/year (Graduation), ₹20,000/year (PG)",
            "other_benefits": "None",
            "duration": "Up to 5 years",
        },
        "deadlines": {
            "application_open": "August",
            "application_close": "October",
        },
        "documents_required": [
            "Class 12th Marksheet", "Income Certificate", "Aadhaar Card", 
            "Bank Passbook", "College ID"
        ],
        "slots": 82000,
        "category": "scholarship",
        "priority_for_jk": False,
    },
    {
        "id": "minority_mcm",
        "name": "Merit-cum-Means Scholarship for Professional and Technical Courses CS",
        "provider": "Ministry of Minority Affairs",
        "portal_url": "https://scholarships.gov.in/",
        "eligibility": {
            "domicile": "India",
            "class_12_min_percent": 50,
            "family_income_max": 250000,
            "streams": ["All"],
            "categories": ["Minority"],
            "gender": "all",
            "disability": False,
            "min_age": 0,
            "max_age": 0,
        },
        "benefits": {
            "tuition_support": "Up to ₹20,000/year",
            "maintenance_allowance": "₹1,000/month (Hosteller), ₹500/month (Day Scholar)",
            "other_benefits": "None",
            "duration": "Course duration",
        },
        "deadlines": {
            "application_open": "August",
            "application_close": "October",
        },
        "documents_required": [
            "Previous Year Marksheet", "Income Certificate", "Minority Certificate", 
            "Aadhaar Card", "Bank Passbook", "Fee Receipt"
        ],
        "slots": 60000,
        "category": "scholarship",
        "priority_for_jk": False,
    },
    {
        "id": "aicte_pragati",
        "name": "AICTE Pragati Scholarship for Girls",
        "provider": "AICTE",
        "portal_url": "https://www.aicte-india.org/schemes/students-development-schemes/Pragati",
        "eligibility": {
            "domicile": "India",
            "class_12_min_percent": 0,
            "family_income_max": 800000,
            "streams": ["All"],
            "categories": ["All"],
            "gender": "female",
            "disability": False,
            "min_age": 0,
            "max_age": 0,
        },
        "benefits": {
            "tuition_support": "None",
            "maintenance_allowance": "₹50,000/year",
            "other_benefits": "None",
            "duration": "Course duration",
        },
        "deadlines": {
            "application_open": "September",
            "application_close": "November",
        },
        "documents_required": [
            "Previous Year Marksheet", "Income Certificate", "Aadhaar Card", 
            "Bank Passbook", "Admission Letter (Technical Degree/Diploma)"
        ],
        "slots": 5000,
        "category": "scholarship",
        "priority_for_jk": False,
    },
    {
        "id": "aicte_saksham",
        "name": "AICTE Saksham Scholarship for Specially-abled Students",
        "provider": "AICTE",
        "portal_url": "https://www.aicte-india.org/schemes/students-development-schemes/Saksham",
        "eligibility": {
            "domicile": "India",
            "class_12_min_percent": 0,
            "family_income_max": 800000,
            "streams": ["All"],
            "categories": ["All"],
            "gender": "all",
            "disability": True,
            "min_age": 0,
            "max_age": 0,
        },
        "benefits": {
            "tuition_support": "None",
            "maintenance_allowance": "₹50,000/year",
            "other_benefits": "None",
            "duration": "Course duration",
        },
        "deadlines": {
            "application_open": "September",
            "application_close": "November",
        },
        "documents_required": [
            "Disability Certificate (min 40%)", "Previous Year Marksheet", 
            "Income Certificate", "Aadhaar Card", "Bank Passbook"
        ],
        "slots": 0,
        "category": "scholarship",
        "priority_for_jk": False,
    },
    {
        "id": "manf",
        "name": "Maulana Azad National Fellowship (MANF)",
        "provider": "UGC / Ministry of Minority Affairs",
        "portal_url": "https://ugc.ac.in/ugc_schemes/",
        "eligibility": {
            "domicile": "India",
            "class_12_min_percent": 55,
            "family_income_max": 600000,
            "streams": ["All"],
            "categories": ["Minority"],
            "gender": "all",
            "disability": False,
            "min_age": 0,
            "max_age": 0,
        },
        "benefits": {
            "tuition_support": "None",
            "maintenance_allowance": "₹31,000/month (JRF) / ₹35,000/month (SRF)",
            "other_benefits": "Contingency Grant up to ₹25,000/year",
            "duration": "5 years (MPhil/PhD)",
        },
        "deadlines": {
            "application_open": "June",
            "application_close": "July",
        },
        "documents_required": [
            "Minority Certificate", "PG Marksheet", "Registration/Admission in PhD/MPhil", 
            "Income Certificate"
        ],
        "slots": 1000,
        "category": "fellowship",
        "priority_for_jk": False,
    },
    {
        "id": "gate_scholarship",
        "name": "GATE Scholarship",
        "provider": "AICTE",
        "portal_url": "https://pgscholarship.aicte-india.org/",
        "eligibility": {
            "domicile": "India",
            "class_12_min_percent": 0,
            "family_income_max": 0,
            "streams": ["All"],
            "categories": ["All"],
            "gender": "all",
            "disability": False,
            "min_age": 0,
            "max_age": 0,
        },
        "benefits": {
            "tuition_support": "None",
            "maintenance_allowance": "₹12,400/month",
            "other_benefits": "None",
            "duration": "24 months or course duration",
        },
        "deadlines": {
            "application_open": "August",
            "application_close": "October",
        },
        "documents_required": [
            "Valid GATE Scorecard", "Aadhaar Card", "Bank Passbook", 
            "Admission Proof in M.E/M.Tech"
        ],
        "slots": 0,
        "category": "fellowship",
        "priority_for_jk": False,
    },
    {
        "id": "ugc_net_jrf",
        "name": "UGC NET Junior Research Fellowship (JRF)",
        "provider": "UGC",
        "portal_url": "https://ugcnet.nta.nic.in/",
        "eligibility": {
            "domicile": "India",
            "class_12_min_percent": 0,
            "family_income_max": 0,
            "streams": ["All"],
            "categories": ["All"],
            "gender": "all",
            "disability": False,
            "min_age": 0,
            "max_age": 30,
        },
        "benefits": {
            "tuition_support": "None",
            "maintenance_allowance": "₹37,000/month",
            "other_benefits": "HRA as per rules, Contingency grant",
            "duration": "5 years",
        },
        "deadlines": {
            "application_open": "March",
            "application_close": "May",
        },
        "documents_required": [
            "UGC NET Award Letter", "Joining Report", "PG Marksheet", 
            "Aadhaar Card", "Bank Passbook"
        ],
        "slots": 0,
        "category": "fellowship",
        "priority_for_jk": False,
    },
    {
        "id": "vidyalakshmi_loan",
        "name": "Vidyalakshmi Education Loan",
        "provider": "Ministry of Finance / NSDL",
        "portal_url": "https://www.vidyalakshmi.co.in/",
        "eligibility": {
            "domicile": "India",
            "class_12_min_percent": 0,
            "family_income_max": 0,
            "streams": ["All"],
            "categories": ["All"],
            "gender": "all",
            "disability": False,
            "min_age": 0,
            "max_age": 0,
        },
        "benefits": {
            "tuition_support": "Up to full course fee as loan",
            "maintenance_allowance": "Living expenses included in loan",
            "other_benefits": "Interest subsidy for EWS (CSIS scheme)",
            "duration": "Repayment starts 1 year after course completion",
        },
        "deadlines": {
            "application_open": "January",
            "application_close": "December",
        },
        "documents_required": [
            "Admission Proof", "Fee Structure", "Aadhaar Card", 
            "PAN Card", "Income Proof of Co-borrower"
        ],
        "slots": 0,
        "category": "loan",
        "priority_for_jk": False,
    },
    {
        "id": "nmdfc_loan",
        "name": "NMDFC Education Loan Scheme",
        "provider": "National Minorities Development & Finance Corporation",
        "portal_url": "https://www.nmdfc.org/",
        "eligibility": {
            "domicile": "India",
            "class_12_min_percent": 0,
            "family_income_max": 120000,
            "streams": ["All"],
            "categories": ["Minority"],
            "gender": "all",
            "disability": False,
            "min_age": 16,
            "max_age": 32,
        },
        "benefits": {
            "tuition_support": "Up to ₹20 Lakhs (Domestic) / ₹30 Lakhs (Abroad)",
            "maintenance_allowance": "None",
            "other_benefits": "Concessional interest rate of 3% p.a.",
            "duration": "Max 5 years for repayment",
        },
        "deadlines": {
            "application_open": "April",
            "application_close": "October",
        },
        "documents_required": [
            "Minority Certificate", "Income Certificate", "Admission Proof", 
            "Fee Structure", "Aadhaar Card", "Guarantor Details"
        ],
        "slots": 0,
        "category": "loan",
        "priority_for_jk": False,
    }
]

def check_eligibility(profile: Dict) -> List[Dict]:
    """
    Checks eligibility against the scholarship database.
    Profile keys expected: stream, income, category, gender, percentage, age, disability, domicile
    """
    matches = []
    
    for scholarship in SCHOLARSHIPS:
        eligibility = scholarship["eligibility"]
        score = 100
        reasons = []
        missing = []
        
        # Domicile Check
        p_domicile = profile.get("domicile", "").upper()
        s_domicile = eligibility.get("domicile", "").upper()
        if s_domicile == "J&K" and p_domicile != "J&K":
            if not p_domicile: missing.append("domicile")
            else: score -= 50
        elif s_domicile == "J&K" and p_domicile == "J&K":
            reasons.append("Matches J&K domicile requirement.")
            
        # Income Check
        p_income = profile.get("income")
        s_income = eligibility.get("family_income_max", 0)
        if s_income > 0:
            if p_income is None: missing.append("income")
            elif p_income > s_income: score -= 40
            else: reasons.append(f"Family income is within the ₹{s_income} limit.")
            
        # Class 12 Percent
        p_percent = profile.get("percentage")
        s_percent = eligibility.get("class_12_min_percent", 0)
        if s_percent > 0:
            if p_percent is None: missing.append("percentage")
            elif p_percent < s_percent: score -= 30
            else: reasons.append(f"Meets the {s_percent}% academic criteria.")
            
        # Category
        p_category = profile.get("category", "All")
        s_categories = eligibility.get("categories", ["All"])
        if "All" not in s_categories:
            if not p_category: missing.append("category")
            elif p_category not in s_categories and "Minority" not in s_categories:
                score -= 30
            elif "Minority" in s_categories and profile.get("minority_religion") is None and p_category != "Minority":
                missing.append("minority_religion")
                score -= 30
            else:
                reasons.append("Matches reserved category requirement.")
                
        # Gender
        p_gender = profile.get("gender", "").lower()
        s_gender = eligibility.get("gender", "all").lower()
        if s_gender != "all":
            if not p_gender: missing.append("gender")
            elif p_gender != s_gender: score -= 50
            else: reasons.append(f"Specifically supports {s_gender} students.")
            
        # Disability
        p_disability = profile.get("disability")
        s_disability = eligibility.get("disability", False)
        if s_disability:
            if p_disability is None: missing.append("disability")
            elif not p_disability: score -= 50
            else: reasons.append("Matches PwD specific criteria.")
            
        # Age
        p_age = profile.get("age")
        s_min_age = eligibility.get("min_age", 0)
        s_max_age = eligibility.get("max_age", 0)
        if s_min_age > 0 or s_max_age > 0:
            if p_age is None: missing.append("age")
            else:
                if (s_min_age > 0 and p_age < s_min_age) or (s_max_age > 0 and p_age > s_max_age):
                    score -= 20
                else: reasons.append("Meets age requirements.")
                
        if score < 0:
            score = 0
            
        if score >= 40:
            match_data = scholarship.copy()
            match_data["match_score"] = score
            match_data["match_reasons"] = reasons
            match_data["missing_info"] = missing
            matches.append(match_data)
            
    # Sort by match_score descending, then prioritize J&K
    matches.sort(key=lambda x: (x["match_score"], x.get("priority_for_jk", False)), reverse=True)
    return matches

def get_scholarship_details(scholarship_id: str) -> Optional[Dict]:
    for s in SCHOLARSHIPS:
        if s["id"] == scholarship_id:
            return s
    return None

def get_deadline_calendar() -> List[Dict]:
    month_map = {
        "January": 1, "February": 2, "March": 3, "April": 4,
        "May": 5, "June": 6, "July": 7, "August": 8,
        "September": 9, "October": 10, "November": 11, "December": 12
    }
    current_month_name = datetime.datetime.now().strftime("%B")
    current_month_idx = month_map.get(current_month_name, 1)
    
    calendar = []
    for s in SCHOLARSHIPS:
        close_month = s["deadlines"]["application_close"]
        close_idx = month_map.get(close_month, 12)
        
        if close_idx < current_month_idx:
            status = "closed"
        elif close_idx == current_month_idx:
            status = "open"
        else:
            status = "upcoming"
            
        calendar.append({
            "name": s["name"],
            "deadline_month": close_month,
            "status": status,
            "portal_url": s["portal_url"]
        })
        
    calendar.sort(key=lambda x: month_map.get(x["deadline_month"], 12))
    return calendar

def render_eligibility_report(matches: List[Dict]) -> str:
    if not matches:
        return "### No matching scholarships found.\\nPlease update your profile details to see more results."
        
    report = "## Your Scholarship Eligibility Report\\n\\n"
    
    groups = {"Strong Match": [], "Likely Eligible": [], "Check Requirements": []}
    for m in matches:
        score = m["match_score"]
        if score > 80:
            groups["Strong Match"].append(m)
        elif score >= 50:
            groups["Likely Eligible"].append(m)
        else:
            groups["Check Requirements"].append(m)
            
    for group_name, items in groups.items():
        if items:
            report += f"### {group_name}\\n"
            for item in items:
                report += f"- **[{item['name']}]({item['portal_url']})** - {item['provider']}\\n"
                if item['match_reasons']:
                    report += f"  - *Why:* {', '.join(item['match_reasons'])}\\n"
                if item['missing_info']:
                    report += f"  - *Missing Info Needed:* {', '.join(item['missing_info'])}\\n"
            report += "\\n"
            
    return report

def get_documents_checklist(scholarship_ids: List[str]) -> List[str]:
    all_docs = set()
    for s_id in scholarship_ids:
        details = get_scholarship_details(s_id)
        if details:
            for doc in details.get("documents_required", []):
                all_docs.add(doc)
    return sorted(list(all_docs))

def get_all_scholarship_categories() -> List[str]:
    categories = set(s.get("category", "") for s in SCHOLARSHIPS if s.get("category"))
    return sorted(list(categories))

def render_scholarship_card(scholarship: Dict, match_info: Dict = None) -> str:
    card = f"### {scholarship['name']}\\n"
    card += f"**Provider:** {scholarship['provider']} | **Type:** {scholarship['category'].title()}\\n\\n"
    
    if match_info:
        score = match_info.get("match_score", 0)
        card += f"**Match Score:** {score}%\\n"
        reasons = match_info.get("match_reasons", [])
        if reasons:
            card += f"> {'; '.join(reasons)}\\n\\n"
            
    card += f"**Benefits:** {scholarship['benefits']['tuition_support']}, {scholarship['benefits']['maintenance_allowance']}\\n"
    card += f"**Deadline:** {scholarship['deadlines']['application_close']}\\n\\n"
    card += f"[Apply Here]({scholarship['portal_url']})\\n"
    card += "---"
    return card

def search_scholarships(query: str) -> List[Dict]:
    q = query.lower()
    results = []
    for s in SCHOLARSHIPS:
        if q in s["name"].lower() or q in s["provider"].lower():
            results.append(s)
    return results
