import pdfplumber
from PyPDF2 import PdfReader


class PdfProcessor:
    def extract_text(self, file_path):
        """Extract text from PDF using pdfplumber, fallback to PyPDF2."""
        pages = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text and text.strip():
                        pages.append({
                            'content': text.strip(),
                            'page': i + 1,
                        })
        except Exception:
            # Fallback to PyPDF2
            reader = PdfReader(file_path)
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text and text.strip():
                    pages.append({
                        'content': text.strip(),
                        'page': i + 1,
                    })

        if not pages:
            raise ValueError('No se pudo extraer texto del PDF.')
        return pages
