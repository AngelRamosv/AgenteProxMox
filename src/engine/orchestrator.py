"""
Motor Orquestador Principal de AgenteProx.
Ejecuta el ciclo de vigilancia continua, auto-reparación y espera activa.
"""
from playwright.sync_api import sync_playwright
import time
import re
from src.core import config
from src.core.exceptions import BrowserClosedError, is_browser_closed_exception
from src.core.browser import check_and_recover_page
from src.modules.teams.sender import send_teams_message
from src.modules.teams.reader import read_latest_message_from_group
from src.modules.vm.client import (
    check_process_via_agent,
    start_bot_via_agent,
)
from src.modules.vm.remediator import (
    check_and_handle_support_message,
)
from src.modules.izzi.keep_alive import izzi_keep_alive

def run_orchestrator():
    """Ejecuta el ciclo infinito de vigilancia y remediación de AgenteProx."""
    print("=" * 60)
    print(" AGENTE PROXMOX - MODO VIGILANCIA RPA (MODULAR SDD)")
    print("=" * 60 + "\n")

    # Cache local para lógica de reportes diarios
    ALERTS_SENT_CACHE = set()

    with sync_playwright() as p:
        while True:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            msg_inicio = f"[{timestamp}] INICIANDO CICLO DE ESCANEO..."
            print(msg_inicio)
            print(f"{'VIX':<24} | {'IP':<15} | PROCESO")
            print("-" * 60)

            try:
                browser = p.chromium.connect_over_cdp(f"http://localhost:{config.DEBUG_PORT}", timeout=15000)
                context = browser.contexts[0]
                page = None
                for pg in context.pages:
                    if ":8006" in pg.url.lower():
                        page = pg
                        break
                
                # Notificación de inicio de ciclo
                send_teams_message(browser, msg_inicio)

                if not page:
                    print("    [INFO] Pestaña Proxmox (:8006) no detectada. (Modo solo Teams / Izzi)")

                if page:
                    check_and_recover_page(page)
                
                time.sleep(0.1)

            except Exception as e:
                print(f"[ERROR] Conexión Navegador: {e}")
                page = None
                browser = None

            # >>> Chequeo INICIAL de soporte <<<
            if browser:
                if page:
                    check_and_recover_page(page)
                try:
                    check_and_handle_support_message(browser, page)
                except BrowserClosedError as e:
                    print(f"    [WARN] Navegador cerrado o desconectado durante chequeo inicial: {e}")
                    browser = None
                    page = None

            # Iterar sobre la lista de máquinas virtuales
            vm_scanned_count = 0
            for target_vmid, target_ip in config.LISTA_VMS:
                vm_scanned_count += 1
                
                if browser and (not browser.is_connected()):
                    print("    [WARN] Navegador desconectado. Abortando escaneo con navegador...")
                    browser = None
                    page = None
                
                # >>> Chequeo INTERMEDIO (ciclo por VM) <<<
                if browser:
                    if page:
                        check_and_recover_page(page)
                    try:
                        check_and_handle_support_message(browser, page)
                    except BrowserClosedError as e:
                        print(f"    [WARN] Navegador cerrado o desconectado durante chequeo intermedio: {e}")
                        browser = None
                        page = None
                    
                    # >>> Clic Anti-Sueño Izzi cada 5 máquinas <<<
                    if browser and vm_scanned_count % 5 == 0:
                        try:
                            izzi_keep_alive(browser, page)
                        except BrowserClosedError as e:
                            print(f"    [WARN] Navegador cerrado o desconectado durante keep-alive Izzi: {e}")
                            browser = None
                            page = None

                display_name = f"{target_vmid} (Agente)"
                visual_status = "unknown"

                if page:
                    try:
                        page.wait_for_selector(".x-grid-item", timeout=3000)
                        row_vm = page.locator(".x-grid-item").filter(has_text=re.compile(rf"^{re.escape(target_vmid.split()[0])}\s")).first
                        if row_vm.count() > 0 and row_vm.is_visible():
                            try:
                                full_text = row_vm.inner_text().split("\n")[0]
                                display_name = full_text.strip()
                            except: 
                                display_name = str(target_vmid)

                            row_html = row_vm.inner_html().lower()
                            if "stop" in row_html or "gray" in row_html:
                                visual_status = "stopped"
                            elif "play" in row_html or "running" in row_html:
                                visual_status = "running"
                    except Exception as e_vis:
                        if is_browser_closed_exception(e_vis):
                            print(f"    [WARN] Navegador cerrado o desconectado al verificar estado visual: {e_vis}")
                            browser = None
                            page = None
                        else:
                            pass

                print(f"    [INFO] ID: {display_name:<18} | Consultando {target_ip}...")

                if target_ip == "0.0.0.0":
                    status = "sin_agente"
                    resultado_txt = "Máquina Apagada o Sin Red (Sin IP)"
                elif visual_status == "stopped":
                    status = "sin_agente"
                    resultado_txt = "Máquina Apagada o Sin Red (Visual)"
                else:
                    status, resultado_txt = check_process_via_agent(target_ip)

                if status == "sin_proceso":
                    print(f"    [WARN] Inactivo. Comprobando arranque de bot...")
                    if start_bot_via_agent(target_ip):
                        time.sleep(12.0)
                        st_2, res_2 = check_process_via_agent(target_ip)
                        resultado_txt = (
                            f"REINICIADO (Antes: {resultado_txt}) -> Ahora: {res_2}"
                        )
                    else:
                        resultado_txt = f"FALLO REINICIO (Antes: {resultado_txt})"

                # --- LÓGICA DE ALERTAS Y FILTROS ---
                keywords = ["Fallo", "Error", "Sin", "Apagada", "Inaccesible", "Detenido", "No Inició"]
                current_id_clean = str(target_vmid).split('(')[0].strip()
                blacklist_clean = [str(x).split('(')[0].strip() for x in config.VMS_IGNORADAS_TEAMS]

                if any(k in resultado_txt for k in keywords):
                    if current_id_clean not in blacklist_clean:
                        if "vix18" not in display_name.lower():
                            today_str = time.strftime("%Y-%m-%d")
                            alert_key = f"{target_ip}|{resultado_txt}|{today_str}"
                            
                            if alert_key not in ALERTS_SENT_CACHE:
                                msg_alerta = f"{display_name} | {target_ip} | {resultado_txt}"
                                if browser:
                                    try:
                                        sent_ok = send_teams_message(browser, msg_alerta, target_chat=config.TEAMS_ALERT_GROUP_NAME)
                                        if sent_ok:
                                            ALERTS_SENT_CACHE.add(alert_key)
                                    except BrowserClosedError as e:
                                        print(f"    [WARN] Navegador cerrado o desconectado al enviar alerta Teams: {e}")
                                        browser = None
                                        page = None
                            else:
                                print(f"    [SILENCIO] Alerta ya enviada hoy para {target_ip}")
                    else:
                        print(f"    [SILENCIO TEAM] VM {target_vmid} ignorada intencionalmente.")

                print(f"{display_name:<24} | {target_ip:<15} | {resultado_txt}")

                # --- LÓGICA VIX18 (Hijas) ---
                if "130" in str(target_vmid) or "vix18" in display_name.lower():
                    print(f"\n    [INFO] VIX18 DETECTADA - Escaneando hijas...")
                    print("    " + "." * 50)
                    for ip_h in config.IPS_HIJAS_VIX18:
                        if browser:
                            if page:
                                check_and_recover_page(page)
                            try:
                                check_and_handle_support_message(browser, page)
                            except BrowserClosedError as e:
                                print(f"    [WARN] Navegador cerrado o desconectado durante escaneo de hijas: {e}")
                                browser = None
                                page = None

                        s_h, txt_h = check_process_via_agent(ip_h)
                        if s_h == "sin_proceso":
                            start_bot_via_agent(ip_h)
                            time.sleep(5)
                            _, txt_h = check_process_via_agent(ip_h)
                            txt_h = "Reactivado (Hija)"

                        print(f"    -> [HIJA] {ip_h:<15} | {txt_h}")
                    print("    " + "." * 50 + "\n")

                print("-" * 60)

            print(f"\n[{time.strftime('%H:%M:%S')}] Escaneo completo. Esperando 30 minutos (Modo Vigilancia Soporte)...")
            
            # --- ESPERA ACTIVA (Soporte) ---
            try:
                for active_step in range(60):  # 60 * 30s = 30 min
                    if browser:
                        if not browser.is_connected():
                            print("    [WARN] Navegador cerrado o desconectado. Esperando reconexión en el siguiente ciclo...")
                            browser = None
                            page = None
                            break
                        if page:
                            check_and_recover_page(page)
                        try:
                            check_and_handle_support_message(browser, page)
                        except BrowserClosedError as e:
                            print(f"    [WARN] Navegador cerrado o desconectado en espera activa: {e}")
                            browser = None
                            page = None
                            break
                        except Exception as e_active:
                            print(f"    [WARN] Error de conexión en espera activa: {e_active}")
                            browser = None
                            page = None
                            break
                            
                        # Clic Anti-Sueño Izzi cada 10 pasos (5 minutos)
                        if active_step % 10 == 0:
                            try:
                                izzi_keep_alive(browser, page)
                            except BrowserClosedError as e:
                                print(f"    [WARN] Navegador cerrado o desconectado en keep-alive de espera activa: {e}")
                                browser = None
                                page = None
                                break
                            except Exception:
                                pass
                    time.sleep(30)
            except KeyboardInterrupt:
                break


def main():
    """Punto de entrada compatible."""
    run_orchestrator()

if __name__ == "__main__":
    main()
