import fitz  # PyMuPDF
from io import BytesIO
from docx import Document

MAX_TEXT_LENGTH = 15000  # Adjust depending on token limits

def extract_text(file_obj, file_type):
    """
    Extract plain text from uploaded docs (PDF, DOCX, TXT).
    """
    text = ""

    if file_type.lower() == "pdf":
        pdf_bytes = file_obj.read()
        pdf_doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = " ".join(page.get_text("text") for page in pdf_doc)

    elif file_type.lower() == "docx":
        document = Document(file_obj)
        text = "\n".join([p.text for p in document.paragraphs])

    elif file_type.lower() == "txt":
        text = file_obj.read().decode("utf-8", errors="ignore")

    else:
        raise ValueError("Unsupported file type")

    if len(text) > MAX_TEXT_LENGTH:
        text = text[:MAX_TEXT_LENGTH] + "\n[Text truncated for length]"

    return text.strip()