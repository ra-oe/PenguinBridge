# PenguinBridge
Note: this README was made by Copilot because i was too lazy to make my own right now so yea also it might be wrong because its retarded
----
A tiny bridge between Python and PenguinMod. Run a small Python server and let PenguinMod send named broadcasts to your Python code - great for quick tooling, prototypes, or adding simple GUI hooks.
Work in progress.

[JOIN MY DISCORD RIGHT NOW: https://discord.gg/mfmjRW7XTm](https://discord.gg/mfmjRW7XTm)
---

## What it does
- Starts a lightweight local server that PenguinMod can talk to.
- Lets you register Python functions as handlers for named events.
- Has a catch-all handler for dynamic messages.
- Plays nice with any Python GUI (pywebview, pygame, tkinter, etc).
- Includes the PenguinMod extension `PenguinBridge.js` in this repo for easy loading.

---

## Quick demo
1. Run `PenguinBridgeServer.py`.
2. Load `PenguinBridge.js` in PenguinMod from this repo, or copy it into the editor.
3. Send broadcasts from the editor - your Python handlers will get them.

---

## Where the extension lives
The PenguinMod extension is at `PenguinBridge.js` in this repository. It talks to the Python server at `http://127.0.0.1:6035` by default.

If you want to load it directly from GitHub, use the raw file URL in the editor's extension import field. For example:

```
https://raw.githubusercontent.com/ra-oe/PenguinBridge/main/PenguinBridge.js
```

---

## How the included extension works (short)
- It polls the Python server every 100 ms at `/poll` for events emitted by Python.
- It can POST broadcasts from the editor to Python at `/broadcast` with JSON body `{ broadcast: string, data: any }`.
- It exposes a few blocks in the editor:
  - Commands to send broadcasts to Python: `broadcast [BROADCAST_NAME] to Python` and `broadcast [BROADCAST_NAME] with data [DATA] to Python`.
  - Hat blocks to receive Python-to-editor broadcasts: `when Python broadcast [EVENT] received` and `when any Python broadcast received`.
  - Reporters: `last Python broadcast event`, `last Python broadcast data`, and `data for Python broadcast [EVENT]`.
  - A command to change the server address: `set Python server address to [URL]`.

Because the extension polls, you do not need a persistent WebSocket connection. If you want lower latency you can modify the extension to use WebSockets and update the server.

---

## Example usage from your own JS code
If you want to trigger Python directly from a script, here is what the extension does under the hood:

```js
fetch("http://127.0.0.1:6035/broadcast", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ broadcast: "close_window", data: { reason: "user" } })
});
```

And the server's `/poll` endpoint returns a JSON array of events like:

```json
[
  { "event": "welcome_message", "data": "hello" },
  { "event": "score_update", "data": { "score": 42 } }
]
```

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

## API (summary)
- PenguinBridge(port=6035, host="127.0.0.1") - create an instance.
- bridge.on(event_name)(func) - register handler for a named event.
- bridge.on_any(func) - register a catch-all handler; func signature: (name, data).
- bridge.start() - start the server.
- bridge.stop() - stop the server.

---

## Troubleshooting
- Nothing arrives? Make sure the editor and Python bridge use the same host/port and your firewall isn't blocking it.
- Testing across machines? Bind to `0.0.0.0` (but be careful - that's less secure).
- Multiple instances? Use different ports.

---

## Contributing
Pull requests and issues welcome. I can also:
- Add a CONTRIBUTING.md
- Add a simple requirements.txt and a tiny example project

---

## License
Add your license here (MIT is fine if you want). I can add LICENSE for you.
