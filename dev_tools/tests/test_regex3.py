import re

def extract_ips(text: str):
    if not text: return []
    text = text.replace("\n", " ").replace("\r", " ")
    
    text = text.replace("'92", "192").replace("’92", "192")
    text = text.replace("Ã", ".1") 
    text = text.replace("?", "7")  
    # CRITICO: Borrar el 192168 pegado que solo estorba y roba numeros a la siguiente IP
    text = text.replace("192168", " ") 
    
    ips = []
    ips.extend(re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", text))
    
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

test_text = "hola buen diat nos pueden ayudar con estas ip por favor, una desde ayer dejo de tomar registros 192 168 49 7? 192168 192ã68 51 17 not done"
print(extract_ips(test_text))
