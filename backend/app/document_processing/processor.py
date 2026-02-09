from app.document_processing.pdf_processor import PdfProcessor
from app.document_processing.docx_processor import DocxProcessor
from app.document_processing.excel_processor import ExcelProcessor
from app.document_processing.txt_processor import TxtProcessor
from app.document_processing.image_processor import ImageProcessor


PROCESSORS = {
    'pdf': PdfProcessor,
    'docx': DocxProcessor,
    'xlsx': ExcelProcessor,
    'xls': ExcelProcessor,
    'txt': TxtProcessor,
    'png': ImageProcessor,
    'jpg': ImageProcessor,
    'jpeg': ImageProcessor,
}


def get_processor(file_type):
    processor_class = PROCESSORS.get(file_type.lower())
    if not processor_class:
        raise ValueError(f'Tipo de archivo no soportado: {file_type}')
    return processor_class()
