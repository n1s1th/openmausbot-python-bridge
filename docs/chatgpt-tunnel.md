# Connect to ChatGPT with a private tunnel

This guide uses an existing local stdio server. It does not publish an unauthenticated
endpoint. OpenAI account/workspace access and Platform tunnel permissions are separate.

1. Open [Platform tunnel settings](https://platform.openai.com/settings/organization/tunnels).
   Select the intended organization, create/reuse a tunnel, and associate the intended
   ChatGPT workspace. Creating a tunnel requires Tunnels Read + Manage; using it
   requires Tunnels Read + Use.
2. Download the current official `tunnel-client` from that page or the
   [official releases](https://github.com/openai/tunnel-client/releases). Choose the
   archive for your Windows architecture and verify it using the release instructions.
   Extract it into a trusted local directory. No tunnel executable is bundled here.
3. Create a restricted runtime key in the same organization. Do not give the long-lived
   runtime an admin key. Keep it out of chat, command history and repository files.
4. In PowerShell, run the following using your own paths and tunnel ID:

```powershell
& 'C:/path/to/tunnel-client/tunnel-client.exe' help quickstart
& 'C:/path/to/tunnel-client/tunnel-client.exe' init --sample sample_mcp_stdio_local --profile openmausbot --profile-dir 'C:/path/to/private-profiles' --tunnel-id YOUR_TUNNEL_ID --mcp-command 'C:/path/to/openmausbot-python-bridge/.venv/Scripts/python.exe C:/path/to/openmausbot-python-bridge/bridge.py' --health-listen-addr '127.0.0.1:0'
```

Use forward slashes in `--mcp-command`: the client's command parser treats backslashes
as escapes. If paths contain spaces, double-quote each complete path inside that
single-quoted command string. Store generated profiles outside the repository.

5. Launch with the helper below. It asks for the runtime key at a hidden prompt, passes
   it through the process environment, runs doctor, and starts the client only if the
   check succeeds. It does not save the credential to disk.

```powershell
.\connect-tunnel.ps1 -ClientPath 'C:/path/to/tunnel-client/tunnel-client.exe' -ProfilePath 'C:/path/to/private-profiles/openmausbot.yaml'
```

6. Keep that terminal and OpenMausBot running. In ChatGPT, open **Plugins → Add →
   Add custom MCP server**. Enter a name, choose **Tunnel**, and select/enter your tunnel.
   For this stdio bridge choose **No authentication** for the upstream; tunnel access
   remains controlled by OpenAI. Review the access warning and create/install the plugin.
   Labels and availability can vary by account and client version.
7. Enable OpenMausBot in a new chat and ask it to call `get_system_health`, then
   `list_bots`. Confirm actual tool calls and the expected live results. Do not assume
   “client started” alone proves that discovery or tool execution works.

Do not paste runtime keys into the plugin form. If doctor reports permission or workspace
errors, resolve the organization/workspace association rather than exposing a public port.
If tunnels are unavailable, keep using a local MCP client until access is available.

Official references:
[Secure MCP Tunnel](https://developers.openai.com/api/docs/guides/secure-mcp-tunnels),
[MCP server security](https://developers.openai.com/plugins/build/mcp-server),
[Authentication](https://developers.openai.com/plugins/build/auth).
