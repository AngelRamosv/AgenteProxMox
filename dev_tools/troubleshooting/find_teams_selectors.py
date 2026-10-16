import requests
from playwright.sync_api import sync_playwright
import re
import traceback

targets = [
    "logs_proxmox",
    "Miguel Angel Ramos Castellanos",
    "RPA izzi soporte II"
]

try:
    r = requests.get("http://localhost:9222/json")
    tabs = r.json()
    
    teams_tab = None
    for tab in tabs:
        if "Teams" in tab.get("title", ""):
            teams_tab = tab
            break
            
    if not teams_tab:
        print("Error: Could not find Teams tab.")
        exit(1)
        
    ws_url = teams_tab.get("webSocketDebuggerUrl")
    print(f"Found Teams tab! Connecting to: {ws_url}")
    
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(ws_url)
        
        print(f"Contexts count: {len(browser.contexts)}")
        for idx, ctx in enumerate(browser.contexts):
            print(f" Context {idx} pages: {len(ctx.pages)}")
            for p_idx, pg in enumerate(ctx.pages):
                try:
                    print(f"   Page {p_idx} title: {pg.title()} (URL: {pg.url})")
                except Exception as e:
                    print(f"   Page {p_idx} error: {e}")
                    
        # Let's dynamically find the active page
        page = None
        for ctx in browser.contexts:
            if ctx.pages:
                page = ctx.pages[0]
                break
                
        if not page:
            print("Error: Context pages list is empty.")
            exit(1)
            
        print(f"Using Page: {page.title()} (URL: {page.url})")
        
        for name in targets:
            print(f"\n========================================")
            print(f"Searching for target: '{name}'")
            print(f"========================================")
            
            clean_name = name.split("...")[0].strip()
            
            # Find all elements matching the text
            loc = page.locator("*:has-text('" + clean_name + "')")
            count = loc.count()
            print(f"Found {count} raw elements containing this text.")
            
            matches = []
            for i in range(count):
                el = loc.nth(i)
                try:
                    tag = el.evaluate("el => el.tagName")
                    role = el.get_attribute("role") or ""
                    tid = el.get_attribute("data-tid") or ""
                    classes = el.get_attribute("class") or ""
                    
                    is_sidebar = el.evaluate("""el => {
                        let current = el;
                        while (current) {
                            let tid = current.getAttribute('data-tid') || '';
                            let role = current.getAttribute('role') || '';
                            let cls = current.className || '';
                            if (tid.includes('chat-list') || role.includes('grid') || cls.includes('sidebar') || cls.includes('left-rail') || cls.includes('navigation')) {
                                return true;
                            }
                            current = current.parentElement;
                        }
                        return false;
                    }""")
                    
                    if is_sidebar:
                        container_info = el.evaluate("""el => {
                            let current = el;
                            while (current) {
                                let tag = current.tagName.toLowerCase();
                                let role = current.getAttribute('role') || '';
                                let tid = current.getAttribute('data-tid') || '';
                                let cls = current.className || '';
                                if (role === 'row' || role === 'listitem' || role === 'treeitem' || tid.includes('item') || tag === 'li' || tag === 'button' || cls.includes('item')) {
                                    return {
                                        tag: current.tagName,
                                        role: current.getAttribute('role') || 'None',
                                        tid: current.getAttribute('data-tid') || 'None',
                                        classes: current.className || 'None',
                                        selector: current.tagName.toLowerCase() + (role ? '[role="' + role + '"]' : '') + (tid ? '[data-tid="' + tid + '"]' : '')
                                    };
                                }
                                current = current.parentElement;
                            }
                            return null;
                        }""")
                        
                        matches.append({
                            "tag": tag,
                            "role": role,
                            "tid": tid,
                            "classes": classes,
                            "container": container_info
                        })
                except Exception as e:
                    pass
            
            seen_selectors = set()
            printed_count = 0
            for match in matches:
                container = match["container"]
                if container:
                    sel = container["selector"]
                    if sel not in seen_selectors:
                        seen_selectors.add(sel)
                        printed_count += 1
                        print(f"Match {printed_count}:")
                        print(f"  - Tag: {match['tag']}")
                        print(f"  - Container Tag: {container['tag']}")
                        print(f"  - Container Role: {container['role']}")
                        print(f"  - Container Data-Tid: {container['tid']}")
                        print(f"  - Container Class: {container['classes']}")
                        print(f"  - RECOMMENDED PLAYWRIGHT LOCATOR:")
                        if container['tid'] != 'None':
                            print(f"    page.locator('[data-tid=\"{container['tid']}\"]').filter(has_text='{clean_name}')")
                        elif container['role'] != 'None':
                            print(f"    page.locator('{container['tag'].lower()}[role=\"{container['role']}\"]').filter(has_text='{clean_name}')")
                        else:
                            print(f"    page.locator('{container['tag'].lower()}').filter(has_text='{clean_name}')")
                            
            if printed_count == 0:
                print("No sidebar container elements matched. Let's dump page-wide candidates:")
                for i in range(min(5, count)):
                    el = loc.nth(i)
                    try:
                        tag = el.evaluate("el => el.tagName")
                        text = el.inner_text().replace('\n', ' ')[:60]
                        print(f"  Candidate {i}: Tag={tag}, Text=\"{text}\"")
                    except: pass
                    
except Exception as e:
    print(f"Execution Error: {e}")
    traceback.print_exc()
