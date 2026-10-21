# Verification

Local verification on Windows used CPython 3.14.7, FastMCP 2.14.7 and MCP SDK 1.30.0
against packaged OpenMausBot server 0.1.118. The original bridge suite passed 11 tests,
including a real stdio round trip and health/bot-list calls. Two Authlib dependency
deprecation warnings were emitted. The user subsequently reported successful health
and bot-list calls from ChatGPT through the private tunnel.

The public suite separates `live` integration tests from portable unit tests and uses
a temporary fixture for configuration tests. Default CI runs without a local app.
The live test detects tool drift: eight expected read tools plus 12 opt-in actions.
It checks schema preservation, health, bot listing, invalid argument rejection and
action blocking. Action execution is tested against a mock only. No live bots are
messaged or changed by the test suite.

To reproduce: run `setup.ps1`, `verify.ps1`, then with the app running `verify.ps1 -Live`.
These results do not certify untested OS/Python/app versions or other people's
ChatGPT accounts. No credentials, tunnel identifiers, bot names, transcripts or
machine-specific verification logs are included in this repository.
