"""
Orquestador de Remediación y Gestión de Solicitudes de Soporte.
"""
import time
import random
from src.core import config
from src.modules.vm.client import (
    stop_bot_via_agent,
    start_bot_via_agent,
    wait_bot_state,
)
from src.modules.izzi.activator import activate_izzi_process
from src.modules.teams.reader import read_latest_message_from_group
from src.modules.teams.sender import send_teams_message
from src.modules.parsing.criteria import matches_criteria
from src.modules.parsing.ip_extractor import extract_ips

# Estado en memoria para evitar bucles de reinicio con el mismo mensaje
LAST_PROCESSED_TEXT = None

def remediate_ips(browser, ips: list) -> list:
    """
    Ejecuta el ciclo completo de remediación (STOP -> pausa 60s -> START -> Izzi)
    para cada dirección IP especificada. Retorna las IPs exitosas.
    """
    verdes = []
    for ip in ips:
        print(f"[VSCode] Analizando equipo... {ip}")
        print(f"[VSCode] Reiniciando bot (STOP/START) para IP: {ip}")

        ok_stop_cmd = stop_bot_via_agent(ip)
        if not ok_stop_cmd:
            print(f"[VSCode] Error: No se pudo enviar STOP a {ip}")
            continue

        ok_stop_state = wait_bot_state(ip, desired_state="no_activo", timeout_sec=90, poll_sec=3)
        if not ok_stop_state:
            print(f"[VSCode] Error: STOP no confirmado (timeout) en {ip}")

        print(f"[VSCode] PAUSA DE SEGURIDAD (60s) para verificar cierre de consolas en {ip}...")
        time.sleep(60)

        print(f"[VSCode] Ejecutando START para IP: {ip}")

        ok_start_cmd = start_bot_via_agent(ip)
        if not ok_start_cmd:
            print(f"[VSCode] Error: No se pudo enviar START a {ip}")
            continue

        ok_start_state = wait_bot_state(ip, desired_state="activo", timeout_sec=120, poll_sec=3)
        if ok_start_state:
            if browser:
                if activate_izzi_process(browser, ip):
                    verdes.append(ip)
            print(f"[VSCode] Reiniciando bot de equipo ({ip}) exitosamente")
        else:
            print(f"[VSCode] Error: START no confirmado (timeout) en {ip}")
            
    return verdes


def check_and_handle_support_message(browser, page_proxmox):
    """
    Inspecciona el chat de soporte en Teams. Si detecta una solicitud válida:
    1. Envía autoreply tras 60s.
    2. Espera 30s y ejecuta remediate_ips.
    3. Confirma el éxito tras 60s.
    """
    global LAST_PROCESSED_TEXT
    
    force_read = (LAST_PROCESSED_TEXT is None)
    res = read_latest_message_from_group(browser, config.TEAMS_SUPPORT_GROUP_NAME, page_proxmox=page_proxmox, force_read=force_read)
    if not res:
        return

    msg_text = res["text"].strip()
    if LAST_PROCESSED_TEXT and msg_text == LAST_PROCESSED_TEXT.strip():
        return

    print("[PAUSA] Mensaje nuevo detectado en Teams (soporte)")
    print(f"    [TEAMS LEIDO] Contenido Validado: \"{msg_text}\"")
    
    LAST_PROCESSED_TEXT = msg_text
    msg_low = msg_text.lower()

    if not matches_criteria(msg_low):
        print("[VSCode] El analisis no corresponde con los criterios reanudando escaneo...")
        return

    ips = extract_ips(msg_low)
    ips = list(set(ips))
    
    if not ips:
        print("[VSCode] El analisis coincide con criterios, pero no se detectaron IPs...")
        return

    print("[VSCode] Analizando... coincide con criterios")
    print(f"[VSCode] Reiniciando {len(ips)} IPs: {', '.join(ips)}")

    # Autoreply Inicial
    try:
        if browser and hasattr(config, 'RESPUESTAS_SOPORTE'):
            frase = random.choice(config.RESPUESTAS_SOPORTE)
            print("[VSCode] Esperando 1 minuto antes de enviar autoreply...")
            time.sleep(60) 
            print(f"    [VSCode] Enviando respuesta autoreply: '{frase}'...")
            send_teams_message(
                browser, 
                message=frase, 
                target_chat=config.TEAMS_SUPPORT_GROUP_NAME,
                reply_to_locator=None,
                force_quote=False
            )
            LAST_PROCESSED_TEXT = frase.strip()

            print("[VSCode] Esperando 30s antes de proceder con el reinicio...")
            time.sleep(30) 
    except Exception as e:
        print(f"[VSCode] Nota: No se envió autoreply ({e})")

    # Ejecutar remediación
    exitos = remediate_ips(browser, ips)
    
    # Mensaje Final de Confirmación
    if exitos:
        try:
            print("[VSCode] Esperando 1 minuto antes de la confirmación final...")
            time.sleep(60)
            
            frase_exito = random.choice(config.RESPUESTAS_EXITO)
            msg_final = f"{frase_exito} {', '.join(exitos)}"
            
            print(f"[VSCode] Enviando confirmación final (mensaje normal): '{msg_final}'...")
            send_teams_message(
                browser,
                message=msg_final,
                target_chat=config.TEAMS_SUPPORT_GROUP_NAME,
                reply_to_locator=None,
                force_quote=False
            )
            LAST_PROCESSED_TEXT = msg_final.strip()
        except Exception as e_fin:
            print(f"[VSCode] Error enviando confirmación final: {e_fin}")

    print("[REANUDAR] Terminado soporte, retomando escaneo normal.\n")
