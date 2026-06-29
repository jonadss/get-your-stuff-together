import sqlite3
from pathlib import Path
from tabulate import tabulate


# ──────────────────────────────────────────────
# PFAD  (relativ zu diesem Skript)
# ──────────────────────────────────────────────

from _paths import PROJEKT_DIR
DB_PFAD = PROJEKT_DIR / "db" / "finac.db"


# ──────────────────────────────────────────────
# Auswertung-FUNKTIONEN
# ──────────────────────────────────────────────

def overview(database: sqlite3.Connection) -> None:

    try:
        cursor = database.cursor()
        cursor.execute("""
        SELECT buchungs_id, buchungstag, betrag, saldo_nach_buchung, verwendungszweck, category
        FROM transaktionen
        ORDER BY
            SUBSTR(buchungstag, 7, 4) DESC,  
            SUBSTR(buchungstag, 4, 2) DESC,  
            SUBSTR(buchungstag, 1, 2) DESC,  
            buchungs_id
    """)
    except:
        raise sqlite3.OperationalError   
    

    return cursor.fetchall()


def bank_balance(database: sqlite3.Connection) -> float:
    cursor = database.cursor()
    cursor.execute("""
        SELECT saldo_nach_buchung
        FROM transaktionen
        ORDER BY
            SUBSTR(buchungstag, 7, 4) DESC,  
            SUBSTR(buchungstag, 4, 2) DESC,  
            SUBSTR(buchungstag, 1, 2) DESC,  
            buchungs_id DESC -- Hier war das Komma zu viel
        LIMIT 1                           
    """)
    row = cursor.fetchone()

    print(f"\n{'─' * 70}")
    if row:
        saldo = row[0]
        return saldo
    else:
        print("  No data in the database yet.")
        return 0.0


#Test funktionen 
def test(database: sqlite3.Connection):
    cursor = database.cursor()
    x = 1
  
    cursor.execute("""
        SELECT buchungs_id, verwendungszweck
        FROM transaktionen
        """)
    row = cursor.fetchall()
    print(row[0])


# ──────────────────────────────────────────────
# EINSTIEGSPUNKT
# ──────────────────────────────────────────────


    

def start_saldo_request():
    if not DB_PFAD.exists():
        print(f"\nERROR: Database not found: '{DB_PFAD}'")
        return None
    try:
        with sqlite3.connect(DB_PFAD) as conn:
            return bank_balance(conn)
    except sqlite3.OperationalError as e:
        print(f"\nERROR: Table not found – please import data first. ({e})")
        return None


# ──────────────────────────────────────────────
# EVALUATION DB FUNCTIONS
# ──────────────────────────────────────────────

def eval_db_connect():
    if not DB_PFAD.exists():
        raise FileNotFoundError(f"Database not found: {DB_PFAD}")
    return sqlite3.connect(DB_PFAD)


def get_all_categories() -> list:
    try:
        with eval_db_connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT DISTINCT category FROM transaktionen
                WHERE category IS NOT NULL
                ORDER BY category
            """)
            return [r[0] for r in cur.fetchall()]
    except (sqlite3.OperationalError, FileNotFoundError):
        return []


def _month_key_from_date(datum_str: str) -> str:
    try:
        return datum_str[6:10] + "-" + datum_str[3:5]
    except Exception:
        return "0000-00"


def get_expenses_by_month_category(category=None) -> dict:
    try:
        with eval_db_connect() as conn:
            cur = conn.cursor()
            if category and category != "all":
                cur.execute("""
                    SELECT buchungstag, SUM(betrag)
                    FROM transaktionen
                    WHERE betrag < 0 AND category = ?
                    GROUP BY SUBSTR(buchungstag,7,4), SUBSTR(buchungstag,4,2)
                """, (category,))
            else:
                cur.execute("""
                    SELECT buchungstag, SUM(betrag)
                    FROM transaktionen
                    WHERE betrag < 0
                    GROUP BY SUBSTR(buchungstag,7,4), SUBSTR(buchungstag,4,2)
                """)
            rows = cur.fetchall()
    except (sqlite3.OperationalError, FileNotFoundError):
        return {}

    result = {}
    for datum, summe in rows:
        key = _month_key_from_date(datum)
        result[key] = result.get(key, 0.0) + abs(summe)
    return dict(sorted(result.items()))


def get_recurring_transactions(amount_limit=None, top=50) -> list:
    try:
        with eval_db_connect() as conn:
            cur = conn.cursor()
            if amount_limit is not None:
                cur.execute("""
                    SELECT verwendungszweck, betrag,
                           COUNT(*) as cnt,
                           MIN(buchungstag) as first_date,
                           MAX(buchungstag) as last_date
                    FROM transaktionen
                    WHERE betrag < 0
                      AND ABS(betrag) <= ?
                    GROUP BY ROUND(betrag, 2),
                             SUBSTR(verwendungszweck, 1, 50)
                    HAVING COUNT(*) >= 2
                    ORDER BY COUNT(*) DESC, ABS(betrag) DESC
                    LIMIT ?
                """, (amount_limit, top))
            else:
                cur.execute("""
                    SELECT verwendungszweck, betrag,
                           COUNT(*) as cnt,
                           MIN(buchungstag) as first_date,
                           MAX(buchungstag) as last_date
                    FROM transaktionen
                    WHERE betrag < 0
                    GROUP BY ROUND(betrag, 2),
                             SUBSTR(verwendungszweck, 1, 50)
                    HAVING COUNT(*) >= 2
                    ORDER BY COUNT(*) DESC, ABS(betrag) DESC
                    LIMIT ?
                """, (top,))
            return cur.fetchall()
    except (sqlite3.OperationalError, FileNotFoundError):
        return []


def get_monthly_income(income_cats: list, month: str, year: str,
                        prev_month: str, prev_year: str) -> dict:
    result = {}
    try:
        with eval_db_connect() as conn:
            cur = conn.cursor()
            for cat in income_cats:
                cur.execute("""
                    SELECT COALESCE(SUM(betrag), 0.0)
                    FROM transaktionen
                    WHERE category = ?
                      AND betrag > 0
                      AND (
                          (SUBSTR(buchungstag,4,2) = ? AND SUBSTR(buchungstag,7,4) = ?)
                          OR (
                              SUBSTR(buchungstag,4,2) = ? AND SUBSTR(buchungstag,7,4) = ?
                              AND CAST(SUBSTR(buchungstag,1,2) AS INTEGER) >= 25
                          )
                      )
                """, (cat, month, year, prev_month, prev_year))
                result[cat] = abs(cur.fetchone()[0])
    except (sqlite3.OperationalError, FileNotFoundError):
        pass
    return result


def get_monthly_fixed_costs(fixed_cats: list, month: str, year: str) -> dict:
    result = {}
    try:
        with eval_db_connect() as conn:
            cur = conn.cursor()
            for cat in fixed_cats:
                cur.execute("""
                    SELECT COALESCE(SUM(betrag), 0.0)
                    FROM transaktionen
                    WHERE category = ?
                      AND betrag < 0
                      AND SUBSTR(buchungstag,4,2) = ?
                      AND SUBSTR(buchungstag,7,4) = ?
                """, (cat, month, year))
                result[cat] = abs(cur.fetchone()[0])
    except (sqlite3.OperationalError, FileNotFoundError):
        pass
    return result


def get_monthly_category_spending(category: str, month: str, year: str) -> float:
    try:
        with eval_db_connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT COALESCE(SUM(ABS(betrag)), 0.0)
                FROM transaktionen
                WHERE betrag < 0
                  AND category = ?
                  AND SUBSTR(buchungstag,4,2) = ?
                  AND SUBSTR(buchungstag,7,4) = ?
            """, (category, month, year))
            return cur.fetchone()[0]
    except (sqlite3.OperationalError, FileNotFoundError):
        return 0.0


def get_all_monthly_spending(categories: list, month: str, year: str) -> dict:
    result = {}
    try:
        with eval_db_connect() as conn:
            cur = conn.cursor()
            for cat in categories:
                cur.execute("""
                    SELECT COALESCE(SUM(ABS(betrag)), 0.0)
                    FROM transaktionen
                    WHERE betrag < 0
                      AND category = ?
                      AND SUBSTR(buchungstag,4,2) = ?
                      AND SUBSTR(buchungstag,7,4) = ?
                """, (cat, month, year))
                result[cat] = cur.fetchone()[0]
    except (sqlite3.OperationalError, FileNotFoundError):
        pass
    return result

