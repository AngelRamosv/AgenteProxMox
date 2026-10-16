import asyncio
import winocr
from PIL import Image
import cv2
import re

async def main():
    img_path = "teams_latest.png"
    img = cv2.imread(img_path)
    
    # Aumentar resolución 3x para que WinOCR vea letras grandes
    img = cv2.resize(img, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Detectar líneas (invertido: fondo negro, lineas blancas)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, 2)
    
    # Borrar lineas horizontales
    h_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (60, 1))
    h_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, h_kernel, iterations=2)
    cnts, _ = cv2.findContours(h_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in cnts:
        cv2.drawContours(img, [c], -1, (255,255,255), 5)
        
    # Borrar lineas verticales
    v_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 60))
    v_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, v_kernel, iterations=2)
    cnts, _ = cv2.findContours(v_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for c in cnts:
        cv2.drawContours(img, [c], -1, (255,255,255), 5)
        
    cv2.imwrite("ocr_no_table.png", img)
    img_pil = Image.open("ocr_no_table.png").convert('RGB')
    
    print("\n--- 6. Probando WinOCR sin líneas de cuadrícula ---")
    res = await winocr.recognize_pil(img_pil, lang="es-ES")
    
    if res and res.text:
        txt = res.text.strip()
        print(f"Texto extraído: {txt}")
        ips = re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", txt)
        print(f"IPS ENCONTRADAS: {ips}")
    else:
        print("WinOCR no extrajo nada.")

if __name__ == "__main__":
    asyncio.run(main())
