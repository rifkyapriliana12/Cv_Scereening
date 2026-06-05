# Ringkasan Project: Auto CV Screening System

## 1. Latar Belakang & Problem

Perusahaan manufaktur sedang growth = hiring besar-besaran.
Tim HR masih manual seleksi CV → **makan waktu, biaya besar, rentan bias manusia**.

**Goal:** Otomatisasi seleksi CV dengan AI/ML agar:
- Lebih efisien & cepat
- Biaya lebih rendah
- Seleksi objektif & berkualitas

---

## 2. Arsitektur Sistem

```
User (HR) input Job Description + upload CV (PDF)
        │
        ▼
┌──────────────────┐
│  Streamlit GUI   │  ← Frontend utama
│  (src/gui.py)    │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  PDF Extractor   │  ← pdfplumber
│  (src/extractor) │     ekstrak teks dari PDF
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Parser (NER)    │  ← Regex + keyword matching
│  (src/parser)    │     ekstrak: nama, email, skills,
│                   │     pendidikan, pengalaman, sertifikasi
└──────┬───────────┘
       │
       ▼
┌──────────────────────────────┐
│  Matcher (Semantic Search)   │  ← all-MiniLM-L6-v2
│  (src/matcher)               │     sentence-transformers
│                              │     Cosine Similarity
└──────┬───────────────────────┘
       │
       ▼
┌──────────────────┐
│  Gap Analyzer    │  ← Skill matching, experience check
│  (src/analyzer)  │     rekomendasi: LOLOS / PERTIMBANGKAN / TIDAK LOLOS
└──────┬───────────┘
       │
       ▼
┌──────────────────────────────┐
│  Output + Export + Audit     │
│  Dashboard | CSV/TXT | Bias  │
└──────────────────────────────┘
```

### Alur proses:

1. **Upload** → HR upload CV (PDF) + input job description
2. **Ekstrak** → Teks diekstrak dari PDF pakai pdfplumber
3. **Parse** → Dari teks mentah, kita ekstrak info terstruktur (nama, skill, pendidikan, dll) pakai regex
4. **Encode** → Teks CV & job desc di-encode jadi vector (angka) pakai sentence-transformers all-MiniLM-L6-v2
5. **Match** → Hitung cosine similarity antara vector CV dan vector job desc → skor 0-100%
6. **Analisis Gap** → Cocokkan skill requirement vs skill CV, cek pengalaman → rekomendasi
7. **Rank** → Urutkan dari skor tertinggi ke terendah
8. **Output** → Tampil di dashboard, bisa di-export CSV/TXT, audit bias

---

## 3. Model & Algoritma AI/ML

| Komponen | Model/Algoritma | Kenapa? |
|----------|----------------|---------|
| **Text Embedding** | `all-MiniLM-L6-v2` (Sentence Transformers) | Ringan (80MB), cepat, akurasi bagus untuk semantic similarity |
| **Similarity** | Cosine Similarity | Sederhana, efektif untuk membandingkan vector embeddings |
| **Info Extraction** | Regex + Keyword Matching | Tanpa perlu training, cukup akurat untuk CV terstruktur |
| **Bias Detection** | Rule-based (deteksi kata usia, gender, suku) | Deteksi dini tanpa model tambahan |

### Kenapa all-MiniLM-L6-v2?

- Ukuran kecil (80MB) → bisa running di laptop biasa, tanpa GPU
- Cepat → proses puluhan CV dalam detik
- Semantic understanding → paham konteks, bukan keyword matching doang
- Multilingual → cukup baik untuk CV Bahasa Indonesia + Inggris

---

## 4. Fitur-Fitur (Sesuai Requirements Assessment)

### [1] Mengumpulkan CV otomatis
**Status: Simulasi** (`src/scraper.py`).
Untuk production, bisa integrasi dengan:
- Selenium untuk download dari job portal
- Email parser untuk attachment CV
- API LinkedIn/Jobstreet

### [2] Ekstraksi informasi relevan ✅ (`src/parser.py`)
- Nama kandidat
- Email & telepon
- Skills (matching 70+ skill keywords)
- Pendidikan (S1/S2/S3, nama universitas)
- Pengalaman (tahun)
- Sertifikasi

### [3] Mencocokkan dengan kualifikasi ✅ (`src/matcher.py` + `src/analyzer.py`)
- Semantic matching pakai sentence-transformers
- Gap analysis: skill apa yg cocok, skill apa yg kurang
- Cek pengalaman minimal

### [4] Menyaring & meranking ✅ (`src/matcher.py`)
- Ranking berdasarkan score semantic similarity
- Filter: LOLOS WAWANCARA (>70% + skill cukup)
- PERTIMBANGKAN (50-70%)
- TIDAK LOLOS (<50% atau skill kurang)

### [5] Daftar kandidat terpilih ✅
- Output langsung tampil di Streamlit
- Bisa download CSV/TXT
- Setiap kandidat ada alasan detail

### [6] Output terstruktur ✅
- Score kecocokan (%)
- Kelebihan & kekurangan
- Rekomendasi
- Alasan detail (gap analysis)
- Export CSV + TXT

### Etika & Bias ✅ (`src/bias_mitigation.py`)
- Anonimisasi: hapus nama, email, telepon, NIK dari CV
- Deteksi bias usia (tanggal lahir)
- Deteksi bias suku/agama
- Deteksi bias gender dari gaya bahasa
- Fairness score: distribusi skor merata?
- Halaman khusus: Bias Audit

---

## 5. Cara Menjalankan

```bash
# 1. Aktifkan virtual environment
env\Scripts\activate

# 2. Install dependencies (kalau belum)
pip install -r requirements.txt

# 3. Jalankan
python main.py
```

Akses di browser: `http://localhost:8501`

Ada 4 halaman (muncul otomatis di sidebar):
1. **Main** → Upload CV + Job Desc → Ranking
2. **Dashboard Analytics** → Statistik & distribusi
3. **Export Report** → Download CSV/TXT
4. **Bias Audit** → Deteksi bias & fairness

---

## 6. Persiapan Jawaban Wawancara

### Q: "Ceritakan project ini"
> Saya membangun sistem otomatisasi seleksi CV menggunakan AI. Tujuannya membantu HR yang kewalahan seleksi CV manual. Sistem ini pakai Natural Language Processing - tepatnya model Sentence Transformers (all-MiniLM-L6-v2) - untuk memahami makna dari CV dan Job Description, bukan sekedar keyword matching.
>
> Cara kerjanya: HR upload CV PDF + input job description → sistem ekstrak teks → parsing informasi penting → encode ke vector → hitung kesamaan → ranking → rekomendasi lolos/tidak. Dilengkapi juga fitur bias audit untuk memastikan seleksi tetap fair.

### Q: "Kenapa pakai model itu?"
> Saya pilih all-MiniLM-L6-v2 karena ringan (80MB), cepat, dan cukup akurat. Bisa jalan di laptop tanpa GPU. Model ini juga memahami konteks kalimat, jadi cocok untuk mencocokkan CV dengan job description secara semantik.

### Q: "Apa tantangan terbesar?"
> Mengekstrak informasi dari CV PDF yang formatnya tidak seragam. Saya atasi dengan regex patterns yang fleksibel dan pipeline parsing bertahap. Tantangan lain: memastikan hasil ranking akurat dan tidak bias.

### Q: "Bagaimana mengatasi bias?"
> Saya buat module bias_mitigation yang:
> 1. Anonimisasi CV (hapus nama, email, telepon, usia)
> 2. Deteksi kata-kata bermuatan gender
> 3. Deteksi indikasi suku/agama
> 4. Pantau distribusi skor (fairness score)
> 5. Halaman khusus audit bias untuk transparansi

### Q: "Apa improvement selanjutnya?"
> 1. Integrasi scraping job portal (Selenium)
> 2. Fine-tune model dengan dataset CV Indonesia
> 3. REAMDE GENERATION berbasis LLM untuk alasan lebih natural
> 4. A/B testing untuk validasi akurasi
> 5. Dashboard real-time untuk HR analytics

### Q: "Apa tech stack?"
> Python, Streamlit (frontend), pdfplumber (PDF parsing), Sentence Transformers (NLP), scikit-learn (cosine similarity), regex (information extraction)

### Q: "Hasilnya seperti apa?"
> Output berupa daftar kandidat terurut berdasarkan score kecocokan (0-100%), lengkap dengan:
> - Kelebihan & kekurangan tiap kandidat
> - Skill yang cocok dan kurang
> - Rekomendasi: LOLOS / PERTIMBANGKAN / TIDAK LOLOS
> - Bisa di-export ke CSV atau TXT

---

## 7. Dictionary Istilah Teknis

| Istilah | Arti Sederhana |
|---------|----------------|
| **Sentence Transformers** | Model AI yang bisa mengubah kalimat jadi angka (vector) |
| **Vector / Embedding** | Representasi numerik dari teks (misal: [0.1, -0.3, 0.7, ...]) |
| **Cosine Similarity** | Cara mengukur kemiripan 2 vector (0 = beda total, 1 = sama persis) |
| **Semantic Search** | Mencari berdasarkan makna, bukan keyword |
| **all-MiniLM-L6-v2** | Model NLP mini tapi powerful dari Microsoft |
| **pdfplumber** | Library Python untuk baca PDF |
| **Streamlit** | Framework Python untuk bikin web app data science cepat |
| **Gap Analysis** | Analisis kesenjangan antara CV dan requirement |
| **Anonimisasi** | Menghapus data pribadi (nama, email, dll) |

---

## 8. Project Structure

```
Auto_CV_Screening/
├── main.py                 # Entry point: streamlit run src/gui.py
├── requirements.txt        # Dependencies
├── RINGKASAN_PROJECT.md    # File ini
├── data/                   # Sample CVs
│   └── CV Sample -Test/
│       └── CV Sample Test/
│           ├── CV Sample 1.pdf
│           ├── CV Sample 2.pdf
│           ├── CV Sample 3.pdf
│           ├── CV Sample 4.pdf
│           ├── CV Sample 5.pdf
│           └── Vacancy.pdf
├── src/
│   ├── gui.py              # Streamlit UI (halaman utama)
│   ├── extractor.py        # Ekstrak teks dari PDF
│   ├── parser.py           # Parse teks → info terstruktur [NEW]
│   ├── matcher.py          # Semantic matching + ranking
│   ├── analyzer.py         # Gap analysis + rekomendasi [NEW]
│   ├── bias_mitigation.py  # Anonimisasi + fairness [NEW]
│   ├── exporter.py         # Export CSV/TXT [NEW]
│   ├── scraper.py          # Simulasi scraping CV
│   └── pages/
│       ├── 2_Dashboard_Analytics.py  # Dashboard statistik [NEW]
│       ├── 3_Export_Report.py        # Export laporan [NEW]
│       └── 4_Bias_Audit.py           # Audit bias [NEW]
├── streamlit/
│   └── config.toml         # Theme Streamlit
└── env/                    # Virtual environment
```

**Legend:** [NEW] = file baru yang saya tambahkan, 0 file existing diubah
