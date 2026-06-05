import re

SKILL_KEYWORDS = [
    "python", "java", "javascript", "typescript", "c++", "c#", "ruby", "go", "rust",
    "php", "swift", "kotlin", "scala", "r", "matlab", "sql", "nosql",
    "react", "angular", "vue", "node", "django", "flask", "spring", "express",
    "docker", "kubernetes", "jenkins", "git", "ci/cd", "aws", "azure", "gcp",
    "tensorflow", "pytorch", "scikit-learn", "pandas", "numpy", "lstm", "transformer",
    "machine learning", "deep learning", "nlp", "computer vision", "llm",
    "tableau", "power bi", "excel", "jira", "confluence",
    "agile", "scrum", "kanban", "saas", "rest api", "graphql",
    "html", "css", "bootstrap", "tailwind", "sass", "jquery",
    "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
    "linux", "unix", "bash", "powershell", "nginx", "apache",
    "microservices", "soa", "event-driven", "kafka", "rabbitmq",
]

DEGREE_KEYWORDS = [
    "s1", "s2", "s3", "d3", "d4",
    "sarjana", "magister", "doktor", "diploma",
    "bachelor", "master", "phd", "doctorate", "associate",
    "strata 1", "strata 2", "strata 3",
]

UNIVERSITY_INDICATORS = [
    "universitas", "university", "institut", "institute",
    "sekolah tinggi", "politeknik", "academy",
]

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
    return match.group(0) if match else None

def extract_phone(text):
    patterns = [
        r'\+62[\d\s\-\(\)]{8,15}',
        r'0\d{2,3}[\s\-]?\d{3,4}[\s\-]?\d{3,6}',
        r'\(\+62\)[\s\-]?\d{3,4}[\s\-]?\d{3,4}[\s\-]?\d{3,4}',
    ]
    for pat in patterns:
        match = re.search(pat, text)
        if match:
            raw = match.group(0).strip()
            raw = re.sub(r'[\s\-\(\)]', '', raw)
            if len(raw) >= 10:
                return match.group(0).strip()
    return None

def extract_name(text):
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    for line in lines[:10]:
        if len(line.split()) in [2, 3, 4]:
            words = line.split()
            if all(w[0].isupper() for w in words if w.isalpha()):
                if not any(kw in line.lower() for kw in ["cv", "curriculum", "vitae", "resume", "phone", "email", "address"]):
                    if not re.search(r'[\d@]', line):
                        return line
    return None

def extract_skills(text):
    text_lower = text.lower()
    found = []
    for skill in SKILL_KEYWORDS:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found.append(skill.title() if skill.islower() else skill)
    return list(dict.fromkeys(found))

def extract_education(text):
    lines = text.split('\n')
    education_entries = []
    current = {"degree": None, "institution": None}
    for line in lines:
        line_lower = line.lower().strip()
        for dk in DEGREE_KEYWORDS:
            if dk in line_lower:
                current["degree"] = line.strip()
                break
        for ui in UNIVERSITY_INDICATORS:
            if ui in line_lower:
                current["institution"] = line.strip()
                break
        if current["degree"] or current["institution"]:
            education_entries.append({k: v for k, v in current.items() if v})
            current = {"degree": None, "institution": None}
    merged = []
    seen_degree = set()
    for entry in education_entries:
        key = entry.get("degree", "") + entry.get("institution", "")
        if key and key not in seen_degree:
            seen_degree.add(key)
            merged.append(entry)
    return merged

def extract_experience_years(text):
    patterns = [
        r'(\d+)[\+]?\s*(?:tahun|years|thn|yr)\s*(?:pengalaman|experience)',
        r'(?:pengalaman|experience)[^\d]{0,30}(\d+)[\+]?\s*(?:tahun|years|thn|yr)',
        r'(\d+)[\+]?\s*(?:tahun|years|thn|yr)',
    ]
    for pat in patterns:
        match = re.search(pat, text.lower())
        if match:
            return int(match.group(1))
    return None

def extract_certifications(text):
    cert_keywords = [
        "certified", "certification", "certificate", "sertifikasi", "bersertifikat",
        "professional", "chartered", "license",
    ]
    lines = text.split('\n')
    certs = []
    capture = False
    for line in lines:
        line_lower = line.lower().strip()
        if any(ck in line_lower for ck in cert_keywords):
            capture = True
        if capture and line.strip():
            certs.append(line.strip())
        if capture and not line.strip():
            capture = False
    return certs if certs else None

def parse_cv(cv_text):
    return {
        "nama": extract_name(cv_text),
        "email": extract_email(cv_text),
        "telepon": extract_phone(cv_text),
        "skills": extract_skills(cv_text),
        "pendidikan": extract_education(cv_text),
        "pengalaman_tahun": extract_experience_years(cv_text),
        "sertifikasi": extract_certifications(cv_text),
        "teks_mentah": cv_text,
    }
