import json
from pathlib import Path
import sys

import pytest
from fastmcp import Client, FastMCP
from fastmcp.client.transports import StdioTransport
from fastmcp.exceptions import ToolError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bridge import READ_TOOLS, WRITE_TOOLS, ToolPolicy, backend_transport, validate_origin


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.parametrize("value", [
    "http://example.com:8799", "http://user:password@localhost:8799",
    "http://127.0.0.1:8799/api", "http://localhost:8799?token=x",
    "https://localhost:8799", "http://localhost", "http://localhost:8799#x",
])
def test_reject_unsafe_origins(value):
    with pytest.raises(ValueError):
        validate_origin(value)


def test_loopback_origins():
    for value in ["http://127.0.0.1:8799", "http://localhost:8799/", "http://[::1]:8799"]:
        assert validate_origin(value) == value.rstrip("/")


def test_child_secrets_not_inherited(monkeypatch, tmp_path):
    script = tmp_path / "mcp-server.js"
    script.write_text("// test fixture only", encoding="utf-8")
    monkeypatch.setenv("OPENMAUSBOT_MCP_SCRIPT", str(script))
    monkeypatch.setenv("OPENMAUSBOT_URL", "http://127.0.0.1:8799")
    monkeypatch.setenv("OPENAI_API_KEY", "test-secret-not-real")
    monkeypatch.setenv("CONTROL_PLANE_API_KEY", "test-secret-not-real")
    monkeypatch.setenv("NODE_OPTIONS", "--inspect")
    transport = backend_transport()
    assert not {"OPENAI_API_KEY", "CONTROL_PLANE_API_KEY", "NODE_OPTIONS"} & transport.env.keys()
    assert transport.env["OPENMAUSBOT_URL"] == "http://127.0.0.1:8799"


@pytest.mark.anyio
async def test_policy_blocks_direct_calls_and_allows_opt_in():
    calls = []
    mock = FastMCP("policy-test")

    @mock.tool
    def create_bot(name: str):
        calls.append(name)
        return {"ok": True}

    mock.add_middleware(ToolPolicy())
    async with Client(mock) as client:
        assert await client.list_tools() == []
        with pytest.raises(ToolError):
            await client.call_tool("create_bot", {"name": "should-not-run"})
    assert calls == []
    enabled = FastMCP("opt-in-test")
    enabled.add_tool(create_bot)
    enabled.add_middleware(ToolPolicy(True))
    async with Client(enabled) as client:
        assert len(await client.list_tools()) == 1
        await client.call_tool("create_bot", {"name": "mock-only"})
    assert calls == ["mock-only"]


@pytest.mark.anyio
@pytest.mark.live
async def test_live_full_stdio_bridge():
    script = Path(__file__).resolve().parents[1] / "bridge.py"
    async with Client(backend_transport(), timeout=140) as upstream:
        tools = await upstream.list_tools()
        schemas = {tool.name: tool.inputSchema for tool in tools}
    assert set(schemas) == READ_TOOLS | WRITE_TOOLS
    transport = StdioTransport(command=sys.executable, args=[str(script)], keep_alive=False)
    async with Client(transport, timeout=140) as client:
        tools = await client.list_tools()
        assert {tool.name for tool in tools} == READ_TOOLS
        assert all(tool.inputSchema == schemas[tool.name] for tool in tools)
        health = await client.call_tool("get_system_health", {})
        payload = json.loads(health.content[0].text)
        assert payload["status"] == "connected"
        assert payload["app"] == "openmausbot"
        bots = await client.call_tool("list_bots", {})
        assert not bots.is_error
        with pytest.raises(ToolError):
            await client.call_tool("send_bot_message", {"bot_id": "never-sent", "text": "never-sent"})
        with pytest.raises(ToolError):
            await client.call_tool("get_bot_messages", {"bot_id": "invalid", "limit": 201})
    enabled = StdioTransport(command=sys.executable, args=[str(script), "--allow-writes"], keep_alive=False)
    async with Client(enabled, timeout=140) as client:
        assert {tool.name for tool in await client.list_tools()} == READ_TOOLS | WRITE_TOOLS
