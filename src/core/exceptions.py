"""
Definición de Excepciones del Núcleo de AgenteProx.
"""

class BrowserClosedError(Exception):
    """Excepción lanzada cuando el navegador, contexto o pestaña se han cerrado o desconectado."""
    pass


def is_browser_closed_exception(e: Exception) -> bool:
    """Verifica si un error dado corresponde a la desconexión o cierre del navegador."""
    msg = str(e).lower()
    return any(x in msg for x in [
        "closed",
        "connection closed",
        "failed to find browser",
        "not connected",
        "browser has been closed",
        "target page, context or browser has been closed",
        "page.bring_to_front: target",
        "context or browser has been closed"
    ])
