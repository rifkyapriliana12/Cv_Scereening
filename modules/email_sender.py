import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from typing import Dict, List, Optional
import json
import os
from datetime import datetime

class EmailSender:
    def __init__(self, smtp_server: str = "", smtp_port: int = 587,
                 sender_email: str = "", sender_password: str = ""):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password

    def send_summary(self, recipient_email: str, results: List[Dict],
                     selected_cv_folder: str = "") -> bool:
        if not all([self.smtp_server, self.sender_email, self.sender_password]):
            print("[EMAIL SIMULATED] SMTP not configured. Summary saved to logs.")
            self._save_summary_log(results)
            return True

        try:
            msg = MIMEMultipart()
            msg["From"] = self.sender_email
            msg["To"] = recipient_email
            msg["Subject"] = "[Automated] CV Screening Results Summary"

            html = self._build_html(results)
            msg.attach(MIMEText(html, "html"))

            if selected_cv_folder and os.path.exists(selected_cv_folder):
                for f in os.listdir(selected_cv_folder):
                    fpath = os.path.join(selected_cv_folder, f)
                    if os.path.isfile(fpath):
                        with open(fpath, "rb") as attachment:
                            part = MIMEBase("application", "octet-stream")
                            part.set_payload(attachment.read())
                            encoders.encode_base64(part)
                            part.add_header("Content-Disposition",
                                            f"attachment; filename={f}")
                            msg.attach(part)

            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(msg)

            print(f"[EMAIL] Summary sent to {recipient_email}")
            return True

        except Exception as e:
            print(f"[EMAIL ERROR] {e}")
            self._save_summary_log(results)
            return False

    def _build_html(self, results: List[Dict]) -> str:
        rows = ""
        for i, (cv_data, scores) in enumerate(results, 1):
            rows += f"""
            <tr>
                <td>{i}</td>
                <td>{cv_data.get('name', 'Unknown')}</td>
                <td>{cv_data.get('email', 'N/A')}</td>
                <td>{scores.get('total_score', 0)}%</td>
                <td>{', '.join(cv_data.get('skills', [])[:5])}</td>
                <td>{"✓ Lolos" if scores.get('total_score', 0) >= 50 else "✗ Tidak"}</td>
            </tr>"""

        return f"""
        <html>
        <head><style>
            table {{ border-collapse: collapse; width: 100%; font-family: Arial; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #2c3e50; color: white; }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
        </style></head>
        <body>
            <h2>Daily CV Screening Report</h2>
            <p>Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
            <table>
                <tr><th>Rank</th><th>Name</th><th>Email</th><th>Score</th><th>Top Skills</th><th>Status</th></tr>
                {rows}
            </table>
        </body></html>
        """

    def _save_summary_log(self, results: List[Dict]):
        log_dir = os.path.join(os.path.dirname(__file__), "..", "data", "output")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "email_summary_log.json")
        data = {
            "timestamp": datetime.now().isoformat(),
            "results": [
                {
                    "name": r[0].get("name"),
                    "score": r[1].get("total_score"),
                    "email": r[0].get("email"),
                }
                for r in results
            ],
        }
        with open(log_file, "w") as f:
            json.dump(data, f, indent=2)
        print(f"[EMAIL LOG] Saved to {log_file}")
