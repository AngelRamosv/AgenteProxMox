from playwright.sync_api import sync_playwright

def test_workaround():
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0]
            page = None
            for pg in context.pages:
                if "frontrpaizzi" in pg.url:
                    page = pg
                    break
            
            page.bring_to_front()
            
            row = page.locator("tr", has_text="192.168.61.23").first
            dropdown = row.locator("p-dropdown").last
            trigger = dropdown.locator(".p-dropdown-trigger").first
            
            print("1. Seleccionando 'Detener Proceso' para resetear el estado...")
            trigger.click(force=True)
            page.wait_for_timeout(1000)
            page.locator("p-dropdownitem").filter(has_text="Detener Proceso").first.click(force=True)
            page.wait_for_timeout(1000)
            
            print("2. Presionando Escape para limpiar cualquier modal no deseado...")
            page.keyboard.press("Escape")
            page.wait_for_timeout(1000)
            
            print("3. Ahora si, seleccionando 'Iniciar Proceso'...")
            trigger.click(force=True)
            page.wait_for_timeout(1000)
            page.locator("p-dropdownitem").filter(has_text="Iniciar Proceso").first.click(force=True)
            page.wait_for_timeout(2000)
            
            dialog = page.locator("p-confirmdialog, div[role='alertdialog']").first
            if dialog.is_visible():
                print("EXITO ABSOLUTO: El modal aparecio despues del workaround!")
                btn = dialog.locator("button.p-confirm-dialog-accept").first
                btn.click(force=True)
                print("CLIC EN 'Si, Enviar' EXITOSO.")
            else:
                print("FALLO: El modal no aparecio ni con el workaround.")
                
            browser.close()
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_workaround()
