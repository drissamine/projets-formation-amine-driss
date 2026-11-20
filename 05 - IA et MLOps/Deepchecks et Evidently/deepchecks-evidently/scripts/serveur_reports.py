#!/usr/bin/env python3
"""Lance un serveur HTTP local sur le projet et ouvre le rapport de synthèse."""
import http.server
from functools import partial
import socketserver
import threading
import webbrowser
from pathlib import Path

PORT = 8765
ROOT = Path(__file__).resolve().parents[1]

handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT))

socketserver.TCPServer.allow_reuse_address = True
httpd = socketserver.TCPServer(("", PORT), handler)
t = threading.Thread(target=httpd.serve_forever, daemon=True)
t.start()

url = f"http://localhost:{PORT}/rapport.html"
print(f"Serveur démarré sur {url}")
print(f"Rapport Deepchecks : http://localhost:{PORT}/artifacts/deepchecks_report.html")
print(f"Rapport Evidently : http://localhost:{PORT}/artifacts/evidently_drift_report.html")
print("Appuie sur Ctrl+C pour arrêter.")

webbrowser.open(url)
try:
    t.join()
except KeyboardInterrupt:
    print("\nArrêt.")
