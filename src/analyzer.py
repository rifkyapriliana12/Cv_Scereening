from parser import parse_cv
from matcher import calculate_match_score
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

REQUIRED_SKILLS_COMMON = [
    "python", "sql", "machine learning", "deep learning", "nlp",
    "docker", "git", "aws", "kubernetes", "tensorflow", "pytorch",
    "react", "node", "java", "javascript", "typescript", "go",
]

def _extract_job_requirements(job_desc):
    jd_lower = job_desc.lower()
    required = []
    for skill in REQUIRED_SKILLS_COMMON:
        if skill in jd_lower:
            required.append(skill)
    exp_match = __import__('re').search(r'(\d+)\+?\s*(?:tahun|years|thn|yr)', jd_lower)
    min_exp = int(exp_match.group(1)) if exp_match else None
    return required, min_exp

def analyze_gap(cv_text, job_desc):
    cv_info = parse_cv(cv_text)
    req_skills, min_exp = _extract_job_requirements(job_desc)

    cv_skills_lower = [s.lower() for s in cv_info["skills"]]
    matched = [s for s in req_skills if s.lower() in cv_skills_lower]
    missing = [s for s in req_skills if s.lower() not in cv_skills_lower]

    exp_ok = True
    exp_note = ""
    if min_exp is not None:
        cv_exp = cv_info["pengalaman_tahun"]
        if cv_exp is None:
            exp_ok = False
            exp_note = f"Tidak disebutkan pengalaman (min {min_exp} thn dibutuhkan)"
        elif cv_exp < min_exp:
            exp_ok = False
            exp_note = f"Pengalaman {cv_exp} thn, kurang dari min {min_exp} thn"
        else:
            exp_note = f"Pengalaman {cv_exp} thn (memenuhi min {min_exp} thn)"

    semantic_score = calculate_match_score(cv_text, job_desc)

    weaknesses = []
    strengths = []
    if missing:
        weaknesses.append(f"Kurang skill: {', '.join(missing[:5])}")
    if not exp_ok:
        weaknesses.append(exp_note)
    if matched:
        strengths.append(f"Skill sesuai: {', '.join(matched[:5])}")
    if exp_ok and min_exp:
        strengths.append(exp_note)
    if semantic_score >= 70:
        strengths.append("Kesesuaian semantik tinggi dengan deskripsi pekerjaan")
    elif semantic_score < 40:
        weaknesses.append("Kesesuaian semantik rendah dengan deskripsi pekerjaan")

    return {
        "cv_info": cv_info,
        "semantic_score": semantic_score,
        "skills_matched": matched,
        "skills_missing": missing,
        "exp_requirement_met": exp_ok,
        "exp_note": exp_note,
        "strengths": strengths,
        "weaknesses": weaknesses,
    }

def generate_detailed_reasoning(gap_result):
    lines = []
    if gap_result["strengths"]:
        lines.append("KELEBIHAN:")
        for s in gap_result["strengths"]:
            lines.append(f"  + {s}")
    if gap_result["weaknesses"]:
        lines.append("KEKURANGAN:")
        for w in gap_result["weaknesses"]:
            lines.append(f"  - {w}")
    if not gap_result["weaknesses"]:
        lines.append("Kandidat memenuhi seluruh kriteria utama.")
    return "\n".join(lines)

def get_recommendation(gap_result):
    score = gap_result["semantic_score"]
    missing = gap_result["skills_missing"]
    exp_ok = gap_result["exp_requirement_met"]
    if score >= 70 and exp_ok and len(missing) <= 1:
        return "LOLOS WAWANCARA"
    elif score >= 50 and exp_ok:
        return "PERTIMBANGKAN"
    else:
        return "TIDAK LOLOS"
