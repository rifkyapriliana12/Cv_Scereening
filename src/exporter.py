import csv
import io
import os

def export_to_csv(ranked_results, filepath=None):
    output = io.StringIO()
    fieldnames = ["Rank", "Kandidat", "Score_Kecocokan", "Rekomendasi", "Kelebihan", "Kekurangan", "Alasan"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for i, r in enumerate(ranked_results, start=1):
        writer.writerow({
            "Rank": i,
            "Kandidat": r.get("Kandidat", ""),
            "Score_Kecocokan": r.get("Score_Kecocokan", ""),
            "Rekomendasi": r.get("Rekomendasi", ""),
            "Kelebihan": r.get("Kelebihan", ""),
            "Kekurangan": r.get("Kekurangan", ""),
            "Alasan": r.get("Alasan", ""),
        })
    content = output.getvalue()
    output.close()
    if filepath:
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            f.write(content)
    return content

def export_summary_text(ranked_results, job_desc=""):
    lines = []
    lines.append("=" * 60)
    lines.append("LAPORAN HASIL SELEKSI CV - AUTO CV SCREENING")
    lines.append("=" * 60)
    if job_desc:
        lines.append(f"\nJob Description: {job_desc[:100]}...")
    lines.append(f"\nTotal Kandidat: {len(ranked_results)}")
    lines.append(f"Tanggal: {__import__('datetime').datetime.now().strftime('%d-%m-%Y %H:%M')}")
    lines.append("\n" + "-" * 60)
    lines.append("PERINGKAT KANDIDAT:")
    lines.append("-" * 60)
    for i, r in enumerate(ranked_results, start=1):
        lines.append(f"\n{i}. {r.get('Kandidat', 'N/A')}")
        lines.append(f"   Skor: {r.get('Score_Kecocokan', 'N/A')}%")
        lines.append(f"   Rekomendasi: {r.get('Rekomendasi', 'N/A')}")
        lines.append(f"   Analisis: {r.get('Alasan', 'N/A')}")
    lolos = [r for r in ranked_results if r.get("Rekomendasi") == "LOLOS WAWANCARA"]
    if lolos:
        lines.append("\n" + "-" * 60)
        lines.append(f"KANDIDAT LOLOS WAWANCARA ({len(lolos)}):")
        for r in lolos:
            lines.append(f"  - {r.get('Kandidat')} (Skor: {r.get('Score_Kecocokan')}%)")
    lines.append("\n" + "=" * 60)
    lines.append("Dihasilkan secara otomatis oleh Enterprise AI CV Screening")
    return "\n".join(lines)
