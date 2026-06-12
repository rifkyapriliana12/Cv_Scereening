import pdfplumber
import re
from typing import Dict, List

class VacancyParser:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.text = self._extract_text()
        self.requirements = self._parse_requirements()
        self.responsibilities = self._parse_responsibilities()
        self.job_title = self._parse_job_title()

    def _extract_text(self) -> str:
        text = ""
        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text

    def _parse_job_title(self) -> str:
        lines = self.text.strip().split("\n")
        return lines[0].strip() if lines else "Unknown Position"

    def _parse_requirements(self) -> List[str]:
        reqs = []
        capture = False
        for line in self.text.split("\n"):
            if "REQUIREMENTS" in line.upper():
                capture = True
                continue
            if "RESPONSIBILITIES" in line.upper():
                capture = False
                continue
            if capture and line.strip():
                req = line.strip().lstrip("•-*◆").strip()
                if req:
                    reqs.append(req)
        return reqs

    def _parse_responsibilities(self) -> List[str]:
        resp = []
        capture = False
        for line in self.text.split("\n"):
            if "RESPONSIBILITIES" in line.upper():
                capture = True
                continue
            if capture and line.strip():
                r = line.strip().lstrip("•-*◆").strip()
                if r:
                    resp.append(r)
        return resp

    def get_requirements_text(self) -> str:
        return " ".join(self.requirements)

    def get_full_text(self) -> str:
        return self.text

    def to_dict(self) -> Dict:
        return {
            "job_title": self.job_title,
            "requirements": self.requirements,
            "responsibilities": self.responsibilities,
        }
