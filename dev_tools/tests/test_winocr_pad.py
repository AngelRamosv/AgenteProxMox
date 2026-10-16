import asyncio
import winocr
from PIL import Image
import cv2
import re

async def main():
    img_path = "teams_latest.png"
    img = cv2.imread(img_path)
    
    # Recortar un área un poco más ancha para no cortar bordes
    h, w = img.shape[:2]
    crop = img[int(h*0.2):h, :int(w * 0.40)]
    
    # Aumentar la resolución del recorte 4x
    crop = cv2.resize(crop, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
    
    # Convertir a grises
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    
    # AÑADIR UN MARCO BLANCO GIGANTE (50 pixeles en todos los lados)
    # Esto le da "respiro" a WinOCR para no confundir bordes con letras
    gray_padded = cv2.copyMakeBorder(gray, 100, 100, 100, 100, cv2.BORDER_CONSTANT, value=[255, 255, 255])
    
    cv2.imwrite("ocr_pad_test.png", gray_padded)
    img_pil = Image.open("ocr_pad_test.png").convert('RGB')
    
    print("\n--- 11. Probando WinOCR con Padding Blanco ---")
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
