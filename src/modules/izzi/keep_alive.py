"""
Rutina de Mantenimiento de Sesión y Keep-Alive Anti-Sueño para Izzi.
"""
import time
from src.core.exceptions import BrowserClosedError, is_browser_closed_exception
from src.core.browser import check_and_recover_page

def izzi_keep_alive(browser, page_proxmox=None):
    """
    Envía un ping de actividad a la pestaña de Izzi para evitar caducidad de sesión por inactividad,
    devolviendo inmediatamente el foco a la pestaña previa.
    """
    try:
        page_izzi = None
        if not browser or not browser.is_connected():
            raise BrowserClosedError("Navegador no conectado.")
            
        active_page = None
        if browser.contexts:
            for ctx in browser.contexts:
                for pg in ctx.pages:
                    try:
                        if pg.is_closed():
                            continue
                        if pg.evaluate("document.hasFocus()"):
                            active_page = pg
                            break
                    except:
                        pass
                if active_page: break

        if browser.contexts:
            for ctx in browser.contexts:
                for pg in ctx.pages:
                    try:
                        if pg.is_closed():
                            continue
                        if "frontrpaizzi" in pg.url:
                            page_izzi = pg
                            break
                    except Exception as e_pg:
                        if is_browser_closed_exception(e_pg):
                            raise BrowserClosedError("Navegador cerrado durante keep alive.") from e_pg
                if page_izzi: break
        
        if page_izzi:
            check_and_recover_page(page_izzi)
            
            print("    [IZZI ANTI-SUEÑO] Enviando ping anti-sueño (clic de actividad) a pestaña Izzi...")
            try:
                page_izzi.bring_to_front()
                time.sleep(0.5)
            except:
                pass
                
            page_izzi.locator("body").click(force=True)
            time.sleep(0.5)
            
            page_to_return = active_page or page_proxmox
            if page_to_return:
                try:
                    page_to_return.bring_to_front()
                    time.sleep(0.5)
                except:
                    pass
            
    except BrowserClosedError:
        raise
    except Exception as e:
        if is_browser_closed_exception(e):
            raise BrowserClosedError("El navegador fue cerrado durante el anti-sueño de Izzi.") from e
        print(f"    [IZZI ANTI-SUEÑO ERROR] {e}")
