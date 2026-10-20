#!/usr/bin/env python3
"""Universal Frontier Engineering Harness — Spatial Multi-Viewport Preview Daemon.

Starts a lightweight, zero-dependency HTTP server for web deliverables,
verifies that the port is serving HTTP 200, and outputs clean clickable URLs:
- Solo Deliverable Viewport: http://localhost:PORT/
- Spatial Multi-Viewport Workbench: http://localhost:PORT/__spatial__
  (Simultaneous Desktop HD 1440x900, Tablet 768x1024, Mobile 390x844)
"""

from __future__ import annotations

import argparse
import http.server
import os
import socket
import socketserver
import sys
import threading
import time
import urllib.request


def generate_spatial_html(port: int, title: str = "DELIVERABLE PREVIEW") -> str:
    """Generates the self-contained Spatial Multi-Viewport Workbench."""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>SPATIAL WORKBENCH // DAEMON PORT {port}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=Space+Mono:wght@400;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-dark: #08090b;
      --bg-panel: #111317;
      --bg-card: #181a20;
      --border-subtle: rgba(255, 255, 255, 0.08);
      --border-active: rgba(0, 240, 255, 0.4);
      --text-main: #f4f4f6;
      --text-muted: #717786;
      --accent-cyan: #00f0ff;
      --accent-lime: #d8ff00;
      --status-green: #10b981;
      --font-ui: 'Plus Jakarta Sans', sans-serif;
      --font-mono: 'Space Mono', monospace;
    }}

    *, *::before, *::after {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      background-color: var(--bg-dark);
      color: var(--text-main);
      font-family: var(--font-ui);
      overflow-x: auto;
      overflow-y: hidden;
      height: 100vh;
      display: flex;
      flex-direction: column;
    }}

    .workbench-header {{
      height: 56px;
      background: var(--bg-panel);
      border-bottom: 1px solid var(--border-subtle);
      padding: 0 24px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-shrink: 0;
      z-index: 100;
    }}

    .brand-section {{
      display: flex;
      align-items: center;
      gap: 16px;
    }}

    .brand-title {{
      font-family: var(--font-mono);
      font-size: 13px;
      font-weight: 700;
      letter-spacing: 0.1em;
      color: var(--text-main);
    }}

    .badge-clean {{
      font-family: var(--font-mono);
      font-size: 10px;
      color: var(--status-green);
      background: rgba(16, 185, 129, 0.12);
      border: 1px solid rgba(16, 185, 129, 0.25);
      padding: 3px 8px;
      border-radius: 12px;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}

    .badge-clean::before {{
      content: "";
      width: 5px;
      height: 5px;
      border-radius: 50%;
      background: var(--status-green);
      box-shadow: 0 0 8px var(--status-green);
    }}

    .controls-section {{
      display: flex;
      align-items: center;
      gap: 16px;
    }}

    .zoom-group {{
      display: flex;
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      border-radius: 4px;
      padding: 2px;
    }}

    .zoom-btn {{
      background: transparent;
      border: none;
      color: var(--text-muted);
      font-family: var(--font-mono);
      font-size: 11px;
      padding: 4px 10px;
      cursor: pointer;
      border-radius: 2px;
      transition: all 0.2s;
    }}

    .zoom-btn:hover, .zoom-btn.active {{
      background: var(--border-subtle);
      color: var(--text-main);
    }}

    .filter-group {{
      display: flex;
      gap: 6px;
    }}

    .filter-pill {{
      background: var(--bg-card);
      border: 1px solid var(--border-subtle);
      color: var(--text-muted);
      font-family: var(--font-mono);
      font-size: 11px;
      padding: 4px 12px;
      border-radius: 4px;
      cursor: pointer;
      transition: all 0.2s;
    }}

    .filter-pill:hover, .filter-pill.active {{
      border-color: var(--accent-cyan);
      color: var(--accent-cyan);
    }}

    .solo-link-btn {{
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid var(--border-subtle);
      color: var(--text-main);
      font-family: var(--font-mono);
      font-size: 11px;
      padding: 6px 14px;
      border-radius: 4px;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: background 0.2s;
    }}

    .solo-link-btn:hover {{
      background: rgba(255, 255, 255, 0.14);
    }}

    .workbench-viewport-stage {{
      flex: 1;
      overflow-x: auto;
      overflow-y: hidden;
      padding: 32px;
      display: flex;
      align-items: flex-start;
      gap: 40px;
      transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      transform-origin: top left;
    }}

    .device-column {{
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
    }}

    .device-meta-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
      font-family: var(--font-mono);
      font-size: 11px;
    }}

    .device-name {{
      color: var(--text-main);
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}

    .device-dims {{
      color: var(--text-muted);
    }}

    .device-chassis {{
      background: var(--bg-panel);
      border: 1px solid var(--border-subtle);
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
      position: relative;
    }}

    .device-frame {{
      border: none;
      display: block;
      background: #000;
    }}

    .chassis-desktop {{ width: 1440px; height: 900px; }}
    .chassis-tablet {{ width: 768px; height: 1024px; }}
    .chassis-mobile {{ width: 390px; height: 844px; border-radius: 36px; }}

    .stage-scale-50 {{ transform: scale(0.5); }}
    .stage-scale-75 {{ transform: scale(0.75); }}
    .stage-scale-100 {{ transform: scale(1.0); }}
  </style>
</head>
<body>

  <header class="workbench-header">
    <div class="brand-section">
      <span class="brand-title">SPATIAL WORKBENCH // DAEMON PORT {port}</span>
      <span class="badge-clean">LIVE MULTI-VIEWPORT WORKBENCH</span>
    </div>

    <div class="controls-section">
      <div class="zoom-group">
        <button class="zoom-btn" onclick="setScale(50, this)">50%</button>
        <button class="zoom-btn active" onclick="setScale(75, this)">75%</button>
        <button class="zoom-btn" onclick="setScale(100, this)">100%</button>
      </div>

      <div class="filter-group">
        <button class="filter-pill active" onclick="filterDevice('all', this)">All</button>
        <button class="filter-pill" onclick="filterDevice('desktop', this)">Desktop</button>
        <button class="filter-pill" onclick="filterDevice('tablet', this)">Tablet</button>
        <button class="filter-pill" onclick="filterDevice('mobile', this)">Mobile</button>
      </div>

      <a href="http://localhost:{port}/" target="_blank" class="solo-link-btn">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6M15 3h6v6M10 14L21 3"/></svg>
        Open Solo Site
      </a>
    </div>
  </header>

  <main class="workbench-viewport-stage stage-scale-75" id="viewport-stage">
    
    <!-- DESKTOP HD (1440 x 900) -->
    <div class="device-column" id="dev-col-desktop">
      <div class="device-meta-header">
        <span class="device-name">Desktop HD</span>
        <span class="device-dims">1440 &times; 900</span>
      </div>
      <div class="device-chassis chassis-desktop">
        <iframe src="http://localhost:{port}/" class="device-frame" style="width: 1440px; height: 900px;" loading="lazy"></iframe>
      </div>
    </div>

    <!-- TABLET PORTRAIT (768 x 1024) -->
    <div class="device-column" id="dev-col-tablet">
      <div class="device-meta-header">
        <span class="device-name">Tablet Portrait</span>
        <span class="device-dims">768 &times; 1024</span>
      </div>
      <div class="device-chassis chassis-tablet">
        <iframe src="http://localhost:{port}/" class="device-frame" style="width: 768px; height: 1024px;" loading="lazy"></iframe>
      </div>
    </div>

    <!-- MOBILE IPHONE 15 (390 x 844) -->
    <div class="device-column" id="dev-col-mobile">
      <div class="device-meta-header">
        <span class="device-name">Mobile iPhone 15</span>
        <span class="device-dims">390 &times; 844</span>
      </div>
      <div class="device-chassis chassis-mobile">
        <iframe src="http://localhost:{port}/" class="device-frame" style="width: 390px; height: 844px;" loading="lazy"></iframe>
      </div>
    </div>

  </main>

  <script>
    function setScale(val, btn) {{
      const stage = document.getElementById('viewport-stage');
      stage.className = `workbench-viewport-stage stage-scale-${{val}}`;
      document.querySelectorAll('.zoom-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
    }}

    function filterDevice(type, btn) {{
      document.querySelectorAll('.filter-pill').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');

      const d = document.getElementById('dev-col-desktop');
      const t = document.getElementById('dev-col-tablet');
      const m = document.getElementById('dev-col-mobile');

      if (type === 'all') {{
        d.style.display = 'flex';
        t.style.display = 'flex';
        m.style.display = 'flex';
      }} else if (type === 'desktop') {{
        d.style.display = 'flex';
        t.style.display = 'none';
        m.style.display = 'none';
      }} else if (type === 'tablet') {{
        d.style.display = 'none';
        t.style.display = 'flex';
        m.style.display = 'none';
      }} else if (type === 'mobile') {{
        d.style.display = 'none';
        t.style.display = 'none';
        m.style.display = 'flex';
      }}
    }}
  </script>
</body>
</html>
"""


def find_free_port(preferred: int = 3000) -> int:
    for port in [preferred, 5173, 5185, 5186, 5187, 5188, 8080, 5000, 4200]:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def is_server_ready(port: int, timeout: int = 5) -> bool:
    start = time.time()
    url = f"http://127.0.0.1:{port}"
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=1) as resp:
                if resp.status in (200, 301, 302, 304):
                    return True
        except Exception:
            time.sleep(0.1)
    return False


def start_server(directory: str, port: int):
    directory = os.path.abspath(directory)
    if not os.path.isdir(directory):
        print(f"Error: Target directory does not exist: {directory}")
        sys.exit(1)

    class SpatialHTTPHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)

        def do_GET(self):
            # Intercept /__spatial__ to render the Multi-Viewport Workbench
            if self.path in ("/__spatial__", "/__spatial"):
                html_bytes = generate_spatial_html(port).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(html_bytes)))
                self.end_headers()
                self.wfile.write(html_bytes)
                return

            return super().do_GET()

        def log_message(self, format, *args):
            pass  # Suppress request spam

    with socketserver.TCPServer(("127.0.0.1", port), SpatialHTTPHandler) as httpd:
        httpd.serve_forever()


def main():
    parser = argparse.ArgumentParser(description="Serve a local directory with Spatial Multi-Viewport Workbench")
    parser.add_argument("directory", nargs="?", default=".", help="Directory to serve (default: current directory)")
    parser.add_argument("--dir", default=None, help="Directory override")
    parser.add_argument("--port", type=int, default=0, help="Port to use (default: auto-detect free port)")
    parser.add_argument("--verify-only", action="store_true", help="Check if port is already running and exit")
    args = parser.parse_args()

    serve_dir = os.path.abspath(args.dir if args.dir else args.directory)
    port = args.port if args.port > 0 else find_free_port(3000)

    if args.verify_only:
        ready = is_server_ready(port)
        if ready:
            print(f"[OK] Server running at http://localhost:{port}")
            sys.exit(0)
        else:
            print(f"[FAIL] No server responding at http://localhost:{port}")
            sys.exit(1)

    t = threading.Thread(target=start_server, args=(serve_dir, port), daemon=True)
    t.start()

    ready = is_server_ready(port, timeout=4)
    if ready:
        print("[WEB PREVIEW READY]")
        print(f"  Solo URL: http://localhost:{port}")
        print(f"  Spatial Workbench URL: http://localhost:{port}/__spatial__")
        print(f"  Directory: {serve_dir}")
        print(f"  Link: 🌐 [Open Web Application (http://localhost:{port})](http://localhost:{port})")
        print(f"  Spatial Link: 🌐 [Open Spatial Workbench (http://localhost:{port}/__spatial__)](http://localhost:{port}/__spatial__)")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            sys.exit(0)
    else:
        print(f"[ERROR] Server failed to start on port {port}")
        sys.exit(1)


if __name__ == "__main__":
    main()
