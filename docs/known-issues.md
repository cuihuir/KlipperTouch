# Known Issues

## P1: Moonraker WebSocket status can become stale after runtime disconnects

Observed behavior: after KlipperTouch runs for a while, UI data can stop refreshing and remain
frozen, including temperatures and printer state. State-changing commands can still work, which
means the HTTP/JSON-RPC command path may still be alive while the status stream is stale.

Likely cause: Moonraker or Klipper service restarts, network interruptions, or explicit UI-side
socket teardown can leave the status subscription inactive. The command path can still work because
HTTP/JSON-RPC calls do not depend on the existing WebSocket subscription.

Required fix direction:

- On startup, query `server/info` first and only start the WebSocket subscription flow after
  Moonraker/Klipper state is usable.
- After WebSocket disconnects, poll `server/info` at low frequency instead of trying to keep the
  stale subscription alive.
- After an intentional socket close, also enter the same `server/info` polling path.
- When `server/info` reports ready, rebuild the status context as needed, reopen the WebSocket,
  and resubscribe all current objects.
- Surface `Moonraker disconnected/reconnecting/subscribed` state through the status model and
  splash/notification UI without blocking HTTP command attempts.
- Add tests for startup not-ready, explicit disconnect, intentional close, `server/info` polling,
  and ready-to-resubscribe recovery.

Validation target: leave KlipperTouch running while restarting Moonraker/Klipper or interrupting
network connectivity, then verify temperatures and status resume without restarting the GUI.
