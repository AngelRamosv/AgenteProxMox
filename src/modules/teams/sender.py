"""
Despachador de Mensajes y Respuestas de Microsoft Teams.
"""
import time
from src.core.exceptions import BrowserClosedError, is_browser_closed_exception
from src.core.browser import check_and_recover_page, get_teams_page
from src.core import config
from src.modules.teams.reader import teams_find_chat_item

def send_teams_message(browser, message: str, target_chat=None, reply_to_locator=None, force_quote=False) -> bool:
    """
    Envía un mensaje o alerta a un chat o canal de Teams.
    Soporta lista de destinos y cita opcional de mensajes previos.
    """
    if target_chat is None:
        target_chat = config.TEAMS_ALERT_GROUP_NAME
        
    if isinstance(target_chat, list):
        success = False
        for chat in target_chat:
            if send_teams_message(browser, message, target_chat=chat, reply_to_locator=reply_to_locator, force_quote=force_quote):
                success = True
        return success
        
    try:
        page_teams = get_teams_page(browser)
        if not page_teams:
            return False 

        check_and_recover_page(page_teams)

        print(f"    [TEAMS] Enviando alerta para: {message.split('|')[0]}...")
        time.sleep(0.1)

        switched_ok = False
        if target_chat:
            chat_item = teams_find_chat_item(page_teams, target_chat)
            if chat_item:
                is_selected = False
                try:
                    is_selected = chat_item.get_attribute("aria-selected") == "true" or "selected" in (chat_item.get_attribute("class") or "").lower()
                except:
                    pass
                if not is_selected:
                    chat_item.click(force=True)
                    time.sleep(1.0)
                else:
                    time.sleep(0.2)
                switched_ok = True
            else:
                if target_chat == config.TEAMS_ALERT_GROUP_NAME and config.TEAMS_CHANNEL_URL:
                    print(f"    [TEAMS] '{target_chat}' no visible en barra lateral. Navegando vía URL de canal...")
                    try:
                        page_teams.goto(config.TEAMS_CHANNEL_URL, wait_until="commit", timeout=10000)
                    except Exception as e_goto:
                        print(f"    [WARN] Navegación URL Teams superó timeout pero continuando: {e_goto}")
                    
                    try:
                        print(f"    [TEAMS] Validando que el canal '{target_chat}' cargó correctamente...")
                        page_teams.wait_for_timeout(3000)
                        page_teams.locator(f"[title*='{target_chat}'], [aria-label*='{target_chat}']").first.wait_for(state="visible", timeout=15000)
                        switched_ok = True
                    except:
                        print(f"    [TEAMS ERROR] El canal '{target_chat}' no cargó a tiempo en la pantalla.")
                        switched_ok = False
                else:
                    switched_ok = False
        else:
            switched_ok = True

        if target_chat and not switched_ok:
            print(f"    [TEAMS ERROR] No se pudo encontrar ni navegar al chat de destino: '{target_chat}'. Abortando para evitar escribir en un chat equivocado.")
            return False
        
        # Lógica de Respuesta Citada
        if reply_to_locator and force_quote:
            try:
                print("    [TEAMS DEBUG] Iniciando efecto de cita en el mensaje original...")
                reply_to_locator.scroll_into_view_if_needed()
                
                box = reply_to_locator.bounding_box()
                if box:
                    page_teams.mouse.move(box['x'] + box['width']/2, box['y'] + box['height']/2)
                else:
                    reply_to_locator.hover()
                
                page_teams.wait_for_timeout(1000)

                btn_quote = page_teams.locator("button[aria-label*='cita'], button[aria-label*='Quote']").first
                if btn_quote.is_visible():
                    print("    [TEAMS DEBUG] Clic directo en ícono de cita.")
                    btn_quote.click()
                else:
                    print("    [TEAMS DEBUG] Buscando los tres puntitos 'Más opciones'...")
                    btn_more = page_teams.locator("button[aria-label*='opciones'], button[aria-label*='options'], [data-tid*='more-options']").last
                    if btn_more.is_visible():
                        btn_more.click(force=True)
                        page_teams.wait_for_timeout(1000)
                        
                        print("    [TEAMS DEBUG] Seleccionando 'Responder con una cita' del menú...")
                        menu_item = page_teams.locator("span, button, [role='menuitem']").filter(has_text="Responder con una cita").last
                        menu_item.click()
                    else:
                        print("    [TEAMS DEBUG] No se encontró el ícono de los tres puntitos.")
                
                page_teams.wait_for_timeout(1000)
            except Exception as e_quote: 
                if is_browser_closed_exception(e_quote):
                    raise BrowserClosedError("El navegador fue cerrado durante el efecto de cita.") from e_quote
                print(f"    [TEAMS DEBUG] Error ejecutando efecto cita: {e_quote}")
        else:
            time.sleep(0.5)

        input_box = page_teams.locator("div[contenteditable='true'], div[data-tid='ckeditor'], [role='textbox']").first
        if input_box.is_visible(timeout=10000):
            input_box.click(force=True)
            
            if reply_to_locator and force_quote:
                page_teams.keyboard.press("Control+End")
                page_teams.keyboard.press("Enter")
                page_teams.keyboard.insert_text(message)
            else:
                input_box.fill(message)
                
            page_teams.keyboard.press("Enter")
            
            try:
                btn_send = page_teams.locator("button[aria-label*='Enviar'], button[aria-label*='Send'], button[data-tid*='send']").first
                if btn_send.is_visible(timeout=1000):
                    btn_send.click(force=True)
            except:
                pass
                
            page_teams.wait_for_timeout(500)
            return True
        else:
            print(f"    [TEAMS ERROR] No se encontró el cuadro de texto para enviar el mensaje a '{target_chat}'.")
            return False
            
    except BrowserClosedError:
        raise
    except Exception as e:
        if is_browser_closed_exception(e):
            raise BrowserClosedError("El navegador fue cerrado al enviar mensaje a Teams.") from e
        print(f"    [TEAMS EXCEPTION] {e}")
        return False
