import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from extractor import extract_text_from_file
from analyzer import analyze_gap, get_recommendation, generate_detailed_reasoning
from exporter import export_to_csv, export_summary_text

st.set_page_config(page_title="Export Report", page_icon="page_facing_up", layout="wide")
st.title("Export Laporan Hasil Seleksi")
st.markdown("Generate laporan terstruktur dalam format CSV atau TXT.")

uploaded_files = st.file_uploader("Upload CV (PDF)", type=["pdf"], accept_multiple_files=True)
job_desc = st.text_area("Job Description", height=150)

if st.button("Proses & Export", type="primary"):
    if not uploaded_files or not job_desc.strip():
        st.error("Upload CV dan isi Job Description terlebih dahulu.")
    else:
        with st.spinner("Memproses..."):
            from matcher import rank_candidates
            cv_data = []
            for f in uploaded_files:
                text = extract_text_from_file(f)
                cv_data.append({"nama_file": f.name, "teks": text})
            ranked = rank_candidates(cv_data, job_desc)
            enriched = []
            for c in cv_data:
                g = analyze_gap(c["teks"], job_desc)
                enriched.append({
                    "Kandidat": c["nama_file"],
                    "Score_Kecocokan": next((r["Score_Kecocokan"] for r in ranked if r["Kandidat"] == c["nama_file"]), 0),
                    "Rekomendasi": get_recommendation(g),
                    "Kelebihan": "; ".join(g["strengths"]),
                    "Kekurangan": "; ".join(g["weaknesses"]),
                    "Alasan": generate_detailed_reasoning(g),
                })
            enriched.sort(key=lambda x: x["Score_Kecocokan"], reverse=True)

        csv_content = export_to_csv(enriched)
        txt_content = export_summary_text(enriched, job_desc)

        st.success(f"{len(enriched)} kandidat diproses!")
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                "Download CSV", data=csv_content,
                file_name="hasil_seleksi_cv.csv", mime="text/csv", use_container_width=True
            )
        with col2:
            st.download_button(
                "Download TXT", data=txt_content,
                file_name="laporan_seleksi_cv.txt", mime="text/plain", use_container_width=True
            )

        with st.expander("Preview Laporan CSV"):
            st.text(csv_content[:2000])
        with st.expander("Preview Laporan TXT"):
            st.text(txt_content[:2000])
