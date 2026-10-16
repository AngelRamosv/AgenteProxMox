"""
Activador de Procesos Robot en el Portal Web de Izzi (PrimeNG).
"""
import time
import re
from src.core.exceptions import BrowserClosedError, is_browser_closed_exception
from src.core.browser import check_and_recover_page

def activate_izzi_process(browser, target_ip: str) -> bool:
    """
    Localiza una máquina por su IP en el dashboard de izzi y dispara 'Iniciar Proceso'.
    """
    print(f"[IZZI LOGIC] Buscando IP {target_ip} en Dashboard...")
    try:
        page = None
        if not browser or not browser.is_connected():
            raise BrowserClosedError("El navegador no está conectado.")
            
        if browser.contexts:
            for ctx in browser.contexts:
                for pg in ctx.pages:
                    try:
                        if pg.is_closed():
                            continue
                        if "frontrpaizzi" in pg.url:
                            page = pg
                            break
                    except Exception as e_pg:
                        if is_browser_closed_exception(e_pg):
                            raise BrowserClosedError("Navegador cerrado al buscar página de Izzi.") from e_pg
                if page: break
        
        if not page:
            print("    [IZZI ERROR] No se encontró la pestaña de Izzi.")
            return False

        check_and_recover_page(page)
        time.sleep(0.1)

        # Invariante: Reset a Página 1
        btn1 = page.locator("ul.pagination li, button, a").filter(has_text="1").first
        if btn1.is_visible():
            btn1.click()
            time.sleep(2.0)

        # 1. Buscar fila (Regex con \b para evitar falsos positivos tipo .4 vs .40)
        try:
            row = page.locator("tr").filter(has_text=re.compile(rf"\b{re.escape(target_ip)}\b"))
        except Exception as e_row:
            if is_browser_closed_exception(e_row):
                raise BrowserClosedError("Navegador cerrado al buscar fila de IP en Izzi.") from e_row
            row = page.locator(f"tr:has-text('{target_ip}')")
        
        # Paginación (P1 y P2)
        if row.count() == 0:
            print("    [IZZI] No encontrado en P1. Intentando P2...")
            btn2 = page.locator("ul.pagination li, button").filter(has_text="2").first
            if btn2.is_visible():
                btn2.click()
                time.sleep(2.0)
                try:
                    row = page.locator("tr").filter(has_text=re.compile(rf"\b{re.escape(target_ip)}\b"))
                except Exception as e_row2:
                    if is_browser_closed_exception(e_row2):
                        raise BrowserClosedError("Navegador cerrado en P2 de Izzi.") from e_row2
                    row = page.locator(f"tr:has-text('{target_ip}')")

        if row.count() > 0:
            print(f"    [IZZI] Fila encontrada para {target_ip}. Buscando controles...")
            row.first.scroll_into_view_if_needed()
            time.sleep(1.0)

            try:
                page.bring_to_front()
                page.wait_for_timeout(1000)
            except:
                pass

            # 2. Click Dropdown PrimeNG <p-dropdown>
            dropdown = row.locator("p-dropdown").filter(has_text="Seleccione un comando").first
            if dropdown.count() == 0:
                dropdown = row.locator("p-dropdown").last
            
            if dropdown.is_visible():
                try:
                    trigger = dropdown.locator(".p-dropdown-trigger, .p-dropdown-label").first
                    if trigger.is_visible():
                        trigger.click(force=True)
                    else:
                        dropdown.click(force=True)
                        
                    page.wait_for_timeout(1500)
                    
                    # 3. Seleccionar "Iniciar Proceso"
                    opcion = page.locator("p-dropdownitem li").filter(has_text="Iniciar Proceso").first
                    if opcion.is_visible():
                        opcion.click(force=True)
                        print(f"    [IZZI] Comando 'Iniciar Proceso' seleccionado en la lista. Esperando confirmación...")
                        page.wait_for_timeout(2000)
                        
                        # 4. Confirmación Final ("Si, Enviar")
                        try:
                            print("    [IZZI] Buscando el botón verde de confirmación en el modal activo...")
                            dialog_visible = page.locator("div[role='alertdialog']").last
                            dialog_visible.wait_for(state="visible", timeout=3000)
                            
                            btn_confirmar = dialog_visible.locator("span.p-button-label").filter(has_text="Si, Enviar").first
                            if btn_confirmar.count() == 0:
                                btn_confirmar = dialog_visible.locator("button.p-confirm-dialog-accept").first
                            
                            btn_confirmar.wait_for(state="visible", timeout=3000)
                            btn_confirmar.click(force=True)
                            
                            print(f"    [IZZI] Clic en botón 'Si, Enviar' exitoso.")
                            return True
    
                        except Exception as e_conf:
                            if is_browser_closed_exception(e_conf):
                                raise BrowserClosedError("Navegador cerrado en confirmación Izzi.") from e_conf
                            print(f"    [IZZI ERROR] No se pudo hacer clic en el botón de confirmación: {e_conf}")
                            return False
                        
                        page.wait_for_timeout(2000)
                    else:
                        print("    [IZZI ERROR] Opción 'Iniciar Proceso' no apareció en la lista.")
                        
                except Exception as e_click:
                    if is_browser_closed_exception(e_click):
                        raise BrowserClosedError("Navegador cerrado durante operaciones de clic en Izzi.") from e_click
                    print(f"    [IZZI CLICK ERROR] {e_click}")
            else:
                print("    [IZZI ERROR] Dropdown PrimeNG no interactuable o no encontrado.")
        else:
            print(f"    [IZZI ERROR] IP {target_ip} no aparece en dashboard.")

    except BrowserClosedError:
        raise
    except Exception as e:
        if is_browser_closed_exception(e):
            raise BrowserClosedError("El navegador fue cerrado durante la activación en Izzi.") from e
        print(f"    [IZZI EXCEPTION] {e}")
        
    return False
