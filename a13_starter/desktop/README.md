# Windows App Shell

This folder contains the desktop wrapper for the existing A13 web project.

## What it does

- Starts the local A13 API server in-process.
- Opens the existing web UI inside a desktop window via `pywebview`.
- Keeps all Windows build tools under `D:\develop\a13-app-tools`.

## Quick smoke test on Windows

```powershell
D:\develop\a13-app-tools\venv\Scripts\python.exe D:\Code\server2026\a13_starter\desktop\launcher.py --smoke-test
```

## Build the Windows app

```powershell
powershell -ExecutionPolicy Bypass -File D:\Code\server2026\a13_starter\desktop\build_windows_app.ps1
```

The build output is written to:

```text
D:\develop\a13-app-tools\build\dist\CareerLoopA13App\CareerLoopA13App.exe
```
