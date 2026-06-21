# PenguinBridge
Bridges Python and Penguinmod

# How to use it (see how it works)
If you want to see how it works, you can just run `PenguinBridgeServer.py` and import the extension `PenguinBridge.js` on [Penguinmod](https://studio.penguinmod.com/editor.html) (or my self hosted [alt url](https://ra-oe.dev/penguinmod/editor.html)) and fuck around with it.

----

# How to use it (in dev)
If you wanna develop using it (cause why not and its *cool*) you gotta save `PenguinBridgeServer.py` in the same directory of your code and import it. Here's an example with *comments*:
```python
import pywebview # (or Pygame, tkinter, etc.)
from penguin_bridge import PenguinBridge

# 1. Create instance
bridge = PenguinBridge(port=6035)

# 2. Wire up your custom logic decorator-style
@bridge.on("close_window")
def handle_close(data):
    print("Webview requested a shutdown!")
    # Close window or quit logic goes here

@bridge.on_any
def catch_all(name, data):
    # This receives absolutely any broadcast sent by PenguinMod automatically
    print(f"Dynamic broadcast received: {name} -> {data}")

# 3. Start the server in background thread so GUI is not frozen
bridge.start()

# 4. Start your actual app/gui
# your shit
```
## this isnt finished so yea
