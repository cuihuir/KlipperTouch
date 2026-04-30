# Known Issues

## P1: Moonraker WebSocket status can become stale after runtime disconnects

Observed behavior: after KlipperTouch runs for a while, UI data can stop refreshing and remain
frozen, including temperatures and printer state. State-changing commands can still work, which
means the HTTP/JSON-RPC command path may still be alive while the status stream is stale.

Likely cause: Moonraker or Klipper service restarts, network interruptions, or half-open
WebSocket connections can leave the existing status subscription inactive. The current stream has
basic reconnect and recovery polling for explicit socket errors, but it may not detect a silent
subscription stall where no `disconnected` or `errorOccurred` signal is emitted.

Required fix direction:

- Track a monotonic `last_status_update_at` timestamp for WebSocket messages that change or
  confirm status.
- Add a low-frequency watchdog, for example 2-5 seconds, that treats missing updates beyond a
  threshold as stale.
- On stale state, close the existing socket, poll `server/info` and `printer/info`, rebuild startup
  status if needed, then reopen the WebSocket and resubscribe all current objects.
- Surface `Moonraker disconnected/reconnecting/subscribed` state through the status model and
  splash/notification UI without blocking HTTP command attempts.
- Add tests for explicit disconnect, socket error, and silent no-message timeout.

Validation target: leave KlipperTouch running while restarting Moonraker/Klipper or interrupting
network connectivity, then verify temperatures and status resume without restarting the GUI.
