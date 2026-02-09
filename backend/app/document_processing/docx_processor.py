from docx import Document


class DocxProcessor:
    def extract_text(self, file_path):
        doc = Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            if para.text.strip():
                full_text.append(para.text.strip())

        # Also extract from tables
        for table in doc.tables:
            for row in table.rows:
                row_text = ' | '.join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    full_text.append(row_text)

        content = '\n'.join(full_text)
        if not content.strip():
            raise ValueError('No se pudo extraer texto del documento DOCX.')

        return [{'content': content, 'page': 1}]
