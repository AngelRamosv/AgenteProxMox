import requests
import json
import websocket
import traceback

targets = [
    "logs_proxmox",
    "Miguel Angel Ramos Castellanos",
    "RPA izzi soporte II"
]

js_expression = """
(() => {
    const targets = ["logs_proxmox", "Miguel Angel Ramos Castellanos", "RPA izzi soporte II"];
    const results = {};
    const all = document.querySelectorAll('*');
    
    for (const name of targets) {
        const cleanName = name.split("...")[0].trim().toLowerCase();
        let foundElement = null;
        
        // Find smallest element containing the text anywhere
        for (const el of all) {
            const text = (el.innerText || "").toLowerCase();
            if (text.includes(cleanName)) {
                if (!foundElement || el.innerText.length < foundElement.innerText.length) {
                    foundElement = el;
                }
            }
        }
        
        if (foundElement) {
            let current = foundElement;
            const path = [];
            
            // Build the parent hierarchy up to 6 levels
            let depth = 0;
            while (current && depth < 8) {
                path.push({
                    tag: current.tagName.toLowerCase(),
                    role: current.getAttribute('role') || 'None',
                    tid: current.getAttribute('data-tid') || 'None',
                    class: current.className || 'None',
                    text: current.innerText ? current.innerText.replace(/\\n/g, ' ').substring(0, 30) : ''
                });
                current = current.parentElement;
                depth++;
            }
            
            results[name] = {
                tag: foundElement.tagName.toLowerCase(),
                role: foundElement.getAttribute('role') || 'None',
                tid: foundElement.getAttribute('data-tid') || 'None',
                class: foundElement.className || 'None',
                path: path
            };
        } else {
            results[name] = { error: "Element not found anywhere on the page" };
        }
    }
    return results;
})()
"""

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
    print(f"Connecting directly to Teams page WebSocket: {ws_url}")
    
    ws = websocket.create_connection(ws_url, suppress_origin=True)
    
    # Send Runtime.evaluate command
    cmd = {
        "id": 1,
        "method": "Runtime.evaluate",
        "params": {
            "expression": js_expression,
            "returnByValue": True
        }
    }
    ws.send(json.dumps(cmd))
    
    # Wait for response
    response_str = ws.recv()
    response = json.loads(response_str)
    
    ws.close()
    
    print("\nRaw Response:")
    print(json.dumps(response, indent=2))
    
    result = response.get("result", {}).get("result", {}).get("value", {})
    
    print("\n================ SELECTORS FOUND ================")
    for name, info in result.items():
        print(f"\nTarget: '{name}'")
        if "error" in info:
            print(f"  Error: {info['error']}")
        else:
            print(f"  - Tag Name: {info['tag']}")
            print(f"  - Role: {info['role']}")
            print(f"  - Data-Tid: {info['tid']}")
            print(f"  - Class Name: {info['class']}")
            print(f"  - Parent DOM Path Hierarchy (starting from element):")
            for idx, step in enumerate(info['path']):
                print(f"    Parent {idx}:")
                print(f"      Tag: {step['tag']}")
                print(f"      Role: {step['role']}")
                print(f"      Data-Tid: {step['tid']}")
                print(f"      Class: {step['class']}")
                print(f"      Text: \"{step['text']}\"")
    print("=================================================")
    
except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()
