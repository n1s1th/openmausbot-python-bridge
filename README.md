# OpenMausBot Python MCP Bridge

Connect a local OpenMausBot installation to MCP clients using Python and FastMCP.
For ChatGPT, use a private OpenAI Secure MCP Tunnel. The bridge opens no HTTP listener
and enables read tools by default.

```text
ChatGPT → Secure MCP Tunnel → Python FastMCP bridge → vendor mcp-server.js → OpenMausBot
Local MCP client ───────────→ Python FastMCP bridge
```

This is an independent integration, not an official OpenMausBot or OpenAI product.
It uses the installed vendor MCP implementation; it does not bundle the app, its
JavaScript source, credentials, or the tunnel-client executable.

## Requirements

- Windows with Python 3.10+ and Node.js on PATH.
- OpenMausBot installed and running.
- For ChatGPT: access to custom MCP plugins and an authorized OpenAI Secure MCP Tunnel.

Tested locally on Windows with CPython 3.14.7, FastMCP 2.14.7 and MCP SDK 1.30.0,
against the packaged OpenMausBot server version 0.1.118. Other combinations are not
verified. The lock file records the exact dependencies used for verification.

## Quick start

```powershell
git clone https://github.com/n1s1th/openmausbot-python-bridge.git
cd openmausbot-python-bridge
.\setup.ps1
.\verify.ps1
.\verify.ps1 -Live
```

The default checks run without OpenMausBot. `-Live` additionally initializes the real
stdio bridge, checks tool schemas, calls health and lists bots. It never messages or
modifies a live bot. Keep OpenMausBot running for this check.

To start the server:

```powershell
.\start.ps1
```

It waits for an MCP client on stdin/stdout. An idle console is normal; Ctrl+C stops it.
Usually your MCP client launches it directly using the configuration below.

If PowerShell blocks scripts, use Python directly without changing machine policy:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m pytest -q -m "not live"
.\.venv\Scripts\python.exe bridge.py
```

## Connect a local MCP client

Copy [examples/mcp-client.json](examples/mcp-client.json) into your client's MCP
configuration and replace both `C:/path/to/...` values with your actual absolute paths.
Do not put API keys or paired tokens in a committed client configuration.

Ask your client:

> Call get_system_health, then list_bots. Show the actual tool results.

A successful health call reports `status: connected` and `app: openmausbot`.
Seeing your real bot list verifies the client-to-app path. A natural-language claim
without an actual tool invocation is not proof of connection.

## Connect ChatGPT

Follow [the private tunnel guide](docs/chatgpt-tunnel.md). Keep OpenMausBot and the
tunnel client running. After adding and enabling the plugin, run the same health and
bot-list prompts in ChatGPT. The bridge itself needs no OpenAI API key; the tunnel
client needs its own restricted runtime credential.

## Available tools

| Default read tools | Explicitly enabled action tools |
| --- | --- |
| `get_system_health` | `send_bot_message` |
| `list_bots` | `send_channel_message` |
| `list_channels` | `create_bot` |
| `list_available_models` | `update_bot_profile` |
| `get_bot_messages` | `create_channel` |
| `get_channel_messages` | `update_channel` |
| `search_messages` | `create_task` |
| `wait_for_conversation` | `switch_task` |
| | `rename_task` |
| | `set_bot_model` |
| | `edit_bot_message` |
| | `interrupt_conversation` |

To enable actions, start with `start.ps1 -AllowWrites` or add `--allow-writes` after
`bridge.py` in the client's command. Restart the client connection and refresh tool
discovery afterward. Action permission is not a replacement for OpenMausBot pairing.
Sending instructions may cause agents to use external tools. Require confirmation in
your client and inspect the intended bot and task first. Unknown tools are blocked,
including future upstream additions. Approval grants, deletion and computer lifecycle
tools are never allowlisted.

## Configuration

| Environment variable | Default / purpose |
| --- | --- |
| `OPENMAUSBOT_MCP_SCRIPT` | `%LOCALAPPDATA%/Programs/openmausbot/resources/server/mcp-server.js` |
| `OPENMAUSBOT_URL` | `http://127.0.0.1:8799`; explicit loopback HTTP origin only |
| `OPENMAUSBOT_TOKEN` | Optional paired session token required by the upstream for some actions |

For a nonstandard installation, set these in the launching process before starting
the client. The bridge does not automatically load `.env` files or discover ports.
Treat the configured Node script and loopback server as trusted code/services.

## Troubleshooting

- **App unreachable:** open OpenMausBot; check its actual port and `OPENMAUSBOT_URL`.
- **Script missing:** set `OPENMAUSBOT_MCP_SCRIPT` to the installed vendor script.
- **Node not found:** install Node.js and reopen your terminal/client.
- **403 on an action:** use OpenMausBot's supported pairing flow and pass its token in
  the launch environment. Do not extract app credential files.
- **Tool disabled:** actions need `--allow-writes`; reconnect and refresh discovery.
- **Local checks pass, ChatGPT fails:** run tunnel doctor and verify the organization,
  workspace association, permissions and running tunnel client.
- **Live schema test fails after an app update:** review the upstream tool changes;
  do not blindly expand the allowlist.

Read [SECURITY.md](SECURITY.md) before connecting transcript data. Dependency
deprecation warnings can occur with the pinned FastMCP/Authlib versions. No public
HTTPS/OAuth deployment is included.

## Development and license

```powershell
.\.venv\Scripts\python.exe -m pytest -q -m "not live"
.\.venv\Scripts\python.exe -m pytest -q
```

The second command includes the live integration test. GitHub Actions runs only the
portable unit tests. See [verification notes](docs/verification.md). MIT licensed;
third-party applications and dependencies retain their own licenses.
