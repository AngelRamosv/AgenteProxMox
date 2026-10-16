"""
Núcleo del sistema AgenteProx (Configuración, Excepciones y Navegador).
"""
from src.core.exceptions import BrowserClosedError, is_browser_closed_exception
from src.core.browser import check_and_recover_page, get_teams_page
from src.core import config

__all__ = [
    "BrowserClosedError",
    "is_browser_closed_exception",
    "check_and_recover_page",
    "get_teams_page",
    "config",
]
