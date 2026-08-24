"""
Script to generate sample career guidance PDF documents into the docs/ folder.
Uses reportlab to generate clean, multi-page PDFs for testing and demonstration.
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

DOCS_DIR = os.path.join(os.path.dirname(__file__), "docs")
os.makedirs(DOCS_DIR, exist_ok=True)

def generate_swe_guide():
    pdf_path = os.path.join(DOCS_DIR, "software_engineering_career_guide.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=12
    )
    h2_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=15,
        leading=18,
        textColor=colors.HexColor('#1E40AF'),
        spaceBefore=14,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=8
    )

    story = []
    story.append(Paragraph("Complete Software Engineering Career & Interview Guide", title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#3B82F6'), spaceAfter=14))

    story.append(Paragraph("1. Career Paths in Software Engineering", h2_style))
    story.append(Paragraph(
        "Software engineering encompasses several distinct specializations: "
        "Frontend Engineers focus on user interfaces, responsive design, state management, and web performance using React, Vue, TypeScript, and modern CSS. "
        "Backend Engineers architect server-side logic, microservices, databases (PostgreSQL, Redis), APIs (REST, GraphQL, gRPC), and distributed caching. "
        "Full-Stack Engineers bridge client and server development, handling end-to-end features. "
        "DevOps / Site Reliability Engineers (SRE) manage CI/CD pipelines, container orchestration (Docker, Kubernetes), cloud infrastructure (AWS, GCP), and observability.",
        body_style
    ))

    story.append(Paragraph("2. Technical Skills & Modern Tech Stack", h2_style))
    story.append(Paragraph(
        "Core foundational skills every software engineer must master include: "
        "Data structures (Trees, Graphs, Hash Tables, Heaps) and Algorithms (Dynamic Programming, Graph traversals, Binary Search). "
        "Version control with Git (branching strategies, rebasing, pull request reviews). "
        "Database design: relational normalization vs document storage, indexing strategies, query optimization, and ACID transactions. "
        "Cloud & Container technologies: Docker containerization, Kubernetes cluster basics, and serverless computing.",
        body_style
    ))

    story.append(Paragraph("3. Technical Interview Preparation Roadmap", h2_style))
    story.append(Paragraph(
        "To excel in software engineering coding rounds, follow a structured 12-week preparation cycle: "
        "Weeks 1-4: Fundamental data structures (Arrays, Strings, HashMaps, Linked Lists, Stacks, Queues). "
        "Weeks 5-8: Intermediate patterns (Two Pointers, Sliding Window, Fast & Slow Pointers, DFS/BFS on Trees and Graphs). "
        "Weeks 9-10: Advanced topics (Dynamic Programming, Dijkstra, Topological Sort, Trie, Union Find). "
        "Weeks 11-12: System design fundamentals (Load Balancers, Consistent Hashing, CAP Theorem, Database Sharding, Caching strategies with Redis/Memcached).",
        body_style
    ))

    story.append(Paragraph("4. Resume Optimization for Engineers", h2_style))
    story.append(Paragraph(
        "To pass Applicant Tracking Systems (ATS) and impress hiring managers: "
        "1. Quantify achievements using the Google XYZ formula: 'Accomplished [X] as measured by [Y], by doing [Z]'. Example: 'Reduced API response latency by 45% (from 400ms to 220ms) by implementing Redis caching and indexing Postgres queries.' "
        "2. Keep the resume strictly to 1 page for engineers with under 5 years of experience. "
        "3. Include direct links to live projects, GitHub repositories, and LinkedIn profile. "
        "4. Categorize technical skills clearly into: Languages, Frameworks, Developer Tools, Databases, and Cloud Technologies.",
        body_style
    ))

    story.append(Paragraph("5. Behavioral Interviews and Salary Negotiation", h2_style))
    story.append(Paragraph(
        "Behavioral rounds evaluate leadership, teamwork, conflict resolution, and adaptability. "
        "Structure every behavioral answer using the STAR method: Situation, Task, Action, and Result. Always highlight your individual contribution and lessons learned. "
        "For salary negotiation: Never reveal your current salary or expectations first. Research market percentiles on Levels.fyi and Glassdoor. "
        "When receiving an initial offer, express enthusiasm, request 48-72 hours to evaluate, and negotiate the entire compensation package (base salary, equity/RSUs, signing bonus, and annual review cycles).",
        body_style
    ))

    doc.build(story)
    print(f"Generated: {pdf_path}")

def generate_ds_ai_guide():
    pdf_path = os.path.join(DOCS_DIR, "data_science_and_ai_roadmap.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=22,
        leading=26,
        textColor=colors.HexColor('#065F46'),
        spaceAfter=12
    )
    h2_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=15,
        leading=18,
        textColor=colors.HexColor('#047857'),
        spaceBefore=14,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#1F2937'),
        spaceAfter=8
    )

    story = []
    story.append(Paragraph("Data Science, Machine Learning & Generative AI Career Roadmap", title_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#10B981'), spaceAfter=14))

    story.append(Paragraph("1. Roles in the Modern AI & Data Ecosystem", h2_style))
    story.append(Paragraph(
        "The data landscape has evolved into distinct disciplines: "
        "Data Analysts focus on descriptive analytics, SQL querying, dashboarding (Tableau, PowerBI), business metrics, and stakeholder reporting. "
        "Data Scientists develop predictive models, perform rigorous statistical hypothesis testing, A/B testing, and exploratory data analysis using Python/R. "
        "Machine Learning Engineers (MLE) bridge the gap between data science and production software, designing training pipelines, feature stores, model serving systems, and latency optimization. "
        "GenAI / LLM Engineers build applications leveraging Large Language Models, RAG architectures, vector databases (ChromaDB, Pinecone), fine-tuning (LoRA, QLoRA), and agentic workflows.",
        body_style
    ))

    story.append(Paragraph("2. Core Technical Competencies for AI Practitioners", h2_style))
    story.append(Paragraph(
        "Key mathematical and programming foundations required: "
        "Mathematics: Linear Algebra (Matrix decompositions, Eigenvalues), Multivariate Calculus (Gradients, Backpropagation), Probability & Statistics (Bayes Rule, Probability Distributions, Confidence Intervals, p-values). "
        "Python Stack: NumPy, Pandas, Scikit-Learn, PyTorch, Hugging Face Transformers, LangChain/LlamaIndex. "
        "SQL Mastery: Window functions (ROW_NUMBER, RANK, LAG/LEAD), CTEs, aggregations, self-joins, and execution plan optimization. "
        "MLOps & Deployment: Docker, MLflow, FastAPI for REST endpoints, model monitoring (data drift, concept drift), and ONNX runtime.",
        body_style
    ))

    story.append(Paragraph("3. Building a Standout Portfolio & GitHub Projects", h2_style))
    story.append(Paragraph(
        "Generic projects like Titanic survival prediction or MNIST digit classification no longer impress recruiters. "
        "Build high-impact, full-lifecycle portfolio projects: "
        "Project 1: Production RAG Application - Ingest proprietary domain documents, utilize chunking strategies, embeddings, hybrid search, and LLM synthesis with citations. Deploy on Streamlit/FastAPI. "
        "Project 2: End-to-End Predictive Pipeline - Real-world dataset, automated data validation, CI/CD retraining with MLflow, and cloud deployment with Docker. "
        "Project 3: Computer Vision or Multimodal Agent - Fine-tuned vision transformer or audio agent with clear evaluation metrics and latency benchmarks.",
        body_style
    ))

    story.append(Paragraph("4. Data Science & ML Interview Formats", h2_style))
    story.append(Paragraph(
        "Typical interview stages for Data Science & ML roles: "
        "Stage 1: Live SQL & Python coding round (algorithmic data manipulation, pandas transformations). "
        "Stage 2: Machine Learning Theory & Deep Dive (bias-variance tradeoff, regularization L1/L2, gradient boosting vs random forest, attention mechanisms, transformer architecture). "
        "Stage 3: ML System Design (e.g., Design a Recommendation Feed for Netflix, Fraud Detection for Payment Gateway, or Search Ranking). Discuss data ingestion, feature engineering, offline/online metrics, training cadence, latency, and cold-start problems. "
        "Stage 4: Behavioral & Business Acumen round.",
        body_style
    ))

    doc.build(story)
    print(f"Generated: {pdf_path}")

if __name__ == "__main__":
    generate_swe_guide()
    generate_ds_ai_guide()
    print("All sample PDF documents created successfully.")
