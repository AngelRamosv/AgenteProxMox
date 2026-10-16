import asyncio
import winocr
from PIL import Image
import concurrent.futures

def _winocr_in_thread(img, lang):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(winocr.recognize_pil(img, lang=lang))
    finally:
        loop.close()

async def main():
    img_path = "teams_latest.png"
    img_original = Image.open(img_path).convert('RGB')
    
    w, h = img_original.size
    
    # Aumentar la imagen 3x con Lanczos para mayor nitidez
    resampling_filter = Image.Resampling.LANCZOS if hasattr(Image, 'Resampling') else Image.ANTIALIAS
    img_large = img_original.convert('L').resize((w * 3, h * 3), resampling_filter)
    
    W, H = img_large.size
    
    print("\n--- 13. Probando Trituradora (WinOCR por rebanadas) ---")
    
    text_completo = ""
    
    # Vamos a rebanar la imagen en 8 tiras horizontales (con un poco de traslape para no cortar letras por la mitad)
    num_tiras = 8
    alto_tira = H // num_tiras
    traslape = 20
    
    for i in range(num_tiras):
        y1 = max(0, i * alto_tira - traslape)
        y2 = min(H, (i + 1) * alto_tira + traslape)
        
        # Cortar rebanada
        tira = img_large.crop((0, y1, W, y2))
        
        # Le pasamos la tira a WinOCR
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(_winocr_in_thread, tira, "es-ES")
            try:
                res = future.result(timeout=5)
                if res and res.text:
                    txt = res.text.strip()
                    if txt:
                        print(f"TIRA {i+1}: {txt}")
                        text_completo += " " + txt
            except:
                pass
                
    print("\n--- TEXTO COMBINADO ---")
    print(text_completo)
    
    import re
    # Aplicar la misma logica ultra-tolerante
    txt_norm = text_completo.replace("'92", "192").replace("’92", "192").replace("192 168", "192.168")
    
    ips = []
    ips.extend(re.findall(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b", txt_norm))
    matches = re.findall(r"\b(192)[ .]+(168)[ .]+(\d{1,3})[ .]+(\d{1,3})\b", txt_norm)
    for m in matches:
        ips.append(f"{m[0]}.{m[1]}.{m[2]}.{m[3]}")
        
    print(f"\nIPS ENCONTRADAS: {ips}")

if __name__ == "__main__":
    asyncio.run(main())
