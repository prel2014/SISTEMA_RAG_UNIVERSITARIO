import pytesseract
from PIL import Image


class ImageProcessor:
    def extract_text(self, file_path):
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image, lang='spa')

        if not text.strip():
            raise ValueError('No se pudo extraer texto de la imagen mediante OCR.')

        return [{'content': text.strip(), 'page': 1}]
