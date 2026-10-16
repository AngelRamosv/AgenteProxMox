from playwright.sync_api import sync_playwright

def test_li():
    with sync_playwright() as p:
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            page = browser.contexts[0].pages[0]
            
            for pg in browser.contexts[0].pages:
                if "frontrpaizzi" in pg.url:
                    page = pg
                    break
                    
            page.bring_to_front()
            
            row = page.locator("tr", has_text="192.168.61.23").first
            row.scroll_into_view_if_needed()
            dropdown = row.locator("p-dropdown").last
            trigger = dropdown.locator(".p-dropdown-trigger").first
            
            # Clic suave en el trigger
            trigger.click()
            page.wait_for_timeout(1000)
            
            # Buscando especificamente el LI (el texto real)
            opcion = page.locator("p-dropdownitem li").filter(has_text="Iniciar Proceso").first
            print("Haciendo clic en el LI directamente (como humano)...")
            opcion.click()
            page.wait_for_timeout(2000)
            
            dialog = page.locator("p-confirmdialog, div[role='alertdialog']").first
            if dialog.is_visible():
                print("EXITO ABSOLUTO: El modal verde aparecio!")
                btn = dialog.locator("button.p-confirm-dialog-accept").first
                btn.click()
                print("CLIC EN 'Si, Enviar' EXITOSO.")
            else:
                print("FALLO: El modal no aparecio al hacer clic en el LI.")
                
            browser.close()
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_li()
