import io
import fitz  # PyMuPDF
import docx
from django.core.exceptions import ValidationError


class FileParser:
    """Handles PDF, DOCX, and TXT parsing in-memory only."""

    MAX_FILE_SIZE_MB = 5
    MAX_PDF_PAGES = 20
    ALLOWED_EXTENSIONS = [".pdf", ".docx", ".txt"]

    def __init__(self, file):
        self.file = file
        self.ext = "." + file.name.lower().split(".")[-1]

    def validate(self):
        if self.ext not in self.ALLOWED_EXTENSIONS:
            raise ValidationError(f"Unsupported file type: {self.ext}")
        if self.file.size > self.MAX_FILE_SIZE_MB * 1024 * 1024:
            raise ValidationError(f"File exceeds {self.MAX_FILE_SIZE_MB} MB limit.")

    def extract_text(self):
        self.validate()
        if self.ext == ".pdf":
            return self._parse_pdf()
        elif self.ext == ".docx":
            return self._parse_docx()
        elif self.ext == ".txt":
            return self._parse_txt()

    def _parse_pdf(self):
        text = []
        with fitz.open(stream=self.file.read(), filetype="pdf") as doc:
            if len(doc) > self.MAX_PDF_PAGES:
                raise ValidationError(f"PDF exceeds {self.MAX_PDF_PAGES} pages.")
            for page in doc:
                text.append(page.get_text("text"))
        return "\n".join(text)

    def _parse_docx(self):
        document = docx.Document(io.BytesIO(self.file.read()))
        return "\n".join([p.text for p in document.paragraphs])

    def _parse_txt(self):
        return self.file.read().decode("utf-8")
