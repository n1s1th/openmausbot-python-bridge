# Documentation website source

Public documentation: https://openmausbot-python-mcp-bridge.copperpearl.chatgpt.site/

`build_site.py` uses Python's standard library to generate the six static pages in
`dist/`. It makes no API calls, loads no credentials, and requires no Node packages.

From the repository root:

```powershell
python website/build_site.py website/dist
python -m http.server 8000 --directory website/dist
```

Open http://127.0.0.1:8000 locally. Stop the preview with Ctrl+C.

The production documentation is hosted with Sites. A GitHub commit alone does not
deploy it. To update production, edit/rebuild this source, then use the owning
account's Sites publishing workflow. Never add deployment credentials or private
hosting state to this public directory. Keep the canonical host and sitemap consistent.

The `.gitignore` excludes build directories by default. If committing regenerated
HTML, explicitly stage the intended static files with `git add -f website/dist`.
