# Setup
Der ganze Kram muss in der WSL ausgeführt werden.
Claude ist echt kein Freund von Windows.

Pycharm in WSL Remote Development starten. 

## UV installieren: 
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```
Source einstellen. Genauer Pfad wird aber auch angegeben.
```bash
source $HOME/.local/bin/env
```
```bash
cd /mnt/e/Programmierung/Python/MCPServer
```

## .venv aufsetzen
.venv muss innerhalb der WSL erstellt werden
```bash
cd /mnt/e/Programmierung/Python/MCPServer
```
```bash
uv venv
```
```bash
source .venv/bin/activate
```

## Pakete installieren
In der `pyproject.toml` sollte folgendes enthalten sein:
```toml
dependencies = [
    "mcp[cli]>=1.11.0",
]
```
```bash
uv sync
```

## MCP in Claude Desktop installieren
```bash
uv mcp install main.py
```

## MCP in Claude Code installieren
`.mcp.json` im Projektordner ablegen für Projektweites MCP

Alternativ, wenns schon in Claude Desktop installiert ist:
```bash
claude mcp add-from-claude-desktop
```
Aber hab ich noch nicht getestet. 

Für globales siehe https://docs.anthropic.com/en/docs/claude-code/mcp

