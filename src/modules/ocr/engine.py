"""
Motor de Reconocimiento Óptico de Caracteres (WinOCR Nativo).
"""
import asyncio
import concurrent.futures
from PIL import Image

try:
    import winocr
    print("    [OCR] Motor WinOCR (Nativo Windows) cargado con éxito.")
except ImportError:
    winocr = None
    print("    [OCR WARN] winocr no instalado. OCR de imágenes no disponible.")


def _winocr_in_thread(img, lang):
    """
    Ejecuta WinOCR en un hilo separado con su propio bucle de eventos
    para evitar conflictos con el event loop de Playwright.
    """
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(winocr.recognize_pil(img, lang=lang))
    finally:
        loop.close()


def ocr_tesseract_from_path(img_path: str) -> str:
    """
    Motor OCR nativo de Windows 10/11 (WinOCR).
    Se ejecuta en un hilo separado para evitar conflictos de asyncio con Playwright.
    """
    if winocr is None:
        print("      [OCR SKIP] WinOCR no disponible.")
        return ""

    # Preprocesamiento de imagen con PIL (escalado 300% + grises)
    try:
        import tempfile
        import os
        temp_dir = os.path.join(tempfile.gettempdir(), "AgenteProx")
        os.makedirs(temp_dir, exist_ok=True)
        tmp_img_path = os.path.join(temp_dir, "ocr_tmp.png")

        img_original = Image.open(img_path)
        w, h = img_original.size
        resampling_filter = Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.ANTIALIAS
        img = img_original.convert('L').resize((w * 3, h * 3), resampling_filter)
        img.save(tmp_img_path)
    except Exception as e:
        print(f"      [OCR DEBUG] Error en preprocesamiento PIL: {e}")
        try:
            img = Image.open(img_path)
        except:
            return ""

    # Ejecutar WinOCR en hilo separado
    for lang_code in ['es-ES', 'en-US']:
        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(_winocr_in_thread, img, lang_code)
                res = future.result(timeout=10)
            if res and hasattr(res, 'text') and res.text:
                txt = res.text.strip()
                if txt:
                    print(f"      [OCR EXITO] ({lang_code}) {txt[:80]}")
                    return txt
        except Exception as e:
            print(f"      [OCR DEBUG] WinOCR ({lang_code}) falló: {e}")
            continue

    print("      [OCR WARN] No se pudo extraer texto de la imagen.")
    return ""

ocr_from_image = ocr_tesseract_from_path
