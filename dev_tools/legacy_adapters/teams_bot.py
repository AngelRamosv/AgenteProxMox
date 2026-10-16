"""
Adaptador de Compatibilidad Hacia Atrás — teams_bot.
Reexporta los componentes modulares de Teams, OCR y Parser según la especificación SPEC-02.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.core.exceptions import BrowserClosedError, is_browser_closed_exception
from src.core.browser import check_and_recover_page, get_teams_page
from src.modules.ocr.engine import ocr_from_image, ocr_tesseract_from_path, winocr
from src.modules.parsing.ip_extractor import extract_ips
from src.modules.teams.reader import (
    SEL_MESSAGE,
    SEL_TEXT,
    SEL_IMAGE,
    is_chat_unread,
    teams_find_chat_item,
    read_last_message_text_plus_image_ocr,
    read_latest_message_from_group,
)
from src.modules.teams.sender import send_teams_message

__all__ = [
    "BrowserClosedError",
    "is_browser_closed_exception",
    "check_and_recover_page",
    "get_teams_page",
    "ocr_from_image",
    "ocr_tesseract_from_path",
    "winocr",
    "extract_ips",
    "SEL_MESSAGE",
    "SEL_TEXT",
    "SEL_IMAGE",
    "is_chat_unread",
    "teams_find_chat_item",
    "read_last_message_text_plus_image_ocr",
    "read_latest_message_from_group",
    "send_teams_message",
]
