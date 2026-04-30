# Performance Sample - 2026-04-30

Validation time: 2026-04-30 12:05 CST

Scope: lightweight local baseline after Job Status, Files, metadata-thread, and
temperature-pager changes. This is not a replacement for Orange Pi hardware profiling.

Command shape:

```bash
QT_QPA_PLATFORM=offscreen \
UV_INDEX_URL=https://pypi.org/simple \
uv run --locked python -m klippertouch --debug
```

Environment:

- Local development machine under the current workspace.
- Configured Moonraker endpoint: `http://3.106.225.214:5025`.
- Mode: controls enabled by local config, but no state-changing commands were sent.
- Sampling method: `ps` once per second for 25 seconds, tracking the child `python3`
  process rather than the `uv` wrapper.

Observed result:

- Startup CPU peak: about `25%`.
- 25-second average CPU: `5.43%`.
- Steady-state CPU after startup: about `3.0-3.5%`.
- Average RSS: `124.2 MiB`.
- Max RSS: `128.7 MiB`.
- Max threads: `13`; steady-state threads: `8`.

Interpretation:

- Current local baseline is materially below the earlier 20% CPU and ~295 MiB RSS
  observation, but the numbers are not directly comparable because this run used
  Qt offscreen rendering.
- The next meaningful profiling pass should run under the target display stack on
  Orange Pi class hardware and should sample per-thread CPU, especially Qt render,
  QML canvas, websocket, and file metadata threads.
