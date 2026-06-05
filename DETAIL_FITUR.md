# Detail Fitur Auto CV Screening System

Dokumen ini menjelaskan setiap fitur secara detail: cara kerja, input → proses → output, dan kode relevan.

---

## Fitur 1: Halaman Utama (Main GUI)
**File:** `src/gui.py`

### Deskripsi
Ini adalah halaman utama yang dilihat HR. Tempat mereka upload CV dan input job description.

### Cara Kerja
1. **Sidebar** → Upload file PDF (bisa multiple)
2. **Area utama** → Input Job Description (textarea)
3. **Tombol** "Mulai Analisis & Ranking Kandidat"
4. Saat diklik:
   - Validasi: ada file? ada job desc?
   - Ekstrak teks dari setiap PDF
   - Match & Rank pakai AI
   - Tampilkan hasil ranking

### Input → Proses → Output
- **Input**: File PDF CV + teks Job Description
- **Proses**: Panggil `extract_text_from_file()` → `rank_candidates()`
- **Output**: Daftar kandidat terurut + skor + progress bar

### Kode Penting
```python
# Lazy loading - library berat baru dipanggil saat tombol diklik
from matcher import rank_candidates

# Ekstrak semua CV
cv_data = []
for file in uploaded_files:
    text = extract_text_from_file(file)
    cv_data.append({"nama_file": file.name, "teks": text})

# Matching & ranking
ranked_list = rank_candidates(cv_data, job_desc)
```

### Catatan Wawancara
- **Kenapa pake Streamlit?** Cepat bikin prototype, cocok untuk internal tool HR, tidak perlu frontend complex
- **Kenapa lazy loading?** Biar halaman pertama load cepat, model AI berat baru dipanggil saat dibutuhkan

---

## Fitur 2: Ekstraktor PDF
**File:** `src/extractor.py`

### Deskripsi
Mengambil teks mentah dari file PDF. Ini langkah pertama sebelum teks bisa diproses lebih lanjut.

### Cara Kerja
- Pakai library `pdfplumber`
- Buka file PDF, loop setiap halaman
- Extract text dari setiap halaman
- Gabung semua teks jadi satu string

### Input → Proses → Output
- **Input**: File PDF (dari Streamlit Uploader)
- **Proses**: `pdfplumber.open()` → `page.extract_text()`
- **Output**: String teks mentah

### Kode Penting
```python
with pdfplumber.open(uploaded_file) as pdf:
    for page in pdf.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
```

### Kenapa pdfplumber?
- Lebih akurat dari PyPDF2 untuk text extraction
- Bisa handle PDF yang复杂 (tabel, kolom)
- Ringan, cepat

---

## Fitur 3: Structured Parser (Info Ekstraksi)
**File:** `src/parser.py`

### Deskripsi
Mengubah teks mentah jadi data terstruktur: siapa namanya, apa skill-nya, pendidikan terakhir, dll.

### Fungsi-Fungsi:

| Fungsi | Output | Contoh |
|--------|--------|--------|
| `extract_name()` | String nama | "Budi Santoso" |
| `extract_email()` | String email | "budi@email.com" |
| `extract_phone()` | String telepon | "08123456789" |
| `extract_skills()` | List skill | ["Python", "Docker", "SQL"] |
| `extract_education()` | List dict pendidikan | [{"degree": "S1 Teknik Informatika", "institution": "Universitas Indonesia"}] |
| `extract_experience_years()` | Integer tahun | 5 |
| `extract_certifications()` | List sertifikasi | ["Certified AWS Practitioner"] |
| `parse_cv()` | Gabungan semua di atas | Dict lengkap |

### Cara Kerja (per fungsi)

**extract_name():**
- Ambil 10 baris pertama (nama biasanya di atas)
- Cari baris dengan 2-4 kata, huruf kapital semua
- Skip baris yang berisi "CV", "email", "phone", dll

**extract_skills():**
- 70+ skill keywords sudah didefinisikan (Python, Java, SQL, Docker, dll)
- Cocokkan tiap keyword ke teks CV (case insensitive)
- Return list skill yang ditemukan

**extract_education():**
- Cari keyword: S1, S2, S3, Bachelor, Master, PhD, dll
- Cari keyword institusi: Universitas, Institut, Politeknik, dll
- Group berdasarkan baris

**extract_experience_years():**
- Regex: cari pola "5 tahun pengalaman" atau "5 years experience"
- Ambil angkanya

### Kode Penting
```python
# Matching 70+ skill keywords
for skill in SKILL_KEYWORDS:
    pattern = r'\b' + re.escape(skill) + r'\b'
    if re.search(pattern, text_lower):
        found.append(skill)

# Regex untuk tahun pengalaman
r'(\d+)[\+]?\s*(?:tahun|years|thn|yr)\s*(?:pengalaman|experience)'
```

### Keterbatasan (jujur aja soal ini)
- Rule-based, bukan ML NER → kurang akurat untuk CV yang unik
- Skill list terbatas pada 70+ keywords yang didefinisikan
- Nama kadang tidak terdeteksi kalau formatnya tidak standar

---

## Fitur 4: Semantic Matcher (AI Matching)
**File:** `src/matcher.py`

### Deskripsi
Ini adalah inti AI-nya. Menggunakan model NLP untuk memahami makna CV dan Job Description, lalu menghitung skor kecocokan.

### Cara Kerja (step by step)

```
Step 1: Load Model
┌──────────────────────────────┐
│  all-MiniLM-L6-v2            │  ← 80MB model dari Sentence Transformers
│  @st.cache_resource          │  ← Load sekali, cache untuk session berikutnya
└──────────────────────────────┘

Step 2: Encode
┌──────────────┐     ┌──────────┐
│ Job Desc     │────→│ Vector A │  (384 angka)
└──────────────┘     └──────────┘
┌──────────────┐     ┌──────────┐
│ CV Text      │────→│ Vector B │  (384 angka)
└──────────────┘     └──────────┘

Step 3: Cosine Similarity
┌─────────────────────────────────────┐
│ similarity = cos(θ) = (A·B)/(|A||B|) │  ← -1 sampai 1
│ score = similarity * 100            │  ← diubah ke persen
└─────────────────────────────────────┘
```

### Input → Proses → Output
- **Input**: Teks CV + Teks Job Description
- **Proses**: Encode → Cosine Similarity
- **Output**: Skor 0-100%

### Kode Penting
```python
@st.cache_resource
def get_model():
    return SentenceTransformer('all-MiniLM-L6-v2')

def calculate_match_score(cv_text, job_desc_text):
    model = get_model()
    embeddings = model.encode([job_desc_text, cv_text])
    job_vector = embeddings[0].reshape(1, -1)
    cv_vector = embeddings[1].reshape(1, -1)
    score = cosine_similarity(job_vector, cv_vector)[0][0]
    return round(score * 100, 2)
```

### Kenapa all-MiniLM-L6-v2?
- **Ukuran**: 80MB (kecil, bisa jalan di laptop tanpa GPU)
- **Kecepatan**: encode 1 teks dalam milidetik
- **Akurasi**: performa bagus di benchmark semantic similarity
- **Multilingual**: bisa handle campuran English-Indonesia
- **Alternatif**: bisa diganti dengan model lebih besar (all-mpnet-base-v2) kalau perlu akurasi lebih

### Catatan Wawancara
- **"Apa bedanya sama keyword matching?"** Keyword matching cari kata yang sama persis. Misal JD bilang "machine learning", CV bilang "ML" → keyword matching gagal. Tapi semantic matching paham bahwa "ML" = "machine learning" secara makna.
- **"Kenapa cosine similarity?"** Sederhana, cepat, dan standar untuk perbandingan vector embeddings.

---

## Fitur 5: Gap Analyzer (Analisis Detail)
**File:** `src/analyzer.py`

### Deskripsi
Setelah dapat skor semantic, fitur ini menganalisis secara detail:
- Skill apa yang cocok?
- Skill apa yang kurang?
- Pengalaman cukup?
- Rekomendasi final?

### Tiga Output Utama:

**1. Strengths & Weaknesses**
```
KELEBIHAN:
  + Skill sesuai: Python, SQL, Machine Learning
  + Pengalaman 5 tahun (memenuhi min 3 tahun)
  + Kesesuaian semantik tinggi dengan deskripsi pekerjaan
KEKURANGAN:
  - Kurang skill: Docker, Kubernetes
```

**2. Rekomendasi**
| Kondisi | Rekomendasi |
|---------|------------|
| Skor >= 70 + exp cukup + kurang skill <= 1 | **LOLOS WAWANCARA** |
| Skor >= 50 + exp cukup | **PERTIMBANGKAN** |
| Skor < 50 atau exp kurang | **TIDAK LOLOS** |

**3. Gap Analysis Detail**
```python
{
  "skills_matched": ["Python", "SQL"],
  "skills_missing": ["Docker", "Kubernetes"],
  "exp_requirement_met": True,
  "semantic_score": 85.5
}
```

### Kode Penting
```python
def analyze_gap(cv_text, job_desc):
    cv_info = parse_cv(cv_text)
    req_skills, min_exp = _extract_job_requirements(job_desc)

    # Bandingkan skill CV vs skill requirement
    matched = [s for s in req_skills if s.lower() in cv_skills_lower]
    missing = [s for s in req_skills if s.lower() not in cv_skills_lower]

    # Cek pengalaman
    if cv_exp < min_exp:
        exp_ok = False
```

### Catatan Wawancara
- **Kenapa perlu Gap Analysis?** Skor doang tidak cukup. HR perlu tahu *kenapa* kandidat cocok/tidak cocok. Gap analysis memberikan alasan yang bisa dijelaskan ke user/stakeholder.
- **Threshold bisa diubah?** Ya, angka 70/50 untuk skor dan threshold skill bisa disesuaikan per posisi.

---

## Fitur 6: Bias Mitigation & Fairness
**File:** `src/bias_mitigation.py`

### Deskripsi
Memastikan sistem seleksi tetap fair dan tidak diskriminatif. Ini menjawab concern etika dalam AI hiring.

### Tiga Fungsi Utama:

**1. Anonimisasi (`anonymize_text`)**
```
Sebelum:              Sesudah:
Budi Santoso          Budi Santoso
budi@email.com        [EMAIL DIHAPUS]
08123456789           [TELEPON DIHAPUS]
```

**2. Deteksi Bias (`detect_potential_bias`)**
Yang dideteksi:
- **Usia**: tanggal lahir, "25 tahun", "born 1995"
- **Suku/Agama**: kata "suku", "agama", "religion"
- **Gender**: kata maskulin vs feminin dalam teks (he/she ratio)

Contoh output:
```
⚠️ Informasi usia terdeteksi (bisa memicu bias usia)
⚠️ Gaya bahasa cenderung maskulin (5 vs 1 kata gender)
```

**3. Fairness Score (`score_fairness`)**
- Hitung rata-rata, standar deviasi skor
- Kalau standar deviasi > 30 → distribusi tidak wajar, perlu dicek
- Butuh minimal 3 kandidat

### Kode Penting
```python
def anonymize_text(text):
    # Hapus email
    text = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[EMAIL DIHAPUS]', text)
    # Hapus telepon Indonesia
    text = re.sub(r'\+62[\d\s\-\(\)]{8,15}', '[TELEPON DIHAPUS]', text)
    return text

def detect_potential_bias(cv_text):
    # Deteksi usia
    for pat in AGE_INDICATORS:
        if re.search(pat, text_lower):
            warnings.append("Informasi usia terdeteksi")
    # Deteksi gender dari gaya bahasa
    male_count = sum(1 for w in GENDER_WORDS_MALE if w in text_lower)
    female_count = sum(1 for w in GENDER_WORDS_FEMALE if w in text_lower)
    if male_count > female_count + 2:
        warnings.append("Gaya bahasa cenderung maskulin")
```

### Catatan Wawancara
- **"Ini bisa menghilangkan bias sepenuhnya?"** Tidak, ini baru deteksi awal. Untuk mitigasi total perlu: anonymization saat matching, diverse training data, dan audit berkala.
- **"Apa yang dimaksud fairness score?"** Kita hitung distribusi skor. Kalau semua kandidat dapat skor mirip-mirip, itu wajar. Tapi kalau ada kelompok tertentu (misal berdasarkan usia) yang skornya selalu rendah, itu indikasi bias sistem.

---

## Fitur 7: Exporter (Export Laporan)
**File:** `src/exporter.py`

### Deskripsi
Menyimpan hasil seleksi ke file yang bisa dibuka di Excel atau dibaca sebagai laporan.

### Dua Format:

**1. CSV (Excel)**
```
Rank | Kandidat | Score | Rekomendasi | Kelebihan | Kekurangan | Alasan
1    | CV1.pdf  | 85.5  | LOLOS       | Skill...  | Kurang...  | KELEBIHAN:...
2    | CV2.pdf  | 45.2  | TIDAK LOLOS | -         | -          | KEKURANGAN:...
```

**2. TXT (Laporan Ringkasan)**
```
============================================================
LAPORAN HASIL SELEKSI CV - AUTO CV SCREENING
============================================================
Total Kandidat: 5
Tanggal: 03-06-2026 17:00

------------------------------------------------------------
PERINGKAT KANDIDAT:
------------------------------------------------------------
1. CV1.pdf
   Skor: 85.5%
   Rekomendasi: LOLOS WAWANCARA
   
KANDIDAT LOLOS WAWANCARA (2):
  - CV1.pdf (Skor: 85.5%)
```

### Kode Penting
```python
def export_to_csv(ranked_results):
    fieldnames = ["Rank", "Kandidat", "Score_Kecocokan", "Rekomendasi", 
                  "Kelebihan", "Kekurangan", "Alasan"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for i, r in enumerate(ranked_results, start=1):
        writer.writerow({...})
```

---

## Fitur 8: Scraper (Simulasi)
**File:** `src/scraper.py`

### Deskripsi
Simulasi pengumpulan CV dari job portal. Saat ini masih placeholder.

### Status Sekarang
```python
def auto_collect_cvs():
    # Logika Selenium/PyAutoGUI bisa ditambahkan di sini
    print("Mengumpulkan CV secara otomatis dari job portal...")
    return len(os.listdir(target_folder))
```

### Untuk Production
Bisa dikembangkan dengan:
1. **Selenium** → Buka job portal (LinkedIn, Jobstreet, Glints), download CV
2. **Email Parser** → Ambil attachment CV dari email lamaran
3. **API** → Integrasi langsung dengan portal (kalau ada API)
4. **PyAutoGUI/RPA** → Automate browser untuk portal yang tidak punya API

---

## Fitur 9: Dashboard Analytics (Halaman 2)
**File:** `src/pages/2_Dashboard_Analytics.py`

### Deskripsi
Halaman untuk melihat statistik dan distribusi hasil seleksi secara visual.

### Fitur di Halaman Ini:
1. **4 Metric Cards**: Total kandidat, rata-rata skor, skor tertinggi, skor terendah
2. **Bar Chart Distribusi Skor**: Grafik skor per kandidat
3. **Bar Chart Rekomendasi**: Berapa LOLOS, PERTIMBANGKAN, TIDAK LOLOS
4. **Fairness Check**: JSON dengan statistik distribusi

### Input → Output
- **Input**: Upload CV + Job Desc (sama seperti halaman utama)
- **Output**: Charts + metrik + fairness score

---

## Fitur 10: Export Report (Halaman 3)
**File:** `src/pages/3_Export_Report.py`

### Deskripsi
Halaman khusus untuk download laporan hasil seleksi.

### Fitur:
1. Upload CV + Job Desc
2. Tombol proses
3. Dua tombol download: CSV dan TXT
4. Preview laporan di halaman (expandable)

---

## Fitur 11: Bias Audit (Halaman 4)
**File:** `src/pages/4_Bias_Audit.py`

### Deskripsi
Halaman untuk audit bias secara khusus. Transparansi penuh ke user.

### Fitur:
1. Upload CV (Job Desc opsional)
2. **Checkbox Anonimisasi**: Lihat perbandingan teks sebelum/sesudah anonimisasi
3. **Checkbox Peringatan Bias**: Tampilkan/sembunyikan peringatan
4. Tiap CV ditampilkan dalam expander dengan peringatan bias
5. Fairness score (kalau ada job desc)
6. Info box tentang keterbatasan deteksi bias

---

## Ringkasan Alur Data (End-to-End)

```
HR Upload PDF       →  src/gui.py (Streamlit)
       │
       ▼
extract_text()      →  src/extractor.py (pdfplumber)
       │
       ▼
parse_cv()          →  src/parser.py (Regex)
       │                    ↓
       │              {nama, email, skills, pendidikan, ...}
       ▼
calculate_match()   →  src/matcher.py (SentenceTransformer + CosineSim)
       │                    ↓
       │              {Score: 85.5%}
       ▼
analyze_gap()       →  src/analyzer.py
       │                    ↓
       │              {strengths, weaknesses, rekomendasi}
       ▼
Tampil di GUI       →  src/gui.py (Streamlit)
       │
       ├── Dashboard  →  src/pages/2_Dashboard_Analytics.py
       ├── Export     →  src/pages/3_Export_Report.py → CSV/TXT
       └── Bias Audit →  src/pages/4_Bias_Audit.py
```

---

## Cara Menjelaskan ke HR/User (Non-Teknis)

Kalau ditanya HR yang non-teknis, jelaskan begini:

> "Sistem ini kerja seperti asisten HR yang sangat pintar. HR tinggal upload CV dan tulis deskripsi pekerjaan yang dibutuhkan. Sistem akan:
> 1. **Baca** semua CV (mirip kita baca, tapi lebih cepat)
> 2. **Pahami** isinya: skill apa saja, pengalaman berapa tahun, pendidikan terakhir
> 3. **Cocokkan** dengan kebutuhan pekerjaan
> 4. **Beri skor** seberapa cocok (0-100%)
> 5. **Urutkan** dari yang paling cocok
> 6. **Kasih alasan** kenapa cocok/tidak
> 7. **Bisa export** ke Excel untuk laporan
> 8. **Cek bias** juga, misal kalau ada CV yang nyebut usia atau suku, sistem kasih peringatan"

---

## FAQ Interview

### Q: "Apa bedanya sistem ini sama ATS (Applicant Tracking System) biasa?"
ATS biasa cuma keyword matching (cari kata "Python" di CV). Sistem ini pakai semantic understanding: paham bahwa "data scientist" dan "machine learning engineer" itu mirip, walaupun kata-katanya beda.

### Q: "Berapa akurat sistem ini?"
Akurasi tergantung kualitas CV dan job description. Untuk CV standar dengan format jelas, cukup akurat. Tapi untuk CV yang unik/aneh formatnya, perlu improvement. Ini prototype yang bisa terus ditingkatkan.

### Q: "Bisa handle berapa banyak CV?"
Bisa ratusan CV dalam hitungan menit. Model all-MiniLM-L6-v2 sangat ringan dan cepat.

### Q: "Apa risikonya?"
Risiko terbesar: false positive (kandidat tidak cocok tapi lolos) dan false negative (kandidat bagus tapi ditolak sistem). Makanya sistem ini dirancang sebagai *assistive tool*, bukan keputusan final. HR tetap perlu review manual untuk kandidat LOLOS.

### Q: "Data CV disimpan di mana?"
Saat ini di memory session Streamlit. Kalau browser ditutup, data hilang. Untuk production perlu database.
