from playwright.sync_api import sync_playwright
import time

def troubleshoot_izzi():
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0]
            
            page = None
            for pg in context.pages:
                if "frontrpaizzi" in pg.url:
                    page = pg
                    break
            
            if not page:
                print("No se encontro pestaña de izzi.")
                return
                
            page.bring_to_front()
            print("1. Pestaña de Izzi traida al frente.")
            
            # Buscando la fila
            row = page.locator("tr", has_text="192.168.61.23").first
            if row.count() == 0:
                print("No se encontro la ip 192.168.61.23, buscando 'Seleccione un comando'")
                row = page.locator("tr", has_text="Seleccione un comando").first
                
            row.scroll_into_view_if_needed()
            print("2. Fila localizada y enfocada.")
            
            dropdown = row.locator("p-dropdown").last
            if not dropdown.is_visible():
                print("ERROR: Dropdown no es visible")
                return
                
            trigger = dropdown.locator(".p-dropdown-trigger").first
            trigger.click(force=True)
            print("3. Clic en el boton del dropdown ejecutado.")
            page.wait_for_timeout(1000)
            
            items = page.locator("p-dropdownitem").all()
            print(f"4. Se encontraron {len(items)} elementos en el dropdown.")
            for i, it in enumerate(items):
                print(f"   Item {i}: {it.inner_text().strip()}")
                
            opcion = page.locator("p-dropdownitem").filter(has_text="Iniciar Proceso").first
            if not opcion.is_visible():
                print("ERROR: La opcion 'Iniciar Proceso' no es visible en la lista.")
                return
                
            print("5. Dando clic normal a 'Iniciar Proceso' (sin force=True)...")
            opcion.click()
            page.wait_for_timeout(2000)
            
            dialog = page.locator("p-confirmdialog, div[role='alertdialog']").first
            print(f"6. Modal de confirmacion visible despues de clic normal? {dialog.is_visible()}")
            
            if not dialog.is_visible():
                print("7. Intentando clic forzado (force=True) porque el clic normal no funciono...")
                trigger.click(force=True)
                page.wait_for_timeout(1000)
                opcion.click(force=True)
                page.wait_for_timeout(2000)
                print(f"8. Modal visible despues de force=True? {dialog.is_visible()}")
                
            if dialog.is_visible():
                print(f"9. HTML del dialogo: {dialog.inner_html()[:200]}...")
                btn = dialog.locator("button").filter(has_text="Si, Enviar").first
                if not btn.is_visible():
                    btn = dialog.locator("button.p-confirm-dialog-accept").first
                
                print(f"10. Boton 'Si, Enviar' encontrado. Texto exacto: '{btn.inner_text()}'")
                print("11. DANDO CLIC FINAL...")
                btn.click()
                print("--- EXITO TOTAL ---")
            else:
                print("--- FALLO TOTAL: El modal jamas aparecio ---")
                
            browser.close()
        except Exception as e:
            print(f"Error crítico: {e}")

if __name__ == "__main__":
    troubleshoot_izzi()
