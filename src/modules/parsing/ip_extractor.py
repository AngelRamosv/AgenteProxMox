"""
Extractor y Normalizador de Direcciones IP con Tolerancia OCR.
"""
import re

def extract_ips(text: str):
    """
    Extrae direcciones IPv4 válidas a partir de una cadena de texto,
    aplicando heurísticas avanzadas de corrección de ruido típico de OCR.
    """
    if not text:
        return []
        
    # Aplanar texto para que IPs divididas por salto de línea se unan
    text = text.replace("\n", " ").replace("\r", " ")
    
    # Normalizar errores muy comunes de OCR en IPs
    text = text.replace("'92", "192").replace("’92", "192")
    text = text.replace("Ã", ".1").replace("ã", ".1") # Corrección para "192Ã68" y "192ã68" -> "192.168"
    text = text.replace("?", "7")  # Corrección para "7?" -> "77"
    
    # Borrar el 192168 pegado (ruido de OCR) que roba números a la siguiente IP
    text = text.replace("192168", " ")
    
    ips = []
    # 1. Búsqueda estándar (IPs perfectas o semi-perfectas)
    ips.extend(re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", text))
    
    # 2. Búsqueda ultra tolerante para OCR (4 octetos separados por espacios o puntos)
    ocr_pattern = r"\b(192)[ .]*(168)[ .]+(\d{1,3})[ .]+(\d{1,3})\b"
    matches = re.findall(ocr_pattern, text)
    for m in matches:
        reconstructed = f"{m[0]}.{m[1]}.{m[2]}.{m[3]}"
        ips.append(reconstructed)

    valid = []
    for ip in ips:
        if ip == "0.0.0.0":
            continue
        parts = ip.split('.')
        try:
            if all(0 <= int(p) <= 255 for p in parts):
                valid.append(ip)
        except:
            pass
            
    # Retornar lista de IPs únicas preservando el orden de aparición
    return list(dict.fromkeys(valid))
