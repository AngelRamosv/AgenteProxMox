import asyncio
import winocr
from PIL import Image
import cv2
import re

async def main():
    img_path = "teams_latest.png"
    img = cv2.imread(img_path)
    
    # Aumentar resolución 4x
    img = cv2.resize(img, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Todo lo más claro que 120 (incluyendo naranja/amarillo) se vuelve blanco. Letras negras se quedan negras.
    _, thresh = cv2.threshold(gray, 120, 255, cv2.THRESH_BINARY)
    
    cv2.imwrite("ocr_simple_thresh.png", thresh)
    img_pil = Image.open("ocr_simple_thresh.png").convert('RGB')
    
    print("\n--- 7. Probando WinOCR con Threshold Simple ---")
    res = await winocr.recognize_pil(img_pil, lang="es-ES")
    
    if res and res.text:
        txt = res.text.strip()
        print(f"Texto extraído: {txt}")
        
        # Regex tolerante que acepta espacios en lugar de puntos
        ips_tolerantes = re.findall(r"\b\d{1,3}[\s\.]+\d{1,3}[\s\.]+\d{1,3}[\s\.]+\d{1,3}\b", txt)
        
        ips_limpias = []
        for ip in ips_tolerantes:
            ip_limpia = re.sub(r'\s+', '.', ip)
            ips_limpias.append(ip_limpia)
            
        print(f"IPS ENCONTRADAS (Limpías): {ips_limpias}")
    else:
        print("WinOCR no extrajo nada.")

if __name__ == "__main__":
    asyncio.run(main())
