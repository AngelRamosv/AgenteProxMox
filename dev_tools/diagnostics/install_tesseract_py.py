import urllib.request
import subprocess
import os

url = "https://github.com/UB-Mannheim/tesseract/releases/download/v5.4.0.20240606/tesseract-ocr-w64-setup-5.4.0.20240606.exe"
out_file = r"C:\Users\sistemas\Desktop\AgenteProx\tesseract_setup.exe"
install_dir = r"C:\Users\sistemas\Desktop\AgenteProx\tesseract_new"

print("Descargando Tesseract (30MB)...")
req = urllib.request.Request(
    url, 
    data=None, 
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
)

with urllib.request.urlopen(req) as response, open(out_file, 'wb') as out:
    data = response.read()
    out.write(data)

print(f"Descargado exitosamente ({len(data) / 1024 / 1024:.2f} MB).")
print("Instalando silenciosamente...")

result = subprocess.run([out_file, "/S", f"/D={install_dir}"], capture_output=True, text=True)

if result.returncode == 0:
    print(f"Instalación exitosa en {install_dir}")
else:
    print(f"Fallo instalacion: {result.returncode}")
    print(result.stderr)
