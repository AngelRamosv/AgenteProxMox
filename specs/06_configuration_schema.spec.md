# SPEC-06: Esquema de Configuración Global

## 1. Alcance
Define las variables de entorno, puertos, destinos de Microsoft Teams, criterios semánticos, inventarios de máquinas virtuales y listas negras de notificación.

## 2. Parámetros de Red y Conectividad
- `DEBUG_PORT` (int): Puerto CDP local de Chrome (`9222`).
- `AGENT_PORT` (int): Puerto HTTP de los micro-agentes (`5555`).
- `AGENT_TIMEOUT` (int): Tiempo de espera inicial para consultas `/status` (`5` segundos).
- `TEAMS_CHANNEL_URL` (str): Enlace directo de respaldo al canal `logs_proxmox`.

## 3. Destinos de Mensajería
- `TEAMS_SUPPORT_GROUP_NAME` (str): Nombre exacto del chat o grupo donde se escuchan las peticiones de reinicio (`"RPA izzi soporte II"`).
- `TEAMS_ALERT_GROUP_NAME` (str): Canal o chat destino para los reportes de fallo y ciclo (`"logs_proxmox"`).

## 4. Criterios de Detección de Soporte
- `CRITERIOS` (list[str]): Coincidencias de texto literal en minúsculas (ej. `"bot detenido"`, `"sin conexión"`).
- `CRITERIOS_REGEX` (list[str]): Expresiones regulares que abarcan verbos de acción (`revisar`, `checar`, `validar`), pedidos de auxilio (`apoyo`, `ayuda`), términos técnicos (`conectar`, `reinic`) y estados de error (`falla`, `traba`, `pasm`).

## 5. Inventario de VMs
- `LISTA_VMS` (list[tuple[str, str]]): Tuplas compuestas por `(ID_VISUAL, DIRECCIÓN_IP)`.
- `IPS_HIJAS_VIX18` (list[str]): Colección de 38 direcciones IP pertenecientes a la máquina padre VIX18 (`130(vix18)`).
- `VMS_IGNORADAS_TEAMS` (list[str]): Lista negra de identificadores de VM que no deben generar alertas en Teams bajo ninguna circunstancia.

## 6. Respuestas Predefinidas
- `RESPUESTAS_SOPORTE` (list[str]): Pool de mensajes emitidos en el Autoreply inicial.
- `RESPUESTAS_EXITO` (list[str]): Pool de mensajes emitidos en la confirmación de remediación exitosa.
