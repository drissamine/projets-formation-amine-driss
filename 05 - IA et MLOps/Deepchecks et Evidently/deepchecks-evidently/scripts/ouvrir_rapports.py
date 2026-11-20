#!/usr/bin/env python3
"""Ouvre les rapports HTML locaux sans lancer de serveur web."""
import webbrowser
from pathlib import Path


def open_html(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Rapport introuvable: {path}")
    webbrowser.open(path.resolve().as_uri())
    print(f"Ouvert: {path}")


def main() -> None:
    repo = Path(__file__).resolve().parents[1]
    reports = [
        repo / "rapport.html",
        repo / "artifacts" / "deepchecks_report.html",
        repo / "artifacts" / "evidently_drift_report.html",
    ]

    for report in reports:
        open_html(report)


if __name__ == "__main__":
    main()
