/**
 * Python Bidirectional Broadcast Extension for PenguinMod
 * Allows triggering Python-side actions and listening for Python-to-project broadcasts.
 */

(function(Scratch) {
  'use strict';

  if (!Scratch) {
    console.error("Scratch/PenguinMod API not found.");
    return;
  }

  class PythonBroadcastBridge {
    constructor() {
      this.lastReceivedEvent = "";
      this.lastReceivedData = "";
      this.eventDataMap = {}; // Event Name -> Last Received Data Payload
      this.pollingInterval = null;
      this.serverUrl = "http://127.0.0.1:6035";

      // Auto-start polling on initialization
      this._startPolling();
    }

    getInfo() {
      return {
        id: 'pythonBroadcast',
        name: 'PenguinBridge',
        color1: '#4B8BBE',
        color2: '#306998', 
        blocks: [
          // Sending to Python
          {
            opcode: 'broadcastToPython',
            blockType: Scratch.BlockType.COMMAND,
            text: 'broadcast [BROADCAST_NAME] to Python',
            arguments: {
              BROADCAST_NAME: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: 'client_ready'
              }
            }
          },
          {
            opcode: 'broadcastWithDataToPython',
            blockType: Scratch.BlockType.COMMAND,
            text: 'broadcast [BROADCAST_NAME] with data [DATA] to Python',
            arguments: {
              BROADCAST_NAME: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: 'player_update'
              },
              DATA: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: '{"x": 100, "y": 200}'
              }
            }
          },
          
          // Event Receivers (Hats)
          {
            opcode: 'whenBroadcastReceived',
            blockType: Scratch.BlockType.HAT,
            text: 'when Python broadcast [EVENT] received',
            arguments: {
              EVENT: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: 'welcome_message'
              }
            }
          },
          {
            opcode: 'whenAnyBroadcastReceived',
            blockType: Scratch.BlockType.HAT,
            text: 'when any Python broadcast received'
          },

          // Data Reporters
          {
            opcode: 'getLastReceivedEvent',
            blockType: Scratch.BlockType.REPORTER,
            text: 'last Python broadcast event'
          },
          {
            opcode: 'getLastReceivedData',
            blockType: Scratch.BlockType.REPORTER,
            text: 'last Python broadcast data'
          },
          {
            opcode: 'getDataForEvent',
            blockType: Scratch.BlockType.REPORTER,
            text: 'data for Python broadcast [EVENT]',
            arguments: {
              EVENT: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: 'console_input'
              }
            }
          },

          // Server configuration
          {
            opcode: 'setServerUrl',
            blockType: Scratch.BlockType.COMMAND,
            text: 'set Python server address to [URL]',
            arguments: {
              URL: {
                type: Scratch.ArgumentType.STRING,
                defaultValue: 'http://127.0.0.1:6035'
              }
            }
          }
        ]
      };
    }

    setServerUrl(args) {
      this.serverUrl = args.URL;
      this._startPolling(); // Restart polling with new URL
    }

    broadcastToPython(args) {
      this._sendBroadcast(args.BROADCAST_NAME, "");
    }

    broadcastWithDataToPython(args) {
      this._sendBroadcast(args.BROADCAST_NAME, args.DATA);
    }

    // Hat Block evaluation
    whenBroadcastReceived(args) {
      // Hat blocks evaluate true when triggered by startHats
      return true;
    }

    whenAnyBroadcastReceived() {
      return true;
    }

    getLastReceivedEvent() {
      return this.lastReceivedEvent;
    }

    getLastReceivedData() {
      return this.lastReceivedData;
    }

    getDataForEvent(args) {
      return this.eventDataMap[args.EVENT] || "";
    }

    _sendBroadcast(name, data) {
      const url = `${this.serverUrl}/broadcast`;
      fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ broadcast: name, data: data })
      }).catch(error => {
        console.error('Bridge Send Error:', error);
      });
    }

    _startPolling() {
      if (this.pollingInterval) {
        clearInterval(this.pollingInterval);
      }

      this.pollingInterval = setInterval(() => {
        fetch(`${this.serverUrl}/poll`)
          .then(res => {
            if (!res.ok) return [];
            return res.json();
          })
          .then(events => {
            if (!Array.isArray(events) || events.length === 0) return;

            events.forEach(evt => {
              const name = evt.event;
              const data = evt.data;

              // Save the values locally
              this.lastReceivedEvent = name;
              this.lastReceivedData = data;
              this.eventDataMap[name] = data;

              // Trigger targeted Hat block
              Scratch.vm.runtime.startHats('pythonBroadcast_whenBroadcastReceived', {
                EVENT: name
              });

              // Trigger general Hat block
              Scratch.vm.runtime.startHats('pythonBroadcast_whenAnyBroadcastReceived');
            });
          })
          .catch(() => {
            // Silently wait for the local server to come online
          });
      }, 100); // Polls every 100 milliseconds
    }
  }

  Scratch.extensions.register(new PythonBroadcastBridge());
})(window.Scratch);