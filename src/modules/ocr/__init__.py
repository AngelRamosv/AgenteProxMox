"""
Módulo OCR de AgenteProx.
"""
from src.modules.ocr.engine import ocr_from_image, ocr_tesseract_from_path

__all__ = ["ocr_from_image", "ocr_tesseract_from_path"]
