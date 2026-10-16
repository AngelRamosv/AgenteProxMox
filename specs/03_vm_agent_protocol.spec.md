# SPEC-03: Protocolo del Micro-Agente en Máquinas Virtuales

## 1. Alcance
Define el contrato de servicio REST del componente `vm_agent.py` desplegado en cada VM Proxmox (puerto TCP 5555). Regula la clasificación de procesos, políticas de terminación y arranque.

## 2. Parámetros del Agente
- **Puerto:** `5555`
- **Host:** `0.0.0.0`
- **Ruta de Acceso Directo de Inicio:** `%USERPROFILE%\Desktop\init - Acceso directo.lnk`
- **Umbral de Memoria para Navegadores:** `40 MB`
- **Procesos Críticos Monitoreados:**
  - `cmd.exe`
  - `chrome.exe`
  - `iexplore.exe`
  - `msedge.exe`
  - `javaw.exe`
  - `siebel.exe`
  - `python.exe` / `pythonw.exe` / `py.exe` (excluyendo el propio agente `vm_agent.py`)

## 3. Endpoints REST

### 3.1 `GET /status`
Retorna el estado de los procesos RPA en el equipo.
- **Respuesta 200 OK (Activo):**
  ```json
  {
    "status": "activo",
    "procesos": ["chrome.exe"]
  }
  ```
- **Respuesta 200 OK (Inactivo):**
  ```json
  {
    "status": "sin_proceso",
    "procesos": []
  }
  ```

### 3.2 `POST /start`
Desencadena la ejecución de la rutina de inicio del bot (`init - Acceso directo.lnk`).
- **Respuesta 200 OK:**
  ```json
  {
    "result": "iniciado"
  }
  ```
- **Respuesta 404 Not Found (Falta archivo):**
  ```json
  {
    "result": "error"
  }
  ```

### 3.3 `POST /stop`
Ejecuta la terminación controlada en 2 fases:
1. **Fase Suave (`terminate`):**
   - Recorre procesos activos vía `psutil`.
   - **Regla de Protección:** No terminar el proceso propio (`os.getpid()`) ni su proceso padre (la consola cmd que hospeda el agente).
   - Enviar `terminate()` a procesos críticos y bots de Python.
2. **Período de Gracia:**
   - Esperar 2.0 segundos.
3. **Fase Forzada (`kill`):**
   - Si los procesos continúan en memoria, ejecutar `kill()`.
- **Respuesta 200 OK:**
  ```json
  {
    "result": "detenido",
    "terminados": ["chrome.exe:1420", "cmd.exe:884"]
  }
  ```
