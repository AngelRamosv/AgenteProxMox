"""
Módulo de Evaluación de Criterios Semánticos de Soporte.
"""
import re
from src.core import config

def matches_criteria(text: str) -> bool:
    """
    Evalúa si un mensaje de Teams coincide con las frases y patrones regex de soporte.
    """
    t = (text or "").lower()
    
    # 1. Coincidencias literales directas
    if any(c in t for c in config.CRITERIOS):
        return True
        
    # 2. Coincidencias flexibles por expresión regular
    for pattern in config.CRITERIOS_REGEX:
        if re.search(pattern, t):
            return True
            
    return False
