import streamlit as st
import os
import pandas as pd
from datetime import datetime
import shutil
import json
from functools import partial

from modules.cv_parser import CVParser
from modules.vacancy_parser import VacancyParser
from modules.email_sender import EmailSender
from modules.google_sheets import GoogleSheetsManager
from modules.scheduler import Scheduler

st.set_page_config(
    page_title="CV Screening Agent - Allure Industries",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data", "cv_samples")
OUTPUT_DIR = os.path.join(BASE_DIR, "data", "output")
VACANCY_PATH = os.path.join(DATA_DIR, "Vacancy.pdf")
SELECTED_DIR = os.path.join(BASE_DIR, "output", "selected_cvs")
SCRAPED_DIR = os.path.join(BASE_DIR, "data", "scraped_cvs")
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(SELECTED_DIR, exist_ok=True)
os.makedirs(SCRAPED_DIR, exist_ok=True)

JOBS_PATH = os.path.join(BASE_DIR, "jobs.json")

def load_jobs():
    default = [{"title": "Junior Architect", "requirements": ["Degree in architecture or related field"], "responsibilities": [], "active": True}]
    if os.path.exists(JOBS_PATH):
        with open(JOBS_PATH, encoding="utf-8-sig") as f:
            return json.load(f)
    return default

def save_jobs(jobs):
    with open(JOBS_PATH, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2, ensure_ascii=False)

def load_config():
    default = {
        "google_sheets_credentials": "",
        "google_sheet_id": "",
        "ai_api_key": "",
        "ai_provider": "gemini",
        "openai_api_key": "",
        "smtp_server": "",
        "smtp_port": 587,
        "smtp_email": "",
        "smtp_password": "",
        "hc_email": "hc@allure-industries.com",
        "jobstreet_email": "",
        "jobstreet_password": "",
        "glints_email": "",
        "glints_password": "",
    }
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH) as f:
            return {**default, **json.load(f)}
    return default

def save_config(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)

@st.cache_resource
def load_models():
    from modules.matcher import CVMatcher
    return CVMatcher()

@st.cache_data
def load_vacancy():
    if os.path.exists(VACANCY_PATH):
        return VacancyParser(VACANCY_PATH)
    return None

def process_all_cvs():
    parser = CVParser()
    cv_files = sorted([
        f for f in os.listdir(DATA_DIR)
        if f.lower().endswith((".pdf", ".docx")) and f.lower() != "vacancy.pdf"
    ])
    results = []
    for fname in cv_files:
        fpath = os.path.join(DATA_DIR, fname)
        try:
            data = parser.parse(fpath)
            results.append(data)
        except Exception as e:
            st.warning(f"Gagal parse {fname}: {e}")
    return results

def run_screening(config, job=None):
    if job is None:
        vacancy = load_vacancy()
        if not vacancy:
            st.error("Tidak ada job vacancy! Buat job dulu di menu Job Editor.")
            return
        req_text = vacancy.get_requirements_text()
        job_title = vacancy.job_title
    else:
        req_text = " ".join(job.get("requirements", []))
        job_title = job.get("title", "Unknown")

    cv_data_list = process_all_cvs()
    if not cv_data_list:
        st.warning("Tidak ada CV (PDF/DOCX) ditemukan!")
        return

    matcher = load_models()

    provider = config.get("ai_provider", "gemini")
    api_key = config.get("openai_api_key", "") if provider == "openai" else config.get("ai_api_key", "")
    use_ai = api_key and st.session_state.get("use_ai", False)
    if use_ai:
        with st.spinner("AI Extraction in progress..."):
            from modules.ai_extractor import AIExtractor
            ai_extractor = AIExtractor(api_key=api_key, provider=provider)
            cv_data_list = ai_extractor.batch_extract(cv_data_list)
            st.info("✅ AI extraction selesai")

    ranked = matcher.rank_candidates(cv_data_list, req_text)

    st.session_state["job_title"] = job_title
    st.session_state["results"] = cv_data_list
    st.session_state["ranked"] = ranked

    for f in os.listdir(SELECTED_DIR):
        fpath = os.path.join(SELECTED_DIR, f)
        if os.path.isfile(fpath):
            os.remove(fpath)

    for cv_data, scores in ranked:
        if scores["total_score"] >= 50:
            src = os.path.join(DATA_DIR, cv_data["filename"])
            dst = os.path.join(SELECTED_DIR, cv_data["filename"])
            if os.path.exists(src):
                shutil.copy2(src, dst)

    emailer = EmailSender(
        smtp_server=config.get("smtp_server", ""),
        smtp_port=config.get("smtp_port", 587),
        sender_email=config.get("smtp_email", ""),
        sender_password=config.get("smtp_password", ""),
    )
    emailer.send_summary(config.get("hc_email", "hc@allure-industries.com"), ranked, SELECTED_DIR)

    gs_cred = config.get("google_sheets_credentials", "")
    if gs_cred and os.path.exists(gs_cred):
        try:
            gs = GoogleSheetsManager(credentials_path=gs_cred, sheet_id=config.get("google_sheet_id", ""))
            url = gs.upload_results(ranked)
            st.success(f"✅ Google Sheets updated: {url}")
        except Exception as e:
            st.warning(f"Google Sheets upload skipped: {e}")
    else:
        gs = GoogleSheetsManager()
        gs.save_to_local_json(ranked)

    return ranked

def page_dashboard(config):
    st.title("📄 CV Screening Agent")
    st.markdown("**Allure Industries - Workshop Cibitung**")
    st.caption(f"Last run: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    vacancy = load_vacancy()
    cv_count = len([f for f in os.listdir(DATA_DIR)
                   if f.lower().endswith((".pdf", ".docx")) and f.lower() != "vacancy.pdf"])
    scraped_count = len([f for f in os.listdir(SCRAPED_DIR) if os.path.isfile(os.path.join(SCRAPED_DIR, f))])

    jobs = load_jobs()
    active_job = next((j for j in jobs if j.get("active")), jobs[0] if jobs else None)
    job_title = active_job["title"] if active_job else (vacancy.job_title if vacancy else "-")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total CV", f"{cv_count} files", help="CV di folder data/cv_samples/")
    with col2:
        st.metric("Posisi", job_title)
    with col3:
        st.metric("Threshold", "≥ 50%")
    with col4:
        st.metric("Scraped", f"{scraped_count} files")

    st.divider()

    col_a, col_b, col_c, col_d, col_e, col_f = st.columns(6)
    steps = [
        ("📂", "Load CVs"), ("📝", "Parse"), ("🤖", "AI Extract"),
        ("🔗", "Match"), ("📊", "Score"), ("🏆", "Rank")
    ]
    for i, (icon, label) in enumerate(steps):
        with [col_a, col_b, col_c, col_d, col_e, col_f][i]:
            st.success(f"{icon} {label}")

    if st.button("🚀 **Jalankan Full Screening**", type="primary", use_container_width=True):
        with st.spinner("Full pipeline running..."):
            result = run_screening(config, job=active_job)
            if result:
                st.success(f"✅ Screening selesai! {len(result)} CV diproses untuk posisi '{job_title}'.")
                st.balloons()

    if "ranked" in st.session_state and st.session_state["ranked"]:
        ranked = st.session_state["ranked"]
        lolos = sum(1 for _, s in ranked if s["total_score"] >= 50)
        st.divider()
        st.subheader("🏆 Hasil Terakhir")
        rows = []
        for i, (cv_data, scores) in enumerate(ranked, 1):
            status = "✅ Lolos" if scores["total_score"] >= 50 else "❌ Tidak"
            rows.append({
                "Rank": i, "Nama": cv_data.get("name", "Unknown"),
                "Total": f"{scores['total_score']:.1f}%",
                "Skills": ", ".join(cv_data.get("skills", [])[:3]),
                "Status": status,
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.info(f"📁 {lolos} CV lolos tersimpan di output/selected_cvs/")
    else:
        st.info("👈 Klik 'Jalankan Full Screening' untuk memulai")

def page_screening(config):
    st.title("📄 Screening Pipeline")

    jobs = load_jobs()
    active_job = next((j for j in jobs if j.get("active")), jobs[0] if jobs else None)
    vacancy = load_vacancy()

    if active_job:
        with st.container(border=True):
            st.subheader(f"📋 {active_job['title']} 🟢 Active")
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                st.markdown("**Requirements:**")
                for req in active_job.get("requirements", []):
                    st.markdown(f"- {req}")
            with col_r2:
                st.markdown("**Responsibilities:**")
                for resp in active_job.get("responsibilities", []):
                    st.markdown(f"- {resp}")
            st.caption("Job ini bisa diedit di menu **Job Editor**")
    elif vacancy:
        with st.container(border=True):
            st.subheader(f"📋 {vacancy.job_title} (dari Vacancy.pdf)")
            col_r1, col_r2 = st.columns(2)
            with col_r1:
                st.markdown("**Requirements:**")
                for req in vacancy.requirements:
                    st.markdown(f"- {req}")
            with col_r2:
                st.markdown("**Responsibilities:**")
                for resp in vacancy.responsibilities:
                    st.markdown(f"- {resp}")

    if st.button("🚀 **Jalankan Screening**", type="primary", use_container_width=True):
        with st.spinner("Memproses..."):
            run_screening(config, job=active_job)
            st.success("✅ Selesai!")
            st.balloons()

    if "ranked" in st.session_state and st.session_state["ranked"]:
        ranked = st.session_state["ranked"]
        st.subheader("🏆 Hasil Ranking Kandidat")
        rows = []
        for i, (cv_data, scores) in enumerate(ranked, 1):
            status = "✅ Lolos" if scores["total_score"] >= 50 else "❌ Tidak"
            rows.append({
                "Rank": i, "Nama": cv_data.get("name", "Unknown"),
                "Email": cv_data.get("email", "-"),
                "Total": f"{scores['total_score']:.1f}%",
                "Semantic": f"{scores['semantic_score']:.1f}%",
                "Skills Match": f"{scores['skill_match_score']:.1f}%",
                "Keyword": f"{scores['keyword_match_score']:.1f}%",
                "Experience": f"{scores['experience_score']:.1f}%",
                "Top Skills": ", ".join(cv_data.get("skills", [])[:4]),
                "Status": status,
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

        for i, (cv_data, scores) in enumerate(ranked, 1):
            status = "✅ Lolos" if scores["total_score"] >= 50 else "❌ Tidak"
            with st.expander(f"{i}. {cv_data.get('name', 'Unknown')} - {scores['total_score']:.1f}% - {status}"):
                col_a1, col_a2 = st.columns(2)
                with col_a1:
                    st.markdown(f"**Email:** {cv_data.get('email', '-')}")
                    st.markdown(f"**Phone:** {cv_data.get('phone', '-')}")
                    st.markdown(f"**Pendidikan:** {cv_data.get('education_level', 'N/A')}")
                with col_a2:
                    st.markdown("**Keahlian:**")
                    for skill in cv_data.get("skills", []):
                        st.markdown(f"- {skill}")

                col_s1, col_s2, col_s3, col_s4 = st.columns(4)
                with col_s1: st.metric("Semantic", f"{scores['semantic_score']:.1f}%")
                with col_s2: st.metric("Skills", f"{scores['skill_match_score']:.1f}%")
                with col_s3: st.metric("Keyword", f"{scores['keyword_match_score']:.1f}%")
                with col_s4: st.metric("Experience", f"{scores['experience_score']:.1f}%")

                reasons = []
                if scores["semantic_score"] >= 60: reasons.append("✅ Semantic cocok dengan requirement")
                elif scores["semantic_score"] < 30: reasons.append("⚠️ Semantic kurang cocok")
                if scores["skill_match_score"] >= 50: reasons.append("✅ Skills relevan")
                else: reasons.append("⚠️ Skills perlu ditingkatkan")
                if scores["experience_score"] >= 50: reasons.append("✅ Pengalaman memadai")
                else: reasons.append("⚠️ Pengalaman masih kurang")
                if scores["total_score"] >= 50: reasons.append("🎯 **Rekomendasi: LANJUT ke Interview**")
                else: reasons.append("📌 **Rekomendasi: TIDAK Lolos seleksi**")
                st.markdown("**Analisis:**")
                for r in reasons:
                    st.markdown(f"- {r}")

        st.divider()
        col_d1, col_d2, col_d3 = st.columns(3)
        with col_d1:
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Download CSV", csv,
                f"cv_screening_results_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                "text/csv", use_container_width=True)
        with col_d2:
            selected_count = sum(1 for _, s in ranked if s["total_score"] >= 50)
            st.info(f"📁 {selected_count} CV tersimpan di selected_cvs/")
        with col_d3:
            if st.button("📧 Kirim Email ke HC", use_container_width=True):
                emailer = EmailSender(
                    smtp_server=config.get("smtp_server", ""),
                    smtp_port=config.get("smtp_port", 587),
                    sender_email=config.get("smtp_email", ""),
                    sender_password=config.get("smtp_password", ""),
                )
                emailer.send_summary(config.get("hc_email", ""), ranked, SELECTED_DIR)
                st.success("✅ Email terkirim (atau tersimpan di log)!")

def page_scraper(config):
    st.title("🕷️ RPA - Download CV dari Employer Portal")
    st.markdown("""
    **Cara kerja:**
    1. Login ke akun **Employer** Jobstreet/Glints (via Playwright)
    2. Cari kandidat berdasarkan keyword
    3. Buka profil kandidat → download CV (PDF) + simpan data profil
    4. CV siap diproses di menu **Screening**
    """)

    js_email = config.get("jobstreet_email", "")
    js_pass = config.get("jobstreet_password", "")
    gl_email = config.get("glints_email", "")
    gl_pass = config.get("glints_password", "")

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.markdown(f"**Jobstreet:** {'✅ Siap' if js_email else '❌ Login belum diatur'}")
        if js_email:
            st.caption(f"Email: {js_email}")
    with col_s2:
        st.markdown(f"**Glints:** {'✅ Siap' if gl_email else '❌ Login belum diatur'}")
        if gl_email:
            st.caption(f"Email: {gl_email}")

    if not js_email and not gl_email:
        st.warning("Belum ada login employer! Masukkan email & password di **Settings → Scraper**")

    with st.container(border=True):
        col_k1, col_k2 = st.columns([3, 1])
        with col_k1:
            keyword = st.text_input("Keyword Pencarian Kandidat", value="architect", key="scrape_kw")
        with col_k2:
            max_cvs = st.number_input("Max CV", min_value=1, max_value=20, value=3, key="scrape_max")

        col_b1, col_b2, col_b3 = st.columns(3)
        with col_b1:
            if st.button("🕸️ **Jobstreet - Cari & Download CV**", use_container_width=True, disabled=not js_email):
                with st.spinner(f"Logging in as employer, searching '{keyword}'..."):
                    from modules.web_scraper import JobPortalScraper
                    scraper = JobPortalScraper(download_dir=SCRAPED_DIR, config=config)
                    files = scraper.scrape_jobstreet(keyword, max_cvs)
                    if files:
                        st.success(f"✅ Berhasil download {len(files)} CV/profile!")
                        for f in files:
                            st.code(os.path.basename(f))
                    else:
                        st.warning("Tidak ada CV terdownload. Cek login/koneksi/screenshot di folder scraped_cvs/.")

        with col_b2:
            if st.button("🕸️ **Glints - Cari & Download CV**", use_container_width=True, disabled=not gl_email):
                with st.spinner(f"Logging in as employer, searching '{keyword}'..."):
                    from modules.web_scraper import JobPortalScraper
                    scraper = JobPortalScraper(download_dir=SCRAPED_DIR, config=config)
                    files = scraper.scrape_glints(keyword, max_cvs)
                    if files:
                        st.success(f"✅ Berhasil download {len(files)} CV/profile!")
                        for f in files:
                            st.code(os.path.basename(f))
                    else:
                        st.warning("Tidak ada CV terdownload. Cek login/koneksi/screenshot di folder scraped_cvs/.")

        with col_b3:
            if st.button("📂 **Refresh File List**", use_container_width=True):
                from modules.web_scraper import JobPortalScraper
                scraper = JobPortalScraper(download_dir=SCRAPED_DIR)
                files = scraper.get_downloaded_files()
                if files:
                    st.write(f"**{len(files)} file terdownload:**")
                    for f in files:
                        fsize = os.path.getsize(f)
                        st.text(f"  📄 {os.path.basename(f)} ({fsize:,} bytes)")
                else:
                    st.info("Belum ada file hasil scraping")

    with st.container(border=True):
        st.subheader("📁 Scraped Files")
        from modules.web_scraper import JobPortalScraper
        scraper = JobPortalScraper(download_dir=SCRAPED_DIR)
        files = scraper.get_downloaded_files()
        if files:
            data = []
            for f in files:
                fsize = os.path.getsize(f)
                mtime = datetime.fromtimestamp(os.path.getmtime(f)).strftime("%Y-%m-%d %H:%M")
                data.append({"File": os.path.basename(f), "Size": f"{fsize:,} bytes", "Modified": mtime})
            st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada file, jalankan scraping terlebih dahulu.")

def page_job_editor(config):
    st.title("📋 Job Editor")
    st.markdown("Buat dan kelola job vacancy untuk screening CV.")

    jobs = load_jobs()

    with st.container(border=True):
        st.subheader("➕ Buat Job Baru")
        with st.form("new_job_form"):
            new_title = st.text_input("Nama Posisi", placeholder="Contoh: Senior Engineer")
            new_reqs = st.text_area("Requirements (1 baris per item)", height=120,
                placeholder="Degree in ...\nMin 2 years experience ...\nSkill: AutoCAD, Revit ...")
            new_resps = st.text_area("Responsibilities (1 baris per item)", height=100,
                placeholder="Membuat design ...\nMengawasi proyek ...")
            if st.form_submit_button("💾 Simpan Job Baru", type="primary"):
                if new_title.strip():
                    reqs = [r.strip() for r in new_reqs.strip().split("\n") if r.strip()]
                    resps = [r.strip() for r in new_resps.strip().split("\n") if r.strip()]
                    for j in jobs:
                        j["active"] = False
                    jobs.append({
                        "title": new_title.strip(),
                        "requirements": reqs,
                        "responsibilities": resps,
                        "active": True,
                    })
                    save_jobs(jobs)
                    st.success(f"✅ Job '{new_title}' tersimpan!")
                    st.rerun()
                else:
                    st.warning("Nama posisi wajib diisi.")

    st.divider()
    st.subheader("📋 Daftar Job")

    if not jobs:
        st.info("Belum ada job. Buat job baru di atas.")
        return

    for i, job in enumerate(jobs):
        with st.container(border=True):
            col_j1, col_j2, col_j3 = st.columns([6, 1, 1])
            with col_j1:
                status = "🟢 Active" if job.get("active") else "⚪ Inactive"
                st.markdown(f"**{job['title']}** - {status}")
                st.caption(f"{len(job.get('requirements', []))} requirements, {len(job.get('responsibilities', []))} responsibilities")
            with col_j2:
                if not job.get("active"):
                    if st.button("✅ Set Active", key=f"act_{i}"):
                        for j in jobs:
                            j["active"] = False
                        jobs[i]["active"] = True
                        save_jobs(jobs)
                        st.rerun()
            with col_j3:
                if st.button("🗑️ Hapus", key=f"del_{i}"):
                    jobs.pop(i)
                    if jobs:
                        jobs[0]["active"] = True
                    save_jobs(jobs)
                    st.rerun()

            with st.expander(f"📝 Lihat Detail", key=f"detail_{i}"):
                new_title = st.text_input("Nama Posisi", value=job["title"], key=f"etitle_{i}")
                new_reqs = st.text_area("Requirements", value="\n".join(job.get("requirements", [])),
                    height=100, key=f"ereqs_{i}")
                new_resps = st.text_area("Responsibilities", value="\n".join(job.get("responsibilities", [])),
                    height=80, key=f"eresps_{i}")
                if st.button("💾 Update", key=f"upd_{i}"):
                    jobs[i]["title"] = new_title
                    jobs[i]["requirements"] = [r.strip() for r in new_reqs.strip().split("\n") if r.strip()]
                    jobs[i]["responsibilities"] = [r.strip() for r in new_resps.strip().split("\n") if r.strip()]
                    save_jobs(jobs)
                    st.success(f"✅ Job '{new_title}' updated!")
                    st.rerun()

def page_settings(config):
    st.title("⚙️ Settings")
    tabs = st.tabs(["🤖 AI Settings", "📊 Google Sheets", "📧 Email SMTP", "⏰ Scheduler", "🕷️ Scraper"])

    with tabs[0]:
        st.subheader("AI Provider")
        config["ai_provider"] = st.selectbox(
            "Pilih AI Provider", ["gemini", "openai"],
            index=0 if config.get("ai_provider", "gemini") == "gemini" else 1,
            label_visibility="collapsed",
        )
        col_k1, col_k2 = st.columns(2)
        with col_k1:
            config["ai_api_key"] = st.text_input(
                "🔑 Gemini API Key",
                value=config.get("ai_api_key", ""),
                type="password",
                help="Dari https://aistudio.google.com/apikey",
            )
            if config.get("ai_api_key"):
                st.caption("✅ Gemini key tersimpan")
        with col_k2:
            config["openai_api_key"] = st.text_input(
                "🔑 OpenAI API Key",
                value=config.get("openai_api_key", ""),
                type="password",
                help="Dari https://platform.openai.com/api-keys",
            )
            if config.get("openai_api_key"):
                st.caption("✅ OpenAI key tersimpan")

        has_key = bool(config.get("ai_api_key") or config.get("openai_api_key"))
        if has_key:
            st.session_state["use_ai"] = st.checkbox("Gunakan AI untuk extraction CV", value=True)
            provider = config.get("ai_provider", "gemini")
            key_preview = (config.get("openai_api_key", "")[:12] + "..."
                          if provider == "openai" else config.get("ai_api_key", "")[:12] + "...")
            st.info(f"🟢 Active: **{provider.upper()}** - Key: `{key_preview}`")

    with tabs[1]:
        config["google_sheets_credentials"] = st.text_input(
            "Path ke credentials JSON",
            value=config.get("google_sheets_credentials", ""),
            help="Download dari Google Cloud Console → Service Account",
        )
        config["google_sheet_id"] = st.text_input(
            "Google Sheet ID (opsional)",
            value=config.get("google_sheet_id", ""),
            help="Kosongi untuk auto-create spreadsheet baru",
        )
        if config["google_sheets_credentials"] and os.path.exists(config["google_sheets_credentials"]):
            st.success("✅ Credentials file found")

    with tabs[2]:
        config["smtp_server"] = st.text_input("SMTP Server", value=config.get("smtp_server", "smtp.gmail.com"))
        config["smtp_port"] = st.number_input("SMTP Port", value=config.get("smtp_port", 587))
        config["smtp_email"] = st.text_input("Sender Email", value=config.get("smtp_email", ""))
        config["smtp_password"] = st.text_input("SMTP Password", value=config.get("smtp_password", ""), type="password")
        config["hc_email"] = st.text_input("HC Recipient Email", value=config.get("hc_email", "hc@allure-industries.com"))

    with tabs[3]:
        st.info("⏰ **Daily Schedule:** Otomatis berjalan setiap jam 23:59")
        if st.button("▶️ Jalankan Scheduler (Background)"):
            scheduler = Scheduler()
            scheduler.run_daily_at_2359(lambda: run_screening(config))
            scheduler.start()
            st.success("✅ Scheduler started (23:59 daily)")

    with tabs[4]:
        st.subheader("🔑 Employer Login Credentials")
        st.caption("Digunakan oleh RPA untuk login ke portal employer dan download CV kandidat")
        col_sc1, col_sc2 = st.columns(2)
        with col_sc1:
            st.markdown("**Jobstreet Employer**")
            config["jobstreet_email"] = st.text_input(
                "Jobstreet Email", value=config.get("jobstreet_email", ""),
                key="js_email", placeholder="employer@company.com"
            )
            config["jobstreet_password"] = st.text_input(
                "Jobstreet Password", value=config.get("jobstreet_password", ""),
                type="password", key="js_pass"
            )
            if config.get("jobstreet_email"):
                st.success("✅ Jobstreet credentials tersimpan")
        with col_sc2:
            st.markdown("**Glints Employer**")
            config["glints_email"] = st.text_input(
                "Glints Email", value=config.get("glints_email", ""),
                key="gl_email", placeholder="employer@company.com"
            )
            config["glints_password"] = st.text_input(
                "Glints Password", value=config.get("glints_password", ""),
                type="password", key="gl_pass"
            )
            if config.get("glints_email"):
                st.success("✅ Glints credentials tersimpan")

    if st.button("💾 **Save Settings**", type="primary", use_container_width=True):
        save_config(config)
        st.success("✅ Settings saved!")

def main():
    config = load_config()

    st.logo("https://cdn-icons-png.flaticon.com/512/3135/3135715.png")

    menu = st.navigation([
        st.Page(partial(page_dashboard, config), title="Dashboard", url_path="dashboard", icon="🏠", default=True),
        st.Page(partial(page_screening, config), title="Screening", url_path="screening", icon="📄"),
        st.Page(partial(page_job_editor, config), title="Job Editor", url_path="jobs", icon="📋"),
        st.Page(partial(page_scraper, config), title="Web Scraper", url_path="scraper", icon="🕷️"),
        st.Page(partial(page_settings, config), title="Settings", url_path="settings", icon="⚙️"),
    ])

    menu.run()

if __name__ == "__main__":
    main()
