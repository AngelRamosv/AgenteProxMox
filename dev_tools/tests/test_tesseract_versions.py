import subprocess
import os

CANDIDATE_TESSERACT_PATHS = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    r"C:\Users\sistemas\AppData\Local\Programs\Tesseract-OCR\tesseract.exe",
    r"C:\Rpa_CX_Bots_Proxmox\Rpa_ExtraccionesAutomatizadas\tesseract\tesseract.exe",
    r"C:\Rpa_CX_Bots_Proxmox\Rpa_Depuracion_CC\tesseract\tesseract.exe"
]

for path in CANDIDATE_TESSERACT_PATHS:
    if os.path.exists(path):
        print(f"\nProbando Tesseract en: {path}")
        try:
            # Ejecutar con --version para ver si crashea
            result = subprocess.run([path, "--version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                print("ESTADO: EXITO - Funciona correctamente!")
                print(result.stdout.strip().split('\n')[0])
            else:
                print(f"ESTADO: ERROR {result.returncode}")
                print(result.stderr)
        except Exception as e:
            print(f"ESTADO: EXCEPCION - {e}")
    else:
        print(f"No existe: {path}")
