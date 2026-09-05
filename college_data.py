from typing import List, Dict, Optional
import re

COLLEGES_DATA = [
    # ---------------- ENGINEERING COLLEGES ----------------
    {
        "id": "nit_srinagar",
        "name": "National Institute of Technology Srinagar",
        "type": "engineering",
        "district": "Srinagar",
        "affiliation": "Central Govt (MoE)",
        "branches": [
            {
                "name": "Computer Science and Engineering",
                "seats_om": 38, "seats_sc": 11, "seats_st": 6, "seats_rba": 0, "total_seats": 77,
                "cutoff_info": "JEE Main ~22000 CRL (OM)"
            },
            {
                "name": "Electronics and Communication Engineering",
                "seats_om": 38, "seats_sc": 11, "seats_st": 6, "seats_rba": 0, "total_seats": 77,
                "cutoff_info": "JEE Main ~30000 CRL (OM)"
            },
            {
                "name": "Electrical Engineering",
                "seats_om": 45, "seats_sc": 13, "seats_st": 7, "seats_rba": 0, "total_seats": 92,
                "cutoff_info": "JEE Main ~38000 CRL (OM)"
            },
            {
                "name": "Mechanical Engineering",
                "seats_om": 45, "seats_sc": 13, "seats_st": 7, "seats_rba": 0, "total_seats": 92,
                "cutoff_info": "JEE Main ~45000 CRL (OM)"
            },
            {
                "name": "Civil Engineering",
                "seats_om": 50, "seats_sc": 15, "seats_st": 8, "seats_rba": 0, "total_seats": 102,
                "cutoff_info": "JEE Main ~50000 CRL (OM)"
            },
            {
                "name": "Information Technology",
                "seats_om": 35, "seats_sc": 10, "seats_st": 5, "seats_rba": 0, "total_seats": 72,
                "cutoff_info": "JEE Main ~25000 CRL (OM)"
            },
            {
                "name": "Chemical Engineering",
                "seats_om": 30, "seats_sc": 9, "seats_st": 5, "seats_rba": 0, "total_seats": 62,
                "cutoff_info": "JEE Main ~55000 CRL (OM)"
            },
            {
                "name": "Metallurgical and Materials Engineering",
                "seats_om": 30, "seats_sc": 9, "seats_st": 5, "seats_rba": 0, "total_seats": 62,
                "cutoff_info": "JEE Main ~65000 CRL (OM)"
            }
        ],
        "fees_per_sem": "Rs. 62,500 (Gen/OBC) - Variable for SC/ST",
        "hostel": True,
        "website": "https://nitsri.ac.in",
        "admission_through": "JoSAA (JEE Main)",
        "naac_grade": "A",
        "established": 1960
    },
    {
        "id": "iust_awantipora",
        "name": "Islamic University of Science & Technology (IUST)",
        "type": "engineering",
        "district": "Pulwama",
        "affiliation": "UT Govt J&K",
        "branches": [
            {
                "name": "Computer Science and Engineering",
                "seats_om": 30, "seats_sc": 5, "seats_st": 5, "seats_rba": 10, "total_seats": 60,
                "cutoff_info": "JKCET Top 1000 / JEE Main"
            },
            {
                "name": "Civil Engineering",
                "seats_om": 30, "seats_sc": 5, "seats_st": 5, "seats_rba": 10, "total_seats": 60,
                "cutoff_info": "JKCET Top 2000"
            },
            {
                "name": "Electrical Engineering",
                "seats_om": 30, "seats_sc": 5, "seats_st": 5, "seats_rba": 10, "total_seats": 60,
                "cutoff_info": "JKCET Top 2500"
            },
            {
                "name": "Electronics & Communication",
                "seats_om": 30, "seats_sc": 5, "seats_st": 5, "seats_rba": 10, "total_seats": 60,
                "cutoff_info": "JKCET Top 3000"
            },
            {
                "name": "Food Technology",
                "seats_om": 30, "seats_sc": 5, "seats_st": 5, "seats_rba": 10, "total_seats": 60,
                "cutoff_info": "JKCET Top 4000"
            }
        ],
        "fees_per_sem": "Rs. 30,000 - 45,000",
        "hostel": True,
        "website": "https://iust.ac.in",
        "admission_through": "JKCET/JEE",
        "naac_grade": "B",
        "established": 2005
    },
    {
        "id": "ssm_parihaspora",
        "name": "SSM College of Engineering",
        "type": "engineering",
        "district": "Baramulla",
        "affiliation": "University of Kashmir",
        "branches": [
            {
                "name": "Computer Science and Engineering",
                "seats_om": 60, "seats_sc": 0, "seats_st": 0, "seats_rba": 0, "total_seats": 120,
                "cutoff_info": "JKCET/Management Quota"
            },
            {
                "name": "Civil Engineering",
                "seats_om": 60, "seats_sc": 0, "seats_st": 0, "seats_rba": 0, "total_seats": 120,
                "cutoff_info": "JKCET/Management"
            }
        ],
        "fees_per_sem": "Rs. 40,000 - 50,000",
        "hostel": True,
        "website": "https://ssmengg.edu.in",
        "admission_through": "JKCET",
        "naac_grade": "",
        "established": 1988
    },
    {
        "id": "miet_jammu",
        "name": "Model Institute of Engineering and Technology",
        "type": "engineering",
        "district": "Jammu",
        "affiliation": "University of Jammu",
        "branches": [
            {
                "name": "Computer Science and Engineering",
                "seats_om": 90, "seats_sc": 15, "seats_st": 10, "seats_rba": 5, "total_seats": 180,
                "cutoff_info": "JKCET/JEE Main"
            },
            {
                "name": "Electronics & Communication",
                "seats_om": 45, "seats_sc": 10, "seats_st": 5, "seats_rba": 0, "total_seats": 90,
                "cutoff_info": "JKCET/JEE Main"
            }
        ],
        "fees_per_sem": "Rs. 50,000 - 65,000",
        "hostel": True,
        "website": "https://mietjammu.in",
        "admission_through": "JKCET",
        "naac_grade": "A",
        "established": 1999
    },
    {
        "id": "gec_jammu",
        "name": "Government College of Engineering and Technology, Jammu",
        "type": "engineering",
        "district": "Jammu",
        "affiliation": "UT Govt J&K",
        "branches": [
            {
                "name": "Computer Science",
                "seats_om": 30, "seats_sc": 5, "seats_st": 5, "seats_rba": 10, "total_seats": 60,
                "cutoff_info": "JKCET Top 500"
            },
            {
                "name": "Civil Engineering",
                "seats_om": 30, "seats_sc": 5, "seats_st": 5, "seats_rba": 10, "total_seats": 60,
                "cutoff_info": "JKCET Top 1500"
            }
        ],
        "fees_per_sem": "Rs. 15,000 - 20,000",
        "hostel": True,
        "website": "https://gcetjammu.org.in",
        "admission_through": "JKCET",
        "naac_grade": "",
        "established": 1994
    },
    {
        "id": "gcet_safapora",
        "name": "Government College of Engineering and Technology Safapora",
        "type": "engineering",
        "district": "Ganderbal",
        "affiliation": "UT Govt J&K",
        "branches": [
            {
                "name": "Computer Science",
                "seats_om": 30, "seats_sc": 5, "seats_st": 5, "seats_rba": 10, "total_seats": 60,
                "cutoff_info": "JKCET"
            },
            {
                "name": "Civil Engineering",
                "seats_om": 30, "seats_sc": 5, "seats_st": 5, "seats_rba": 10, "total_seats": 60,
                "cutoff_info": "JKCET"
            }
        ],
        "fees_per_sem": "Rs. 15,000",
        "hostel": False,
        "website": "https://gcetkashmir.ac.in",
        "admission_through": "JKCET",
        "naac_grade": "",
        "established": 2017
    },
    {
        "id": "bgsbu_rajouri",
        "name": "Baba Ghulam Shah Badshah University",
        "type": "engineering",
        "district": "Rajouri",
        "affiliation": "UT Govt J&K",
        "branches": [
            {
                "name": "Computer Science and Engineering",
                "seats_om": 30, "seats_sc": 5, "seats_st": 5, "seats_rba": 10, "total_seats": 60,
                "cutoff_info": "JKCET/JEE"
            },
            {
                "name": "Information Technology",
                "seats_om": 30, "seats_sc": 5, "seats_st": 5, "seats_rba": 10, "total_seats": 60,
                "cutoff_info": "JKCET/JEE"
            }
        ],
        "fees_per_sem": "Rs. 35,000",
        "hostel": True,
        "website": "https://bgsbu.ac.in",
        "admission_through": "JKCET",
        "naac_grade": "B++",
        "established": 2002
    },
    {
        "id": "govt_poly_srinagar",
        "name": "Government Polytechnic College Srinagar",
        "type": "engineering",
        "district": "Srinagar",
        "affiliation": "JKBOTE",
        "branches": [
            {
                "name": "Civil Engineering Diploma",
                "seats_om": 30, "seats_sc": 5, "seats_st": 5, "seats_rba": 10, "total_seats": 60,
                "cutoff_info": "Merit based (10th/12th)"
            }
        ],
        "fees_per_sem": "Rs. 3,000",
        "hostel": True,
        "website": "https://kashmirpolytechnic.com",
        "admission_through": "BOPEE Polytechnic",
        "naac_grade": "",
        "established": 1958
    },

    # ---------------- MEDICAL COLLEGES ----------------
    {
        "id": "gmc_srinagar",
        "name": "Government Medical College (SMHS), Srinagar",
        "type": "medical",
        "district": "Srinagar",
        "affiliation": "University of Kashmir",
        "branches": [
            {
                "name": "MBBS",
                "seats_om": 90, "seats_sc": 16, "seats_st": 20, "seats_rba": 20, "total_seats": 200,
                "cutoff_info": "NEET ~590-625 (OM)"
            }
        ],
        "fees_per_sem": "Rs. 15,000 (Annual)",
        "hostel": True,
        "website": "https://gmcs.edu.in",
        "admission_through": "BOPEE (NEET)",
        "naac_grade": "A",
        "established": 1959
    },
    {
        "id": "gmc_jammu",
        "name": "Government Medical College, Jammu",
        "type": "medical",
        "district": "Jammu",
        "affiliation": "University of Jammu",
        "branches": [
            {
                "name": "MBBS",
                "seats_om": 90, "seats_sc": 16, "seats_st": 20, "seats_rba": 20, "total_seats": 200,
                "cutoff_info": "NEET ~580-610 (OM)"
            }
        ],
        "fees_per_sem": "Rs. 15,000 (Annual)",
        "hostel": True,
        "website": "https://gmcjammu.nic.in",
        "admission_through": "BOPEE (NEET)",
        "naac_grade": "A",
        "established": 1973
    },
    {
        "id": "gmc_doda",
        "name": "Government Medical College, Doda",
        "type": "medical",
        "district": "Doda",
        "affiliation": "University of Jammu",
        "branches": [
            {
                "name": "MBBS",
                "seats_om": 45, "seats_sc": 8, "seats_st": 10, "seats_rba": 10, "total_seats": 100,
                "cutoff_info": "NEET ~540-560 (OM)"
            }
        ],
        "fees_per_sem": "Rs. 15,000 (Annual)",
        "hostel": True,
        "website": "https://gmcdoda.in",
        "admission_through": "BOPEE (NEET)",
        "naac_grade": "",
        "established": 2020
    },
    {
        "id": "gmc_rajouri",
        "name": "Government Medical College, Rajouri",
        "type": "medical",
        "district": "Rajouri",
        "affiliation": "University of Jammu",
        "branches": [
            {
                "name": "MBBS",
                "seats_om": 45, "seats_sc": 8, "seats_st": 10, "seats_rba": 10, "total_seats": 100,
                "cutoff_info": "NEET ~530-550 (OM)"
            }
        ],
        "fees_per_sem": "Rs. 15,000 (Annual)",
        "hostel": True,
        "website": "https://gmcrajouri.in",
        "admission_through": "BOPEE (NEET)",
        "naac_grade": "",
        "established": 2019
    },
    {
        "id": "gmc_anantnag",
        "name": "Government Medical College, Anantnag",
        "type": "medical",
        "district": "Anantnag",
        "affiliation": "University of Kashmir",
        "branches": [
            {
                "name": "MBBS",
                "seats_om": 45, "seats_sc": 8, "seats_st": 10, "seats_rba": 10, "total_seats": 100,
                "cutoff_info": "NEET ~550-570 (OM)"
            }
        ],
        "fees_per_sem": "Rs. 15,000 (Annual)",
        "hostel": True,
        "website": "https://gmcanantnag.net",
        "admission_through": "BOPEE (NEET)",
        "naac_grade": "",
        "established": 2019
    },
    {
        "id": "gmc_kathua",
        "name": "Government Medical College, Kathua",
        "type": "medical",
        "district": "Kathua",
        "affiliation": "University of Jammu",
        "branches": [
            {
                "name": "MBBS",
                "seats_om": 45, "seats_sc": 8, "seats_st": 10, "seats_rba": 10, "total_seats": 100,
                "cutoff_info": "NEET ~540-560 (OM)"
            }
        ],
        "fees_per_sem": "Rs. 15,000 (Annual)",
        "hostel": True,
        "website": "https://gmckathua.in",
        "admission_through": "BOPEE (NEET)",
        "naac_grade": "",
        "established": 2019
    },
    {
        "id": "gmc_baramulla",
        "name": "Government Medical College, Baramulla",
        "type": "medical",
        "district": "Baramulla",
        "affiliation": "University of Kashmir",
        "branches": [
            {
                "name": "MBBS",
                "seats_om": 45, "seats_sc": 8, "seats_st": 10, "seats_rba": 10, "total_seats": 100,
                "cutoff_info": "NEET ~550-570 (OM)"
            }
        ],
        "fees_per_sem": "Rs. 15,000 (Annual)",
        "hostel": True,
        "website": "https://gmcbaramulla.com",
        "admission_through": "BOPEE (NEET)",
        "naac_grade": "",
        "established": 2019
    },
    {
        "id": "skims_soura",
        "name": "SKIMS Soura",
        "type": "medical",
        "district": "Srinagar",
        "affiliation": "Deemed University",
        "branches": [
            {
                "name": "MBBS",
                "seats_om": 45, "seats_sc": 8, "seats_st": 10, "seats_rba": 10, "total_seats": 100,
                "cutoff_info": "NEET ~600-640 (OM)"
            }
        ],
        "fees_per_sem": "Rs. 25,000 (Annual)",
        "hostel": True,
        "website": "https://skims.ac.in",
        "admission_through": "BOPEE (NEET)",
        "naac_grade": "A+",
        "established": 1982
    },
    {
        "id": "skims_bemina",
        "name": "SKIMS Medical College, Bemina",
        "type": "medical",
        "district": "Srinagar",
        "affiliation": "Deemed University",
        "branches": [
            {
                "name": "MBBS",
                "seats_om": 45, "seats_sc": 8, "seats_st": 10, "seats_rba": 10, "total_seats": 100,
                "cutoff_info": "NEET ~570-590 (OM)"
            }
        ],
        "fees_per_sem": "Rs. 20,000 (Annual)",
        "hostel": True,
        "website": "https://skimsbemina.edu.in",
        "admission_through": "BOPEE (NEET)",
        "naac_grade": "A",
        "established": 1989
    },
    {
        "id": "gamc_akhnoor",
        "name": "Government Ayurvedic Medical College, Akhnoor",
        "type": "medical",
        "district": "Jammu",
        "affiliation": "University of Jammu",
        "branches": [
            {
                "name": "BAMS",
                "seats_om": 25, "seats_sc": 5, "seats_st": 6, "seats_rba": 6, "total_seats": 60,
                "cutoff_info": "NEET ~400 (OM)"
            }
        ],
        "fees_per_sem": "Rs. 10,000 (Annual)",
        "hostel": True,
        "website": "https://gamcjammu.org",
        "admission_through": "BOPEE (NEET)",
        "naac_grade": "",
        "established": 2017
    },
    {
        "id": "gumc_ganderbal",
        "name": "Government Unani Medical College, Ganderbal",
        "type": "medical",
        "district": "Ganderbal",
        "affiliation": "University of Kashmir",
        "branches": [
            {
                "name": "BUMS",
                "seats_om": 25, "seats_sc": 5, "seats_st": 6, "seats_rba": 6, "total_seats": 60,
                "cutoff_info": "NEET ~400 (OM)"
            }
        ],
        "fees_per_sem": "Rs. 10,000 (Annual)",
        "hostel": True,
        "website": "https://gumck.in",
        "admission_through": "BOPEE (NEET)",
        "naac_grade": "",
        "established": 2020
    },

    # ---------------- PROFESSIONAL & AGRICULTURE ----------------
    {
        "id": "ku_srinagar",
        "name": "University of Kashmir",
        "type": "university",
        "district": "Srinagar",
        "affiliation": "UT Govt J&K",
        "branches": [
            {
                "name": "BA/BSc/BCom",
                "seats_om": 500, "seats_sc": 80, "seats_st": 100, "seats_rba": 100, "total_seats": 1000,
                "cutoff_info": "CUET / Merit"
            },
            {
                "name": "LLB",
                "seats_om": 25, "seats_sc": 5, "seats_st": 5, "seats_rba": 5, "total_seats": 50,
                "cutoff_info": "KUET Entrance"
            }
        ],
        "fees_per_sem": "Rs. 5,000 - 15,000",
        "hostel": True,
        "website": "https://kashmiruniversity.net",
        "admission_through": "CUET / KUET",
        "naac_grade": "A+",
        "established": 1948
    },
    {
        "id": "ju_jammu",
        "name": "University of Jammu",
        "type": "university",
        "district": "Jammu",
        "affiliation": "UT Govt J&K",
        "branches": [
            {
                "name": "BA/BSc/BCom",
                "seats_om": 500, "seats_sc": 80, "seats_st": 100, "seats_rba": 100, "total_seats": 1000,
                "cutoff_info": "CUET / Merit"
            },
            {
                "name": "BBA",
                "seats_om": 40, "seats_sc": 5, "seats_st": 5, "seats_rba": 5, "total_seats": 60,
                "cutoff_info": "JUET Entrance"
            }
        ],
        "fees_per_sem": "Rs. 5,000 - 15,000",
        "hostel": True,
        "website": "https://jammuuniversity.ac.in",
        "admission_through": "CUET / JUET",
        "naac_grade": "A+",
        "established": 1969
    },
    {
        "id": "cuk_ganderbal",
        "name": "Central University of Kashmir",
        "type": "university",
        "district": "Ganderbal",
        "affiliation": "Central Govt",
        "branches": [
            {
                "name": "Integrated BSc-MSc Physics",
                "seats_om": 20, "seats_sc": 5, "seats_st": 3, "seats_rba": 0, "total_seats": 40,
                "cutoff_info": "CUET"
            },
            {
                "name": "BA LLB",
                "seats_om": 25, "seats_sc": 5, "seats_st": 5, "seats_rba": 0, "total_seats": 50,
                "cutoff_info": "CUET"
            }
        ],
        "fees_per_sem": "Rs. 8,000 - 20,000",
        "hostel": True,
        "website": "https://cukashmir.ac.in",
        "admission_through": "CUET",
        "naac_grade": "B++",
        "established": 2009
    },
    {
        "id": "cuj_samba",
        "name": "Central University of Jammu",
        "type": "university",
        "district": "Samba",
        "affiliation": "Central Govt",
        "branches": [
            {
                "name": "Integrated Science",
                "seats_om": 20, "seats_sc": 5, "seats_st": 3, "seats_rba": 0, "total_seats": 40,
                "cutoff_info": "CUET"
            }
        ],
        "fees_per_sem": "Rs. 8,000 - 20,000",
        "hostel": True,
        "website": "https://cujammu.ac.in",
        "admission_through": "CUET",
        "naac_grade": "B++",
        "established": 2011
    },
    {
        "id": "skuast_kashmir",
        "name": "SKUAST-Kashmir",
        "type": "agriculture",
        "district": "Srinagar",
        "affiliation": "UT Govt J&K",
        "branches": [
            {
                "name": "B.Sc Agriculture",
                "seats_om": 45, "seats_sc": 8, "seats_st": 10, "seats_rba": 10, "total_seats": 100,
                "cutoff_info": "SKUAST Entrance"
            },
            {
                "name": "BVSc & AH",
                "seats_om": 30, "seats_sc": 5, "seats_st": 5, "seats_rba": 8, "total_seats": 60,
                "cutoff_info": "SKUAST Entrance"
            },
            {
                "name": "B.Tech Food Technology",
                "seats_om": 20, "seats_sc": 3, "seats_st": 3, "seats_rba": 4, "total_seats": 40,
                "cutoff_info": "SKUAST Entrance"
            }
        ],
        "fees_per_sem": "Rs. 15,000 - 25,000",
        "hostel": True,
        "website": "https://skuastkashmir.ac.in",
        "admission_through": "UET",
        "naac_grade": "A",
        "established": 1982
    },
    {
        "id": "skuast_jammu",
        "name": "SKUAST-Jammu",
        "type": "agriculture",
        "district": "Jammu",
        "affiliation": "UT Govt J&K",
        "branches": [
            {
                "name": "B.Sc Agriculture",
                "seats_om": 45, "seats_sc": 8, "seats_st": 10, "seats_rba": 10, "total_seats": 100,
                "cutoff_info": "SKUAST Entrance"
            },
            {
                "name": "BVSc & AH",
                "seats_om": 30, "seats_sc": 5, "seats_st": 5, "seats_rba": 8, "total_seats": 60,
                "cutoff_info": "SKUAST Entrance"
            }
        ],
        "fees_per_sem": "Rs. 15,000 - 25,000",
        "hostel": True,
        "website": "https://skuast.org",
        "admission_through": "CET",
        "naac_grade": "A",
        "established": 1999
    },
    {
        "id": "gdc_law_srinagar",
        "name": "Government Law College, Srinagar",
        "type": "professional",
        "district": "Srinagar",
        "affiliation": "University of Kashmir",
        "branches": [
            {
                "name": "LLB",
                "seats_om": 30, "seats_sc": 5, "seats_st": 5, "seats_rba": 10, "total_seats": 60,
                "cutoff_info": "Entrance / Merit"
            }
        ],
        "fees_per_sem": "Rs. 10,000",
        "hostel": False,
        "website": "https://kashmiruniversity.net",
        "admission_through": "Entrance",
        "naac_grade": "",
        "established": 1980
    }
]


def search_colleges(query: str, district: str = None, college_type: str = None, category: str = None) -> List[Dict]:
    """
    Fuzzy keyword search across college names, branches, admission modes.
    Optional filters by district, type, and reservation category.
    Returns matching colleges sorted by relevance score.
    """
    results = []
    q = query.lower().strip() if query else ""

    for college in COLLEGES_DATA:
        # Apply strict filters first
        if district and district.lower() != college["district"].lower():
            continue
        if college_type and college_type.lower() != college["type"].lower():
            continue
        
        # Check category capacity if specified
        if category:
            cat_key = f"seats_{category.lower()}"
            has_seats = False
            for b in college.get("branches", []):
                if b.get(cat_key, 0) > 0 or b.get("total_seats", 0) > 0:
                    has_seats = True
                    break
            if not has_seats:
                continue

        # Calculate a relevance score based on the query
        score = 0
        if not q:
            score = 1
        else:
            if q in college["name"].lower():
                score += 10
            if q in college["id"].lower():
                score += 5
            if q in college["district"].lower():
                score += 2
            if q in college["admission_through"].lower():
                score += 3
            
            # Check branches
            for branch in college.get("branches", []):
                if q in branch["name"].lower():
                    score += 5
                    break
                if q in branch["cutoff_info"].lower():
                    score += 1
                    break

        if score > 0:
            results.append((score, college))
            
    # Sort by score descending
    results.sort(key=lambda x: x[0], reverse=True)
    return [c for score, c in results]


def get_seat_matrix(college_id: str, category: str = "OM") -> Optional[Dict]:
    """
    Returns branch-wise seat counts for a specific reservation category.
    Returns None if college_id not found.
    """
    college = get_college_by_id(college_id)
    if not college:
        return None

    cat_key = f"seats_{category.lower()}"
    matrix = {}
    
    for branch in college.get("branches", []):
        matrix[branch["name"]] = branch.get(cat_key, 0)

    return matrix


def get_colleges_by_district(district: str) -> List[Dict]:
    """
    Returns all colleges in a specific district
    Case-insensitive matching
    """
    return [c for c in COLLEGES_DATA if c["district"].lower() == district.lower()]


def get_all_districts() -> List[str]:
    """
    Returns sorted list of unique districts that have colleges
    """
    districts = set(c["district"] for c in COLLEGES_DATA)
    return sorted(list(districts))


def get_all_college_types() -> List[str]:
    """
    Returns list of unique college types
    """
    types = set(c["type"] for c in COLLEGES_DATA)
    return sorted(list(types))


def get_cutoff_comparison(college_ids: List[str], branch: str = None) -> List[Dict]:
    """
    Side-by-side comparison of cutoffs across colleges
    If branch specified, filters to that branch only
    """
    comparison = []
    
    for cid in college_ids:
        college = get_college_by_id(cid)
        if not college:
            continue
            
        branches_to_check = college.get("branches", [])
        if branch:
            # simple substring match for branch names
            b_q = branch.lower()
            branches_to_check = [b for b in branches_to_check if b_q in b["name"].lower()]
            
        for b in branches_to_check:
            comparison.append({
                "college_name": college["name"],
                "college_id": college["id"],
                "branch": b["name"],
                "cutoff_info": b["cutoff_info"],
                "total_seats": b["total_seats"]
            })
            
    return comparison


def render_college_card(college: Dict) -> str:
    """
    Returns formatted markdown string for displaying a college
    Includes name, district, type, branches with seats, fees, admission mode, website
    """
    md = []
    md.append(f"### {college['name']}")
    
    badges = [
        f"📍 **{college['district']}**",
        f"🏛️ {college['type'].capitalize()}",
        f"📅 Est. {college['established']}"
    ]
    if college.get("naac_grade"):
        badges.append(f"🎖️ NAAC: {college['naac_grade']}")
        
    md.append(" | ".join(badges))
    md.append("")
    md.append(f"- **Affiliation:** {college['affiliation']}")
    md.append(f"- **Admission Through:** {college['admission_through']}")
    md.append(f"- **Fees:** {college['fees_per_sem']}")
    md.append(f"- **Hostel Available:** {'Yes' if college['hostel'] else 'No'}")
    md.append(f"- **Website:** [{college['website']}]({college['website']})")
    
    md.append("\n#### Branch & Seat Matrix (Total Intake)")
    for b in college.get("branches", []):
        md.append(f"- **{b['name']}**: {b['total_seats']} seats *(Cutoff: {b['cutoff_info']})*")
        
    return "\n".join(md)


def get_college_by_id(college_id: str) -> Optional[Dict]:
    """
    Direct lookup by ID
    """
    for c in COLLEGES_DATA:
        if c["id"] == college_id:
            return c
    return None


COLLEGE_COORDINATES = {
    "nit_srinagar": (34.1245, 74.8384),
    "iust_awantipora": (33.9267, 75.0167),
    "ssm_parihaspora": (34.1481, 74.6067),
    "miet_jammu": (32.6500, 74.8700),
    "gec_jammu": (32.7000, 74.8700),
    "gcet_safapora": (34.2268, 74.7063),
    "bgsbu_rajouri": (33.3813, 74.3142),
    "govt_poly_srinagar": (34.0750, 74.8100),
    "gmc_srinagar": (34.0837, 74.8080),
    "gmc_jammu": (32.7357, 74.8690),
    "gmc_doda": (33.1464, 75.5458),
    "gmc_rajouri": (33.3750, 74.3100),
    "gmc_anantnag": (33.7311, 75.1522),
    "gmc_kathua": (32.3739, 75.5186),
    "gmc_baramulla": (34.2000, 74.3400),
    "skims_soura": (34.1350, 74.7990),
    "skims_bemina": (34.0800, 74.7700),
    "gamc_akhnoor": (32.8980, 74.7380),
    "gumc_ganderbal": (34.2167, 74.7700),
    "ku_srinagar": (34.1264, 74.8360),
    "ju_jammu": (32.7194, 74.8694),
    "cuk_ganderbal": (34.2200, 74.7800),
    "cuj_samba": (32.5583, 75.1167),
    "skuast_kashmir": (34.1500, 74.8833),
    "skuast_jammu": (32.6500, 74.8200),
    "gdc_law_srinagar": (34.0900, 74.8000),
}


def get_colleges_map_data(colleges: Optional[List[Dict]] = None) -> List[Dict]:
    """
    Returns coordinate data for st.map visualization across J&K.
    """
    target = colleges if colleges is not None else COLLEGES_DATA
    map_points = []
    for c in target:
        coords = COLLEGE_COORDINATES.get(c["id"])
        if coords:
            map_points.append({
                "name": c["name"],
                "latitude": coords[0],
                "longitude": coords[1],
                "district": c["district"],
                "type": c["type"]
            })
    return map_points

