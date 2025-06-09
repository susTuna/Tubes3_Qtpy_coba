import pdfplumber

def extract_text_from_pdf(path: str) -> str:
    """
    Extract all text from a PDF file robustly.
    Returns a single string.
    """
    text_parts = []
    try:
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
    except Exception as e:
        # you might log the error and return empty or partial
        print(f"[PDF ERROR] {path}: {e}")
    return "\n".join(text_parts)
