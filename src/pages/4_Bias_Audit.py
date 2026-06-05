import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from extractor import extract_text_from_file
from bias_mitigation import anonymize_text, detect_potential_bias, score_fairness
from analyzer import analyze_gap

st.set_page_config(page_title="Bias Audit", page_icon="search", layout="wide")
st.title("Bias & Fairness Audit")
st.markdown("Deteksi potensi bias pada CV dan audit kewajaran sistem seleksi.")

uploaded_files = st.file_uploader("Upload CV (PDF)", type=["pdf"], accept_multiple_files=True)
job_desc = st.text_area("Job Description (opsional untuk fairness scoring)", height=100)

col1, col2 = st.columns(2)
anonymize = col1.checkbox("Anonimisasi CV (hapus nama, email, telepon)", value=True)
show_warnings = col2.checkbox("Tampilkan peringatan bias per CV", value=True)

if st.button("Audit Sekarang", type="primary"):
    if not uploaded_files:
        st.error("Upload minimal 1 CV.")
    else:
        with st.spinner("Menganalisis bias..."):
            all_warnings = []
            gap_results = []
            for f in uploaded_files:
                text = extract_text_from_file(f)
                display_text = anonymize_text(text) if anonymize else text
                warnings = detect_potential_bias(text)
                all_warnings.append({"file": f.name, "warnings": warnings, "text_preview": display_text[:500]})
                if job_desc.strip():
                    gap_results.append(analyze_gap(text, job_desc))

        st.success(f"{len(uploaded_files)} CV dianalisis.")

        for item in all_warnings:
            if show_warnings and item["warnings"]:
                with st.expander(f"{item['file']} - {len(item['warnings'])} peringatan"):
                    for w in item["warnings"]:
                        st.warning(w)
                    st.text_area("Preview Teks (Anonim)", item["text_preview"], height=150)
            else:
                with st.expander(f"{item['file']} - Tidak ada indikasi bias terdeteksi"):
                    st.text_area("Preview Teks (Anonim)", item["text_preview"], height=150)

        if gap_results:
            st.subheader("Distribusi Skor & Fairness")
            fairness = score_fairness(gap_results)
            if fairness:
                st.json(fairness)

        st.info(
            "Catatan: Deteksi bias ini bersifat indikatif awal. "
            "Untuk audit bias menyeluruh, disarankan kombinasi dengan:\n"
            "- Analisis dampak berbeda (demographic parity, equal opportunity)\n"
            "- Review manual oleh tim HR yang diverse\n"
            "- Evaluasi berkala terhadap hasil rekrutmen aktual"
        )
