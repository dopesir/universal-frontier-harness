---
name: live-preview
description: Managed background server runner for UI and web deliverables. Enforces Rule 20 (interactive web applications must be served over HTTP rather than raw directory text).
---

# Live Preview Server

Launches a non-blocking managed background HTTP server for frontend deliverables.

## Usage
```bash
python skills/live-preview/scripts/serve_preview.py [directory] [--port 8080]
```

Ensures agents never dump raw local directory paths when delivering web apps.
Provides immediate `http://localhost:PORT` links.
