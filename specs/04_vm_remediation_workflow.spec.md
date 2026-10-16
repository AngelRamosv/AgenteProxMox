# SPEC-04: Flujo de Remediación y Soporte de VMs

## 1. Alcance
Define la máquina de estados y temporizadores involucrados en la atención automatizada de solicitudes de soporte desde Teams y la auto-recuperación de bots inactivos.

## 2. Diagrama de Flujo de Soporte y Remediación

```mermaid
sequenceDiagram
    autonumber
    actor Soporte as Usuario Teams
    participant Bot as Teams Listener
    participant Remed as VM Remediator
    participant Node as Nodo VM (:5555)
    participant Izzi as Portal Izzi

    Soporte->>Bot: "Favor de revisar la ip 192.168.49.77"
    Bot->>Remed: Mensaje nuevo + Criterio Coincidente + IPs detectadas
    Remed->>Remed: Espera orgánica de 60s
    Remed->>Soporte: Autoreply: "Lo checamos un momento por favor..."
    Remed->>Remed: Espera técnica de 30s
    
    loop Por cada IP detectada
        Remed->>Node: POST /stop (Timeout 30s, 3 intentos)
        Remed->>Node: Poll GET /status hasta 'sin_proceso' (máx 90s)
        Remed->>Remed: Pausa de seguridad de 60s (cierre de consolas)
        Remed->>Node: POST /start (Timeout 30s, 3 intentos)
        Remed->>Node: Poll GET /status hasta 'activo' (máx 120s)
        Remed->>Izzi: Activar robot en dashboard (Dropdown -> Iniciar Proceso -> Confirmar)
    end
    
    Remed->>Remed: Espera orgánica de 60s
    Remed->>Soporte: Confirmación final: "Las maquinas ya estan trabajando 192.168.49.77"
```

## 3. Temporizadores Críticos
- **Espera previa al Autoreply:** `60 segundos` (imita el tiempo de lectura humano).
- **Espera post-Autoreply:** `30 segundos` antes de iniciar la remediación.
- **Timeout confirmación STOP:** `90 segundos` con sondeo cada `3 segundos`.
- **Pausa de Seguridad STOP $\to$ START:** `60 segundos` indispensables para asegurar que las conexiones de red y sesiones de consola cierren limpiamente en Windows.
- **Timeout confirmación START:** `120 segundos` con sondeo cada `3 segundos`.
- **Espera previa a Confirmación Final:** `60 segundos`.

## 4. Gestión de Reintentos de Conexión
Toda llamada HTTP a los micro-agentes de las VMs debe:
- Ignorar proxies del sistema (`proxies={"http": None, "https": None}`).
- Realizar hasta 3 intentos con pausas de 2 segundos en caso de fallo transitorio.
- Precalentar la ruta de red con un paquete ICMP (`is_pingable`).
