====================================================================
  AUTOMATED CV SCREENING AGENT
  Allure Industries - Workshop Cibitung
  Technical Assessment: AI Specialist
====================================================================

A. RINGKASAN SISTEM
====================================================================

Sistem ini adalah Automated CV Screening Agent yang menggunakan
AI/ML untuk mengotomatiskan proses seleksi CV. Dirancang untuk
perusahaan manufaktur yang sedang dalam masa pertumbuhan dengan
intensitas hiring yang tinggi.

Fitur Utama:
1. Input: Folder berisi file PDF/DOCX
2. Proses: Ekstraksi informasi + Semantic Matching + Scoring
3. Output: Google Sheets, Folder CV lolos, Email ke HC
4. Automation: Scheduler 23:59, Web Scraper Jobstreet/Glints


B. KESESUAIAN DENGAN REQUIREMENT
====================================================================

| Requirement                                    | Status    | Keterangan                              |
|------------------------------------------------|-----------|-----------------------------------------|
| Folder berisi file (pdf/docx)                  | ✅ SESUAI | Support PDF & DOCX                      |
| Google Sheets hasil seleksi                    | ✅ SESUAI | Via gspread API + backup JSON           |
| Folder terpisah CV lolos                       | ✅ SESUAI | output/selected_cvs/                    |
| Email otomatis ke HC                           | ✅ SESUAI | SMTP + fallback log                     |
| Scheduler otomatis jam 23:59                   | ✅ SESUAI | Background thread scheduler             |
| Web scraper/RPA Jobstreet & Glints             | ✅ SESUAI | Playwright + headless browser           |
| Menggunakan AI (Claude/Gemini/ChatGPT)         | ✅ SESUAI | Integrasi Gemini & OpenAI API           |
| Ranking kandidat berdasarkan score             | ✅ SESUAI | Semantic 35% + Skills 30% + Keyword 20% |
|                                           |           | + Experience 15%                        |
| Presentasi (PPTX/PDF)                          | ✅ SESUAI | 14 slides PPTX siap presentasi          |


C. CARA PENGGUNAAN / EXPLANATION GUIDE
====================================================================

--- Cara Menjalankan Sistem ---

1. Buka terminal / command prompt
2. Masuk ke folder project:
     cd C:\Users\LOQ\OneDrive\Dokumen\Auto_CV_Screening

3. Aktifkan virtual environment:
     .\env\Scripts\activate

4. Jalankan Streamlit App:
     streamlit run app.py

5. Buka browser ke: http://localhost:8501


--- Cara Menjelaskan ke Interviewer ---

"Saya telah membangun Automated CV Screening Agent dengan
pendekatan sebagai berikut:

1. INPUT: Sistem menerima CV dalam format PDF dan DOCX dari
   sebuah folder. Bisa juga dari hasil scraping job portal.

2. PROCESSING:
   - Text Extraction: PDF/DOCX di-parse menggunakan pdfplumber
     dan python-docx
   - AI Extraction (optional): Bisa menggunakan Gemini/OpenAI
     API untuk ekstraksi data yang lebih akurat
   - Semantic Matching: Menggunakan Sentence Transformers model
     multilingual untuk membandingkan CV dengan job requirement
   - Scoring: 4 komponen - Semantic (35%), Skills Match (30%),
     Keyword Relevance (20%), Experience (15%)

3. OUTPUT:
   - Ranked candidate list dengan detail score
   - Google Sheets otomatis ter-update
   - Folder CV kandidat yang lolos terpisah
   - Email ringkasan otomatis ke tim HC

4. AUTOMATION:
   - Berjalan otomatis setiap jam 23:59 via scheduler
   - Web scraper untuk mengambil CV dari Jobstreet & Glints
     menggunakan Playwright (headless browser)

5. AI INTEGRATION:
   - Bisa menggunakan Gemini API (gratis) atau OpenAI API
   - Untuk extraction data CV yang lebih akurat
   - Fallback ke regex-based extraction jika tanpa API key

Keunggulan sistem ini:
- Multilingual (support Bahasa Indonesia & Inggris)
- CPU-only (tidak perlu GPU)
- Open source stack (zero license cost)
- Threshold lolos bisa diadjust
- Hasil konsisten, zero human bias"


D. ANALISIS: DATA TAMBAHAN YANG DIPERLUKAN
====================================================================

1. DATABASE REFERENSI SKILL & INDUSTRI
   - Standarisasi nama skill (misal: "Ms. Office" vs "Microsoft Office",
     "AutoCAD" vs "Autocad", "PPT" vs "PowerPoint")
   - Mapping skill berdasarkan industri/job family
   - Weighting skill berdasarkan level (basic, intermediate, advanced)
   - Contoh: Database skills.cloud / O*NET database

2. HISTORICAL HIRING DATA
   - Data kandidat sebelumnya (yang lolos vs tidak lolos)
   - Feedback dari interviewer untuk fine-tuning scoring weights
   - Performance review data karyawan yang sudah diterima
   - Untuk: supervised learning / model improvement

3. COMPANY CULTURE & VALUES DICTIONARY
   - Soft skills & cultural fit indicators
   - Keywords yang merepresentasikan budaya perusahaan
   - Values & behavioral traits yang dicari
   - Untuk: filter cultural fit (bukan cuma technical match)

4. BENCHMARK GAJI & PASAR
   - Rentang gaji per posisi & level
   - Ekspektasi kandidat vs budget perusahaan
   - Lokasi penempatan & willingness to relocate
   - Untuk: filter kandidat yang realistis secara ekspektasi

5. DATABASE SERTIFIKASI & PENDIDIKAN
   - Akreditasi institusi pendidikan
   - Validitas sertifikasi profesional
   - Peringkat universitas (jika relevan)
   - Untuk: validasi kredensial kandidat

6. DATA KEGAGALAN DI TAHAP SEBELUMNYA
   - Alasan kandidat gagal di interview
   - Alasan kandidat gagal di background check
   - Alasan kandidat menolak offer
   - Untuk: preventif filter di awal screening

7. JOB DESCRIPTION DATABASE
   - Template JD per posisi
   - Required vs preferred qualifications
   - Years of experience per level (junior/mid/senior)
   - Untuk: standardisasi matching criteria


E. ANALISIS: TOOLS/APLIKASI TAMBAHAN YANG DIBUTUHKAN
====================================================================

1. LLM API (WAJIB UNTUK PRODUCTION)
   - Google Gemini API (gratis tier available)
   - OpenAI API (ChatGPT)
   - Anthropic Claude API
   - Fungsi: extraction data CV lebih akurat, reasoning,
     explanation generation, bias detection

2. GOOGLE CLOUD / CLOUD PLATFORM
   - Google Cloud Console (untuk Service Account)
   - Google Sheets API + Drive API
   - Cloud Storage untuk menyimpan CV & hasil
   - Cloud Scheduler (alternatif scheduler)
   - Cost: ~$0-20/bulan tergantung usage

3. DATABASE (UNTUK HISTORY & TRACKING)
   - PostgreSQL (open source, recommended)
   - MongoDB (untuk dokumen tidak terstruktur)
   - Fungsi: menyimpan history screening, tracking kandidat
     dari waktu ke waktu, analytics & reporting

4. QUEUE SYSTEM (UNTUK HIGH VOLUME)
   - RabbitMQ atau Redis Queue
   - Celery (Python task queue)
   - Fungsi: handle processing CV dalam jumlah besar
     secara async, anti bottleneck

5. DASHBOARD & MONITORING
   - Grafana (visualisasi metrics)
   - Metabase (business intelligence)
   - Streamlit Cloud (hosting dashboard)
   - Fungsi: track metrics - time-to-hire, acceptance rate,
     jumlah CV per hari, bottleneck detection

6. VERSION CONTROL & CI/CD
   - Git + GitHub/GitLab
   - GitHub Actions / GitLab CI
   - Docker (containerization)
   - Fungsi: automated testing, deployment pipeline,
     environment consistency

7. OCR ENGINE (UNTUK CV SCAN/GAMBAR)
   - Tesseract OCR (open source)
   - Google Document AI
   - Azure Form Recognizer
   - Fungsi: extract teks dari CV yang discan (image-based PDF)

8. WEB SCRAPER ENHANCEMENT
   - Playwright / Selenium (already implemented)
   - Scrapy framework (untuk scale)
   - Proxy rotation service (BrightData, Smartproxy)
   - Fungsi: scraping tanpa kena block, scale ke banyak portal

9. MONITORING & ALERTING
   - Sentry (error tracking)
   - Prometheus + Grafana (metrics)
   - Email/Slack/Telegram notification
   - Fungsi: detect pipeline failure, alert jika ada error

10. ADDITIONAL API INTEGRATIONS
    - LinkedIn API (jika approved)
    - Jobstreet API (jika tersedia)
    - Email API (SendGrid, Mailgun untuk reliable delivery)
    - Fungsi: integrate dengan ekosistem existing

11. SECURITY & COMPLIANCE
    - Data encryption (at rest & in transit)
    - Access control & audit log
    - GDPR/Privacy compliance
    - Fungsi: protect candidate data privacy


F. TOTAL ESTIMASI BIAYA (PRODUCTION)
====================================================================

| Komponen               | Monthly Cost (Estimasi) |
|------------------------|------------------------|
| Cloud VM (1 CPU, 2GB)  | $10-20                 |
| LLM API (Gemini)       | $0 (free tier)         |
| atau OpenAI API        | $5-20                  |
| Database (PostgreSQL)  | $10-15                 |
| Domain + SSL           | $1-3                   |
| Email API              | $0-10                  |
| Monitoring             | $0 (open source)       |
|------------------------|------------------------|
| TOTAL                  | $21-68/bulan           |


G. ARSITEKTUR SISTEM (FULL DIAGRAM)
====================================================================

INPUT LAYER:
  [Jobstreet] [Glints] [Manual Upload] [Email Inbox]
         |
         v
PROCESSING LAYER:
  [PDF Parser] [DOCX Parser] [AI Extractor] [OCR]
  [Text Cleaner] [Language Detector] [NER]
         |
         v
MATCHING & SCORING LAYER:
  [Semantic Embedding] [Skills Match] [Keyword Match]
  [Experience Calc] [Weighted Scoring] [LLM Reasoning]
         |
         v
OUTPUT LAYER:
  [Google Sheets] [Selected CVs Folder] [Email to HC]
  [Dashboard] [API Endpoints] [Notification]


====================================================================
  Dokumen ini dibuat untuk Technical Assessment AI Specialist
  Allure Industries - Workshop Cibitung
====================================================================
