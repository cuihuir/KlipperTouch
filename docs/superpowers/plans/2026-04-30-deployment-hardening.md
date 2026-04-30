# Deployment Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the validated EGLFS/Mali-G52 deployment the maintained production path while preserving an explicit X11 rollback service.

**Architecture:** Keep all runtime service assets in `deploy/`. Make `klippertouch-eglfs.service` installable and boot-default capable, remove the stale Wayland service example, add an idempotent systemd installer, and document control validation. Tests stay focused on deployment assets and documentation strings so future service drift is caught.

**Tech Stack:** systemd, Bash, Qt EGLFS/KMS, PySide6/QML, pytest.

---

### Task 1: Make EGLFS The Installable Default

**Files:**
- Modify: `deploy/klippertouch-eglfs.service`
- Modify: `deploy/klippertouch-eglfs-start.sh`
- Modify: `deploy/klippertouch.service`
- Modify: `deploy/klippertouch-start.sh`
- Test: `tests/unit/test_deploy_assets.py`

- [ ] **Step 1: Write the failing test**

Add assertions that `deploy/klippertouch-eglfs.service` has `[Install]`, `WantedBy=multi-user.target`, `Restart=always`, no `Experiment` description, and does not set verbose scenegraph/KMS logging by default. Add assertions that both default client commands omit `--debug` and keep `--allow-controls --fullscreen`.

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
UV_INDEX_URL=https://pypi.org/simple uv run --locked --extra dev pytest -q tests/unit/test_deploy_assets.py
```

Expected: FAIL because EGLFS is still static/manual and debug logging is still enabled.

- [ ] **Step 3: Implement the service changes**

Update the EGLFS service to production wording, add restart policy and `[Install]`, remove default `QSG_INFO=1` and verbose `QT_LOGGING_RULES`, and remove `--debug` from both X11 and EGLFS default client commands.

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
UV_INDEX_URL=https://pypi.org/simple uv run --locked --extra dev pytest -q tests/unit/test_deploy_assets.py
```

Expected: PASS.

### Task 2: Add Idempotent Systemd Installer

**Files:**
- Create: `deploy/install-systemd.sh`
- Test: `tests/unit/test_deploy_assets.py`

- [ ] **Step 1: Write the failing test**

Add a test that runs `bash -n deploy/install-systemd.sh`, checks executable mode, and asserts the script installs both service files, both launcher scripts, the EGLFS KMS config, runs `systemctl daemon-reload`, enables EGLFS by default, disables X11 by default, and supports `x11` rollback mode.

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
UV_INDEX_URL=https://pypi.org/simple uv run --locked --extra dev pytest -q tests/unit/test_deploy_assets.py
```

Expected: FAIL because `deploy/install-systemd.sh` does not exist.

- [ ] **Step 3: Implement the installer**

Create a Bash script with `set -euo pipefail`, a positional mode argument of `eglfs` or `x11`, `install -m` calls for assets, optional config installation that does not overwrite an existing config unless `KLIPPERTOUCH_OVERWRITE_CONFIG=1`, `systemctl daemon-reload`, and enable/disable logic for the selected mode.

- [ ] **Step 4: Run test to verify it passes**

Run:

```bash
UV_INDEX_URL=https://pypi.org/simple uv run --locked --extra dev pytest -q tests/unit/test_deploy_assets.py
```

Expected: PASS.

### Task 3: Remove Stale Wayland Example And Update Docs

**Files:**
- Delete: `deploy/systemd/klippertouch.service.example`
- Modify: `tests/unit/test_deployment_docs.py`
- Modify: `docs/deployment.md`
- Modify: `docs/deployment_cn.md`

- [ ] **Step 1: Write the failing test**

Change `tests/unit/test_deployment_docs.py` to assert the stale Wayland example file is absent, the docs mention `deploy/install-systemd.sh eglfs`, and the docs include a control validation checklist with temperature target, motion, extrusion, print control, emergency stop, and tuning controls.

- [ ] **Step 2: Run test to verify it fails**

Run:

```bash
UV_INDEX_URL=https://pypi.org/simple uv run --locked --extra dev pytest -q tests/unit/test_deployment_docs.py
```

Expected: FAIL because the Wayland example still exists and docs do not yet mention the installer/checklist.

- [ ] **Step 3: Implement docs cleanup**

Delete the stale Wayland example and update both deployment guides to describe EGLFS as the default, X11 as rollback, installer usage, reduced logging, and the control validation checklist.

- [ ] **Step 4: Run docs tests**

Run:

```bash
UV_INDEX_URL=https://pypi.org/simple uv run --locked --extra dev pytest -q tests/unit/test_deployment_docs.py
```

Expected: PASS.

### Task 4: Verify And Deploy To 227

**Files:**
- No source changes

- [ ] **Step 1: Run full local verification**

Run:

```bash
UV_INDEX_URL=https://pypi.org/simple uv run --locked --extra dev pytest -q
UV_INDEX_URL=https://pypi.org/simple uv run --locked --extra dev ruff check src tests tools
UV_INDEX_URL=https://pypi.org/simple uv run --locked --extra dev mypy src/klippertouch
```

Expected: all pass.

- [ ] **Step 2: Install service assets on 227**

Copy `deploy/` assets to the target and run the installer in EGLFS mode. Confirm `klippertouch-eglfs.service` is enabled and active, and `klippertouch.service` is disabled.

- [ ] **Step 3: Leave reboot validation explicit**

Do not reboot without operator confirmation. Record that reboot validation is the remaining hardware step after enabling the service.

