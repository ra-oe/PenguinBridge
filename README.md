# PenguinBridge

A tiny bridge between Python and PenguinMod. Run a small Python server and let PenguinMod send named broadcasts to your Python code - great for quick tooling, prototypes, or adding simple GUI hooks.

Status: WIP

---

## What it does
- Starts a lightweight local server that PenguinMod can talk to.
- Lets you register Python functions as handlers for named events.
- Has a catch-all handler for dynamic messages.
- Plays nice with any Python GUI (pywebview, pygame, tkinter, etc).

---

## Quick demo
1. Run `PenguinBridgeServer.py`.
2. Load `PenguinBridge.js` in PenguinMod (or your self-hosted editor).
3. Send broadcasts from the editor - your Python handlers will get them.

---

## Requirements
- Python 3.8+
- No external services needed; communication happens over a local port (default: 6035).
- If you want, I can add `requirements.txt` for dependencies.

---

## Quickstart (dev)
Drop `PenguinBridgeServer.py` into your project and import the helper. Example:

```python
# example.py
from penguin_bridge import PenguinBridge
import threading
import time

bridge = PenguinBridge(port=6035)

@bridge.on("close_window")
def handle_close(data):
    print("Editor asked to close:", data)
    # add logic to close your GUI or stop the app

@bridge.on_any
def catch_all(name, data):
    print(f"{name} -> {data}")

# Run the server in a background thread so your GUI/main loop isn't blocked
t = threading.Thread(target=bridge.start, daemon=True)
t.start()

try:
    # your app logic here
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    bridge.stop()
```

Notes:
- Use a different port if 6035 is taken.
- If your GUI toolkit has its own event loop, run the bridge in another thread or process.

---

## How it works (short)
PenguinMod's JS extension connects to a local endpoint and posts named events + payloads. PenguinBridge dispatches those to the handler you registered in Python (either a specific event handler or the catch-all).

---

## API (summary)
- PenguinBridge(port=6035, host="127.0.0.1") - create an instance.
- bridge.on(event_name)(func) - register handler for a named event.
- bridge.on_any(func) - register a catch-all handler; func signature: (name, data).
- bridge.start() - start the server.
- bridge.stop() - stop the server.

If you want, I can pull exact function signatures from the code and add them here.

---

## Example PenguinMod snippet
Adjust this to match your extension:

```js
// PenguinBridge.js
fetch("http://127.0.0.1:6035/broadcast", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ name: "close_window", data: { reason: "user" } })
});
```

---

## Troubleshooting
- Nothing arrives? Make sure the editor and Python bridge use the same host/port and your firewall isn't blocking it.
- Testing across machines? Bind to `0.0.0.0` (but be careful - that's less secure).
- Multiple instances? Use different ports.

---

## Contributing
Pull requests and issues welcome. If you want, I can:
- Commit this README update
- Add a CONTRIBUTING.md
- Add a simple requirements.txt and a tiny example repo

---

## License
Add your license here (MIT is fine if you want). I can add LICENSE for you.
