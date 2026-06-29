from pathlib import Path
import sqlite3
import json
import sys
import shutil

from _paths import PROJEKT_DIR

DB_PFAD     = PROJEKT_DIR / "db" / "finac.db"
CAT_JSON    = PROJEKT_DIR / "db" / "categories.json"
BUDGET_JSON = PROJEKT_DIR / "db" / "budget.json"


def _bundled_default(filename: str) -> Path | None:
    """Gibt den Pfad zur eingebetteten Standarddatei zurück (nur im Executable)."""
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS) / "defaults" / filename
    return None


def startup_check() -> None:

    db_dir = PROJEKT_DIR / "db"
    db_dir.mkdir(parents=True, exist_ok=True)

    if not DB_PFAD.exists():
        sqlite3.connect(DB_PFAD).close()
        print(f"[startup] Database created: {DB_PFAD}")

    # categories.json: beim ersten Start die eingebettete Standarddatei kopieren
    if not CAT_JSON.exists():
        bundled = _bundled_default("categories.json")
        if bundled and bundled.exists():
            shutil.copy(bundled, CAT_JSON)
        else:
            with open(CAT_JSON, "w", encoding="utf-8") as f:
                json.dump({}, f)
        print(f"[startup] JSON created:      {CAT_JSON}")

    if not BUDGET_JSON.exists():
        with open(BUDGET_JSON, "w", encoding="utf-8") as f:
            json.dump({}, f)
        print(f"[startup] JSON created:      {BUDGET_JSON}")