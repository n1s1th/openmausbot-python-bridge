# Security

The bridge is stdio-only. It does not create a public API, open firewall ports, or
implement an OAuth server. Use only trusted MCP clients. Read tools can retrieve
private transcripts; read-only does not mean public or non-sensitive.

Use OpenAI Secure MCP Tunnel for a private ChatGPT connection. The UI may describe
the upstream as “No authentication” because stdio has no separate OAuth flow; the
tunnel still requires OpenAI organization/workspace authorization and a runtime key.
Never expose OpenMausBot's REST port or this bridge through an unauthenticated public
HTTP forwarder. A public deployment needs properly implemented authentication and
access control and is outside this project's scope.

Keep tokens in a secret manager or process environment. Never commit `.env`, profiles,
API keys, session tokens, private keys, logs or transcripts. The bridge filters the
backend child environment so unrelated API keys and Node options are not forwarded.
The Python process and tunnel client still run inside your local trust boundary.

Action tools are blocked both in discovery and direct invocation unless explicitly
enabled. Unknown tools are always blocked. Action calls can cause external agent
activity; use client approval controls. The vendor implementation handles schemas,
paired session tokens and task semantics.

Keep stderr private: upstream errors may contain operation details. Review dependency
and upstream changes before upgrading, run unit and live tests, and rotate credentials
if exposed. Do not post secrets or private transcripts in public issues. For a security
report, contact the repository owner privately through their GitHub profile first and
request a secure reporting channel.
