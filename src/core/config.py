"""
Módulo de Configuración del Núcleo.
Importa y expone la configuración global de AgenteProx garantizando coherencia en todo el sistema.
"""
import sys
import os

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

import config as _root_config

# Exponer explícitamente los atributos principales para autocompletado y tipado
DEBUG_PORT = getattr(_root_config, "DEBUG_PORT", 9222)
AGENT_PORT = getattr(_root_config, "AGENT_PORT", 5555)
AGENT_TIMEOUT = getattr(_root_config, "AGENT_TIMEOUT", 5)
TEAMS_CHANNEL_URL = getattr(_root_config, "TEAMS_CHANNEL_URL", "")
TEAMS_SUPPORT_GROUP_NAME = getattr(_root_config, "TEAMS_SUPPORT_GROUP_NAME", "RPA izzi soporte II")
TEAMS_ALERT_GROUP_NAME = getattr(_root_config, "TEAMS_ALERT_GROUP_NAME", "logs_proxmox")
CRITERIOS = getattr(_root_config, "CRITERIOS", [])
CRITERIOS_REGEX = getattr(_root_config, "CRITERIOS_REGEX", [])
LAST_TEAMS_HASH = getattr(_root_config, "LAST_TEAMS_HASH", None)
ALERTS_SENT_CACHE = getattr(_root_config, "ALERTS_SENT_CACHE", set())
LISTA_VMS = getattr(_root_config, "LISTA_VMS", [])
IPS_HIJAS_VIX18 = getattr(_root_config, "IPS_HIJAS_VIX18", [])
VMS_IGNORADAS_TEAMS = getattr(_root_config, "VMS_IGNORADAS_TEAMS", [])
RESPUESTAS_SOPORTE = getattr(_root_config, "RESPUESTAS_SOPORTE", [])
RESPUESTAS_EXITO = getattr(_root_config, "RESPUESTAS_EXITO", [])
CACHED_URLS = getattr(_root_config, "CACHED_URLS", {})

# Exponer el módulo completo para accesos dinámicos
_module = sys.modules[__name__]
for _k, _v in _root_config.__dict__.items():
    if not _k.startswith("__"):
        setattr(_module, _k, _v)
