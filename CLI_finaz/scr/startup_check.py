from pathlib import Path
import sqlite3
import json


SKRIPT_DIR  = Path(__file__).parent
PROJEKT_DIR = SKRIPT_DIR.parent

DB_PFAD     = PROJEKT_DIR / "db" / "finac.db"
CAT_JSON    = PROJEKT_DIR / "db" / "categories.json"
BUDGET_JSON = PROJEKT_DIR / "db" / "budget.json"


def startup_check() -> None:

    db_dir = PROJEKT_DIR / "db"
    db_dir.mkdir(parents=True, exist_ok=True)

    
    if not DB_PFAD.exists():
        sqlite3.connect(DB_PFAD).close()
        print(f"[startup] Database created: {DB_PFAD}")

    
    for json_pfad, leer_inhalt in (
        (CAT_JSON,    {}),
        (BUDGET_JSON, {}),
    ):
        if not json_pfad.exists():
            with open(json_pfad, "w", encoding="utf-8") as f:
                json.dump(leer_inhalt, f)
            print(f"[startup] JSON created:      {json_pfad}")