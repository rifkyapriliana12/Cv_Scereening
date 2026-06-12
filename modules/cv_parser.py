import pdfplumber
import re
import os
from typing import Dict, List, Optional

class CVParser:
    def __init__(self):
        self.skill_keywords = [
            "autocad", "sketchup", "revit", "lumion", "enscape", "photoshop",
            "microsoft office", "vray", "twinmotion", "d5 render", "cad",
            "architectural design", "3d modeling", "rendering", "drafting",
            "project management", "communication", "teamwork", "presentation",
            "building codes", "construction management", "site supervision",
            "interior design", "landscape architecture", "structural design",
            "python", "java", "javascript", "sql", "machine learning", "ai",
            "data analysis", "excel", "power bi", "tableau", "sap",
        ]

    def extract_text_from_pdf(self, path: str) -> str:
        text = ""
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text

    def extract_text_from_docx(self, path: str) -> str:
        try:
            from docx import Document
            doc = Document(path)
            return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except ImportError:
            return "[ERROR: python-docx not installed]"

    def extract_text(self, path: str) -> str:
        ext = os.path.splitext(path)[1].lower()
        if ext == ".pdf":
            return self.extract_text_from_pdf(path)
        elif ext == ".docx":
            return self.extract_text_from_docx(path)
        return ""

    def extract_name(self, text: str) -> str:
        lines = text.strip().split("\n")
        for line in lines[:10]:
            line = line.strip()
            if line and len(line.split()) <= 4 and not re.match(r'^[\d\s\+\-\(\)]+$', line):
                return line
        return "Unknown"

    def extract_email(self, text: str) -> Optional[str]:
        match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        return match.group(0) if match else None

    def extract_phone(self, text: str) -> Optional[str]:
        match = re.search(r'(\+?[\d\s\-\(\)]{7,20})', text)
        if match:
            return match.group(0).strip()
        return None

    def extract_linkedin(self, text: str) -> Optional[str]:
        match = re.search(r'(https?://)?(www\.)?linkedin\.com/in/[\w\-/]+', text)
        return match.group(0) if match else None

    def extract_skills(self, text: str) -> List[str]:
        skill_title_map = {
            "autocad": "AutoCAD", "cad": "CAD", "sketchup": "SketchUp",
            "revit": "Revit", "lumion": "Lumion", "enscape": "Enscape",
            "photoshop": "Photoshop", "microsoft office": "Microsoft Office",
            "vray": "V-Ray", "twinmotion": "Twinmotion", "d5 render": "D5 Render",
            "architectural design": "Architectural Design", "3d modeling": "3D Modeling",
            "rendering": "Rendering", "drafting": "Drafting",
            "project management": "Project Management", "communication": "Communication",
            "teamwork": "Teamwork", "presentation": "Presentation",
            "building codes": "Building Codes", "construction management": "Construction Management",
            "site supervision": "Site Supervision", "interior design": "Interior Design",
            "landscape architecture": "Landscape Architecture",
            "structural design": "Structural Design",
            "python": "Python", "java": "Java", "javascript": "JavaScript",
            "sql": "SQL", "machine learning": "Machine Learning", "ai": "AI",
            "data analysis": "Data Analysis", "excel": "Excel",
            "power bi": "Power BI", "tableau": "Tableau", "sap": "SAP",
        }
        found = set()
        text_lower = text.lower()
        for key, label in skill_title_map.items():
            if key in text_lower:
                found.add(label)
        return sorted(found)

    def extract_education(self, text: str) -> List[str]:
        edu_keywords = [
            "sarjana", "bachelor", "master", "diploma", "sma", "smk", "s1", "s2", "d3",
            "university", "universitas", "institute", "sekolah", "pendidikan", "education",
            "vocational", "politeknik", "academy", "akademi", "phd", "doctor",
        ]
        lines = text.split("\n")
        edu_info = []
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(kw in line_lower for kw in edu_keywords):
                context = line.strip()
                if i + 1 < len(lines):
                    context += " " + lines[i + 1].strip()
                edu_info.append(context)
        return edu_info[:5]

    def extract_experience_years(self, text: str) -> int:
        date_patterns = re.findall(r'(19|20)\d{2}\s*[-–to]+\s*((19|20)\d{2}|sekarang|present|saat ini)', text.lower())
        years = set()
        for match in date_patterns:
            year = int(match[0])
            years.add(year)
        if not years:
            year_matches = re.findall(r'(19|20)\d{2}', text)
            for y in year_matches:
                years.add(int(y))
        return len(years) if years else 0

    def extract_education_level(self, text: str) -> str:
        text_lower = text.lower()
        if any(kw in text_lower for kw in ["phd", "doctor", "s3"]):
            return "Doctorate"
        if any(kw in text_lower for kw in ["master", "s2", "magister"]):
            return "Master"
        if any(kw in text_lower for kw in ["bachelor", "sarjana", "s1"]):
            return "Bachelor"
        if any(kw in text_lower for kw in ["diploma", "d3", "d4"]):
            return "Diploma"
        if any(kw in text_lower for kw in ["sma", "smk", "high school", "sekolah"]):
            return "High School"
        return "Unknown"

    def extract_experience_details(self, text: str) -> List[str]:
        exp_lines = []
        keywords = ["experience", "pengalaman", "bekerja", "work", "career", "karier",
                    "riwayat", "professional", "employment", "pekerjaan"]
        lines = text.split("\n")
        capture = False
        for line in lines:
            if any(kw in line.lower() for kw in keywords):
                capture = True
            if capture and line.strip():
                exp_lines.append(line.strip())
            if capture and ("education" in line.lower() or "pendidikan" in line.lower()):
                break
        return exp_lines[:20]

    def extract_languages(self, text: str) -> List[str]:
        lang_map = {
            "bahasa indonesia": "Indonesian", "english": "English", "indonesian": "Indonesian",
            "inggris": "English", "japanese": "Japanese", "mandarin": "Mandarin",
            "jepang": "Japanese", "china": "Mandarin", "arab": "Arabic",
            "belanda": "Dutch", "prancis": "French", "jerman": "German",
            "korea": "Korean",
        }
        found = []
        text_lower = text.lower()
        for keyword, lang_name in lang_map.items():
            if keyword in text_lower and lang_name not in found:
                found.append(lang_name)
        return found

    def compute_experience_score(self, text: str) -> float:
        years_pattern = re.findall(r'(\d+)\s*(tahun|year|thn|th|\+?\s*years?)', text.lower())
        total_years = 0
        for num, unit in years_pattern:
            total_years += int(num)
        return min(total_years / 10.0, 1.0)

    def parse(self, path: str) -> Dict:
        text = self.extract_text(path)
        filename = os.path.basename(path)

        return {
            "filename": filename,
            "filetype": os.path.splitext(path)[1].lower(),
            "name": self.extract_name(text),
            "email": self.extract_email(text),
            "phone": self.extract_phone(text),
            "linkedin": self.extract_linkedin(text),
            "skills": self.extract_skills(text),
            "education": self.extract_education(text),
            "education_level": self.extract_education_level(text),
            "languages": self.extract_languages(text),
            "experience_years_est": self.extract_experience_years(text),
            "experience_score": self.compute_experience_score(text),
            "experience_details": self.extract_experience_details(text),
            "raw_text": text,
        }

    def batch_parse(self, folder_path: str) -> List[Dict]:
        results = []
        supported = {".pdf", ".docx"}
        for fname in sorted(os.listdir(folder_path)):
            if fname.lower() == "vacancy.pdf":
                continue
            ext = os.path.splitext(fname)[1].lower()
            if ext in supported:
                fpath = os.path.join(folder_path, fname)
                try:
                    data = self.parse(fpath)
                    results.append(data)
                except Exception as e:
                    results.append({
                        "filename": fname,
                        "name": f"[ERROR: {e}]",
                        "email": None, "phone": None, "skills": [],
                        "education": [], "raw_text": "",
                    })
        return results
