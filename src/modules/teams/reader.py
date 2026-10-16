"""
Lector de Mensajes y Chats de Microsoft Teams con Soporte OCR.
"""
import time
import re
from collections import deque
from src.core.exceptions import BrowserClosedError, is_browser_closed_exception
from src.core.browser import check_and_recover_page, get_teams_page
from src.modules.ocr.engine import ocr_from_image
from src.modules.parsing.ip_extractor import extract_ips

# Selectores estables Teams
SEL_MESSAGE = 'div[data-tid="chat-pane-message"]'
SEL_TEXT    = 'div[data-message-content] p'
SEL_IMAGE   = 'img[data-tid^="lazy-image"]'

# Deduplicación por data-mid (ID único asignado por Teams)
_seen_mids = set()
_seen_q = deque(maxlen=500)

def _mark_mid(mid: str) -> bool:
    """Registra y valida si un mensaje ya ha sido procesado previamente."""
    if not mid:
        return True
    if mid in _seen_mids:
        return False
    _seen_mids.add(mid)
    _seen_q.append(mid)
    if len(_seen_q) == _seen_q.maxlen:
        _seen_mids.clear()
        _seen_mids.update(_seen_q)
    return True


def is_chat_unread(chat_item) -> bool:
    """
    Determina si un ítem de chat en la barra lateral tiene mensajes no leídos
    inspeccionando el DOM del elemento (peso de fuente negrita, atributos ARIA o badges).
    """
    try:
        unread_detected = chat_item.evaluate("""el => {
            const elements = [el, ...el.querySelectorAll('*')];
            for (const elem of elements) {
                const weight = window.getComputedStyle(elem).fontWeight;
                if (weight === 'bold' || parseInt(weight) >= 700) {
                    return true;
                }
                
                const label = elem.getAttribute('aria-label') || '';
                const tid = elem.getAttribute('data-tid') || '';
                const cls = elem.getAttribute('class') || '';
                
                const labelLower = label.toLowerCase();
                if (labelLower.includes('unread') || 
                    labelLower.includes('sin leer') || 
                    labelLower.includes('no leído') || 
                    labelLower.includes('no leido') ||
                    labelLower.includes('mensajes nuevos')) {
                    return true;
                }
                
                if (tid.toLowerCase().includes('unread') || 
                    tid.toLowerCase().includes('badge') || 
                    tid.toLowerCase().includes('counter') ||
                    cls.toLowerCase().includes('unread') || 
                    cls.toLowerCase().includes('badge') ||
                    cls.toLowerCase().includes('counter')) {
                    return true;
                }
            }
            return false;
        }""")
        return bool(unread_detected)
    except Exception as e:
        print(f"      [DEBUG] Error comprobando no leído: {e}")
        return False


def teams_find_chat_item(page, name: str):
    """Localiza un canal o chat en la barra lateral izquierda de Teams."""
    pattern = re.compile(re.escape(name), re.IGNORECASE)
    
    # Restringir la búsqueda a la barra lateral izquierda para evitar coincidencias con el historial
    sidebar = page.locator("[data-tid='chat-list'], [role='grid'], [role='list'], nav, .chat-list, .left-rail, [data-tid='simple-collab-dnd-rail']").first
    
    try:
        if sidebar.count() > 0:
            sidebar_candidates = [
                sidebar.locator("div[role='treeitem']").filter(has_text=pattern).first,
                sidebar.locator(".fui-TreeItem").filter(has_text=pattern).first,
                sidebar.locator("[data-tid*='chat-list-item']").filter(has_text=pattern).first,
                sidebar.locator("[role='row']").filter(has_text=pattern).first,
                sidebar.locator("[role='listitem']").filter(has_text=pattern).first,
                sidebar.locator("span").filter(has_text=pattern).first,
            ]
            for loc in sidebar_candidates:
                if loc.count() > 0:
                    return loc
    except Exception as e:
        if is_browser_closed_exception(e):
            raise BrowserClosedError("Navegador cerrado durante búsqueda de chat en barra lateral.") from e
        print(f"      [TEAMS DEBUG] Error buscando en barra lateral: {e}")

    # Fallback general en toda la página
    candidates = [
        page.locator("div[role='treeitem']").filter(has_text=pattern).first,
        page.locator(".fui-TreeItem").filter(has_text=pattern).first,
        page.locator("[data-tid*='chat-list-item']").filter(has_text=pattern).first,
        page.locator("[role='row']").filter(has_text=pattern).first,
        page.locator("[role='listitem']").filter(has_text=pattern).first,
        page.locator("span").filter(has_text=pattern).first,
    ]
    for loc in candidates:
        try:
            if loc.count() > 0:
                return loc
        except Exception as e:
            if is_browser_closed_exception(e):
                raise BrowserClosedError("Navegador cerrado durante fallback de búsqueda de chat.") from e
    return None


def read_last_message_text_plus_image_ocr(page):
    """
    Lee el contenido textual y procesa mediante OCR imágenes adjuntas del último mensaje.
    """
    try:
        try:
            page.wait_for_selector(SEL_MESSAGE, timeout=5000)
        except:
            return None

        last = page.locator(SEL_MESSAGE).last
        mid = last.get_attribute("data-mid") or ""

        if not _mark_mid(mid):
            return None

        parts = []

        # A) Texto directo
        txt_locator = last.locator(SEL_TEXT)
        if txt_locator.count() > 0:
            text_content = " ".join(txt_locator.all_inner_texts()).strip()
            if text_content:
                parts.append(text_content)

        # B) Imagen -> OCR
        all_imgs = last.locator("img").all()
        content_img = None
        for img_candidate in all_imgs:
            try:
                src = img_candidate.get_attribute("src") or ""
                data_tid = img_candidate.get_attribute("data-tid") or ""
                classes = img_candidate.get_attribute("class") or ""
                if any(x in data_tid.lower() or x in classes.lower() or x in src.lower() for x in ["emoji", "avatar"]):
                    continue
                content_img = img_candidate
                break
            except:
                pass

        ocr_text = ""
        import tempfile
        import os
        temp_dir = os.path.join(tempfile.gettempdir(), "AgenteProx")
        os.makedirs(temp_dir, exist_ok=True)
        img_path = os.path.join(temp_dir, "teams_latest.png")

        if content_img:
            print("    [DEBUG] Capturando imagen del mensaje para OCR (Intentando alta resolución)...")

            # Estrategia 1: Modal gigante en alta resolución
            try:
                content_img.scroll_into_view_if_needed(timeout=2000)
                content_img.click(force=True, timeout=3000)
                page.wait_for_timeout(4000) 
                
                modal_img = page.locator("div[role='dialog'] img, [data-tid='media-viewer'] img").last
                
                try:
                    if modal_img.is_visible(timeout=1000):
                        print("      [DEBUG] Descargando archivo original en alta definición desde la memoria del navegador...")
                        img_src = modal_img.get_attribute("src")
                        
                        if img_src and img_src.startswith("blob:"):
                            base64_data = page.evaluate("""async (url) => {
                                const response = await fetch(url);
                                const blob = await response.blob();
                                return new Promise((resolve) => {
                                    const reader = new FileReader();
                                    reader.onloadend = () => resolve(reader.result.split(',')[1]);
                                    reader.readAsDataURL(blob);
                                });
                            }""", img_src)
                            
                            import base64
                            with open(img_path, "wb") as f:
                                f.write(base64.b64decode(base64_data))
                        else:
                            modal_img.screenshot(path=img_path)
                            
                        ocr_text = ocr_from_image(img_path)
                except:
                    pass
                
                page.keyboard.press("Escape")
                page.wait_for_timeout(500)
            except Exception as e_modal:
                print(f"      [DEBUG] No se pudo capturar en modo gigante: {e_modal}")
                try:
                    page.keyboard.press("Escape")
                except:
                    pass

            # Estrategia 2: Screenshot del contenedor DIV del mensaje
            if not ocr_text.strip():
                try:
                    last.scroll_into_view_if_needed(timeout=2000)
                    page.wait_for_timeout(300)
                    last.screenshot(path=img_path)
                    ocr_text = ocr_from_image(img_path)
                except Exception as e_div:
                    print(f"      [DEBUG] Captura de div falló: {e_div}")

            # Estrategia 3: Screenshot de la miniatura
            if not ocr_text.strip():
                try:
                    content_img.screenshot(path=img_path)
                    ocr_text = ocr_from_image(img_path)
                except Exception as e_img:
                    print(f"      [DEBUG] Captura de img miniatura falló: {e_img}")

        if ocr_text.strip():
            parts.append(f"[OCR: {ocr_text.strip()}]")

        final_text = " ".join(parts).strip()
        if not final_text:
            final_text = last.inner_text()

        ips = extract_ips(final_text)
        stable_locator = page.locator(f"[data-mid='{mid}']").last

        return {"mid": mid, "text": final_text, "ips": ips, "locator": stable_locator}
    except Exception as e:
        print(f"    [TEAMS INTERNAL ERROR] {e}")
        return None


def read_latest_message_from_group(browser, group_name: str, page_proxmox=None, force_read=False):
    """
    Navega silenciosamente al grupo de Teams especificado y extrae el último mensaje disponible.
    """
    try:
        page = get_teams_page(browser)
        if not page:
            return None
        
        check_and_recover_page(page)
        
        item = teams_find_chat_item(page, group_name)
        if not item:
            return None
        
        # Evitar clics innecesarios para prevenir fugas de memoria y conservar foco
        is_selected = False
        try:
            is_selected = item.get_attribute("aria-selected") == "true" or "selected" in (item.get_attribute("class") or "").lower()
        except:
            pass
            
        is_unread = False
        if not is_selected:
            is_unread = is_chat_unread(item)
            
        should_click = not is_selected and (is_unread or force_read)
        
        if should_click:
            try: 
                item.click(force=True)
                time.sleep(1.5)
            except Exception as e:
                if is_browser_closed_exception(e):
                    raise BrowserClosedError("Navegador cerrado al hacer clic en chat.") from e
        elif not is_selected:
            return None
        else:
            time.sleep(0.2)

        result = read_last_message_text_plus_image_ocr(page)
        if not result:
            return None
            
        final_text = result["text"]
        if final_text:
            print(f"    [TEAMS EXTRACT] \"{final_text[:60]}...\"")
            
        return result

    except BrowserClosedError:
        raise
    except Exception as e:
        if is_browser_closed_exception(e):
            raise BrowserClosedError("El navegador fue cerrado durante la lectura de Teams.") from e
        print(f"[TEAMS ERROR] {e}")
        return None
