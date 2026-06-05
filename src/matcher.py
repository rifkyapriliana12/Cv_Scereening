# src/matcher.py
import streamlit as st

# Trik Cache & Lazy Load: Import library berat HANYA di dalam fungsi
@st.cache_resource
def get_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer('all-MiniLM-L6-v2')

def calculate_match_score(cv_text, job_desc_text):
    from sklearn.metrics.pairwise import cosine_similarity
    
    model = get_model()
    embeddings = model.encode([job_desc_text, cv_text])
    
    job_vector = embeddings[0].reshape(1, -1)
    cv_vector = embeddings[1].reshape(1, -1)
    
    score = cosine_similarity(job_vector, cv_vector)[0][0]
    return round(score * 100, 2)

def generate_reasoning(score):
    if score >= 75:
        return "Sangat Cocok: Keterampilan dan pengalaman sangat selaras dengan kriteria."
    elif score >= 50:
        return "Cukup Cocok: Memiliki beberapa keahlian relevan, namun ada kualifikasi yang kurang."
    else:
        return "Tidak Cocok: Pengalaman dan keahlian tidak sesuai dengan kebutuhan posisi."

def rank_candidates(cv_data, job_desc_text):
    results = []
    for cv in cv_data:
        score = calculate_match_score(cv["teks"], job_desc_text)
        reason = generate_reasoning(score)
        results.append({
            "Kandidat": cv["nama_file"],
            "Score_Kecocokan": score,
            "Alasan": reason
        })
    
    return sorted(results, key=lambda x: x["Score_Kecocokan"], reverse=True)