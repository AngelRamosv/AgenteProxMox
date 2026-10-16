# 📐 Spec-Driven Development (SDD) — AgenteProx

Este directorio contiene las especificaciones formales que rigen la arquitectura, contratos de interfaces, protocolos de comunicación y flujos operativos de **AgenteProx**.

Bajo la metodología **Spec-Driven Development (SDD)**, toda funcionalidad, refactorización o adición al código debe adherirse estrictamente a estas especificaciones técnicas para garantizar estabilidad, mantenibilidad y compatibilidad operativa.

---

## 📑 Índice de Especificaciones

| Código | Especificación | Descripción |
|---|---|---|
| **[SPEC-01]** | [01_system_architecture.spec.md](01_system_architecture.spec.md) | Arquitectura del sistema, topología de red, integración CDP con Chrome y ciclo de vida del orquestador. |
| **[SPEC-02]** | [02_teams_and_ocr.spec.md](02_teams_and_ocr.spec.md) | Monitoreo de Microsoft Teams, motor WinOCR nativo, extracción difusa de IPs y criterios de soporte. |
| **[SPEC-03]** | [03_vm_agent_protocol.spec.md](03_vm_agent_protocol.spec.md) | Contrato de API REST HTTP del micro-agente en VMs (`/status`, `/start`, `/stop`), gestión de procesos y memoria. |
| **[SPEC-04]** | [04_vm_remediation_workflow.spec.md](04_vm_remediation_workflow.spec.md) | Máquina de estados de auto-remediación, tiempos de espera orgánica (60s), reintentos y confirmaciones. |
| **[SPEC-05]** | [05_izzi_portal_automation.spec.md](05_izzi_portal_automation.spec.md) | Automatización web de `frontrpaizzi` (PrimeNG), navegación P1/P2, diálogo de confirmación y Keep-Alive anti-sueño. |
| **[SPEC-06]** | [06_configuration_schema.spec.md](06_configuration_schema.spec.md) | Esquema de configuración global, inventario de VMs, listas negras de alertas y respuestas predefinidas. |

---

## 🏛 Principios de Diseño Modular

1. **Desacoplamiento Estricto:** Cada módulo en `src/modules/` es autónomo y no depende de estados globales mutables no encapsulados.
2. **Cero Interrupción del Usuario:** Las interacciones del navegador (Teams, izzi) operan en segundo plano evitando robar el foco (`bring_to_front`) a menos que sea estrictamente necesario para la visibilidad de un modal.
3. **Resiliencia y Auto-Recuperación:** Fallos en el navegador o en la red local no detienen el ciclo de escaneo; el orquestador captura las excepciones de desconexión y se reconecta automáticamente en el siguiente ciclo.
4. **Compatibilidad Hacia Atrás:** La raíz del proyecto mantiene adaptadores transparentes (`agente_prox.py`, `config.py`, `teams_bot.py`, `vm_utils.py`) para asegurar que scripts por lotes y accesos directos existentes continúen operando sin modificación.
