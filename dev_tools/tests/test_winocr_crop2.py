import asyncio
import winocr
from PIL import Image
import cv2
import re

async def main():
    img_path = "teams_latest.png"
    img = cv2.imread(img_path)
    
    h, w = img.shape[:2]
    # Cortar el texto de "Hola buen dia" (aprox el 25% superior)
    # y quedarnos solo con la columna de IPs (aprox el 30% izquierdo)
    crop = img[int(h * 0.25):h, :int(w * 0.30)]
    
    # Aumentar la resolución del recorte 4x
    crop = cv2.resize(crop, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
    
    # Simple conversión a grises (sin binarización que destruya el naranja)
    crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    
    cv2.imwrite("ocr_crop2_test.png", crop)
    img_pil = Image.open("ocr_crop2_test.png").convert('RGB')
    
    print("\n--- 9. Probando WinOCR con Recorte Exacto de IPs ---")
    res = await winocr.recognize_pil(img_pil, lang="es-ES")
    
    if res and res.text:
        txt = res.text.strip()
        print(f"Texto extraído:\n{txt}\n")
        
        # Extraer IPs usando regex tolerante
        ips_tolerantes = re.findall(r"\b\d{1,3}[\s\.]+\d{1,3}[\s\.]+\d{1,3}[\s\.]+\d{1,3}\b", txt)
        
        ips_limpias = []
        for ip in ips_tolerantes:
            ip_limpia = re.sub(r'\s+', '.', ip)
            ips_limpias.append(ip_limpia)
            
        print(f"IPS ENCONTRADAS: {ips_limpias}")
    else:
        print("WinOCR no extrajo nada.")

if __name__ == "__main__":
    asyncio.run(main())
