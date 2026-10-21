"""Private stdio FastMCP bridge to the installed OpenMausBot MCP server."""
import argparse
import os
from pathlib import Path
import shutil
from urllib.parse import urlsplit

from fastmcp import Client, FastMCP
from fastmcp.client.transports import StdioTransport
from fastmcp.exceptions import ToolError
from fastmcp.server.middleware import Middleware

READ_TOOLS = frozenset({
    "get_system_health", "list_bots", "list_channels", "list_available_models",
    "get_bot_messages", "get_channel_messages", "search_messages", "wait_for_conversation",
})
WRITE_TOOLS = frozenset({
    "send_bot_message", "send_channel_message", "create_bot", "update_bot_profile",
    "create_channel", "update_channel", "create_task", "switch_task", "rename_task",
    "set_bot_model", "edit_bot_message", "interrupt_conversation",
})


def validate_origin(value):
    parsed = urlsplit(value)
    if (parsed.scheme != "http" or parsed.hostname not in {"127.0.0.1", "localhost", "::1"}
            or parsed.username or parsed.password or parsed.path not in {"", "/"}
            or parsed.query or parsed.fragment):
        raise ValueError("OPENMAUSBOT_URL must be a loopback HTTP origin without credentials")
    if not parsed.port:
        raise ValueError("OPENMAUSBOT_URL requires an explicit port")
    return value.rstrip("/")


def backend_transport():
    default = Path(os.environ.get("LOCALAPPDATA", "")) / "Programs/openmausbot/resources/server/mcp-server.js"
    script = Path(os.environ.get("OPENMAUSBOT_MCP_SCRIPT", str(default))).resolve()
    if not script.is_file() or script.name != "mcp-server.js":
        raise ValueError("Set OPENMAUSBOT_MCP_SCRIPT to the installed mcp-server.js")
    node = shutil.which("node")
    if not node:
        raise ValueError("Node.js is required and must be on PATH")
    origin = validate_origin(os.environ.get("OPENMAUSBOT_URL", "http://127.0.0.1:8799"))
    # Deliberately do not inherit unrelated API keys, tunnel credentials or NODE_OPTIONS.
    env = {key: os.environ[key] for key in (
        "SYSTEMROOT", "WINDIR", "PATH", "PATHEXT", "TEMP", "TMP", "USERPROFILE",
        "LOCALAPPDATA", "APPDATA", "HOME",
    ) if key in os.environ}
    env["OPENMAUSBOT_URL"] = origin
    if os.environ.get("OPENMAUSBOT_TOKEN"):
        env["OPENMAUSBOT_TOKEN"] = os.environ["OPENMAUSBOT_TOKEN"]
    return StdioTransport(command=node, args=[str(script)], env=env, keep_alive=False)


class ToolPolicy(Middleware):
    def __init__(self, allow_writes=False):
        self.allowed = READ_TOOLS | WRITE_TOOLS if allow_writes else READ_TOOLS

    async def on_list_tools(self, context, call_next):
        return [tool for tool in await call_next(context) if tool.name in self.allowed]

    async def on_call_tool(self, context, call_next):
        if context.message.name not in self.allowed:
            raise ToolError("Tool disabled by bridge policy; write tools require --allow-writes")
        return await call_next(context)


def build_server(allow_writes=False):
    server = FastMCP.as_proxy(Client(backend_transport(), timeout=135), name="OpenMausBot Python Bridge")
    server.add_middleware(ToolPolicy(allow_writes))
    return server


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-writes", action="store_true", help="Enable the 12 named action tools")
    args = parser.parse_args()
    build_server(args.allow_writes).run(transport="stdio", show_banner=False)
