import os
import json
import re
from typing import Dict, List, Optional
from datetime import datetime

class AIExtractor:
    def __init__(self, api_key: str = "", provider: str = "gemini"):
        self.api_key = api_key
        self.provider = provider
        self.client = None

    def _init_gemini(self):
        try:
            from google import genai
            self.client = genai.Client(api_key=self.api_key)
        except ImportError:
            raise ImportError("google-genai not installed. Run: pip install google-genai")

    def _init_openai(self):
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("openai not installed. Run: pip install openai")

    def extract_with_ai(self, cv_text: str, cv_filename: str = "") -> Dict:
        if not self.api_key:
            return self._fallback_extraction(cv_text, cv_filename)

        if self.provider == "gemini":
            return self._extract_gemini(cv_text, cv_filename)
        elif self.provider in ("openai", "chatgpt"):
            return self._extract_openai(cv_text, cv_filename)
        else:
            return self._fallback_extraction(cv_text, cv_filename)

    def _extract_gemini(self, cv_text: str, cv_filename: str) -> Dict:
        self._init_gemini()
        prompt = f"""Extract information from this CV/resume in JSON format. Return ONLY valid JSON.

CV Text:
{cv_text[:3000]}

Return this exact JSON structure:
{{
  "name": "Full Name",
  "email": "email@example.com",
  "phone": "phone number",
  "linkedin": "linkedin url or empty string",
  "skills": ["skill1", "skill2", ...],
  "education_level": "Bachelor/Master/Doctorate/Diploma/High School/Unknown",
  "education_details": "brief education info",
  "total_experience_years": number,
  "languages": ["language1", ...],
  "certifications": ["cert1", ...],
  "current_position": "current job title or empty",
  "summary": "brief professional summary"
}}
"""
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
            )
            text = response.text.strip()
            text = re.sub(r'^```(?:json)?\s*', '', text)
            text = re.sub(r'\s*```$', '', text)
            return json.loads(text)
        except Exception as e:
            print(f"[AI] Gemini extraction error: {e}")
            return self._fallback_extraction(cv_text, cv_filename)

    def _extract_openai(self, cv_text: str, cv_filename: str) -> Dict:
        self._init_openai()
        prompt = f"""Extract information from this CV/resume in JSON format. Return ONLY valid JSON.

CV Text:
{cv_text[:3000]}

Return this exact JSON structure:
{{
  "name": "Full Name",
  "email": "email@example.com",
  "phone": "phone number",
  "linkedin": "linkedin url or empty string",
  "skills": ["skill1", "skill2", ...],
  "education_level": "Bachelor/Master/Doctorate/Diploma/High School/Unknown",
  "education_details": "brief education info",
  "total_experience_years": number,
  "languages": ["language1", ...],
  "certifications": ["cert1", ...],
  "current_position": "current job title or empty",
  "summary": "brief professional summary"
}}
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
            )
            text = response.choices[0].message.content.strip()
            text = re.sub(r'^```(?:json)?\s*', '', text)
            text = re.sub(r'\s*```$', '', text)
            return json.loads(text)
        except Exception as e:
            print(f"[AI] OpenAI extraction error: {e}")
            return self._fallback_extraction(cv_text, cv_filename)

    def _fallback_extraction(self, cv_text: str, cv_filename: str) -> Dict:
        lines = cv_text.split("\n")
        name = "Unknown"
        for line in lines[:10]:
            line = line.strip()
            if line and len(line.split()) <= 4 and not re.match(r'^[\d\s\+\-\(\)]+$', line):
                name = line
                break

        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', cv_text)
        email = email_match.group(0) if email_match else ""

        phone_match = re.search(r'(\+?[\d\s\-\(\)]{7,20})', cv_text)
        phone = phone_match.group(0).strip() if phone_match else ""

        linkedin_match = re.search(r'(https?://)?(www\.)?linkedin\.com/in/[\w\-/]+', cv_text)
        linkedin = linkedin_match.group(0) if linkedin_match else ""

        skill_keywords = [
            "autocad", "sketchup", "revit", "lumion", "enscape", "photoshop",
            "python", "java", "javascript", "sql", "machine learning",
            "microsoft office", "project management", "cad",
        ]
        skills = []
        cv_lower = cv_text.lower()
        for skill in skill_keywords:
            if skill in cv_lower:
                skills.append(skill.title())

        edu_level = "Unknown"
        if any(kw in cv_lower for kw in ["phd", "doctor", "s3"]):
            edu_level = "Doctorate"
        elif any(kw in cv_lower for kw in ["master", "s2", "magister"]):
            edu_level = "Master"
        elif any(kw in cv_lower for kw in ["bachelor", "sarjana", "s1"]):
            edu_level = "Bachelor"
        elif any(kw in cv_lower for kw in ["diploma", "d3", "d4"]):
            edu_level = "Diploma"
        elif any(kw in cv_lower for kw in ["sma", "smk", "high school"]):
            edu_level = "High School"

        exp_years = 0
        year_pattern = re.findall(r'(\d+)\s*(tahun|year|thn|th|\+?\s*years?)', cv_lower)
        for num, unit in year_pattern:
            exp_years += int(num)

        return {
            "name": name,
            "email": email,
            "phone": phone,
            "linkedin": linkedin,
            "skills": skills,
            "education_level": edu_level,
            "education_details": "",
            "total_experience_years": exp_years,
            "languages": [],
            "certifications": [],
            "current_position": "",
            "summary": cv_text[:200].replace("\n", " "),
        }

    def batch_extract(self, cv_data_list: List[Dict]) -> List[Dict]:
        enriched = []
        for cv_data in cv_data_list:
            raw_text = cv_data.get("raw_text", "")
            filename = cv_data.get("filename", "")
            ai_data = self.extract_with_ai(raw_text, filename)
            enriched.append({**cv_data, **ai_data})
        return enriched
