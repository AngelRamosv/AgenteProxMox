import cv2, asyncio, winocr
import numpy as np
from PIL import Image

def trick_winocr():
    img = cv2.imread('teams_latest.png')
    h, w = img.shape[:2]
    
    # Recorte agresivo: nos quedamos solo con la parte inferior izquierda
    crop = img[int(h*0.45):int(h*0.95), 0:int(w*0.35)]
    gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    
    # Ampliar masivamente (6X)
    gray = cv2.resize(gray, None, fx=6, fy=6, interpolation=cv2.INTER_LINEAR)
    _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    
    # TRUCO: Crear un lienzo blanco enorme
    canvas = np.ones((thresh.shape[0] + 200, thresh.shape[1] + 600), dtype=np.uint8) * 255
    
    # Dibujar texto falso en el lienzo
    cv2.putText(canvas, "La direccion IP solicitada es:", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,), 4)
    
    # Pegar nuestra imagen recortada (thresh) debajo del texto
    canvas[150:150+thresh.shape[0], 50:50+thresh.shape[1]] = thresh
    
    # Dibujar más texto después
    cv2.putText(canvas, "Fin del reporte.", (50, 150 + thresh.shape[0] + 50), cv2.FONT_HERSHEY_SIMPLEX, 2, (0,), 4)
    
    # Guardar para debug opcional
    cv2.imwrite("canvas_debug.png", canvas)
    
    pil_img = Image.fromarray(canvas).convert('RGB')
    
    print("-" * 50)
    for lang in ['es-ES', 'en-US']:
        try:
            res = asyncio.run(winocr.recognize_pil(pil_img, lang=lang))
            txt = res.text.strip() if res.text else ''
            print(f'WINOCR ({lang}): {repr(txt)}')
        except Exception as e:
            print(f'WINOCR ({lang}) Error: {e}')
    print("-" * 50)

trick_winocr()
