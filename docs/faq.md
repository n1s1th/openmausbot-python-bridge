# OpenMausBot ChatGPT integration: frequently asked questions

## What is the OpenMausBot Python MCP bridge?

An independent Python stdio proxy built with FastMCP. It connects MCP clients to
the vendor mcp-server.js shipped with an installed OpenMausBot app, preserving tool
schemas and results while enforcing an explicit allowlist.

## How do I connect OpenMausBot to ChatGPT?

Install the bridge, configure OpenAI Secure MCP Tunnel to launch it, add a custom
MCP plugin using the authorized tunnel, and enable the plugin in a chat. Follow the
[ChatGPT tunnel guide](chatgpt-tunnel.md), then verify actual health and bot-list calls.

## Does the bridge need an OpenAI API key?

No. The separate OpenAI tunnel client needs its own restricted runtime credential.
OpenMausBot may require a paired session token for actions.

## Can I use it without ChatGPT?

Yes. A compatible local MCP client can launch the Python bridge directly over stdio,
without an OpenAI tunnel. Start with the [example configuration](../examples/mcp-client.json).

## Can ChatGPT send instructions to bots?

The bridge supports message-sending tools, but actions are disabled by default.
Enable --allow-writes explicitly, satisfy app pairing requirements, restart the
connection and refresh discovery. Agent instructions can cause external tool use.

## Does it expose a public API?

No. The bridge is stdio-only and accepts only loopback upstream origins. The
documentation website is public; private tunnel profiles, credentials and bot data
are not part of that website. See the [security policy](../SECURITY.md).

## Is this an official OpenMausBot or OpenAI plugin?

No. This is an independent MIT-licensed integration. Third-party applications and
dependencies retain their own ownership and licenses.

## What proves that the connection works?

An actual get_system_health call reporting status: connected and app: openmausbot,
followed by list_bots returning the expected team. A natural-language claim or a
“tunnel started” message alone does not prove the complete connection works.

## Which versions are verified?

Windows, Python 3.14.7, FastMCP 2.14.7, MCP SDK 1.30.0 and packaged OpenMausBot server
0.1.118 were used for local verification. Run unit and live tests after updates.
