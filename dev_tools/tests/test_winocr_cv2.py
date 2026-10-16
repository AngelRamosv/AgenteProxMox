import asyncio
import winocr
from PIL import Image
import cv2

async def main():
    img_path = "teams_latest.png"
    
    print("\n--- 4. Probando WinOCR con OpenCV (Adaptive Threshold) ---")
    img_cv = cv2.imread(img_path)
    # Aumentar 400%
    img_cv = cv2.resize(img_cv, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
    
    # Grises
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    
    # Adaptive Threshold (Limpia sombras y fondos naranjas dejando solo letras negras puras)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 51, 10)
    
    cv2.imwrite("ocr_tmp_test3.png", thresh)
    img_pil = Image.open("ocr_tmp_test3.png").convert('RGB')
    
    res4 = await winocr.recognize_pil(img_pil, lang="es-ES")
    print("Texto con Adaptive:", res4.text)

if __name__ == "__main__":
    asyncio.run(main())
