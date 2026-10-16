import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r"C:\Rpa_CX_Bots_Proxmox\Rpa_ExtraccionesAutomatizadas\tesseract\tesseract.exe"

def test():
    try:
        img_original = Image.open('teams_latest.png')
        w, h = img_original.size
        
        # El preprocesamiento original que siempre te funcionó (3x Lanczos + Grises)
        resampling = Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.ANTIALIAS
        img = img_original.convert('L').resize((w * 3, h * 3), resampling)
        
        print("Ejecutando Tesseract en la imagen...")
        txt = pytesseract.image_to_string(img, lang="spa+eng")
        
        print("-" * 50)
        print("TEXTO EXTRAÍDO:")
        print(txt)
        print("-" * 50)
    except Exception as e:
        print(f"Error: {e}")

test()
