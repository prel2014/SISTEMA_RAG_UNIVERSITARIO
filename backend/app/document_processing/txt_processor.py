class TxtProcessor:
    def extract_text(self, file_path):
        # Try common encodings
        for encoding in ['utf-8', 'latin-1', 'cp1252']:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                if content.strip():
                    return [{'content': content.strip(), 'page': 1}]
            except (UnicodeDecodeError, UnicodeError):
                continue

        raise ValueError('No se pudo leer el archivo de texto.')
