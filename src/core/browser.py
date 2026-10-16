"""
Gestor de Ciclo de Vida del Navegador y Recuperación de Pestañas (CDP).
"""
import time
import re
from src.core.exceptions import BrowserClosedError, is_browser_closed_exception
from src.core import config

LAST_PREVENTIVE_RELOADS = {}

def check_and_recover_page(page, force_reload=False):
    """
    Verifica el estado de una pestaña activa.
    Aplica el hack de visibilidad, recarga preventiva cada 2 horas y auto-recuperación si colapsa.
    """
    global LAST_PREVENTIVE_RELOADS
    
    if not page or page.is_closed():
        return False
        
    current_time = time.time()
    page_url = page.url or ""
    
    # Identificar tipo de página para llevar control de recargas independiente
    page_key = None
    if "teams.microsoft.com" in page_url:
        page_key = "teams"
    elif "frontrpaizzi" in page_url:
        page_key = "izzi"
    elif ":8006" in page_url:
        page_key = "proxmox"
        
    if page_key:
        if page_key not in LAST_PREVENTIVE_RELOADS:
            LAST_PREVENTIVE_RELOADS[page_key] = current_time
        elif current_time - LAST_PREVENTIVE_RELOADS[page_key] > 7200:
            print(f"    [INFO] Ejecutando recarga preventiva de {page_key.upper()} para liberar memoria (límite 2h)...")
            force_reload = True
            LAST_PREVENTIVE_RELOADS[page_key] = current_time

    # Asegurar visibilidad en segundo plano (Visibility Hack)
    try:
        page.evaluate(
            "Object.defineProperty(document, 'visibilityState', {value: 'visible', writable: true}); "
            "document.dispatchEvent(new Event('visibilitychange'));"
        )
    except:
        pass

    try:
        # Detectar y manejar la pantalla de lanzamiento de Teams (Evita quedarse atrapado en 'dl/launcher')
        if "teams.microsoft.com" in page_url and ("launcher.html" in page_url or "dl/launcher" in page_url):
            print("    [WARN] Detectada pantalla de lanzamiento de Teams. Intentando redirección a versión web...")
            try:
                btn_web = page.locator("button, a, div").filter(has_text=re.compile(r"(Usar la aplicación web en su lugar|Use the web app instead)", re.IGNORECASE)).first
                if btn_web.count() > 0 and btn_web.is_visible():
                    btn_web.click(force=True)
                    time.sleep(3.0)
                    print("    [INFO] Clic en 'Usar la aplicación web en su lugar' enviado.")
                    page_url = page.url or ""
            except Exception as e_launch:
                print(f"    [DEBUG] No se pudo hacer redirección web: {e_launch}")

        if force_reload:
            raise Exception("Force reload requested for memory cleanup")
            
        page.wait_for_function("true", timeout=3000)
        return True
    except Exception as e:
        msg = str(e).lower()
        if force_reload or any(x in msg for x in ["crashed", "crash", "closed", "timeout", "detached"]):
            print(f"    [WARN] Pestaña caída, congelada o solicitada recarga para liberar memoria ({e}). Recargando...")
            try:
                page.reload(timeout=20000)
                time.sleep(2.0)
                page.wait_for_function("true", timeout=5000)
                
                try:
                    page.evaluate(
                        "Object.defineProperty(document, 'visibilityState', {value: 'visible', writable: true}); "
                        "document.dispatchEvent(new Event('visibilitychange'));"
                    )
                except: pass
                
                print("    [INFO] Pestaña recuperada/recargada con éxito.")
                return True
            except Exception as e_reload:
                print(f"    [ERROR] Falló la recarga de pestaña: {e_reload}. Intentando navegación directa...")
                try:
                    url_dest = page_url or config.TEAMS_CHANNEL_URL
                    page.goto(url_dest, timeout=25000)
                    time.sleep(2.0)
                    page.wait_for_function("true", timeout=5000)
                    
                    try:
                        page.evaluate(
                            "Object.defineProperty(document, 'visibilityState', {value: 'visible', writable: true}); "
                            "document.dispatchEvent(new Event('visibilitychange'));"
                        )
                    except: pass
                    
                    print("    [INFO] Pestaña recuperada con éxito mediante navegación directa.")
                    return True
                except Exception as e_goto:
                    print(f"    [ERROR] Falló la navegación directa de recuperación: {e_goto}. Cerrando pestaña muerta.")
                    try:
                        page.close()
                    except:
                        pass
        else:
            print(f"    [WARN] Excepción no crítica en comprobación de pestaña: {e}")
    return False


def get_teams_page(browser):
    """Localiza o crea la pestaña de Microsoft Teams en el navegador conectado."""
    try:
        if not browser: return None
        if not browser.is_connected():
            raise BrowserClosedError("El navegador no está conectado.")
        if not browser.contexts: return None
        
        # 1. Buscar si ya existe la pestaña
        for ctx in browser.contexts:
            for pg in ctx.pages:
                try:
                    if pg.is_closed():
                        continue
                    if "teams.microsoft.com" in pg.url:
                        return pg
                except Exception as e:
                    if is_browser_closed_exception(e):
                        raise BrowserClosedError("La página fue cerrada o desconectada.") from e
                        
        # 2. Si no existe, la abrimos automáticamente
        print("    [INFO] No se encontró la pestaña de Teams. Abriendo pestaña nueva...")
        context = browser.contexts[0]
        new_page = context.new_page()
        new_page.goto(config.TEAMS_CHANNEL_URL, wait_until="commit", timeout=15000)
        time.sleep(3.0)
        return new_page
        
    except BrowserClosedError:
        raise
    except Exception as e:
        if is_browser_closed_exception(e):
            raise BrowserClosedError("Error de navegador cerrado en get_teams_page.") from e
    return None
