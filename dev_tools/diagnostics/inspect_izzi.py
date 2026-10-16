from playwright.sync_api import sync_playwright
import time

def interact_and_inspect():
    with sync_playwright() as p:
        print("Conectando al navegador en vivo...")
        try:
            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            context = browser.contexts[0]
            page = context.pages[0]
            
            # Buscar la página de Izzi
            for pg in context.pages:
                if "frontrpaizzi" in pg.url:
                    page = pg
                    break
            
            page.bring_to_front()
            print("Pestaña Izzi al frente.")
            
            # 1. Buscar la fila
            row = page.locator("tr").filter(has_text="192.168.61.23")
            if row.count() == 0:
                print("No se encontro la fila. Buscando cualquier fila con 'Seleccione un comando'...")
                row = page.locator("tr").filter(has_text="Seleccione un comando").first
                
            print("Fila encontrada. Dando clic al Dropdown...")
            
            # 2. Clic en Dropdown
            dropdown = row.locator("p-dropdown")
            if dropdown.count() > 0:
                dropdown.first.click(force=True)
                page.wait_for_timeout(1000)
                
                # 3. Clic en Iniciar Proceso
                item = page.locator("p-dropdownitem li").filter(has_text="Iniciar Proceso")
                if item.count() > 0:
                    print("Dando clic en Iniciar Proceso...")
                    item.first.click(force=True)
                    page.wait_for_timeout(2000) # Esperar a que salga el modal
                
                # 4. Extraer todo el HTML para buscar el botón
                html = page.content()
                with open("izzi_dom_dump.html", "w", encoding="utf-8") as f:
                    f.write(html)
                print("HTML volcado a izzi_dom_dump.html")
                
            browser.close()
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    interact_and_inspect()
