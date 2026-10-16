import asyncio
import winocr
from PIL import Image
import cv2
import re

async def main():
    img_path = "teams_latest.png"
    img = cv2.imread(img_path)
    
    # Recortar solo la cuarta parte izquierda de la imagen (donde están las IPs)
    h, w = img.shape[:2]
    crop = img[:, :int(w * 0.25)]
    
    # Aumentar la resolución del recorte 4x
    crop = cv2.resize(crop, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
    
    cv2.imwrite("ocr_crop_test.png", crop)
    img_pil = Image.open("ocr_crop_test.png").convert('RGB')
    
    print("\n--- 8. Probando WinOCR con Recorte de Columna Izquierda ---")
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
