import asyncio
import winocr
from PIL import Image
import cv2
import numpy as np
import re

async def main():
    img_path = "teams_latest.png"
    img = cv2.imread(img_path)
    
    # 1. Aumentar tamaño para mejor visión
    h, w = img.shape[:2]
    crop = img[int(h*0.2):h, :int(w*0.5)] # Solo la mitad izquierda donde están los datos
    img_large = cv2.resize(crop, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
    
    gray = cv2.cvtColor(img_large, cv2.COLOR_BGR2GRAY)
    
    # 2. Invertir colores y binarizar para encontrar dónde hay texto
    # (Usar un umbral alto para atrapar tanto texto negro como naranja)
    inv = cv2.bitwise_not(gray)
    _, thresh = cv2.threshold(inv, 100, 255, cv2.THRESH_BINARY)
    
    # 3. Dilatar horizontalmente para fusionar números en bloques (palabras)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 10))
    dilated = cv2.dilate(thresh, kernel, iterations=2)
    
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=lambda c: cv2.boundingRect(c)[1]) # Ordenar de arriba hacia abajo
    
    print("\n--- 12. Disección Láser con WinOCR ---")
    todas_las_ips = []
    
    for idx, c in enumerate(contours):
        x, y, w, h = cv2.boundingRect(c)
        if w > 30 and h > 15: # Ignorar ruidos pequeños
            # Extraer el pedacito de la imagen original en grises
            roi = gray[max(0, y-10):y+h+10, max(0, x-10):x+w+10]
            
            # Estirar contraste para que el fondo sea blanco y el texto negro
            roi_norm = cv2.normalize(roi, None, 0, 255, cv2.NORM_MINMAX)
            
            # MAGIA: Añadir 50 píxeles de padding blanco para engañar a WinOCR
            roi_padded = cv2.copyMakeBorder(roi_norm, 50, 50, 50, 50, cv2.BORDER_CONSTANT, value=[255])
            
            cv2.imwrite(f"ocr_frag_{idx}.png", roi_padded)
            img_pil = Image.open(f"ocr_frag_{idx}.png").convert('RGB')
            
            try:
                res = await winocr.recognize_pil(img_pil, lang="es-ES")
                if res and res.text:
                    txt = res.text.strip()
                    
                    # Normalizar OCR (cambiar '92 por 192, etc)
                    txt = txt.replace("'92", "192").replace("’92", "192")
                    txt = txt.replace("192 168", "192.168")
                    
                    # Buscar IPs
                    ips = re.findall(r"\b\d{1,3}[\s\.]+\d{1,3}[\s\.]+\d{1,3}[\s\.]+\d{1,3}\b", txt)
                    # Tolerante con 192.168
                    ips += [f"{m[0]}.{m[1]}.{m[2]}.{m[3]}" for m in re.findall(r"\b(192)[ .]+(168)[ .]+(\d{1,3})[ .]+(\d{1,3})\b", txt)]
                    
                    for ip in ips:
                        ip_limpia = re.sub(r'\s+', '.', ip)
                        if ip_limpia not in todas_las_ips:
                            todas_las_ips.append(ip_limpia)
                            print(f"-> FRAGMENTO {idx} LEYÓ IP: {ip_limpia}")
            except:
                pass
                
    print(f"\nTOTAL IPS EXTRAIDAS: {todas_las_ips}")

if __name__ == "__main__":
    asyncio.run(main())
