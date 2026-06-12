====================================================================
  RINGKASAN PROJECT: AUTOMATED CV SCREENING AGENT
  Allure Industries - Workshop Cibitung
  AI Specialist Technical Assessment
====================================================================

A. FITUR YANG TELAH DIBANGUN
====================================================================

✅ 1. INPUT CV (PDF & DOCX)
   - Support PDF via pdfplumber
   - Support DOCX via python-docx
   - Batch processing semua file dalam folder

✅ 2. EKSTRAKSI INFORMASI OTOMATIS
   - Nama, Email, Phone, LinkedIn
   - Skills (30+ keyword terdeteksi)
   - Pendidikan & Education Level (SMA/S1/S2/S3)
   - Bahasa yang dikuasai
   - Tahun pengalaman

✅ 3. AI EXTRACTION (OPTIONAL)
   - Integrasi Google Gemini API
   - Integrasi OpenAI / ChatGPT API
   - Fallback ke regex-based extraction jika tanpa API key
   - Extraction lebih akurat dengan LLM

✅ 4. SEMANTIC MATCHING & SCORING
   - Model: paraphrase-multilingual-MiniLM-L12-v2
   - Multilingual (Indonesia + Inggris)
   - Scoring: Semantic 35% + Skills Match 30% 
              + Keyword 20% + Experience 15%
   - Threshold lolos: ≥ 50%

✅ 5. JOB EDITOR (MULTI-POSISI)
   - Buat job baru dengan requirements sendiri
   - Edit & update job kapan saja
   - Pilih active job untuk screening
   - Data tersimpan di jobs.json

✅ 6. RANKING & OUTPUT
   - Ranking kandidat terurut berdasarkan score
   - Detail breakdown score per komponen
   - Reasoning & analisis per kandidat
   - Status: LOLOS / TIDAK LOLOS

✅ 7. GOOGLE SHEETS INTEGRATION
   - Upload hasil screening otomatis
   - Service Account authentication
   - Auto-create spreadsheet jika belum ada
   - Backup JSON jika credentials tidak tersedia

✅ 8. EMAIL OTOMATIS KE HC
   - SMTP support (Gmail, dll)
   - HTML formatted email dengan tabel hasil
   - Attach CV kandidat yang lolos
   - Fallback ke log file jika SMTP tidak dikonfigurasi

✅ 9. SCHEDULER OTOMATIS (23:59)
   - Background thread scheduler
   - Menjalankan screening otomatis setiap jam 23:59
   - Email hasil langsung ke tim HC

✅ 10. WEB SCRAPER / RPA
    - Scrape Jobstreet (lowongan pekerjaan)
    - Scrape Glints (lowongan pekerjaan)
    - Menggunakan Playwright (headless browser)
    - Download otomatis ke folder scraped_cvs/
    - Tanpa perlu API resmi dari portal

✅ 11. SIDEBAR NAVIGATION (BURGER MENU)
    - 5 halaman: Dashboard, Screening, Job Editor, 
      Web Scraper, Settings
    - Navigasi mudah & profesional
    - Masing-masing fitur punya halaman sendiri

✅ 12. PRESENTASI SLIDE (PPTX)
    - 14 slides siap presentasi
    - Problem Statement, Arsitektur, Model, 
      Results, Analisis, Roadmap

✅ 13. SETTINGS & KONFIGURASI
    - AI API Key (Gemini & OpenAI)
    - Google Sheets credentials
    - SMTP Email settings
    - Scheduler control
    - Semua tersimpan di config.json


B. KESESUAIAN DENGAN REQUIREMENT
====================================================================

| Requirement                              | Status    |
|------------------------------------------|-----------|
| Folder berisi file (pdf/docx)            | ✅ SESUAI |
| Google Sheets hasil seleksi              | ✅ SESUAI |
| Folder terpisah CV lolos                 | ✅ SESUAI |
| Email otomatis ke HC                     | ✅ SESUAI |
| Scheduler jam 23:59                      | ✅ SESUAI |
| Web scraper / RPA Jobstreet & Glints     | ✅ SESUAI |
| Menggunakan AI (Gemini/OpenAI/Claude)    | ✅ SESUAI |


C. STRUKTUR PROJECT
====================================================================

Auto_CV_Screening/
├── app.py                    # Streamlit app (main)
├── config.json               # API keys & settings
├── jobs.json                 # Job vacancies database
├── requirements.txt          # Dependencies
├── README.txt                # Dokumentasi lengkap
├── modules/
│   ├── cv_parser.py          # PDF/DOCX parser
│   ├── vacancy_parser.py     # Vacancy.pdf parser
│   ├── matcher.py            # Semantic matching engine
│   ├── ai_extractor.py       # AI extraction (Gemini/OpenAI)
│   ├── email_sender.py       # SMTP email automation
│   ├── google_sheets.py      # Google Sheets integration
│   ├── web_scraper.py        # Jobstreet/Glints scraper
│   ├── scheduler.py          # 23:59 daily scheduler
│   └── presentation.py       # PPTX slide generator
├── data/
│   ├── cv_samples/           # Input CV PDF files
│   ├── scraped_cvs/          # Hasil scraping
│   └── output/               # Logs & backups
├── output/
│   └── selected_cvs/         # CV kandidat lolos
└── presentation/
    └── AI_Specialist_Technical_Assessment.pptx


D. ANALISIS: DATA TAMBAHAN YANG DIPERLUKAN
====================================================================

1.  DATABASE REFERENSI SKILL & INDUSTRI
    - Standarisasi nama skill (misal: "Ms. Office" vs "Microsoft Office")
    - Mapping skill berdasarkan industri/job family
    - Weighting skill berdasarkan level (basic, intermediate, advanced)
    - Sumber: O*NET database, skills.cloud

2.  HISTORICAL HIRING DATA
    - Data kandidat sebelumnya (lolos vs tidak lolos)
    - Feedback interviewer untuk fine-tuning scoring
    - Performance review karyawan yang sudah diterima
    - Untuk supervised learning / model improvement

3.  COMPANY CULTURE & VALUES DICTIONARY
    - Soft skills & cultural fit indicators
    - Keywords representasi budaya perusahaan
    - Values & behavioral traits yang dicari
    - Untuk filter cultural fit

4.  BENCHMARK GAJI & PASAR
    - Rentang gaji per posisi & level
    - Ekspektasi kandidat vs budget perusahaan
    - Lokasi & willingness to relocate
    - Untuk filter kandidat realistis

5.  DATABASE SERTIFIKASI & PENDIDIKAN
    - Akreditasi institusi pendidikan
    - Validitas sertifikasi profesional
    - Peringkat universitas
    - Untuk validasi kredensial

6.  DATA KEGAGALAN TAHAP SEBELUMNYA
    - Alasan kandidat gagal interview
    - Alasan gagal background check
    - Alasan menolak offer
    - Untuk preventive filter di awal

7.  JOB DESCRIPTION DATABASE
    - Template JD per posisi
    - Required vs preferred qualifications
    - Years of experience per level
    - Untuk standarisasi matching criteria


E. ANALISIS: TOOLS/APLIKASI TAMBAHAN YANG DIBUTUHKAN
====================================================================

1.  LLM API
    - Gemini API / OpenAI API / Claude API
    - Untuk extraction lebih akurat & reasoning
    - Cost: $0 (Gemini free tier) - $20/bulan

2.  GOOGLE CLOUD / CLOUD PLATFORM
    - Service Account untuk Google Sheets
    - Cloud Storage untuk file CV
    - Cost: $0-20/bulan

3.  DATABASE (POSTGRESQL / MONGODB)
    - History screening & tracking kandidat
    - Analytics & reporting
    - Cost: $10-15/bulan

4.  QUEUE SYSTEM (RABBITMQ / REDIS)
    - Handle high-volume CV processing
    - Async task management
    - Cost: $0 (open source)

5.  DASHBOARD & MONITORING
    - Grafana / Metabase untuk visualisasi
    - Track metrics: time-to-hire, acceptance rate
    - Cost: $0 (open source)

6.  VERSION CONTROL & CI/CD
    - Git + GitHub/GitLab
    - Automated testing & deployment
    - Docker containerization
    - Cost: $0 (free tier)

7.  OCR ENGINE
    - Tesseract OCR / Google Document AI
    - Untuk CV yang discan (image-based PDF)
    - Cost: $0 (Tesseract) / $0-50 (Google)

8.  PROXY ROTATION SERVICE
    - BrightData / Smartproxy
    - Untuk scraping tanpa kena block
    - Cost: $0-50/bulan

9.  MONITORING & ALERTING
    - Sentry (error tracking)
    - Prometheus + Grafana (metrics)
    - Slack/Telegram notification
    - Cost: $0 (open source)

10. EMAIL DELIVERY API
    - SendGrid / Mailgun
    - Untuk reliable email delivery
    - Cost: $0-10/bulan

11. SECURITY & COMPLIANCE
    - Data encryption (at rest & in transit)
    - Access control & audit log
    - GDPR/Privacy compliance


F. TOTAL ESTIMASI BIAYA PRODUCTION
====================================================================

| Komponen               | Monthly Cost |
|------------------------|--------------|
| Cloud VM (1 CPU, 2GB)  | $10-20       |
| LLM API (Gemini)       | $0 (free)    |
| Database               | $10-15       |
| Domain + SSL           | $1-3         |
| Email API              | $0-10        |
| Scraper Proxy          | $0-50        |
|------------------------|--------------|
| TOTAL                  | $21-98/bulan |


G. HASIL SCREENING (SAMPLE)
====================================================================

Posisi: Junior Architect

| Rank | Nama          | Score | Semantic | Skills | Status |
|------|---------------|-------|----------|--------|--------|
| 1    | Bayu          | 58.4% | 56.5%    | 53.9%  | ✅ Lolos |
| 2    | Mohamad       | 57.2% | 52.3%    | 46.1%  | ✅ Lolos |
| 3    | Indri         | 55.8% | 71.0%    | 50.0%  | ✅ Lolos |
| 4    | Dani          | 53.3% | 53.7%    | 75.0%  | ✅ Lolos |
| 5    | Permana Abadi | 44.4% | 55.8%    | 42.9%  | ❌ Tidak |

Threshold lolos: ≥ 50%


H. CARA MENJALANKAN
====================================================================

1. Buka terminal:
     cd C:\Users\LOQ\OneDrive\Dokumen\Auto_CV_Screening

2. Aktifkan virtual environment:
     .\env\Scripts\activate

3. Jalankan Streamlit App:
     streamlit run app.py

4. Buka browser: http://localhost:8501

5. (Opsional) Masukkan API key di menu Settings:
   - Gemini: https://aistudio.google.com/apikey
   - OpenAI: https://platform.openai.com/api-keys


====================================================================
  Dokumen disusun untuk Technical Assessment AI Specialist
  Allure Industries - Workshop Cibitung
====================================================================
