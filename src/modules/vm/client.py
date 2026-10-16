"""
Cliente de Comunicación y Control de Nodos VM (HTTP e ICMP).
"""
import requests
import subprocess
import platform
import time
from src.core import config

def is_pingable(ip: str) -> bool:
    """Envía un paquete ICMP para validar conectividad física con la VM."""
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    cmd = ['ping', param, '1', ip]
    try:
        return subprocess.call(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0
    except:
        return False


def check_process_via_agent(ip: str):
    """
    Consulta el estado de los procesos RPA en el nodo remoto a través del micro-agente.
    Retorna (código_estado, descripción).
    """
    url = f"http://{ip}:{config.AGENT_PORT}/status"
    no_proxy = {"http": None, "https": None}

    try:
        response = requests.get(url, timeout=config.AGENT_TIMEOUT, proxies=no_proxy)
        if response.status_code == 200:
            data = response.json()
            procs = data.get("procesos", [])
            if procs:
                return "activo", f"Activo ({', '.join(procs)})"
            else:
                return "sin_proceso", "Sin procesos RPA corriendo"
        return "error_status", "Agente responde pero status no 200"

    except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError):
        try:
            time.sleep(2.0)
            response = requests.get(url, timeout=10, proxies=no_proxy)
            if response.status_code == 200:
                data = response.json()
                procs = data.get("procesos", [])
                if procs:
                    return "activo", f"Activo ({', '.join(procs)}) [Retry]"
                else:
                    return "sin_proceso", "Sin procesos RPA corriendo [Retry]"
        except:
            if is_pingable(ip):
                return "sin_agente", "PC Encendida | Agente No Inició (Revisar .bat)"
            else:
                return "sin_agente", "Máquina Apagada o Sin Red (Ping Falló)"

    except Exception as e:
        return "sin_agente", f"Error Agente ({str(e)[:20]})"

    return "sin_agente", "Falla General"


def start_bot_via_agent(ip: str) -> bool:
    """Envía la orden de inicio al micro-agente remoto."""
    is_pingable(ip)
    for intento in range(3):
        try:
            url = f"http://{ip}:{config.AGENT_PORT}/start"
            res = requests.post(url, timeout=30, proxies={"http": None, "https": None})
            if res.status_code == 200:
                return True
        except Exception:
            if intento < 2:
                time.sleep(2)
    return False


def stop_bot_via_agent(ip: str) -> bool:
    """Envía la orden de terminación al micro-agente remoto."""
    is_pingable(ip)
    for intento in range(3):
        try:
            url = f"http://{ip}:{config.AGENT_PORT}/stop"
            res = requests.post(url, timeout=30, proxies={"http": None, "https": None})
            if res.status_code == 200:
                return True
        except Exception:
            if intento < 2:
                time.sleep(2)
    return False


def wait_bot_state(ip: str, desired_state: str, timeout_sec=90, poll_sec=3) -> bool:
    """Espera activamente a que el bot alcance un estado deseado ('activo' o 'no_activo')."""
    t0 = time.time()
    while time.time() - t0 < timeout_sec:
        st, _ = check_process_via_agent(ip)
        if desired_state == "activo" and st == "activo":
            return True
        if desired_state == "no_activo" and st != "activo":
            return True
        time.sleep(poll_sec)
    return False
