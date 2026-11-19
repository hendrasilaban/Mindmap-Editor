#!/usr/bin/env python3
# ================================================================
# open_editor.py — jalankan editor mind map draft TC di browser.
# Sub-project: PRD to Draft TC
# ================================================================
"""Buka `mindmap-editor.html` lewat server lokal, lalu arahkan browser ke situ.

Dijalankan di background, URL-nya tetap terbaca: setiap baris dicetak dengan `flush=True`.
Tanpa itu Python menahan buffer stdout untuk keluaran non-terminal — terukur 2026-08-28, saat
perintah ini dipindahkan ke background oleh harness dan file output-nya tinggal 0 byte, jadi
alamat yang harus dibuka QA tidak pernah muncul di mana pun.

KENAPA PERLU SERVER, padahal editornya satu file HTML yang bisa di-klik dua kali:

  **File System Access API** (`showSaveFilePicker`) — yang membuat tombol Simpan MENIMPA berkas
  `.mm` aslinya, bukan menumpuk unduhan di folder Downloads — hanya aktif di *secure context*.
  `http://localhost` termasuk secure context; `file://` tergantung browser dan versinya. Jadi
  membuka lewat server ini adalah cara yang PASTI memberi QA tombol Simpan yang sesungguhnya.

Membuka file HTML-nya langsung tetap bisa. Yang hilang cuma kemampuan menimpa berkas: Simpan akan
mengunduh salinan, dan QA harus memindahkannya sendiri. Editor menyebutkan itu di status bar-nya.

    python tools/open_editor.py                # port bebas, langsung buka browser
    python tools/open_editor.py --port 8787
    python tools/open_editor.py --no-browser   # untuk dipakai dari dalam IDE

Ctrl+C untuk berhenti.
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

    def log_message(self, fmt, *args):        # tenang — QA tidak perlu melihat log request
        pass


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Buka editor mind map draft TC.")
    ap.add_argument("--port", type=int)
    ap.add_argument("--no-browser", action="store_true")
    a = ap.parse_args(argv)

    if not (HERE / PAGE).exists():
        print(f"[REFUSED] {PAGE} tidak ada di {HERE}", file=sys.stderr)
        return 1

    port = free_port(a.port)
    url = f"http://127.0.0.1:{port}/{PAGE}"

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", port), Handler) as srv:
        print(f"editor : {url}", flush=True)
        print(f"folder : {HERE}", flush=True)
        print("Simpan di editor akan MENIMPA berkas .mm yang dibuka (Chrome/Edge).", flush=True)
        print("Ctrl+C untuk berhenti.\n", flush=True)
        if not a.no_browser:
            threading.Timer(0.4, lambda: webbrowser.open(url)).start()
        with contextlib.suppress(KeyboardInterrupt):
            srv.serve_forever()
    print("\nberhenti.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
