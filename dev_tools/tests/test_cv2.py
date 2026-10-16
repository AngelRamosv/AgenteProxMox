import cv2, asyncio, winocr
import numpy as np
from PIL import Image

def test_ocr():
    img = cv2.imread('teams_latest.png')
    h, w = img.shape[:2]
    
    # Recortar solo la mitad inferior (donde está la tabla con la IP)
    crop = img[int(h*0.4):h, 0:w]
    
    # Escalar agresivamente (5X)
    crop = cv2.resize(crop, None, fx=5, fy=5, interpolation=cv2.INTER_CUBIC)
    
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    
    _, thresh_otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    thresh_adapt = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 51, 15)
    
    strategies = [
        ("CROP_RAW", crop),
        ("CROP_GRAY", gray),
        ("CROP_OTSU", thresh_otsu),
        ("CROP_ADAPT", thresh_adapt)
    ]
    
    for name, mat in strategies:
        pil_img = Image.fromarray(mat).convert('RGB')
        res = asyncio.run(winocr.recognize_pil(pil_img, lang='es-ES'))
        txt = res.text.strip() if res.text else ''
        print(f'{name}:\n{txt}\n')

test_ocr()
