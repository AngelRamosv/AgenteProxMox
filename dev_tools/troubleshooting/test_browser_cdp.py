import requests
import traceback
from playwright.sync_api import sync_playwright

try:
    # Get version details
    r = requests.get("http://localhost:9222/json/version")
    version_data = r.json()
    print("Browser Version Info:")
    for k, v in version_data.items():
        print(f" - {k}: {v}")
        
    browser_ws = version_data.get("webSocketDebuggerUrl")
    print(f"\nConnecting Playwright directly to Browser WebSocket: {browser_ws}")
    
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(browser_ws)
        print("Connected!")
        print(f"Contexts: {len(browser.contexts)}")
        for idx, ctx in enumerate(browser.contexts):
            print(f" Context {idx} pages: {len(ctx.pages)}")
            for p_idx, pg in enumerate(ctx.pages):
                print(f"   Page {p_idx}: {pg.title()} (URL: {pg.url})")
                
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
