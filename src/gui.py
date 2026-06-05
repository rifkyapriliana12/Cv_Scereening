# src/gui.py
import streamlit as st
from extractor import extract_text_from_file

def run_app():
    # Pengaturan dasar halaman
    st.set_page_config(page_title="Enterprise CV Screening", page_icon="🏢", layout="wide")

    # Header Aplikasi
    st.title("🏢 Enterprise AI CV Screening")
    st.markdown("Sistem Cerdas Penyeleksian Kandidat Berbasis AI (NLP MiniLM-L6-v2)")
    st.divider()

    # Sidebar
    with st.sidebar:
        st.header("📂 1. Upload Dokumen")
        st.markdown("Unggah CV kandidat dalam format PDF di sini.")
        
        uploaded_files = st.file_uploader(
            "Pilih file PDF CV", 
            type=["pdf"], 
            accept_multiple_files=True
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} file berhasil diunggah siap diproses.")

    # Area Utama
    st.header("📝 2. Kriteria Pekerjaan")
    job_desc = st.text_area(
        "Masukkan Detail Job Description:", 
        height=200,
        placeholder="Contoh: Dibutuhkan Junior Architect dengan pengalaman 2 tahun..."
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Tombol Eksekusi
    if st.button("🚀 Mulai Analisis & Ranking Kandidat", type="primary", use_container_width=True):
        if not uploaded_files:
            st.error("⚠️ Silakan unggah minimal 1 CV di panel sebelah kiri (Sidebar) terlebih dahulu.")
        elif not job_desc.strip():
            st.warning("⚠️ Job Description tidak boleh kosong.")
        else:
            # Spinner langsung muncul, user tidak merasa nge-hang!
            with st.spinner("Mengaktifkan AI dan memproses kecocokan kandidat... Mohon tunggu sebentar."):
                
                # --- LAZY LOADING DI SINI ---
                # Library AI yang berat baru dipanggil saat tombol diklik
                from matcher import rank_candidates
                
                # 1. Ekstraksi teks
                cv_data = []
                for file in uploaded_files:
                    text = extract_text_from_file(file)
                    cv_data.append({"nama_file": file.name, "teks": text})
                
                # 2. Proses Matching
                ranked_list = rank_candidates(cv_data, job_desc)
            
            # Tampilan Hasil
            st.success("✅ Analisis Selesai!")
            st.header("🏆 Hasil Ranking Kandidat")
            
            for i, res in enumerate(ranked_list):
                icon = "🥇" if i == 0 else "👤"
                score_val = float(res['Score_Kecocokan'])
                
                with st.expander(f"{icon} Rank {i+1} - {res['Kandidat']} (Skor: {score_val:.2f}%)", expanded=(i==0)):
                    progress_value = max(0.0, min(1.0, score_val / 100.0))
                    st.progress(progress_value)
                    st.markdown("**Analisis AI:**")
                    st.info(res['Alasan'])

if __name__ == "__main__":
    run_app()