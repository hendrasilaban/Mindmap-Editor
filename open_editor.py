#!/usr/bin/env python3
# ================================================================
# open_editor.py — run the draft TC mind map editor in the browser.
# Sub-project: PRD to Draft TC
# ================================================================
"""Serve `mindmap-editor.html` from a local server, then point the browser at it.

When run in the background, the URL is still readable: every line is printed with `flush=True`.
Without it Python buffers stdout for non-terminal output — measured 2026-08-28, when this command
was moved to the background by the harness and its output file stayed at 0 bytes, so the address
QA needed to open never appeared anywhere.

WHY A SERVER, when the editor is a single HTML file you can just double-click:

  The **File System Access API** (`showSaveFilePicker`) — which makes the Save button OVERWRITE the
  original `.mm` file instead of piling downloads into the Downloads folder — only works in a
  *secure context*. `http://localhost` is a secure context; `file://` depends on the browser and its
  version. So opening through this server is the GUARANTEED way to give QA a real Save button.

Opening the HTML file directly still works. All you lose is the ability to overwrite the file:
Save downloads a copy, and QA has to move it by hand. The editor says so in its status bar.

    python open_editor.py                # any free port, opens the browser
    python open_editor.py --port 8787
    python open_editor.py --no-browser   # for use from inside an IDE

Ctrl+C to stop.
"""
from __future__ import annotations

import argparse
import contextlib
import http.server
import socket
import socketserver
import sys
import threading
import webbrowser
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAGE = "mindmap-editor.html"


def free_port(preferred: int | None) -> int:
    if preferred:
        return preferred
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(HERE), **kw)

    def log_message(self, fmt, *args):        # quiet — QA does not need to see request logs
        pass


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Open the draft TC mind map editor.")
    ap.add_argument("--port", type=int)
    ap.add_argument("--no-browser", action="store_true")
    a = ap.parse_args(argv)

    if not (HERE / PAGE).exists():
        print(f"[REFUSED] {PAGE} not found in {HERE}", file=sys.stderr)
        return 1

    port = free_port(a.port)
    url = f"http://127.0.0.1:{port}/{PAGE}"

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", port), Handler) as srv:
        print(f"editor : {url}", flush=True)
        print(f"folder : {HERE}", flush=True)
        print("Save in the editor will OVERWRITE the opened .mm file (Chrome/Edge).", flush=True)
        print("Ctrl+C to stop.\n", flush=True)
        if not a.no_browser:
            threading.Timer(0.4, lambda: webbrowser.open(url)).start()
        with contextlib.suppress(KeyboardInterrupt):
            srv.serve_forever()
    print("\nstopped.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
