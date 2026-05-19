
from ui_toolkit import *
from ui_styles import UI


# ──────────────────────────────────────────────
# PFADE
# ──────────────────────────────────────────────

SKRIPT_DIR   = Path(__file__).parent
PROJEKT_DIR  = SKRIPT_DIR.parent
DB_PFAD      = PROJEKT_DIR / "db" / "finac.db"
CAT_JSON     = PROJEKT_DIR / "db" / "categories.json"


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


def _kategorien_speichern(kategorien: dict) -> None:
    CAT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(CAT_JSON, "w", encoding="utf-8") as f:
        json.dump(kategorien, f, indent=2, ensure_ascii=False)


# ──────────────────────────────────────────────
# DATENBANK – CATEGORY UPDATEN
# ──────────────────────────────────────────────

def update_category_on_database(database: sqlite3.Connection) -> int:

    kategorien = _kategorien_laden()
    if not kategorien:
        return 0

    cursor = database.cursor()
    cursor.execute("""
        SELECT buchungs_id, verwendungszweck
        FROM transaktionen
        ORDER BY buchungs_id
    """)
    rows = cursor.fetchall()

    if not rows:
        return 0

    aktualisiert = 0

    for buchungs_id, zweck in rows:
        zweck_str = str(zweck or "").upper()
        gefundene_kategorie = None

        for kategorie_name, woerter in kategorien.items():
            if any(wort.upper() in zweck_str for wort in woerter):
                gefundene_kategorie = kategorie_name
                break

        cursor.execute("""
            UPDATE transaktionen
            SET category = ?
            WHERE buchungs_id = ?
        """, (gefundene_kategorie, buchungs_id))

        if cursor.rowcount:
            aktualisiert += 1

    database.commit()
    return aktualisiert


def start_category_update():
    ui = UI()
    if not DB_PFAD.exists():
        ui.draw_header("[red]FEHLER:[/red] Datenbank nicht gefunden.")
        return
    try:
        with sqlite3.connect(DB_PFAD) as conn:
            ui.draw_header("[bold #fa7ff6]Kategorien werden angewendet...[/bold #fa7ff6]")
            anzahl = update_category_on_database(conn)
            ui.draw_header(f"[green]Fertig –[/green] {anzahl} Transaktionen aktualisiert.")
    except sqlite3.OperationalError as e:
        ui.draw_header(f"[red]FEHLER (Datenbank):[/red] {e}")


# ──────────────────────────────────────────────
# KATEGORIE ERSTELLEN / LÖSCHEN
# ──────────────────────────────────────────────

def _draw_kategorien_panel(ui: UI, kategorien: dict) -> None:
    
    if not kategorien:
        ui.draw_header("[yellow]Noch keine Kategorien vorhanden.[/yellow]")
        return

    table = Table(
        box=box.SIMPLE,
        show_header=True,
        header_style="bold #fa7ff6",
        expand=True,
        padding=(0, 1),
    )
    table.add_column("Kategorie", width=20, style="bold white")
    table.add_column("Wortpool",  ratio=1,  style="#888888")

    for name, woerter in kategorien.items():
        table.add_row(name, ", ".join(woerter) if woerter else "–")

    console.print(Panel(
        table,
        title="[bold green]Kategorien[/]",
        border_style="bold blue",
        box=box.ROUNDED,
    ))

######################################
###########User Interaktion###########
######################################

def manage_categories():

    ui = UI()
    kategorien = _kategorien_laden()

    commands = ["new", "delete", "wordpool", "apply", "help", "back", "exit"]

    while True:
        _draw_kategorien_panel(ui, kategorien)
        completer = WordCompleter(commands, ignore_case=True)

        try:
            user_input = prompt(
                "categories -- enter command: ",
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
            ui.draw_header(
                "[bold #fa7ff6]new[/]      – Neue Kategorie erstellen\n"
                "[bold #fa7ff6]delete[/]   – Kategorie löschen\n"
                "[bold #fa7ff6]wordpool[/] – Wörter einer Kategorie bearbeiten\n"
                "[bold #fa7ff6]apply[/]    – Kategorien auf Datenbank anwenden\n"
                "[bold #fa7ff6]back[/]     – Zurück"
            )

        # neu kategorie
        elif user_input == "new":
            try:
                name = prompt("  Kategoriename: ").strip()
            except (KeyboardInterrupt, EOFError):
                continue

            if not name:
                ui.draw_header("[yellow]Kein Name eingegeben.[/yellow]")
                continue
            if name in kategorien:
                ui.draw_header(f"[yellow]Kategorie '{name}' existiert bereits.[/yellow]")
                continue

            kategorien[name] = []
            _kategorien_speichern(kategorien)
            ui.draw_header(f"[green]Kategorie '[bold]{name}[/bold]' erstellt.[/green]")

        
        elif user_input == "delete":
            if not kategorien:
                ui.draw_header("[yellow]Keine Kategorien vorhanden.[/yellow]")
                continue

            cat_completer = WordCompleter(list(kategorien.keys()), ignore_case=True)
            try:
                name = prompt(
                    "  Zu löschende Kategorie: ",
                    completer=cat_completer,
                ).strip()
            except (KeyboardInterrupt, EOFError):
                continue

            if name not in kategorien:
                ui.draw_header(f"[red]Kategorie '{name}' nicht gefunden.[/red]")
                continue

            del kategorien[name]
            _kategorien_speichern(kategorien)
            ui.draw_header(f"[green]Kategorie '[bold]{name}[/bold]' gelöscht.[/green]")

       
        elif user_input == "wordpool":
            _manage_wordpool(ui, kategorien)

        
        elif user_input == "apply":
            start_category_update()

        else:
            console.print(f"[red]Unbekanntes Kommando:[/red] {user_input}")



def _manage_wordpool(ui: UI, kategorien: dict) -> None:
 
    if not kategorien:
        ui.draw_header("[yellow]Keine Kategorien vorhanden. Bitte zuerst eine erstellen.[/yellow]")
        return

    # Kategorie auswählen
    cat_completer = WordCompleter(list(kategorien.keys()), ignore_case=True)
    try:
        name = prompt(
            "  Kategorie wählen: ",
            completer=cat_completer,
        ).strip()
    except (KeyboardInterrupt, EOFError):
        return

    if name not in kategorien:
        ui.draw_header(f"[red]Kategorie '{name}' nicht gefunden.[/red]")
        return

    commands = ["add", "remove", "back", "exit"]

    while True:
        woerter = kategorien[name]
        _draw_wordpool_panel(ui, name, woerter)

        completer = WordCompleter(commands, ignore_case=True)
        try:
            user_input = prompt(
                f"wordpool ({name}) -- enter command: ",
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

        
        elif user_input == "add":
            try:
                wort = prompt("  Neues Wort: ").strip()
            except (KeyboardInterrupt, EOFError):
                continue

            if not wort:
                ui.draw_header("[yellow]Kein Wort eingegeben.[/yellow]")
                continue
            if wort in woerter:
                ui.draw_header(f"[yellow]'{wort}' ist bereits im Wortpool.[/yellow]")
                continue

            kategorien[name].append(wort)
            _kategorien_speichern(kategorien)
            ui.draw_header(f"[green]'[bold]{wort}[/bold]' hinzugefügt.[/green]")

        
        elif user_input == "remove":
            if not woerter:
                ui.draw_header("[yellow]Wortpool ist leer.[/yellow]")
                continue

            wort_completer = WordCompleter(woerter, ignore_case=True)
            try:
                wort = prompt(
                    "  Zu entfernendes Wort: ",
                    completer=wort_completer,
                ).strip()
            except (KeyboardInterrupt, EOFError):
                continue

            if wort not in kategorien[name]:
                ui.draw_header(f"[red]'{wort}' nicht im Wortpool gefunden.[/red]")
                continue

            kategorien[name].remove(wort)
            _kategorien_speichern(kategorien)
            ui.draw_header(f"[green]'[bold]{wort}[/bold]' entfernt.[/green]")

        else:
            console.print(f"[red]Unbekanntes Kommando:[/red] {user_input}")







# ──────────────────────────────────────────────
# WORTPOOL UI
# ──────────────────────────────────────────────

def _draw_wordpool_panel(ui: UI, name: str, woerter: list) -> None:
    table = Table(
        box=box.SIMPLE,
        show_header=True,
        header_style="bold #fa7ff6",
        expand=True,
        padding=(0, 1),
    )
    table.add_column("#",     width=4,  justify="right", style="#808080")
    table.add_column("Wort", ratio=1,  style="bold white")

    for i, wort in enumerate(woerter, 1):
        table.add_row(str(i), wort)

    if not woerter:
        table.add_row("–", "[italic #888888]Noch keine Wörter[/]")

    console.print(Panel(
        table,
        title=f"[bold green]Wortpool – {name}[/]",
        border_style="bold blue",
        box=box.ROUNDED,
    ))



