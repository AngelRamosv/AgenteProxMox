"""
Módulo de Parsing (Extracción de IPs y Criterios) de AgenteProx.
"""
from src.modules.parsing.ip_extractor import extract_ips
from src.modules.parsing.criteria import matches_criteria

__all__ = ["extract_ips", "matches_criteria"]
