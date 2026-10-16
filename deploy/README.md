# 🚀 Despliegue del Micro-Agente en VMs (Windows)

Este directorio contiene los artefactos necesarios para instalar y ejecutar el micro-agente espía en cada una de las máquinas virtuales de Proxmox.

---

## 📦 Archivos

| Archivo | Función |
|---|---|
| `vm_agent.py` | Micro-servicio REST HTTP en Flask (puerto TCP 5555) que consulta `/status`, arranca `/start` y detiene `/stop` procesos RPA. |
| `iniciar_agente.bat` | Script por lotes para iniciar el agente en segundo plano. |
| `deploy_masivo.bat` | Script administrativo para copiar `vm_agent.py` de forma automatizada hacia múltiples VMs usando el recurso compartido `\\IP\c$`. |

---

## 🛠 Requisitos en cada VM

1. **Python 3 instalado** y agregado al `PATH`.
2. Dependencias de Python:
   ```cmd
   pip install flask psutil
   ```
3. **Acceso directo en el Escritorio:**
   Debe existir exactamente el archivo:
   `%USERPROFILE%\Desktop\init - Acceso directo.lnk`
   Este acceso directo es el que el agente invoca cuando el orquestador solicita un arranque (`/start`).
4. **Firewall de Windows:**
   - Permitir tráfico entrante en el puerto TCP `5555`.
   - Permitir paquetes entrantes ICMPv4 (Ping).

---

## ⚙ Ejecución Automática al Iniciar Windows
Para que el agente se inicie automáticamente tras cualquier reinicio de la VM:
1. Presionar `Win + R` y escribir:
   ```cmd
   shell:startup
   ```
2. Pegar allí un acceso directo hacia `iniciar_agente.bat`.
