

from ui_toolkit import *
from ui_styles import UI


# ──────────────────────────────────────────────
# PFADE
# ──────────────────────────────────────────────

SKRIPT_DIR   = Path(__file__).parent
PROJEKT_DIR  = SKRIPT_DIR.parent
DB_PFAD      = PROJEKT_DIR / "db" / "finac.db"
CAT_JSON     = PROJEKT_DIR / "db" / "categories.json"
BUDGET_JSON  = PROJEKT_DIR / "db" / "budget.json"


# ──────────────────────────────────────────────
# JSON HILFSFUNKTIONEN
# ──────────────────────────────────────────────

def _kategorien_laden() -> dict:

    if not CAT_JSON.exists():
        return {}
    try:
        with open(CAT_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _budget_laden() -> dict:

    if not BUDGET_JSON.exists():
        return {}
    try:
        with open(BUDGET_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _budget_speichern(budget: dict) -> None:
    BUDGET_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(BUDGET_JSON, "w", encoding="utf-8") as f:
        json.dump(budget, f, indent=2, ensure_ascii=False)


# ──────────────────────────────────────────────
# DATENBANK – AUSGABEN PRO KATEGORIE
# ──────────────────────────────────────────────

def _ausgaben_pro_kategorie(zeitraum: str) -> dict:

    if not DB_PFAD.exists():
        return {}

    now   = datetime.now()
    monat = f"{now.month:02d}"
    jahr  = str(now.year)

    # Datumsformat in DB: DD.MM.YYYY
    if zeitraum == "monat":
        where = f"AND SUBSTR(buchungstag, 4, 2) = '{monat}' AND SUBSTR(buchungstag, 7, 4) = '{jahr}'"
    elif zeitraum == "jahr":
        where = f"AND SUBSTR(buchungstag, 7, 4) = '{jahr}'"
    else:
        where = ""

    try:
        with sqlite3.connect(DB_PFAD) as conn:
            cur = conn.cursor()
            cur.execute(f"""
                SELECT category, SUM(betrag)
                FROM transaktionen
                WHERE betrag < 0
                  AND category IS NOT NULL
                  {where}
                GROUP BY category
            """)
            rows = cur.fetchall()
    except sqlite3.OperationalError:
        return {}

    # Betrag ist negativ → abs() für lesbare Ausgabe
    return {cat: abs(summe) for cat, summe in rows if cat}


# ──────────────────────────────────────────────
# UI – DRAW FUNKTIONEN
# ──────────────────────────────────────────────

def _draw_budget_panel(ui: UI, budget: dict, zeitraum: str) -> None:

    kategorien  = _kategorien_laden()
    ausgaben    = _ausgaben_pro_kategorie(zeitraum)
    breite      = console.width
    balken_len  = max(20, min(40, breite - 55))

    zeitraum_label = {"monat": "current month", "jahr": "current year", "gesamt": "total"}
    titel_suffix   = zeitraum_label.get(zeitraum, zeitraum)

    
    table = Table(
        box=box.SIMPLE,
        show_header=True,
        header_style="bold #fa7ff6",
        expand=True,
        padding=(0, 1),
    )
    table.add_column("Category",       width=18, style="bold white")
    table.add_column("Limit (€)",      width=12, justify="right")
    table.add_column("Expenses (€)",   width=14, justify="right")
    table.add_column("Remaining (€)",  width=15, justify="right")
    table.add_column("Period",         width=14, style="#888888")
    table.add_column("Progress",       ratio=1)

    hat_limit    = []
    ohne_limit   = []

    for kat in sorted(kategorien.keys()):
        if kat in budget:
            hat_limit.append(kat)
        else:
            ohne_limit.append(kat)

    for kat in hat_limit:
        info       = budget[kat]
        limit      = info.get("limit", 0.0)
        zr         = info.get("zeitraum", "monat")
        verbraucht = ausgaben.get(kat, 0.0)
        rest       = limit - verbraucht
        prozent    = min(verbraucht / limit, 1.0) if limit > 0 else 0.0

        # Farbe je nach Auslastung
        if prozent >= 1.0:
            farbe = "bold red"
            status = "ÜBERSCHRITTEN"
        elif prozent >= 0.8:
            farbe = "bold yellow"
            status = ""
        else:
            farbe = "bold green"
            status = ""

        
        gefuellt  = int(prozent * balken_len)
        leer      = balken_len - gefuellt
        balken    = Text()
        balken.append("█" * gefuellt, style=farbe)
        balken.append("░" * leer,     style="#444444")
        balken.append(f"  {prozent*100:.0f}%{' ' + status if status else ''}", style=farbe)

        
        zr_label = {"monat": "Month", "jahr": "Year", "gesamt": "Total"}.get(zr, zr)

        table.add_row(
            kat,
            f"{limit:.2f}",
            Text(f"{verbraucht:.2f}", style=farbe),
            Text(f"{rest:+.2f}",      style=farbe),
            zr_label,
            balken,
        )

    
    ohne_text = ""
    if ohne_limit:
        ohne_text_obj = Text("\n  No limit:  ", style="#808080")
        ohne_text_obj.append(", ".join(ohne_limit), style="italic #555555")
        ohne_text = ohne_text_obj

    group_items = [
        Align.center(Text(f"Budget Overview  –  {titel_suffix}", style="bold #fa7ff6")),
        table,
    ]
    if ohne_limit:
        group_items.append(ohne_text)

    return Panel(
        Group(*group_items),
        title="[bold green]Budget[/]",
        border_style="bold blue",
        box=box.ROUNDED,
    )


# ──────────────────────────────────────────────
# HILFS-INPUT
# ──────────────────────────────────────────────

def _eingabe_limit(ui: UI) -> float | None:
    
        try:
            raw = prompt("  Limit (€): ").strip().replace(",", ".")
        except (KeyboardInterrupt, EOFError):
            return None

        if raw == "":
            ui.draw_header("[yellow]No amount entered.[/yellow]")
            #continue
        try:
            wert = float(raw)
            if wert <= 0:
                ui.draw_header("[red]Please enter an amount greater than 0.[/red]")
                #continue
            return wert
        except ValueError:
            ui.draw_header(
                f"[red]Ungültige Eingabe '[bold]{raw}[/bold]' – "
                f"bitte eine Zahl eingeben (z.B. 250 oder 300.50).[/red]"
            )

######################################
###########User Interaktion###########
######################################


def _eingabe_zeitraum(ui: UI) -> str | None:
    
    zeitraum_completer = WordCompleter(["monat", "jahr", "gesamt"], ignore_case=True)
    while True:
        try:
            raw = prompt(
                "  Zeitraum (monat / jahr / gesamt): ",
                completer=zeitraum_completer,
            ).strip().lower()
        except (KeyboardInterrupt, EOFError):
            return None

        if raw in ("monat", "jahr", "gesamt"):
            return raw
        ui.draw_header(
            f"[red]Ungültige Eingabe '[bold]{raw}[/bold]' – "
            f"bitte 'monat', 'jahr' oder 'gesamt' eingeben.[/red]"
        )


# ──────────────────────────────────────────────
# BUDGET BEARBEITEN
# ──────────────────────────────────────────────

def _budget_edit(ui: UI, budget: dict) -> dict:

    kategorien = _kategorien_laden()
    if not kategorien:
        ui.draw_header("[yellow]No categories found. Please create some in 'categories' first.[/yellow]")
        return budget

    kat_namen = sorted(kategorien.keys())
    commands  = ["set", "remove", "back", "exit"]

    while True:
        _draw_budget_panel(ui, budget, "monat")
        completer = WordCompleter(commands, ignore_case=True)

        try:
            user_input = prompt(
                "budget edit -- enter command: ",
                completer=completer,
            ).strip().lower()
        except (KeyboardInterrupt, EOFError):
            ui.draw_exit_panel()

        if user_input == "":
            continue

        elif user_input == "back":
            return budget

        elif user_input == "exit":
            ui.draw_exit_panel()

        # ── Limit setzen / ändern ────────────────────────────────────────────
        elif user_input == "set":
            kat_completer = WordCompleter(kat_namen, ignore_case=True)
            try:
                kat = prompt(
                    "  Kategorie auswählen: ",
                    completer=kat_completer,
                ).strip()
            except (KeyboardInterrupt, EOFError):
                continue

            if kat not in kategorien:
                ui.draw_header(f"[red]Category '[bold]{kat}[/bold]' not found.[/red]")
                continue

            
            if kat in budget:
                alt = budget[kat]

                ui.draw_header(
                    f"[#808080]Current:[/]  Limit [bold]{alt['limit']:.2f} €[/bold]  "
                    f"/ Period [bold]{alt['zeitraum']}[/bold]  –  enter new value:"
                )

            limit = _eingabe_limit(ui)
            if limit is None:
                continue

            zeitraum = _eingabe_zeitraum(ui)
            if zeitraum is None:
                continue

            budget[kat] = {"limit": limit, "zeitraum": zeitraum}
            _budget_speichern(budget)
            ui.draw_header(
                f"[green]Limit set:[/green] [bold]{kat}[/bold]  →  "
                f"{limit:.2f} € / {zeitraum}"
            )

        
        elif user_input == "remove":
            mit_limit = [k for k in kat_namen if k in budget]
            if not mit_limit:
                ui.draw_header("[yellow]No category with a limit found.[/yellow]")
                continue

            rm_completer = WordCompleter(mit_limit, ignore_case=True)
            try:
                kat = prompt(
                    "  Limit entfernen für: ",
                    completer=rm_completer,
                ).strip()
            except (KeyboardInterrupt, EOFError):
                continue

            if kat not in budget:
                ui.draw_header(f"[red]No limit found for '[bold]{kat}[/bold]'.[/red]")
                continue

            del budget[kat]
            _budget_speichern(budget)
            ui.draw_header(f"[green]Limit for '[bold]{kat}[/bold]' removed.[/green]")

        else:
            console.print(f"[red]Unknown command:[/red] {user_input}")


# ──────────────────────────────────────────────
# HAUPTMENÜ
# ──────────────────────────────────────────────

def manage_budget() -> None:
 
    ui       = UI()
    budget   = _budget_laden()
    zeitraum = "monat"   # Standard-Ansicht

    commands = ["show", "edit", "zeitraum", "help", "back", "exit"]

    _draw_budget_panel(ui, budget, zeitraum)

    while True:
        
        completer = WordCompleter(commands, ignore_case=True)

        try:
            user_input = prompt(
                "budget -- enter command: ",
                completer=completer,
            ).strip().lower()
        except (KeyboardInterrupt, EOFError):
            #ui.draw_exit_panel()
            return

        if user_input == "":
            continue

        elif user_input == "back":
            return

        elif user_input == "exit":
            ui.draw_exit_panel()

        elif user_input == "help":
            console.print("\n[bold cyan]Available commands:[/bold cyan]")
            console.print("  [green]show[/green]       – refresh the budget overview")
            console.print("  [green]edit[/green]       – edit budget limits")
            console.print("    [green]set[/green]      – set or update the limit for a category")
            console.print("    [green]remove[/green]   – remove the limit for a category")
            console.print("  [green]zeitraum[/green]   – change display period (monat / jahr / gesamt)")
            console.print("  [green]back[/green]       – go back")
            console.print("  [green]exit[/green]       – quit the program\n")

        elif user_input == "show":
            budget = _budget_laden()   # frisch laden

        
        elif user_input == "zeitraum":
            zr = _eingabe_zeitraum(ui)
            if zr:
                zeitraum = zr
                ui.draw_header(f"[green]Period set:[/green] [bold]{zeitraum}[/bold]")

        # ── Limits bearbeiten ────────────────────────────────────────────────
        elif user_input == "edit":
            budget = _budget_edit(ui, budget)

        else:
            console.print(f"[red]Unknown command:[/red] {user_input}")


