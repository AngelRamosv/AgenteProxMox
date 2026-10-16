import asyncio
import winocr
from PIL import Image
import cv2
import numpy as np
import re

async def main():
    img_path = "teams_latest.png"
    img_cv = cv2.imread(img_path)
    
    # 1. Aumentar la resolucion 2x para que OpenCV vea mejor los detalles
    img_cv = cv2.resize(img_cv, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    
    # Invertir para que el texto sea blanco y el fondo negro
    inv = cv2.bitwise_not(gray)
    
    # Binarizar
    _, thresh = cv2.threshold(inv, 120, 255, cv2.THRESH_BINARY)
    
    # Dilatar horizontalmente para conectar las letras de una IP/palabra en un solo bloque
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 5))
    dilated = cv2.dilate(thresh, kernel, iterations=1)
    
    # Encontrar contornos de esos bloques
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    print("\n--- 5. Probando WinOCR por Fragmentos (Diseccionador) ---")
    
    encontradas = []
    
    # Ordenar contornos de arriba a abajo, de izquierda a derecha
    contours = sorted(contours, key=lambda c: (cv2.boundingRect(c)[1], cv2.boundingRect(c)[0]))
    
    for idx, c in enumerate(contours):
        x, y, w, h = cv2.boundingRect(c)
        if w > 20 and h > 10: # Ignorar ruido muy pequeño
            # Expandir el recuadro un poquito (padding)
            p = 5
            y1 = max(0, y-p)
            y2 = min(img_cv.shape[0], y+h+p)
            x1 = max(0, x-p)
            x2 = min(img_cv.shape[1], x+w+p)
            
            roi = img_cv[y1:y2, x1:x2]
            
            # Guardar el fragmento y pasarlo a PIL
            cv2.imwrite(f"ocr_tmp_frag_{idx}.png", roi)
            img_pil = Image.open(f"ocr_tmp_frag_{idx}.png").convert('RGB')
            
            try:
                res = await winocr.recognize_pil(img_pil, lang="en-US") # en-US suele ser mejor para numeros y puntos
                if res and res.text:
                    txt = res.text.strip()
                    # Buscar IP en este fragmento
                    ips = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", txt)
                    if ips:
                        encontradas.extend(ips)
                        print(f"FRAG {idx} -> IP Encontrada: {ips[0]}")
            except:
                pass
                
    print(f"\nTOTAL IPS EXTRAIDAS: {encontradas}")

if __name__ == "__main__":
    asyncio.run(main())
