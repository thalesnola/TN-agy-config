---
name: google-colab
description: Interact with Google Colab via the official CLI (google-colab-cli) and MCP server (colab-mcp). Use when running remote Python scripts, Jupyter notebooks (.ipynb), GPU/TPU workloads (T4, L4, A100), managing Colab runtimes, or bridging local AI agents directly to Google Colab in the browser.
---

# Google Colab Toolkit: CLI & MCP Integration

This skill provides operational guidance for controlling Google Colab both via the command-line interface (`colab`) and the Model Context Protocol server (`colab-mcp`).

---

## 1. Google Colab CLI (`colab`)

Executable path: `%USERPROFILE%\.local\bin\colab.exe` (installed via `uv tool`).
Global state location: `~/.config/colab-cli/sessions.json`

### Authentication
- **Default strategy**: `oauth2` or `adc` (Application Default Credentials).
- **OAuth2**: First command will prompt to visit an authorization URL and paste back the authorization code.
- **ADC** (recommended for headless execution):
  ```powershell
  gcloud auth application-default login --scopes=openid,https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/colaboratory,https://www.googleapis.com/auth/drive.file
  ```
- **Check authentication & sessions**:
  ```powershell
  colab sessions
  ```

### Lifecycle Management
- **Provision CPU runtime**:
  ```powershell
  colab new -s my-session
  ```
- **Provision GPU/TPU runtime**:
  ```powershell
  colab new -s gpu-session --gpu T4
  # Options: T4, L4, A100, H100, v5e1, v6e1. Add --high-mem for high-RAM shape.
  ```
- **Inspect status & resources**:
  ```powershell
  colab status -s my-session
  ```
- **Stop runtime (CRITICAL to avoid burning compute units)**:
  ```powershell
  colab stop -s my-session
  ```

### Code Execution
- **Run local script on remote VM**:
  ```powershell
  colab exec -s my-session -f script.py
  ```
- **Run local notebook (.ipynb) and save output**:
  ```powershell
  colab exec -s my-session -f notebook.ipynb
  # Writes results to notebook_output.ipynb
  ```
- **Piped execution**:
  ```powershell
  echo "import torch; print(torch.cuda.is_available())" | colab exec -s gpu-session
  ```
- **Ephemeral one-shot execution (`colab run`)**:
  Allocates VM, runs script, retrieves outputs, and immediately tears down VM:
  ```powershell
  colab run --gpu T4 train.py
  ```

### File Management & Drive
- **List remote files**:
  ```powershell
  colab ls -s my-session /content
  ```
- **Upload / Download files**:
  ```powershell
  colab upload -s my-session local_file.csv /content/data.csv
  colab download -s my-session /content/model.pt ./model.pt
  ```
- **Mount Google Drive**:
  ```powershell
  colab drivemount -s my-session
  ```

---

## 2. Colab MCP Server (`colab-mcp`)

Executable path: `%USERPROFILE%\.local\bin\colab-mcp.exe`
Registered in:
- `~/.gemini/config/mcp_config.json` (Antigravity global)
- `~/.claude.json` (Claude Code)

### How Colab MCP Works
1. When launched, `colab-mcp` exposes the bootstrap tool `open_colab_browser_connection`.
2. When called, it opens a Google Colab notebook session in the browser containing authentication hash parameters (`#mcpProxyToken=...&mcpProxyPort=...`).
3. The Colab browser frontend connects via WebSocket to the local server.
4. `colab-mcp` emits `notifications/tools/list_changed`, immediately unlocking live notebook editing, cell manipulation, and execution tools directly within the agent.
