# src/extractor.py
import pdfplumber

def extract_text_from_file(uploaded_file):
    """Mengekstrak teks langsung dari file PDF yang diunggah ke Streamlit"""
    text = ""
    try:
        # pdfplumber bisa langsung membaca file object dari Streamlit
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception as e:
        print(f"Error membaca {uploaded_file.name}: {e}")
    return text