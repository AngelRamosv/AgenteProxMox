# 🛡️ AgenteProx — Spec-Driven Development (SDD) & Modular Architecture

Sistema automatizado de vigilancia de infraestructura, auto-remediación de procesos y atención de soporte L1 para bots RPA desplegados en Proxmox VE.

---

## 🏛️ Estructura del Proyecto

El proyecto se encuentra organizado bajo una estructura modular limpia y profesional:

```
AgenteProx/
├── specs/                          # 📐 ESPECIFICACIONES FORMALES (SDD)
│   ├── README.md                   # Índice general y principios rectores
│   ├── 01_system_architecture.spec.md  # Arquitectura, topología y ciclo orquestador
│   ├── 02_teams_and_ocr.spec.md    # Selectores Teams, WinOCR e IP parsing
│   ├── 03_vm_agent_protocol.spec.md# Contrato API REST HTTP de las VMs (/status, /start, /stop)
│   ├── 04_vm_remediation_workflow.spec.md # Máquina de estados y temporizadores de soporte
│   ├── 05_izzi_portal_automation.spec.md  # PrimeNG, P1/P2 y keep-alive anti-sueño
│   └── 06_configuration_schema.spec.md   # Esquema de configuración y variables globales
│
├── src/                            # 🧩 CÓDIGO FUENTE MODULAR
│   ├── core/                       # Núcleo del sistema (browser, config, exceptions)
│   ├── modules/                    # Módulos de dominio (ocr, parsing, teams, izzi, vm)
│   └── engine/                     # Orquestador del bucle principal
│
├── deploy/                         # 🚀 ARTEFACTOS DE INSTALACIÓN EN VMS
│   ├── vm_agent.py                 # Micro-agente HTTP Flask
│   ├── iniciar_agente.bat          # Lanzador local en VM
│   ├── deploy_masivo.bat           # Despliegue administrativo por red
│   └── README.md                   # Guía de instalación y autoinicio (shell:startup)
│
├── dev_tools/                      # 🔬 HERRAMIENTAS HISTÓRICAS Y DIAGNÓSTICO
│   ├── tests/                      # Scripts de pruebas aisladas (test_*.py)
│   ├── troubleshooting/            # Scripts de diagnóstico (troubleshoot_*.py, scratch)
│   ├── diagnostics/                # Instaladores, scripts de inspección y file_prox
│   ├── legacy_adapters/            # Adaptadores de compatibilidad histórica (teams_bot, vm_utils)
│   └── samples_and_dumps/          # Capturas de prueba, volcados DOM e imágenes
│
├── agente_prox.py                  # 🏁 Punto de entrada principal para ejecutar el agente
├── config.py                       # ⚙️ Archivo de configuración principal (parámetros y listas)
└── README.md                       # 📖 Documentación general
```

---

## 🚀 Inicio Rápido

### 1. Iniciar Google Chrome en Modo Depuración
```cmd
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\ChromeBot"
```
Asegúrate de tener abiertas las sesiones autenticadas de Teams, Izzi y Proxmox.

### 2. Ejecutar AgenteProx
```cmd
cd C:\Users\sistemas\Desktop\AgenteProx
.venv\Scripts\python.exe agente_prox.py
```
O simplemente ejecutando `python agente_prox.py` dentro de tu entorno virtual.
