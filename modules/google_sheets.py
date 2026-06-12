import os
import json
from typing import Dict, List, Optional
from datetime import datetime

class GoogleSheetsManager:
    def __init__(self, credentials_path: str = "", sheet_id: str = ""):
        self.credentials_path = credentials_path
        self.sheet_id = sheet_id
        self.client = None

    def _auth(self):
        if not self.credentials_path or not os.path.exists(self.credentials_path):
            raise FileNotFoundError(
                f"Google Sheets credentials not found at: {self.credentials_path}\n"
                "Download service account JSON from Google Cloud Console."
            )
        import gspread
        from google.oauth2.service_account import Credentials
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = Credentials.from_service_account_file(self.credentials_path, scopes=scopes)
        self.client = gspread.authorize(creds)

    def upload_results(self, ranked_results: List[tuple], sheet_title: str = "CV Screening Results"):
        if not self.client:
            self._auth()
        if not self.sheet_id:
            spreadsheet = self.client.create(sheet_title)
            self.sheet_id = spreadsheet.id
            print(f"[GSHEETS] Created new spreadsheet ID: {self.sheet_id}")
        else:
            spreadsheet = self.client.open_by_key(self.sheet_id)

        sheet = spreadsheet.sheet1
        sheet.clear()

        headers = [
            "Rank", "Nama", "Email", "Phone", "Total Score (%)",
            "Semantic Score", "Skills Match", "Keyword Match", "Experience Score",
            "Skills", "Pendidikan", "Status", "Timestamp"
        ]
        sheet.append_row(headers)

        rows = []
        for i, (cv_data, scores) in enumerate(ranked_results, 1):
            status = "Lolos" if scores["total_score"] >= 50 else "Tidak Lolos"
            rows.append([
                i,
                cv_data.get("name", "Unknown"),
                cv_data.get("email", "-"),
                cv_data.get("phone", "-"),
                scores["total_score"],
                scores["semantic_score"],
                scores["skill_match_score"],
                scores["keyword_match_score"],
                scores["experience_score"],
                ", ".join(cv_data.get("skills", [])[:8]),
                cv_data.get("education_level", "N/A"),
                status,
                datetime.now().strftime("%Y-%m-%d %H:%M"),
            ])

        if rows:
            sheet.append_rows(rows)

        print(f"[GSHEETS] Uploaded {len(rows)} rows to spreadsheet: {spreadsheet.url}")
        return spreadsheet.url

    def save_to_local_json(self, ranked_results: List[tuple], output_path: str = ""):
        if not output_path:
            output_path = os.path.join(os.path.dirname(__file__), "..", "data", "output")
        os.makedirs(output_path, exist_ok=True)

        data = []
        for i, (cv_data, scores) in enumerate(ranked_results, 1):
            data.append({
                "rank": i,
                "name": cv_data.get("name"),
                "email": cv_data.get("email"),
                "phone": cv_data.get("phone"),
                "total_score": scores["total_score"],
                "semantic_score": scores["semantic_score"],
                "skill_match_score": scores["skill_match_score"],
                "keyword_match_score": scores["keyword_match_score"],
                "experience_score": scores["experience_score"],
                "skills": cv_data.get("skills", []),
                "education_level": cv_data.get("education_level", ""),
                "status": "Lolos" if scores["total_score"] >= 50 else "Tidak Lolos",
                "timestamp": datetime.now().isoformat(),
            })

        filepath = os.path.join(output_path, "google_sheets_backup.json")
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"[GSHEETS] Backup saved to {filepath}")
        return filepath

    def set_credentials(self, cred_path: str, sheet_id: str = ""):
        self.credentials_path = cred_path
        self.sheet_id = sheet_id
