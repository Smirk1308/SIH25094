import re
from typing import List, Dict, Optional, Any

# Job Data Structure
JOBS: List[Dict[str, Any]] = [
    {
        "id": "jkssb_junior_assistant",
        "title": "Junior Assistant",
        "department": "Various Government Departments",
        "board": "JKSSB",
        "qualification": "Graduate",
        "age_range": "18-40",
        "salary_range": "Level 4 (25500-81100)",
        "vacancies_recent": 1889,
        "exam_pattern": {
            "stages": ["Type Test", "CBT (Computer Based Test)"],
            "format": "Objective Type",
            "negative_marking": True
        },
        "key_subjects": ["General English", "General Awareness", "Numerical & Reasoning Ability", "Basic Computer Concepts"],
        "portal_url": "https://jkssb.nic.in",
        "category": "government",
        "difficulty_level": "moderate",
        "preparation_months": 4,
        "streams_eligible": ["Any"]
    },
    {
        "id": "jkssb_sub_inspector",
        "title": "Sub-Inspector (Police)",
        "department": "Home Department (J&K Police)",
        "board": "JKSSB",
        "qualification": "Graduate",
        "age_range": "18-28",
        "salary_range": "Level 6C (35700-113100)",
        "vacancies_recent": 1200,
        "exam_pattern": {
            "stages": ["CBT", "PST (Physical Standard Test)", "PET (Physical Endurance Test)"],
            "format": "Objective Type",
            "negative_marking": True
        },
        "key_subjects": ["Current Affairs", "English", "General Knowledge", "Reasoning", "Basic Math"],
        "portal_url": "https://jkssb.nic.in",
        "category": "government",
        "difficulty_level": "hard",
        "preparation_months": 6,
        "streams_eligible": ["Any"]
    },
    {
        "id": "jkssb_accounts_assistant",
        "title": "Accounts Assistant",
        "department": "Finance Department",
        "board": "JKSSB",
        "qualification": "Graduate",
        "age_range": "18-40",
        "salary_range": "Level 5 (29200-92300)",
        "vacancies_recent": 972,
        "exam_pattern": {
            "stages": ["CBT"],
            "format": "Objective Type",
            "negative_marking": True
        },
        "key_subjects": ["General Knowledge with special reference to J&K", "Accountancy & Book Keeping", "General English", "Statistics", "Mathematics", "General Economics", "General Science", "Knowledge of Computers"],
        "portal_url": "https://jkssb.nic.in",
        "category": "government",
        "difficulty_level": "hard",
        "preparation_months": 6,
        "streams_eligible": ["Commerce", "Any"]
    },
    {
        "id": "jkssb_patwari",
        "title": "Patwari",
        "department": "Revenue Department",
        "board": "JKSSB",
        "qualification": "Graduate",
        "age_range": "18-40",
        "salary_range": "Level 4 (25500-81100)",
        "vacancies_recent": 400,
        "exam_pattern": {
            "stages": ["Working knowledge of Urdu (Descriptive)", "CBT"],
            "format": "Subjective + Objective",
            "negative_marking": True
        },
        "key_subjects": ["Urdu Language", "General Awareness", "Reasoning", "Basic Mathematics", "Computer Fundamentals"],
        "portal_url": "https://jkssb.nic.in",
        "category": "government",
        "difficulty_level": "moderate",
        "preparation_months": 5,
        "streams_eligible": ["Any"]
    },
    {
        "id": "jkssb_forest_guard",
        "title": "Forest Guard",
        "department": "Forest, Ecology and Environment Department",
        "board": "JKSSB",
        "qualification": "10+2",
        "age_range": "18-40",
        "salary_range": "Level 2 (19900-63200)",
        "vacancies_recent": 300,
        "exam_pattern": {
            "stages": ["Physical Test", "Written Test"],
            "format": "Objective Type",
            "negative_marking": True
        },
        "key_subjects": ["Basic Science", "General Knowledge", "Basic Mathematics"],
        "portal_url": "https://jkssb.nic.in",
        "category": "government",
        "difficulty_level": "easy",
        "preparation_months": 3,
        "streams_eligible": ["Any"]
    },
    {
        "id": "jkssb_lab_assistant",
        "title": "Lab Assistant",
        "department": "Various",
        "board": "JKSSB",
        "qualification": "10+2 with Science",
        "age_range": "18-40",
        "salary_range": "Level 2 (19900-63200)",
        "vacancies_recent": 150,
        "exam_pattern": {
            "stages": ["CBT"],
            "format": "Objective Type",
            "negative_marking": True
        },
        "key_subjects": ["Physics", "Chemistry", "Biology", "Basic Computer"],
        "portal_url": "https://jkssb.nic.in",
        "category": "government",
        "difficulty_level": "moderate",
        "preparation_months": 4,
        "streams_eligible": ["PCB", "PCM"]
    },
    {
        "id": "jkssb_junior_steno",
        "title": "Junior Stenographer",
        "department": "General Administration Department",
        "board": "JKSSB",
        "qualification": "Graduate",
        "age_range": "18-40",
        "salary_range": "Level 6B (35600-112800)",
        "vacancies_recent": 250,
        "exam_pattern": {
            "stages": ["Shorthand Test", "Type Test", "CBT"],
            "format": "Skill Test + Objective",
            "negative_marking": True
        },
        "key_subjects": ["English", "General Knowledge", "Computer Knowledge"],
        "portal_url": "https://jkssb.nic.in",
        "category": "government",
        "difficulty_level": "moderate",
        "preparation_months": 6,
        "streams_eligible": ["Any"]
    },
    {
        "id": "jkssb_pharmacist",
        "title": "Pharmacist",
        "department": "Health & Medical Education",
        "board": "JKSSB",
        "qualification": "B.Pharm/D.Pharm",
        "age_range": "18-40",
        "salary_range": "Level 4 (25500-81100)",
        "vacancies_recent": 120,
        "exam_pattern": {
            "stages": ["CBT"],
            "format": "Objective Type",
            "negative_marking": True
        },
        "key_subjects": ["Pharmacy core subjects", "General Knowledge", "Science"],
        "portal_url": "https://jkssb.nic.in",
        "category": "government",
        "difficulty_level": "moderate",
        "preparation_months": 4,
        "streams_eligible": ["Medical"]
    },
    {
        "id": "jkpsc_kas",
        "title": "KAS (J&K Administrative Service)",
        "department": "General Administration Department",
        "board": "JKPSC",
        "qualification": "Graduate",
        "age_range": "21-32",
        "salary_range": "Level 8 (47600-151100)",
        "vacancies_recent": 250,
        "exam_pattern": {
            "stages": ["Prelims (Objective)", "Mains (Descriptive)", "Interview"],
            "format": "Subjective + Objective",
            "negative_marking": True
        },
        "key_subjects": ["General Studies", "CSAT", "Optional Subject (Mains)"],
        "portal_url": "https://jkpsc.nic.in",
        "category": "government",
        "difficulty_level": "very_hard",
        "preparation_months": 12,
        "streams_eligible": ["Any"]
    },
    {
        "id": "jkpsc_medical_officer",
        "title": "Medical Officer",
        "department": "Health & Medical Education",
        "board": "JKPSC",
        "qualification": "MBBS",
        "age_range": "18-40",
        "salary_range": "Level 9 (52700-166700)",
        "vacancies_recent": 900,
        "exam_pattern": {
            "stages": ["Written Test (Objective)"],
            "format": "Objective Type",
            "negative_marking": True
        },
        "key_subjects": ["MBBS Curriculum Topics"],
        "portal_url": "https://jkpsc.nic.in",
        "category": "government",
        "difficulty_level": "hard",
        "preparation_months": 6,
        "streams_eligible": ["Medical"]
    },
    {
        "id": "jkpsc_ae",
        "title": "Assistant Engineer (Civil/Elec)",
        "department": "Public Works Department",
        "board": "JKPSC",
        "qualification": "B.Tech/BE",
        "age_range": "18-40",
        "salary_range": "Level 8A (50700-160600)",
        "vacancies_recent": 150,
        "exam_pattern": {
            "stages": ["Written Test (Objective)", "Interview"],
            "format": "Objective Type",
            "negative_marking": True
        },
        "key_subjects": ["Core Engineering Subjects", "General Knowledge"],
        "portal_url": "https://jkpsc.nic.in",
        "category": "government",
        "difficulty_level": "hard",
        "preparation_months": 6,
        "streams_eligible": ["Engineering"]
    },
    {
        "id": "jkpsc_lecturer",
        "title": "Assistant Professor / Lecturer",
        "department": "Higher Education Department",
        "board": "JKPSC",
        "qualification": "PG + NET/SET or PhD",
        "age_range": "18-40",
        "salary_range": "Level 10 (57700-182400)",
        "vacancies_recent": 400,
        "exam_pattern": {
            "stages": ["Written Test", "Interview"],
            "format": "Objective Type",
            "negative_marking": True
        },
        "key_subjects": ["Subject Specific Core Topics"],
        "portal_url": "https://jkpsc.nic.in",
        "category": "government",
        "difficulty_level": "hard",
        "preparation_months": 6,
        "streams_eligible": ["Any"]
    },
    {
        "id": "jkpsc_vas",
        "title": "Veterinary Assistant Surgeon",
        "department": "Animal Husbandry Department",
        "board": "JKPSC",
        "qualification": "BVSc",
        "age_range": "18-40",
        "salary_range": "Level 9 (52700-166700)",
        "vacancies_recent": 100,
        "exam_pattern": {
            "stages": ["Written Test"],
            "format": "Objective Type",
            "negative_marking": True
        },
        "key_subjects": ["Veterinary Sciences Core"],
        "portal_url": "https://jkpsc.nic.in",
        "category": "government",
        "difficulty_level": "moderate",
        "preparation_months": 6,
        "streams_eligible": ["Medical"]
    },
    {
        "id": "jkbank_po",
        "title": "Probationary Officer",
        "department": "J&K Bank",
        "board": "JK Bank",
        "qualification": "Graduate",
        "age_range": "20-32",
        "salary_range": "JMG Scale I (36000-63840)",
        "vacancies_recent": 250,
        "exam_pattern": {
            "stages": ["Prelims (Objective)", "Mains (Objective+Descriptive)", "Interview"],
            "format": "Objective Type",
            "negative_marking": True
        },
        "key_subjects": ["English Language", "Quantitative Aptitude", "Reasoning Ability", "General/Financial Awareness"],
        "portal_url": "https://www.jkbank.com",
        "category": "banking",
        "difficulty_level": "hard",
        "preparation_months": 6,
        "streams_eligible": ["Any"]
    },
    {
        "id": "jkbank_ba",
        "title": "Banking Associate",
        "department": "J&K Bank",
        "board": "JK Bank",
        "qualification": "Graduate",
        "age_range": "20-30",
        "salary_range": "Clerical Cadre (17900-47920)",
        "vacancies_recent": 1500,
        "exam_pattern": {
            "stages": ["Single Online Exam (Objective)"],
            "format": "Objective Type",
            "negative_marking": True
        },
        "key_subjects": ["English Language", "Quantitative Aptitude", "Reasoning Ability"],
        "portal_url": "https://www.jkbank.com",
        "category": "banking",
        "difficulty_level": "moderate",
        "preparation_months": 4,
        "streams_eligible": ["Any"]
    },
    {
        "id": "jkbank_it",
        "title": "IT Officer",
        "department": "J&K Bank",
        "board": "JK Bank",
        "qualification": "B.Tech CS/IT or MCA",
        "age_range": "20-32",
        "salary_range": "JMG Scale I (36000-63840)",
        "vacancies_recent": 50,
        "exam_pattern": {
            "stages": ["Written Test", "Interview"],
            "format": "Objective Type",
            "negative_marking": True
        },
        "key_subjects": ["Professional Knowledge (IT)", "Reasoning", "English Language", "General Awareness"],
        "portal_url": "https://www.jkbank.com",
        "category": "banking",
        "difficulty_level": "hard",
        "preparation_months": 5,
        "streams_eligible": ["Engineering"]
    },
    {
        "id": "ssc_cgl",
        "title": "SSC CGL (Various Ministries)",
        "department": "Central Government",
        "board": "Central",
        "qualification": "Graduate",
        "age_range": "18-32",
        "salary_range": "Level 4 to 8 (25500-151100)",
        "vacancies_recent": 7500,
        "exam_pattern": {
            "stages": ["Tier I", "Tier II", "Skill Test (for some)"],
            "format": "Objective Type",
            "negative_marking": True
        },
        "key_subjects": ["Quantitative Aptitude", "General Intelligence & Reasoning", "English Comprehension", "General Awareness"],
        "portal_url": "https://ssc.nic.in",
        "category": "central",
        "difficulty_level": "hard",
        "preparation_months": 8,
        "streams_eligible": ["Any"]
    },
    {
        "id": "upsc_cse",
        "title": "UPSC CSE (IAS/IPS/IFS)",
        "department": "Central Government",
        "board": "Central",
        "qualification": "Graduate",
        "age_range": "21-32",
        "salary_range": "Level 10 (56100-177500)",
        "vacancies_recent": 1100,
        "exam_pattern": {
            "stages": ["Prelims", "Mains", "Interview"],
            "format": "Subjective + Objective",
            "negative_marking": True
        },
        "key_subjects": ["History", "Geography", "Polity", "Economy", "Science & Tech", "Current Affairs", "Optional"],
        "portal_url": "https://upsc.gov.in",
        "category": "central",
        "difficulty_level": "very_hard",
        "preparation_months": 12,
        "streams_eligible": ["Any"]
    },
    {
        "id": "rrb_ntpc",
        "title": "Railway NTPC",
        "department": "Indian Railways",
        "board": "Central",
        "qualification": "12th/Graduate",
        "age_range": "18-33",
        "salary_range": "Level 2 to 6 (19900-112400)",
        "vacancies_recent": 35000,
        "exam_pattern": {
            "stages": ["CBT 1", "CBT 2", "Skill Test", "Document Verification"],
            "format": "Objective Type",
            "negative_marking": True
        },
        "key_subjects": ["Mathematics", "General Intelligence & Reasoning", "General Awareness"],
        "portal_url": "https://indianrailways.gov.in",
        "category": "central",
        "difficulty_level": "hard",
        "preparation_months": 6,
        "streams_eligible": ["Any"]
    },
    {
        "id": "indian_army_agnipath",
        "title": "Agniveer",
        "department": "Indian Army",
        "board": "Central",
        "qualification": "10th/12th pass",
        "age_range": "17.5-21",
        "salary_range": "Custom Package (30000-40000/month)",
        "vacancies_recent": 40000,
        "exam_pattern": {
            "stages": ["Online CEE", "Physical Fitness Test", "Medical Test"],
            "format": "Objective Type",
            "negative_marking": True
        },
        "key_subjects": ["General Knowledge", "General Science", "Maths", "Logical Reasoning"],
        "portal_url": "https://joinindianarmy.nic.in",
        "category": "defence",
        "difficulty_level": "moderate",
        "preparation_months": 4,
        "streams_eligible": ["Any"]
    },
    {
        "id": "ssc_chsl",
        "title": "SSC CHSL",
        "department": "Central Government",
        "board": "Central",
        "qualification": "12th Pass",
        "age_range": "18-27",
        "salary_range": "Level 2 to 4 (19900-81100)",
        "vacancies_recent": 4500,
        "exam_pattern": {
            "stages": ["Tier I", "Tier II", "Skill Test"],
            "format": "Objective Type",
            "negative_marking": True
        },
        "key_subjects": ["English Language", "General Intelligence", "Quantitative Aptitude", "General Awareness"],
        "portal_url": "https://ssc.nic.in",
        "category": "central",
        "difficulty_level": "moderate",
        "preparation_months": 6,
        "streams_eligible": ["Any"]
    },
    {
        "id": "capf_ac",
        "title": "CAPF Assistant Commandant",
        "department": "BSF/CRPF/ITBP",
        "board": "Central",
        "qualification": "Graduate",
        "age_range": "20-25",
        "salary_range": "Level 10 (56100-177500)",
        "vacancies_recent": 322,
        "exam_pattern": {
            "stages": ["Written Test", "Physical Standard/Efficiency Test", "Interview"],
            "format": "Objective+Descriptive",
            "negative_marking": True
        },
        "key_subjects": ["General Ability & Intelligence", "General Studies, Essay & Comprehension"],
        "portal_url": "https://upsc.gov.in",
        "category": "defence",
        "difficulty_level": "hard",
        "preparation_months": 8,
        "streams_eligible": ["Any"]
    },
    {
        "id": "private_sde",
        "title": "Software Developer",
        "department": "IT Services (TCS/Infosys/Wipro)",
        "board": "Private",
        "qualification": "B.Tech/MCA",
        "age_range": "21-30",
        "salary_range": "3.5LPA - 8LPA",
        "vacancies_recent": 1000,
        "exam_pattern": {
            "stages": ["Online Assessment", "Technical Interview", "HR Interview"],
            "format": "Aptitude + Coding",
            "negative_marking": False
        },
        "key_subjects": ["Aptitude", "Data Structures", "Algorithms", "Programming (Java/Python/C++)"],
        "portal_url": "Various company portals",
        "category": "private",
        "difficulty_level": "moderate",
        "preparation_months": 4,
        "streams_eligible": ["Engineering"]
    },
    {
        "id": "private_data_analyst",
        "title": "Data Analyst",
        "department": "IT & Consulting",
        "board": "Private",
        "qualification": "Graduate",
        "age_range": "21-35",
        "salary_range": "4LPA - 10LPA",
        "vacancies_recent": 500,
        "exam_pattern": {
            "stages": ["Technical Assignment", "Interviews"],
            "format": "Practical",
            "negative_marking": False
        },
        "key_subjects": ["SQL", "Python/R", "Excel", "Data Visualization (Tableau/PowerBI)"],
        "portal_url": "LinkedIn/Naukri",
        "category": "private",
        "difficulty_level": "moderate",
        "preparation_months": 6,
        "streams_eligible": ["Engineering", "Commerce", "Any"]
    },
    {
        "id": "private_nursing",
        "title": "Healthcare / Staff Nurse",
        "department": "Private Hospitals",
        "board": "Private",
        "qualification": "BSc Nursing / GNM",
        "age_range": "21-40",
        "salary_range": "15,000 - 40,000 / month",
        "vacancies_recent": 200,
        "exam_pattern": {
            "stages": ["Interview", "Skill Assessment"],
            "format": "Practical",
            "negative_marking": False
        },
        "key_subjects": ["Nursing Fundamentals", "Anatomy", "Medical-Surgical Nursing"],
        "portal_url": "Hospital specific portals",
        "category": "private",
        "difficulty_level": "moderate",
        "preparation_months": 2,
        "streams_eligible": ["Medical"]
    },
    {
        "id": "private_teacher",
        "title": "School Teacher",
        "department": "Private Schools",
        "board": "Private",
        "qualification": "B.Ed + CTET/TET preferred",
        "age_range": "21-45",
        "salary_range": "15,000 - 50,000 / month",
        "vacancies_recent": 800,
        "exam_pattern": {
            "stages": ["Demo Class", "Interview"],
            "format": "Practical",
            "negative_marking": False
        },
        "key_subjects": ["Subject Knowledge", "Pedagogy", "Child Psychology"],
        "portal_url": "School specific portals",
        "category": "private",
        "difficulty_level": "moderate",
        "preparation_months": 2,
        "streams_eligible": ["Any"]
    },
    {
        "id": "private_tourism",
        "title": "Tourism & Hospitality Executive",
        "department": "Hotels & Travel Agencies",
        "board": "Private",
        "qualification": "BHM / BA Tourism",
        "age_range": "18-35",
        "salary_range": "15,000 - 35,000 / month",
        "vacancies_recent": 300,
        "exam_pattern": {
            "stages": ["Interview"],
            "format": "Verbal",
            "negative_marking": False
        },
        "key_subjects": ["Communication", "Hospitality Management", "Local Geography"],
        "portal_url": "Industry specific",
        "category": "private",
        "difficulty_level": "easy",
        "preparation_months": 2,
        "streams_eligible": ["Any"]
    },
    {
        "id": "private_digital_marketing",
        "title": "Digital Marketing Executive",
        "department": "Marketing Agencies",
        "board": "Private",
        "qualification": "Graduate + Certifications",
        "age_range": "21-35",
        "salary_range": "3LPA - 6LPA",
        "vacancies_recent": 400,
        "exam_pattern": {
            "stages": ["Assignment", "Interview"],
            "format": "Practical",
            "negative_marking": False
        },
        "key_subjects": ["SEO", "SEM", "Social Media Marketing", "Content Strategy"],
        "portal_url": "LinkedIn/Naukri",
        "category": "private",
        "difficulty_level": "moderate",
        "preparation_months": 3,
        "streams_eligible": ["Any"]
    },
    {
        "id": "entrepreneur_jkedi",
        "title": "Entrepreneur (JKEDI Scheme)",
        "department": "J&K Entrepreneurship Development Institute",
        "board": "Private",
        "qualification": "10+2 / Graduate",
        "age_range": "18-40",
        "salary_range": "Business Income (Seed funding up to 5L)",
        "vacancies_recent": 0,
        "exam_pattern": {
            "stages": ["Training", "Business Plan Submission"],
            "format": "Practical",
            "negative_marking": False
        },
        "key_subjects": ["Business Management", "Accounting", "Marketing", "Domain Skills"],
        "portal_url": "http://www.jkedi.org",
        "category": "private",
        "difficulty_level": "hard",
        "preparation_months": 6,
        "streams_eligible": ["Any"]
    },
    {
        "id": "startup_india",
        "title": "Startup Founder",
        "department": "Startup India / J&K Policy",
        "board": "Private",
        "qualification": "None / Graduate",
        "age_range": "18-50",
        "salary_range": "Equity / Revenue",
        "vacancies_recent": 0,
        "exam_pattern": {
            "stages": ["Pitch Deck", "Incubation", "Fundraising"],
            "format": "Practical",
            "negative_marking": False
        },
        "key_subjects": ["Product Development", "Sales", "Finance", "Leadership"],
        "portal_url": "https://www.startupindia.gov.in",
        "category": "private",
        "difficulty_level": "very_hard",
        "preparation_months": 12,
        "streams_eligible": ["Any"]
    }
]

# Skill to Career Mapping
SKILL_CAREER_MAP: Dict[str, List[str]] = {
    "python": ["Software Developer", "Data Analyst", "IT Officer"],
    "java": ["Software Developer", "IT Officer"],
    "c++": ["Software Developer", "IT Officer"],
    "sql": ["Data Analyst", "Software Developer", "IT Officer"],
    "accounting": ["Accounts Assistant", "Probationary Officer", "Banking Associate", "Entrepreneur (JKEDI Scheme)", "Startup Founder"],
    "biology": ["Lab Assistant", "Pharmacist", "Medical Officer", "Veterinary Assistant Surgeon", "Healthcare / Staff Nurse"],
    "mathematics": ["Junior Assistant", "Accounts Assistant", "Patwari", "SSC CGL", "Railway NTPC", "SSC CHSL", "Banking Associate", "Probationary Officer"],
    "english": ["Junior Assistant", "Sub-Inspector (Police)", "Accounts Assistant", "Junior Stenographer", "Probationary Officer", "Banking Associate", "SSC CGL", "SSC CHSL"],
    "general_knowledge": ["Junior Assistant", "Sub-Inspector (Police)", "Accounts Assistant", "Patwari", "Forest Guard", "KAS (J&K Administrative Service)", "UPSC CSE (IAS/IPS/IFS)"],
    "physics": ["Lab Assistant", "Assistant Engineer (Civil/Elec)", "Agniveer"],
    "chemistry": ["Lab Assistant", "Pharmacist"],
    "law": ["Sub-Inspector (Police)", "KAS (J&K Administrative Service)"],
    "commerce": ["Accounts Assistant", "Probationary Officer", "Banking Associate"],
    "computer_science": ["Junior Assistant", "Accounts Assistant", "IT Officer", "Software Developer", "Data Analyst"],
    "communication": ["KAS (J&K Administrative Service)", "Tourism & Hospitality Executive", "School Teacher", "Digital Marketing Executive", "Startup Founder"],
    "agriculture": ["Veterinary Assistant Surgeon", "KAS (J&K Administrative Service)", "Entrepreneur (JKEDI Scheme)"],
    "urdu": ["Patwari"],
    "shorthand": ["Junior Stenographer"],
    "typing": ["Junior Assistant", "Junior Stenographer"],
    "nursing": ["Healthcare / Staff Nurse"],
    "teaching": ["Assistant Professor / Lecturer", "School Teacher"],
    "marketing": ["Digital Marketing Executive", "Tourism & Hospitality Executive", "Entrepreneur (JKEDI Scheme)", "Startup Founder"],
    "seo": ["Digital Marketing Executive"],
    "data_visualization": ["Data Analyst"],
    "management": ["KAS (J&K Administrative Service)", "Entrepreneur (JKEDI Scheme)", "Startup Founder"],
    "history": ["UPSC CSE (IAS/IPS/IFS)", "KAS (J&K Administrative Service)"],
    "geography": ["UPSC CSE (IAS/IPS/IFS)", "KAS (J&K Administrative Service)"],
    "polity": ["UPSC CSE (IAS/IPS/IFS)", "KAS (J&K Administrative Service)", "Sub-Inspector (Police)"],
    "economy": ["UPSC CSE (IAS/IPS/IFS)", "KAS (J&K Administrative Service)", "Accounts Assistant", "Probationary Officer"],
    "reasoning": ["Junior Assistant", "Sub-Inspector (Police)", "Patwari", "Probationary Officer", "Banking Associate", "SSC CGL", "Railway NTPC", "SSC CHSL", "Agniveer"],
    "finance": ["Accounts Assistant", "Probationary Officer", "Banking Associate", "Startup Founder"],
    "social_media": ["Digital Marketing Executive"],
    "content_writing": ["Digital Marketing Executive"],
    "leadership": ["Startup Founder", "KAS (J&K Administrative Service)", "UPSC CSE (IAS/IPS/IFS)"],
    "sales": ["Startup Founder", "Entrepreneur (JKEDI Scheme)"],
    "hospitality": ["Tourism & Hospitality Executive"],
    "civil_engineering": ["Assistant Engineer (Civil/Elec)"],
    "electrical_engineering": ["Assistant Engineer (Civil/Elec)"],
    "pedagogy": ["School Teacher", "Assistant Professor / Lecturer"],
    "child_psychology": ["School Teacher"],
    "research": ["Assistant Professor / Lecturer"],
    "veterinary_science": ["Veterinary Assistant Surgeon"],
    "pharmacy": ["Pharmacist"],
    "medicine": ["Medical Officer"],
    "excel": ["Data Analyst", "Accounts Assistant", "Junior Assistant"],
    "physical_fitness": ["Sub-Inspector (Police)", "Forest Guard", "Agniveer", "CAPF Assistant Commandant"],
    "current_affairs": ["Sub-Inspector (Police)", "KAS (J&K Administrative Service)", "Probationary Officer", "UPSC CSE (IAS/IPS/IFS)", "SSC CGL"],
    "aptitude": ["Probationary Officer", "Banking Associate", "SSC CGL", "Railway NTPC", "SSC CHSL", "Software Developer"]
}

def search_jobs(query: str, board: str = None, qualification: str = None, district: str = None) -> List[Dict[str, Any]]:
    """Search jobs using fuzzy keyword matching and optional filters."""
    query = query.lower() if query else ""
    results = []
    
    for job in JOBS:
        if board and board.lower() not in job['board'].lower():
            continue
            
        if qualification and qualification.lower() not in job['qualification'].lower() and qualification.lower() not in [s.lower() for s in job['streams_eligible']]:
            # Simple check for eligibility
            if not ("any" in [s.lower() for s in job['streams_eligible']]):
                continue
                
        # Scoring based on text match
        score = 0
        if query:
            searchable_text = f"{job['title']} {job['department']} {job['qualification']} {' '.join(job['key_subjects'])}".lower()
            if query in job['title'].lower():
                score += 10
            if query in job['department'].lower():
                score += 5
            words = query.split()
            for w in words:
                if w in searchable_text:
                    score += 1
            
            if score == 0:
                continue
                
        results.append((score, job))
        
    # Sort by score descending
    results.sort(key=lambda x: x[0], reverse=True)
    return [job for score, job in results]

def match_skills_to_careers(skills: List[str], qualification: str = None) -> List[Dict[str, Any]]:
    """Match student skills to career paths and return ranked paths."""
    skills = [s.lower() for s in skills]
    career_scores = {}
    
    # Calculate matches
    for skill in skills:
        for sk, careers in SKILL_CAREER_MAP.items():
            if skill in sk or sk in skill:
                for career in careers:
                    career_scores[career] = career_scores.get(career, 0) + 1
                    
    matched_results = []
    for career_title, match_count in career_scores.items():
        # Find corresponding jobs
        matching_jobs = [j for j in JOBS if j['title'] == career_title]
        
        for job in matching_jobs:
            if qualification:
                q_lower = qualification.lower()
                eligibles = [s.lower() for s in job['streams_eligible']]
                if "any" not in eligibles and q_lower not in eligibles and q_lower not in job['qualification'].lower():
                    continue

            # Determine skills relevant to this job from the map
            required_skills = []
            for k, v in SKILL_CAREER_MAP.items():
                if career_title in v:
                    required_skills.append(k)
                    
            matched_s = [s for s in required_skills if any(usr_s in s or s in usr_s for usr_s in skills)]
            missing_s = [s for s in required_skills if s not in matched_s]
            
            score = (len(matched_s) / len(required_skills)) * 100 if required_skills else 0
            
            matched_results.append({
                "job": job,
                "skill_match_score": round(score, 2),
                "matched_skills": matched_s,
                "missing_skills": missing_s
            })
            
    # Sort by skill match score descending
    matched_results.sort(key=lambda x: x['skill_match_score'], reverse=True)
    return matched_results

def get_exam_preparation_plan(job_id: str) -> Optional[Dict[str, Any]]:
    """Return a structured exam preparation plan for a given job."""
    job = get_job_by_id(job_id)
    if not job:
        return None
        
    months = job['preparation_months']
    subjects = job['key_subjects']
    
    # Generic planning logic based on months and subjects
    weekly_hours_per_subject = 20 // len(subjects) if subjects else 5
    
    plan = {
        "title": f"Preparation Plan for {job['title']}",
        "duration_months": months,
        "subjects": [{"name": sub, "recommended_hours_per_week": weekly_hours_per_subject} for sub in subjects],
        "timeline": [],
        "resources": [
            "Standard NCERT textbooks (Classes 8-12) for basics",
            "Lucent's General Knowledge",
            "Arihant Publications guides for specific subjects",
            f"Previous year question papers of {job['board']}"
        ],
        "practice": [
            "Take 1 mock test every Sunday",
            "Daily current affairs reading (30 mins)",
            "Revision of previous day's topics (1 hour)"
        ]
    }
    
    # Generate timeline
    for m in range(1, months + 1):
        if m <= months * 0.5:
            focus = "Foundation building and covering syllabus basics"
        elif m <= months * 0.8:
            focus = "Advanced topics and intensive subject study"
        else:
            focus = "Revision, mock tests, and previous year papers"
            
        plan["timeline"].append({
            "month": m,
            "focus": focus
        })
        
    return plan

def get_jobs_by_board(board: str) -> List[Dict[str, Any]]:
    """Filter jobs by recruiting board."""
    return [job for job in JOBS if job['board'].lower() == board.lower()]

def get_all_boards() -> List[str]:
    """Return sorted list of unique boards."""
    boards = {job['board'] for job in JOBS}
    return sorted(list(boards))

def get_all_skills() -> List[str]:
    """Return sorted list of all skills in SKILL_CAREER_MAP."""
    return sorted(list(SKILL_CAREER_MAP.keys()))

def get_job_by_id(job_id: str) -> Optional[Dict[str, Any]]:
    """Direct lookup by job ID."""
    for job in JOBS:
        if job['id'] == job_id:
            return job
    return None

def render_job_card(job: Dict[str, Any]) -> str:
    """Format a markdown card for a job listing."""
    return f"""
### {job['title']}
**Board/Dept:** {job['board']} - {job['department']}
**Qualification:** {job['qualification']} (Streams: {', '.join(job['streams_eligible'])})
**Age Limit:** {job['age_range']}
**Salary:** {job['salary_range']}
**Recent Vacancies:** {job['vacancies_recent']}

**Exam Pattern:** {', '.join(job['exam_pattern']['stages'])} ({job['exam_pattern']['format']})
**Key Subjects:** {', '.join(job['key_subjects'])}

[Official Portal]({job['portal_url']})
"""

def render_skill_gap_report(matched_careers: List[Dict[str, Any]]) -> str:
    """Format markdown showing matched careers, scores, and gaps."""
    if not matched_careers:
        return "No matching careers found based on provided skills."
        
    report = "## Skill Gap Analysis & Career Matches\n\n"
    for match in matched_careers[:5]:  # Top 5
        job = match['job']
        score = match['skill_match_score']
        m_skills = ", ".join(match['matched_skills']) if match['matched_skills'] else "None"
        miss_skills = ", ".join(match['missing_skills']) if match['missing_skills'] else "None"
        
        report += f"### {job['title']} (Score: {score}%)\n"
        report += f"- **Matched Skills:** {m_skills}\n"
        report += f"- **Missing Skills (To Learn):** {miss_skills}\n"
        report += f"- **Salary Range:** {job['salary_range']}\n"
        report += f"- **Board:** {job['board']}\n\n"
        
    return report

if __name__ == "__main__":
    # Test cases
    print("Total Jobs:", len(JOBS))
    print("Total Skills:", len(get_all_skills()))
    print("Boards:", get_all_boards())
    
    print("\n--- Search Test ---")
    results = search_jobs("assistant")
    for r in results:
        print(r['title'])
        
    print("\n--- Skill Match Test ---")
    matches = match_skills_to_careers(["python", "sql", "communication"])
    print(render_skill_gap_report(matches))
