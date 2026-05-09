import io
import pdfplumber


def extract_text_from_pdf(uploaded_file) -> str:
    """
    Extract all text from a PDF uploaded via Streamlit's file_uploader.
    Returns a cleaned string of the full resume content.
    """
    text_chunks = []

    try:
        pdf_bytes = uploaded_file.read()
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_chunks.append(page_text)

        full_text = "\n\n".join(text_chunks)
        return _clean_text(full_text)

    except Exception:
        return ""


def _clean_text(text: str) -> str:
    """Remove excessive whitespace and normalize line breaks."""
    lines = text.splitlines()
    cleaned = [line.strip() for line in lines if line.strip()]
    return "\n".join(cleaned)
