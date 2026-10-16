"""
Adaptador de Compatibilidad Hacia Atrás — vm_utils.
Reexporta los componentes modulares de VM, Izzi y Remediación según las especificaciones SPEC-04 y SPEC-05.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.modules.vm.client import (
    is_pingable,
    check_process_via_agent,
    start_bot_via_agent,
    stop_bot_via_agent,
    wait_bot_state,
)
from src.modules.vm.remediator import (
    remediate_ips,
    check_and_handle_support_message,
    LAST_PROCESSED_TEXT,
)
from src.modules.izzi.activator import activate_izzi_process
from src.modules.izzi.keep_alive import izzi_keep_alive
from src.modules.parsing.ip_extractor import extract_ips
from src.modules.parsing.criteria import matches_criteria

__all__ = [
    "is_pingable",
    "check_process_via_agent",
    "start_bot_via_agent",
    "stop_bot_via_agent",
    "wait_bot_state",
    "remediate_ips",
    "check_and_handle_support_message",
    "LAST_PROCESSED_TEXT",
    "activate_izzi_process",
    "izzi_keep_alive",
    "extract_ips",
    "matches_criteria",
]
