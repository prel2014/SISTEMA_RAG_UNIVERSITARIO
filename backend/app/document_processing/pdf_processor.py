import pdfplumber
from PyPDF2 import PdfReader


class PdfProcessor:
    def extract_text(self, file_path, app=None):
        """Extract text from PDF using pdfplumber, fallback to PyPDF2.

        When app is provided and VISION_ENABLED is true, also extracts
        embedded images per page and injects LLM descriptions into content.
        """
        vision_enabled = app is not None and app.config.get('VISION_ENABLED', False)

        if vision_enabled:
            return self._extract_with_vision(file_path, app)
        return self._extract_text_only(file_path)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _extract_text_only(self, file_path):
        pages = []
        try:
            with pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    text = page.extract_text()
                    if text and text.strip():
                        pages.append({'content': text.strip(), 'page': i + 1})
        except Exception:
            reader = PdfReader(file_path)
            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                if text and text.strip():
                    pages.append({'content': text.strip(), 'page': i + 1})

        if not pages:
            raise ValueError('No se pudo extraer texto del PDF.')
        return pages

    def _extract_with_vision(self, file_path, app):
        import fitz  # PyMuPDF
        from app.document_processing.vision import describe_image

        min_size   = app.config.get('VISION_MIN_IMAGE_SIZE', 80)
        max_images = app.config.get('VISION_MAX_IMAGES_PAGE', 5)
        ollama_url = app.config.get('OLLAMA_BASE_URL', 'http://localhost:11434')
        llm_model  = app.config.get('LLM_MODEL', 'gemma3:4b')

        pages = []
        doc_fitz = None
        try:
            doc_fitz = fitz.open(file_path)

            try:
                with pdfplumber.open(file_path) as pdf:
                    for i, page in enumerate(pdf.pages):
                        text = page.extract_text() or ''
                        text = text.strip()

                        # --- vision: images for this page ---
                        descriptions = []
                        if i < len(doc_fitz):
                            fitz_page = doc_fitz[i]
                            img_count = 0
                            for img_info in fitz_page.get_images(full=True):
                                if img_count >= max_images:
                                    break
                                xref = img_info[0]
                                try:
                                    img_dict = doc_fitz.extract_image(xref)
                                    w = img_dict.get('width', 0)
                                    h = img_dict.get('height', 0)
                                    if w < min_size or h < min_size:
                                        continue
                                    desc = describe_image(img_dict['image'], ollama_url, llm_model)
                                    if desc:
                                        img_count += 1
                                        idx = img_count
                                        descriptions.append(f'[Imagen {idx}: {desc}]')
                                        print(f'[Vision] PDF pág {i+1} img {idx}: {desc[:80]}...')
                                except Exception as e:
                                    print(f'[Vision] Error en imagen xref={xref}: {e}')

                        combined = text
                        if descriptions:
                            combined = (text + '\n' + '\n'.join(descriptions)).strip()

                        if combined:
                            pages.append({'content': combined, 'page': i + 1})

            except Exception:
                # pdfplumber failed — fallback to PyPDF2 (no vision on fallback path)
                reader = PdfReader(file_path)
                for i, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text and text.strip():
                        pages.append({'content': text.strip(), 'page': i + 1})

        finally:
            if doc_fitz is not None:
                doc_fitz.close()

        if not pages:
            raise ValueError('No se pudo extraer texto del PDF.')
        return pages
