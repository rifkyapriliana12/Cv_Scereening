import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from extractor import extract_text_from_file
from analyzer import analyze_gap, get_recommendation, generate_detailed_reasoning
from bias_mitigation import score_fairness

st.set_page_config(page_title="Dashboard Analytics", page_icon="bar_chart", layout="wide")
st.title("Dashboard Analitik Seleksi CV")
st.markdown("Ringkasan statistik dan distribusi kandidat berdasarkan hasil analisis AI.")

uploaded_files = st.file_uploader("Upload CV (PDF)", type=["pdf"], accept_multiple_files=True)
job_desc = st.text_area("Job Description", height=150)

if st.button("Analisis & Tampilkan Dashboard", type="primary"):
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
            gap_results = [analyze_gap(c["teks"], job_desc) for c in cv_data]
            enriched = []
            for i, (r, g) in enumerate(zip(ranked, gap_results)):
                r["Rekomendasi"] = get_recommendation(g)
                r["Kelebihan"] = "; ".join(g["strengths"])
                r["Kekurangan"] = "; ".join(g["weaknesses"])
                r["Alasan"] = generate_detailed_reasoning(g)
                enriched.append(r)

        st.success("Analisis selesai!")

        col1, col2, col3, col4 = st.columns(4)
        scores = [r["Score_Kecocokan"] for r in enriched]
        col1.metric("Total Kandidat", len(enriched))
        col2.metric("Rata-rata Skor", f"{sum(scores)/len(scores):.1f}%" if scores else "0%")
        col3.metric("Skor Tertinggi", f"{max(scores):.1f}%" if scores else "0%")
        col4.metric("Skor Terendah", f"{min(scores):.1f}%" if scores else "0%")

        st.subheader("Distribusi Skor Kandidat")
        chart_data = {"Kandidat": [r["Kandidat"] for r in enriched], "Skor": scores}
        st.bar_chart(chart_data, x="Kandidat", y="Skor", use_container_width=True)

        recs = {}
        for r in enriched:
            rec = r.get("Rekomendasi", "TIDAK LOLOS")
            recs[rec] = recs.get(rec, 0) + 1
        if recs:
            st.subheader("Rekomendasi Kandidat")
            rec_df = {"Rekomendasi": list(recs.keys()), "Jumlah": list(recs.values())}
            st.bar_chart(rec_df, x="Rekomendasi", y="Jumlah", use_container_width=True)

        fairness = score_fairness(gap_results)
        if fairness:
            st.subheader("Fairness Check")
            st.json(fairness)
