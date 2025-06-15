import PyPDF2
import os
import re

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file using PyPDF2"""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return ""
    return text

def clean_text(text):
    text = text.strip().replace("\n", " ").replace("\r", "").replace("Â", "").replace("ï¼", "")  # Remove unwanted characters
    text = re.sub(r'\s+', ' ', text)  
    return text

def prepare_texts_from_pdf(pdf_path: str) -> tuple[str, str] | None:
    """
    Fungsi utama yang baru: Mengekstrak dan mempersiapkan teks dari PDF.
    Langsung mengembalikan dua versi teks tanpa menyimpan ke file.
    
    Returns:
        Sebuah tuple (full_text_for_regex, text_for_pattern) jika berhasil,
        atau None jika gagal.
    """
    raw_text = extract_text_from_pdf(pdf_path)
    
    if not raw_text:
        return None
    
    regex_text = clean_text(raw_text)
    
    text_for_pattern = raw_text.replace('\n', ' ').replace('\r', ' ').strip().lower()

    return regex_text, text_for_pattern

def save_extracted_texts(pdf_path, output_regex, output_pattern):
    """Extract and save text in two formats: raw and linear"""
    # Create directories if they don't exist
    os.makedirs(os.path.dirname(output_regex), exist_ok=True)
    os.makedirs(os.path.dirname(output_pattern), exist_ok=True)
    
    text = prepare_texts_from_pdf(pdf_path)
    
    if not text:
        print(f"No text extracted from {pdf_path}")
        return False
    
    regex_text, pattern_text = text

    # Simpan untuk regex (APA ADANYA, persis aslinya)
    with open(output_regex, 'w', encoding='utf-8') as f:
        f.write(regex_text)

    with open(output_pattern, 'w', encoding='utf-8') as f:
        f.write(pattern_text)
    
    print(f"Text extracted and saved: {output_regex}, {output_pattern}")
    return True