import re
import random

GENDER_WORDS_MALE = [
    "he", "him", "his", "himself", "gentleman", "mr", "man", "men", "boy", "boys",
]
GENDER_WORDS_FEMALE = [
    "she", "her", "hers", "herself", "lady", "ms", "mrs", "miss", "woman", "women", "girl", "girls",
]
AGE_INDICATORS = [
    r'\b\d{2}\s*(?:tahun|thn|years?\s*old|yo)\b',
    r'\blahir\b.*?\d{4}',
    r'\bborn\b.*?\d{4}',
    r'\btanggal\s*lahir\b',
]
ETHNIC_INDICATORS = [
    r'\bsuku\b', r'\bagama\b', r'\breligion\b', r'\bethnic\b',
    r'\bwarga\s*negara\b',
]

def anonymize_text(text):
    result = text
    result = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '[EMAIL DIHAPUS]', result)
    result = re.sub(r'\+62[\d\s\-\(\)]{8,15}', '[TELEPON DIHAPUS]', result)
    result = re.sub(r'0\d{2,3}[\s\-]?\d{3,4}[\s\-]?\d{3,6}', '[TELEPON DIHAPUS]', result)
    result = re.sub(r'\b(\d{6})\s*-\s*(\d{6})\b', '[NIK DIHAPUS]', result)
    return result

def detect_potential_bias(cv_text):
    text_lower = cv_text.lower()
    warnings = []
    for pat in AGE_INDICATORS:
        if re.search(pat, text_lower, re.IGNORECASE):
            warnings.append("Informasi usia terdeteksi (bisa memicu bias usia)")
            break
    for pat in ETHNIC_INDICATORS:
        if re.search(pat, text_lower, re.IGNORECASE):
            warnings.append("Informasi suku/agama terdeteksi (bisa memicu bias)")
            break
    male_count = sum(1 for w in GENDER_WORDS_MALE if re.search(r'\b' + w + r'\b', text_lower, re.IGNORECASE))
    female_count = sum(1 for w in GENDER_WORDS_FEMALE if re.search(r'\b' + w + r'\b', text_lower, re.IGNORECASE))
    if male_count > female_count + 2:
        warnings.append(f"Gaya bahasa cenderung maskulin ({male_count} vs {female_count} kata gender)")
    elif female_count > male_count + 2:
        warnings.append(f"Gaya bahasa cenderung feminin ({female_count} vs {male_count} kata gender)")
    return warnings

def score_fairness(gap_results_list):
    if len(gap_results_list) < 3:
        return None
    scores = [r["semantic_score"] for r in gap_results_list]
    mean_s = sum(scores) / len(scores)
    variance = sum((s - mean_s) ** 2 for s in scores) / len(scores)
    std_dev = variance ** 0.5
    return {
        "jumlah_kandidat": len(scores),
        "rata_rata_skor": round(mean_s, 2),
        "standar_deviasi": round(std_dev, 2),
        "skor_terendah": round(min(scores), 2),
        "skor_tertinggi": round(max(scores), 2),
        "distribusi_wajar": std_dev < 30,
        "catatan": "Distribusi skor normal" if std_dev < 30 else "Distribusi skor cukup lebar, periksa kemungkinan bias"
    }
