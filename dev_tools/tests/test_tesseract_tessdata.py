import subprocess
import os

tesseract_path = r"C:\Rpa_CX_Bots_Proxmox\Rpa_ExtraccionesAutomatizadas\tesseract\tesseract.exe"
tessdata_path = r"C:\Rpa_CX_Bots_Proxmox\Rpa_ExtraccionesAutomatizadas\tesseract\tessdata"

print(f"Existe Tesseract? {os.path.exists(tesseract_path)}")
print(f"Existe Tessdata? {os.path.exists(tessdata_path)}")

env = os.environ.copy()
env["TESSDATA_PREFIX"] = tessdata_path

try:
    result = subprocess.run([tesseract_path, "teams_latest.png", "stdout"], env=env, capture_output=True, text=True, timeout=10)
    if result.returncode == 0:
        print("ESTADO: EXITO!")
        print(result.stdout)
    else:
        print(f"ESTADO: ERROR {result.returncode}")
        print(result.stderr)
except Exception as e:
    print(f"EXCEPCION: {e}")
