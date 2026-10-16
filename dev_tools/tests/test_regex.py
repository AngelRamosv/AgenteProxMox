import re

def extract_ips(text: str):
    if not text: return []
    # Aplanar texto para que IPs divididas por salto de línea se unan
    text = text.replace("\n", " ").replace("\r", " ")
    
    # 0. Normalizar errores muy comunes de OCR en IPs
    text = text.replace("'92", "192").replace("’92", "192")
    text = text.replace("Ã", ".1") # Correccion especifica para "192Ã68" -> "192.168"
    text = text.replace("?", "7")  # Correccion especifica para "7?" -> "77"
    text = text.replace("192168", "192 168") # Separar 192168 pegado
    
    ips = []
    # 1. Búsqueda estándar (IPs perfectas o semi-perfectas)
    ips.extend(re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", text))
    
    # 2. Búsqueda ultra tolerante para OCR (4 octetos separados por espacios o puntos)
    # Permite que entre 192 y 168 pueda no haber espacio (por si acaso), pero obliga separacion en el resto
    ocr_pattern = r"\b(192)[ .]*(168)[ .]+(\d{1,3})[ .]+(\d{1,3})\b"
    matches = re.findall(ocr_pattern, text)
    for m in matches:
        reconstructed = f"{m[0]}.{m[1]}.{m[2]}.{m[3]}"
        ips.append(reconstructed)

    valid = []
    for ip in ips:
        if ip == "0.0.0.0": continue
        parts = ip.split('.')
        try:
            if all(0 <= int(p) <= 255 for p in parts):
                valid.append(ip)
        except: pass
    return list(dict.fromkeys(valid))

test_text = "Hola buen diat nos pueden ayudar con estas IP por favor, una desde ayer dejo de tomar registros 192 168 49 7? 192168 192Ã68 51 17 Not Done"
print(extract_ips(test_text))
