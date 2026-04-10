

from ui_toolkit import *
from ui_styles import UI


# ──────────────────────────────────────────────
# PFADE
# ──────────────────────────────────────────────

SKRIPT_DIR     = Path(__file__).parent
PROJEKT_DIR    = SKRIPT_DIR.parent
DB_PFAD        = PROJEKT_DIR / "db" / "finac.db"
CAT_JSON       = PROJEKT_DIR / "db" / "categories.json"
BUDGET_JSON    = PROJEKT_DIR / "db" / "budget.json"
EVAL_JSON      = PROJEKT_DIR / "db" / "evaluation.json"


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


def _eval_config_laden() -> dict:

    if not EVAL_JSON.exists():
        return {"einkommen_kategorien": [], "fixkosten_kategorien": []}
    try:
        with open(EVAL_JSON, "r", encoding="utf-8") as f:
            data = json.load(f)
            data.setdefault("einkommen_kategorien", [])
            data.setdefault("fixkosten_kategorien", [])
            return data
    except (json.JSONDecodeError, OSError):
        return {"einkommen_kategorien": [], "fixkosten_kategorien": []}


def _eval_config_speichern(config: dict) -> None:
    EVAL_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(EVAL_JSON, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


# ──────────────────────────────────────────────
# DB HILFSFUNKTIONEN
# ──────────────────────────────────────────────

def _db_connect() -> sqlite3.Connection:
    if not DB_PFAD.exists():
        raise FileNotFoundError(f"Datenbank nicht gefunden: {DB_PFAD}")
    return sqlite3.connect(DB_PFAD)


def _alle_kategorien_in_db() -> list[str]:

    try:
        with _db_connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT DISTINCT category FROM transaktionen
                WHERE category IS NOT NULL
                ORDER BY category
            """)
            return [r[0] for r in cur.fetchall()]
    except (sqlite3.OperationalError, FileNotFoundError):
        return []


def _monat_key(datum_str: str) -> str:
    """DD.MM.YYYY → 'YYYY-MM' für Sortierung."""
    try:
        return datum_str[6:10] + "-" + datum_str[3:5]
    except Exception:
        return "0000-00"


def _ausgaben_nach_monat_kategorie(kategorie: str | None = None) -> dict:
    """
    Gibt { "2025-01": 234.50, "2025-02": 189.00, ... } zurück.
    Wenn kategorie=None → alle Ausgaben zusammen.
    """
    try:
        with _db_connect() as conn:
            cur = conn.cursor()
            if kategorie and kategorie != "all":
                cur.execute("""
                    SELECT buchungstag, SUM(betrag)
                    FROM transaktionen
                    WHERE betrag < 0 AND category = ?
                    GROUP BY SUBSTR(buchungstag,7,4), SUBSTR(buchungstag,4,2)
                """, (kategorie,))
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

    ergebnis = {}
    for datum, summe in rows:
        key = _monat_key(datum)
        ergebnis[key] = ergebnis.get(key, 0.0) + abs(summe)
    return dict(sorted(ergebnis.items()))


def _letzte_n_monate_keys(n: int) -> list[str]:

    now   = datetime.now()
    monate = []
    for i in range(n - 1, -1, -1):
        monat = now.month - i
        jahr  = now.year
        while monat <= 0:
            monat += 12
            jahr  -= 1
        monate.append(f"{jahr}-{monat:02d}")
    return monate


# ──────────────────────────────────────────────
# LESS-AUSGABE HILFSFUNKTION
# ──────────────────────────────────────────────

def _less(panel) -> None:
    breite = console.width
    buf    = io.StringIO()
    tmp    = RichConsole(file=buf, width=breite, highlight=False, force_terminal=True)
    tmp.print(panel)
    subprocess.run(
        ["less", "-R", "-S", "--prompt= Pfeiltasten scrollen | q = zurück"],
        input=buf.getvalue(), text=True
    )


# ──────────────────────────────────────────────
# AUSWERTUNG 1 – VERGLEICH ZUM VORMONAT
# ──────────────────────────────────────────────

def _auswertung_vergleich(ui: UI) -> None:

    alle_kat  = ["all"] + _alle_kategorien_in_db()
    if not alle_kat:
        ui.draw_header("[yellow]Keine kategorisierten Buchungen gefunden.[/yellow]")
        return

    kat_completer = WordCompleter(alle_kat, ignore_case=True)
    try:
        kat = prompt("  Kategorie (Tab = Vorschläge, 'all' = alle): ",
                     completer=kat_completer).strip()
    except (KeyboardInterrupt, EOFError):
        return

    if kat not in alle_kat:
        ui.draw_header(f"[red]Kategorie '[bold]{kat}[/bold]' nicht gefunden.[/red]")
        return

    vergleich_optionen = ["3", "6", "12"]
    v_completer        = WordCompleter(vergleich_optionen, ignore_case=True)
    try:
        n_raw = prompt("  Vergleichszeitraum in Monaten (3 / 6 / 12): ",
                       completer=v_completer).strip()
    except (KeyboardInterrupt, EOFError):
        return

    try:
        n = int(n_raw)
        if n <= 0:
            raise ValueError
    except ValueError:
        ui.draw_header(f"[red]Ungültige Eingabe '[bold]{n_raw}[/bold]'.[/red]")
        return

    daten        = _ausgaben_nach_monat_kategorie(kat if kat != "all" else None)
    monate_keys  = _letzte_n_monate_keys(n + 1)   # +1 weil aktueller Monat dabei
    aktuell_key  = monate_keys[-1]
    vergl_keys   = monate_keys[:-1]

    aktuell_summe = daten.get(aktuell_key, 0.0)
    vergl_werte   = [daten.get(k, 0.0) for k in vergl_keys]
    vergl_durch   = sum(vergl_werte) / len(vergl_werte) if vergl_werte else 0.0
    differenz     = aktuell_summe - vergl_durch
    diff_farbe    = "bold red" if differenz > 0 else "bold green"

    # ── Balken-Chart ─────────────────────────────────────────────────────────
    max_wert   = max([aktuell_summe] + vergl_werte + [0.01])
    balken_len = 35

    table = Table(box=box.SIMPLE, show_header=True,
                  header_style="bold #fa7ff6", expand=True, padding=(0, 1))
    table.add_column("Monat",      width=10)
    table.add_column("Ausgaben €", width=12, justify="right")
    table.add_column("Verlauf",    ratio=1)

    for key in monate_keys[:-1]:
        wert    = daten.get(key, 0.0)
        gefuellt = int((wert / max_wert) * balken_len)
        balken   = Text("█" * gefuellt, style="#888888")
        table.add_row(key, f"{wert:.2f}", balken)

    # Aktueller Monat hervorgehoben
    gef_akt  = int((aktuell_summe / max_wert) * balken_len)
    b_akt    = Text("█" * gef_akt, style="bold #fa7ff6")
    table.add_row(
        Text(aktuell_key + " ◀", style="bold white"),
        Text(f"{aktuell_summe:.2f}", style="bold white"),
        b_akt,
    )

    zusammenfassung = Table.grid(expand=True, padding=(0, 2))
    zusammenfassung.add_column(ratio=1)
    zusammenfassung.add_column(ratio=1)
    zusammenfassung.add_column(ratio=1)
    zusammenfassung.add_row(
        Text(f"Aktueller Monat:  {aktuell_summe:.2f} €",   style="bold white"),
        Text(f"Ø letzter {n} Monate:  {vergl_durch:.2f} €", style="#aaaaaa"),
        Text(f"Differenz:  {differenz:+.2f} €",              style=diff_farbe),
    )

    kat_label = kat if kat != "all" else "Alle Kategorien"
    _less(Panel(
        Group(Align.center(zusammenfassung), Text(""), table),
        title=f"[bold green]Vergleich zum Vormonat – {kat_label}[/]",
        border_style="bold blue", box=box.ROUNDED,
    ))


# ──────────────────────────────────────────────
# AUSWERTUNG 2 – SAISONALE SCHWANKUNGEN
# ──────────────────────────────────────────────

def _auswertung_saison(ui: UI) -> None:

    alle_kat = _alle_kategorien_in_db()
    if not alle_kat:
        ui.draw_header("[yellow]Keine kategorisierten Buchungen gefunden.[/yellow]")
        return

    kat_completer = WordCompleter(alle_kat, ignore_case=True)
    try:
        kat = prompt("  Kategorie (Tab = Vorschläge): ",
                     completer=kat_completer).strip()
    except (KeyboardInterrupt, EOFError):
        return

    if kat not in alle_kat:
        ui.draw_header(f"[red]Kategorie '[bold]{kat}[/bold]' nicht gefunden.[/red]")
        return

    daten       = _ausgaben_nach_monat_kategorie(kat)
    monate_keys = _letzte_n_monate_keys(12)
    werte       = [(k, daten.get(k, 0.0)) for k in monate_keys]
    max_wert    = max(w for _, w in werte) if werte else 0.01
    balken_len  = 40

    # Top-3 Spitzen
    sortiert   = sorted(werte, key=lambda x: x[1], reverse=True)
    spitzen    = {k for k, _ in sortiert[:3]}

    table = Table(box=box.SIMPLE, show_header=True,
                  header_style="bold #fa7ff6", expand=True, padding=(0, 1))
    table.add_column("Monat",      width=10)
    table.add_column("Ausgaben €", width=12, justify="right")
    table.add_column("Verlauf",    ratio=1)

    for key, wert in werte:
        gefuellt = int((wert / max_wert) * balken_len) if max_wert > 0 else 0
        ist_spitze = key in spitzen and wert > 0
        farbe    = "bold red" if ist_spitze else "bold #4a9eff"
        balken   = Text()
        balken.append("█" * gefuellt, style=farbe)
        if ist_spitze:
            balken.append("  ▲ Spitze", style="bold red")
        table.add_row(
            Text(key, style="bold white" if ist_spitze else "white"),
            Text(f"{wert:.2f}", style="bold white" if ist_spitze else "white"),
            balken,
        )

    _less(Panel(
        table,
        title=f"[bold green]Saisonale Schwankungen – {kat} (letztes Jahr)[/]",
        border_style="bold blue", box=box.ROUNDED,
    ))


# ──────────────────────────────────────────────
# AUSWERTUNG 3 – ABO-FALLE DADADADAHHHHH
# ──────────────────────────────────────────────

def _auswertung_abo(ui: UI) -> None:

    try:
        limit_raw = prompt("  Maximalbetrag pro Buchung (€, Enter = 15): ").strip()
    except (KeyboardInterrupt, EOFError):
        return

    if limit_raw == "":
        limit = 15.0
    else:
        limit_raw = limit_raw.replace(",", ".")
        try:
            limit = float(limit_raw)
        except ValueError:
            ui.draw_header(f"[red]Ungültige Eingabe.[/red]")
            return

    try:
        with _db_connect() as conn:
            cur = conn.cursor()
            # Buchungen unter Limit → nach Verwendungszweck + Betrag gruppieren
            cur.execute("""
                SELECT verwendungszweck, betrag,
                       COUNT(*) as anzahl,
                       MIN(buchungstag) as erstes,
                       MAX(buchungstag) as letztes
                FROM transaktionen
                WHERE betrag < 0
                  AND ABS(betrag) <= ?
                GROUP BY ROUND(betrag, 2),
                         SUBSTR(verwendungszweck, 1, 40)
                HAVING COUNT(*) >= 2
                ORDER BY COUNT(*) DESC, betrag ASC
            """, (limit,))
            rows = cur.fetchall()
    except (sqlite3.OperationalError, FileNotFoundError) as e:
        ui.draw_header(f"[red]FEHLER:[/red] {e}")
        return

    if not rows:
        ui.draw_header("[yellow]Keine wiederkehrenden Abbuchungen unter dem Limit gefunden.[/yellow]")
        return

    table = Table(box=box.SIMPLE, show_header=True,
                  header_style="bold #fa7ff6", expand=True, padding=(0, 1))
    table.add_column("Betrag €",   width=10, justify="right")
    table.add_column("Anzahl",     width=8,  justify="right", style="#888888")
    table.add_column("Rhythmus",   width=12, style="bold")
    table.add_column("Erstes",     width=12, style="#888888")
    table.add_column("Letztes",    width=12, style="#888888")
    table.add_column("Verwendungszweck", ratio=1, style="#aaaaaa")

    gesamt_monatlich = 0.0
    gesamt_jaehrlich = 0.0

    for zweck, betrag, anzahl, erstes, letztes in rows:
        # Rhythmus schätzen: Monatsabstand zwischen erstem und letztem
        try:
            e_m = int(erstes[3:5]) + int(erstes[6:10]) * 12
            l_m = int(letztes[3:5]) + int(letztes[6:10]) * 12
            abstand_monate = (l_m - e_m) / max(anzahl - 1, 1)
        except Exception:
            abstand_monate = 0

        if abstand_monate <= 2:
            rhythmus       = Text("monatlich", style="bold #fa7ff6")
            gesamt_monatlich += abs(betrag)
        else:
            rhythmus       = Text("jährlich",  style="bold yellow")
            gesamt_jaehrlich += abs(betrag)

        breite  = console.width
        max_len = max(20, breite - 70)
        zweck_k = str(zweck or "–")[:max_len]

        table.add_row(
            Text(f"{abs(betrag):.2f}", style="bold red"),
            str(anzahl),
            rhythmus,
            str(erstes),
            str(letztes),
            zweck_k,
        )

    fuss = Table.grid(expand=True, padding=(0, 2))
    fuss.add_column(ratio=1)
    fuss.add_column(ratio=1)
    fuss.add_row(
        Text(f"Monatliche Abos gesamt:  {gesamt_monatlich:.2f} €",    style="bold #fa7ff6"),
        Text(f"Jährliche Abos gesamt:   {gesamt_jaehrlich:.2f} €",    style="bold yellow"),
    )

    _less(Panel(
        Group(table, Text(""), Align.center(fuss)),
        title=f"[bold green]Abo-Falle – Abbuchungen ≤ {limit:.2f} €[/]",
        border_style="bold blue", box=box.ROUNDED,
    ))


# ──────────────────────────────────────────────
# AUSWERTUNG 4 – WIEDERKEHRENDE BUCHUNGEN
# ──────────────────────────────────────────────

def _auswertung_wiederkehrend(ui: UI) -> None:

    try:
        with _db_connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT verwendungszweck, betrag,
                       COUNT(*) as anzahl,
                       MIN(buchungstag) as erstes,
                       MAX(buchungstag) as letztes
                FROM transaktionen
                WHERE betrag < 0
                GROUP BY ROUND(betrag, 2),
                         SUBSTR(verwendungszweck, 1, 50)
                HAVING COUNT(*) >= 2
                ORDER BY COUNT(*) DESC, ABS(betrag) DESC
                LIMIT 50
            """)
            rows = cur.fetchall()
    except (sqlite3.OperationalError, FileNotFoundError) as e:
        ui.draw_header(f"[red]FEHLER:[/red] {e}")
        return

    if not rows:
        ui.draw_header("[yellow]Keine wiederkehrenden Buchungen gefunden.[/yellow]")
        return

    table = Table(box=box.SIMPLE, show_header=True,
                  header_style="bold #fa7ff6", expand=True, padding=(0, 1))
    table.add_column("Betrag €",   width=10, justify="right")
    table.add_column("Anzahl",     width=8,  justify="right", style="#888888")
    table.add_column("Erstes",     width=12, style="#888888")
    table.add_column("Letztes",    width=12, style="#888888")
    table.add_column("Verwendungszweck", ratio=1, style="#aaaaaa")

    breite = console.width
    for zweck, betrag, anzahl, erstes, letztes in rows:
        max_len = max(20, breite - 65)
        zweck_k = str(zweck or "–")[:max_len]
        table.add_row(
            Text(f"{abs(betrag):.2f}", style="bold red"),
            str(anzahl),
            str(erstes),
            str(letztes),
            zweck_k,
        )

    _less(Panel(
        table,
        title="[bold green]Wiederkehrende Buchungen (Top 50)[/]",
        border_style="bold blue", box=box.ROUNDED,
    ))


# ──────────────────────────────────────────────
# AUSWERTUNG 5 – ANTEIL AM EINKOMMEN
# ──────────────────────────────────────────────

def _auswertung_einkommen(ui: UI, config: dict) -> None:

    eink_kats  = config.get("einkommen_kategorien", [])
    fix_kats   = config.get("fixkosten_kategorien", [])

    if not eink_kats:
        ui.draw_header("[yellow]Keine Einkommen-Kategorien konfiguriert.\n"
                       "Bitte unter 'settings → einkommen' zuweisen.[/yellow]")
        return
    if not fix_kats:
        ui.draw_header("[yellow]Keine Fixkosten-Kategorien konfiguriert.\n"
                       "Bitte unter 'settings → fixkosten' zuweisen.[/yellow]")
        return

    now   = datetime.now()
    monat = f"{now.month:02d}"
    jahr  = str(now.year)

    def _summe(kategorien: list[str], nur_positiv: bool) -> dict:
        """{ kategorie: summe } für den aktuellen Monat."""
        ergebnis = {}
        try:
            with _db_connect() as conn:
                cur = conn.cursor()
                for kat in kategorien:
                    sign = "> 0" if nur_positiv else "< 0"
                    cur.execute(f"""
                        SELECT COALESCE(SUM(betrag), 0.0)
                        FROM transaktionen
                        WHERE category = ?
                          AND betrag {sign}
                          AND SUBSTR(buchungstag,4,2) = ?
                          AND SUBSTR(buchungstag,7,4) = ?
                    """, (kat, monat, jahr))
                    ergebnis[kat] = abs(cur.fetchone()[0])
        except (sqlite3.OperationalError, FileNotFoundError):
            pass
        return ergebnis

    einnahmen_detail = _summe(eink_kats, nur_positiv=True)
    fixkosten_detail = _summe(fix_kats,  nur_positiv=False)

    gesamt_eink = sum(einnahmen_detail.values())
    gesamt_fix  = sum(fixkosten_detail.values())
    anteil      = (gesamt_fix / gesamt_eink * 100) if gesamt_eink > 0 else 0.0
    warnung     = anteil > 50

    # ── Einnahmen-Tabelle 
    t_eink = Table(box=box.SIMPLE, show_header=True,
                   header_style="bold #fa7ff6", expand=True, padding=(0,1))
    t_eink.add_column("Kategorie",  width=20, style="bold white")
    t_eink.add_column("Einnahmen €",width=14, justify="right", style="bold green")

    for kat, summe in einnahmen_detail.items():
        t_eink.add_row(kat, f"{summe:.2f}")
    t_eink.add_row(Text("GESAMT", style="bold #fa7ff6"),
                   Text(f"{gesamt_eink:.2f}", style="bold #fa7ff6"))

    #  Fixkosten-Tabelle 
    t_fix = Table(box=box.SIMPLE, show_header=True,
                  header_style="bold #fa7ff6", expand=True, padding=(0,1))
    t_fix.add_column("Kategorie",  width=20, style="bold white")
    t_fix.add_column("Fixkosten €",width=14, justify="right", style="bold red")

    for kat, summe in fixkosten_detail.items():
        t_fix.add_row(kat, f"{summe:.2f}")
    t_fix.add_row(Text("GESAMT", style="bold #fa7ff6"),
                  Text(f"{gesamt_fix:.2f}", style="bold #fa7ff6"))

    #  Ergebnis-Zeile 
    anteil_farbe = "bold red" if warnung else "bold green"
    ergebnis_text = Text()
    ergebnis_text.append(f"Fixkosten-Anteil am Einkommen: ", style="bold white")
    ergebnis_text.append(f"{anteil:.1f}%", style=anteil_farbe)
    if warnung:
        ergebnis_text.append("  ⚠  Über der 50%-Marke!", style="bold red")
    else:
        ergebnis_text.append("  ✓  Unter der 50%-Marke", style="bold green")

    monat_label = f"{monat}/{jahr}"
    _less(Panel(
        Group(
            Align.center(Text(f"Monat: {monat_label}", style="#888888")),
            Text(""),
            t_eink,
            Text(""),
            t_fix,
            Text(""),
            Align.center(ergebnis_text),
        ),
        title="[bold green]Anteil Fixkosten am Einkommen[/]",
        border_style="bold blue", box=box.ROUNDED,
    ))


# ──────────────────────────────────────────────
# AUSWERTUNG 6 – BUDGET-WARNUNG (HOCHRECHNUNG)
# ──────────────────────────────────────────────

def _auswertung_budget_warnung(ui: UI) -> None:

    budget    = _budget_laden()
    alle_kat  = _alle_kategorien_in_db()

    kat_mit_budget = [k for k in alle_kat if k in budget]
    if not kat_mit_budget:
        ui.draw_header("[yellow]Keine Kategorien mit Budget-Limit gefunden.\n"
                       "Bitte zuerst unter 'budget' Limits setzen.[/yellow]")
        return

    kat_completer = WordCompleter(kat_mit_budget, ignore_case=True)
    try:
        kat = prompt("  Kategorie (Tab = Vorschläge): ",
                     completer=kat_completer).strip()
    except (KeyboardInterrupt, EOFError):
        return

    if kat not in budget:
        ui.draw_header(f"[red]Kein Budget für '[bold]{kat}[/bold]' gefunden.[/red]")
        return

    now        = datetime.now()
    monat      = f"{now.month:02d}"
    jahr       = str(now.year)
    tag        = now.day
    tage_monat = 30   # Vereinfachung; könnte mit calendar.monthrange exakter sein

    limit = budget[kat]["limit"]

    try:
        with _db_connect() as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT COALESCE(SUM(ABS(betrag)), 0.0)
                FROM transaktionen
                WHERE betrag < 0
                  AND category = ?
                  AND SUBSTR(buchungstag,4,2) = ?
                  AND SUBSTR(buchungstag,7,4) = ?
            """, (kat, monat, jahr))
            bisher = cur.fetchone()[0]
    except (sqlite3.OperationalError, FileNotFoundError) as e:
        ui.draw_header(f"[red]FEHLER:[/red] {e}")
        return

    # Hochrechnung auf vollen Monat
    pro_tag    = bisher / tag if tag > 0 else 0.0
    hochrechnung = pro_tag * tage_monat
    rest_budget  = limit - bisher
    rest_tage    = tage_monat - tag
    ueberschreitung = hochrechnung > limit
    diff         = hochrechnung - limit

    # Fortschrittsbalken (aktuell + Prognose)
    balken_len    = 40
    ist_prozent   = min(bisher / limit, 1.0) if limit > 0 else 0.0
    prog_prozent  = min(hochrechnung / limit, 1.0) if limit > 0 else 0.0

    ist_balken  = int(ist_prozent  * balken_len)
    prog_balken = int(prog_prozent * balken_len)

    balken_ist  = Text()
    balken_ist.append("█" * ist_balken,           style="bold #4a9eff")
    balken_ist.append("░" * (balken_len - ist_balken), style="#444444")
    balken_ist.append(f"  {ist_prozent*100:.0f}%", style="bold #4a9eff")

    balken_prog = Text()
    prog_farbe  = "bold red" if ueberschreitung else "bold yellow"
    balken_prog.append("█" * prog_balken,                style=prog_farbe)
    balken_prog.append("░" * (balken_len - prog_balken), style="#444444")
    balken_prog.append(f"  {prog_prozent*100:.0f}%",     style=prog_farbe)

    warn_text = Text()
    if ueberschreitung:
        warn_text.append(
            f"  ⚠  Prognose überschreitet das Budget um {diff:+.2f} €!",
            style="bold red"
        )
    else:
        warn_text.append(
            f"  ✓  Budget wird voraussichtlich eingehalten  (noch {abs(diff):.2f} € Puffer)",
            style="bold green"
        )

    info = Table.grid(expand=True, padding=(0, 2))
    info.add_column(ratio=1)
    info.add_column(ratio=1)
    info.add_column(ratio=1)
    info.add_row(
        Text(f"Limit:        {limit:.2f} €",          style="bold white"),
        Text(f"Bisher ({tag}. Tag):  {bisher:.2f} €", style="bold #4a9eff"),
        Text(f"Hochrechnung: {hochrechnung:.2f} €",    style=prog_farbe),
    )
    info.add_row(
        Text(f"Ø pro Tag:    {pro_tag:.2f} €",         style="#888888"),
        Text(f"Restbudget:   {rest_budget:.2f} €",     style="#888888"),
        Text(f"Resttage:     {rest_tage}",              style="#888888"),
    )

    _less(Panel(
        Group(
            Align.center(Text(f"Kategorie: {kat}  |  Budget: {limit:.2f} €", style="bold #fa7ff6")),
            Text(""),
            info,
            Text(""),
            Text("  Aktuell:  ", style="#888888"), balken_ist,
            Text("  Prognose: ", style="#888888"), balken_prog,
            Text(""),
            Align.center(warn_text),
        ),
        title="[bold green]Budget-Warnung – Hochrechnung[/]",
        border_style="bold blue", box=box.ROUNDED,
    ))


# ──────────────────────────────────────────────
# EINSTELLUNGEN – KATEGORIEN ZUWEISEN
# ──────────────────────────────────────────────

def _settings_kategorien_zuweisen(ui: UI, config: dict, typ: str) -> dict:
    """
    Weist Kategorien als Einkommen oder Fixkosten zu.
    typ: "einkommen" | "fixkosten"
    """
    key       = f"{typ}_kategorien"
    alle_kat  = list(_kategorien_laden().keys())
    aktuell   = config.get(key, [])

    label = "Einkommen" if typ == "einkommen" else "Fixkosten"

    console.print(Panel(
        Group(
            Text(f"Aktuell als {label} markiert:", style="bold #fa7ff6"),
            Text(", ".join(aktuell) if aktuell else "– keine –", style="#888888"),
            Text(""),
            Text("add <Kategorie>    – hinzufügen", style="#aaaaaa"),
            Text("remove <Kategorie> – entfernen",  style="#aaaaaa"),
            Text("back               – zurück",      style="#aaaaaa"),
        ),
        title=f"[bold green]{label}-Kategorien[/]",
        border_style="bold blue", box=box.ROUNDED,
    ))

    commands = ["add", "remove", "back", "exit"]

    while True:
        completer = WordCompleter(commands, ignore_case=True)
        try:
            raw = prompt(f"  settings ({typ}): ",
                         completer=completer).strip().lower()
        except (KeyboardInterrupt, EOFError):
            return config

        if raw in ("back", ""):
            return config
        elif raw == "exit":
            ui.draw_exit_panel()

        elif raw == "add":
            kat_completer = WordCompleter(
                [k for k in alle_kat if k not in aktuell], ignore_case=True
            )
            try:
                kat = prompt("  Kategorie hinzufügen: ",
                             completer=kat_completer).strip()
            except (KeyboardInterrupt, EOFError):
                continue
            if kat not in alle_kat:
                ui.draw_header(f"[red]Kategorie '[bold]{kat}[/bold]' nicht gefunden.[/red]")
                continue
            if kat in aktuell:
                ui.draw_header(f"[yellow]'{kat}' ist bereits in der Liste.[/yellow]")
                continue
            aktuell.append(kat)
            config[key] = aktuell
            _eval_config_speichern(config)
            ui.draw_header(f"[green]'{kat}' als {label} hinzugefügt.[/green]")

        elif raw == "remove":
            if not aktuell:
                ui.draw_header("[yellow]Liste ist leer.[/yellow]")
                continue
            rm_completer = WordCompleter(aktuell, ignore_case=True)
            try:
                kat = prompt("  Kategorie entfernen: ",
                             completer=rm_completer).strip()
            except (KeyboardInterrupt, EOFError):
                continue
            if kat not in aktuell:
                ui.draw_header(f"[red]'{kat}' nicht in der Liste.[/red]")
                continue
            aktuell.remove(kat)
            config[key] = aktuell
            _eval_config_speichern(config)
            ui.draw_header(f"[green]'{kat}' entfernt.[/green]")

        else:
            console.print(f"[red]Unbekanntes Kommando:[/red] {raw}")


# ──────────────────────────────────────────────
# HAUPT-ÜBERSICHTS-PANEL
# ──────────────────────────────────────────────

def _draw_eval_menu(ui: UI) -> None:
    table = Table(box=box.SIMPLE, show_header=False, expand=True, padding=(0, 1))
    table.add_column(width=4,  style="#808080")
    table.add_column(width=22, style="bold #fa7ff6")
    table.add_column(ratio=1,  style="#888888")

    zeilen = [
        ("1", "vergleich",    "Ausgaben einer Kategorie vs. Ø der letzten N Monate"),
        ("2", "saison",       "Monatliche Entwicklung einer Kategorie über 12 Monate"),
        ("3", "abo",          "Regelmäßige Kleinabbuchungen (Abo-Falle) aufdecken"),
        ("4", "wiederkehrend","Alle wiederkehrenden Buchungen auflisten"),
        ("5", "einkommen",    "Anteil der Fixkosten am Einkommen (50%-Check)"),
        ("6", "prognose",     "Budget-Hochrechnung für laufenden Monat"),
        ("",  "",             ""),
        ("",  "settings",     "Einkommen- & Fixkosten-Kategorien konfigurieren"),
    ]
    for nr, cmd, beschreibung in zeilen:
        table.add_row(nr, cmd, beschreibung)

    console.print(Panel(
        table,
        title="[bold green]Evaluation – Auswertungen[/]",
        border_style="bold blue", box=box.ROUNDED,
    ))


# ──────────────────────────────────────────────
# HAUPTMENÜ
# ──────────────────────────────────────────────

def manage_evaluation() -> None:
    
    ui     = UI()
    config = _eval_config_laden()

    commands = [
        "vergleich", "saison", "abo", "wiederkehrend",
        "einkommen", "prognose", "settings", "help", "back", "exit",
    ]

    while True:
        _draw_eval_menu(ui)
        completer = WordCompleter(commands, ignore_case=True)

        try:
            user_input = prompt(
                "evaluation -- enter command: ",
                completer=completer,
            ).strip().lower()
        except (KeyboardInterrupt, EOFError):
            ui.draw_exit_panel()

        if user_input == "":
            continue
        elif user_input == "back":
            return
        elif user_input == "exit":
            ui.draw_exit_panel()

        elif user_input == "help":
            ui.draw_header(
                "[bold #fa7ff6]vergleich[/]     – Vergleich zum Vormonat / Ø N Monate\n"
                "[bold #fa7ff6]saison[/]        – Saisonale Schwankungen über 12 Monate\n"
                "[bold #fa7ff6]abo[/]           – Abo-Falle: Kleinabbuchungen aufdecken\n"
                "[bold #fa7ff6]wiederkehrend[/] – Wiederkehrende Buchungen auflisten\n"
                "[bold #fa7ff6]einkommen[/]     – Fixkosten-Anteil am Einkommen (50%-Check)\n"
                "[bold #fa7ff6]prognose[/]      – Budget-Hochrechnung laufender Monat\n\n"
                "[bold #fa7ff6]settings[/]      – Einkommen & Fixkosten konfigurieren\n"
                "[bold #fa7ff6]back[/]          – Zurück"
            )

        elif user_input == "vergleich":
            _auswertung_vergleich(ui)

        elif user_input == "saison":
            _auswertung_saison(ui)

        elif user_input == "abo":
            _auswertung_abo(ui)

        elif user_input == "wiederkehrend":
            _auswertung_wiederkehrend(ui)

        elif user_input == "einkommen":
            config = _eval_config_laden()
            _auswertung_einkommen(ui, config)

        elif user_input == "prognose":
            _auswertung_budget_warnung(ui)

        elif user_input == "settings":
            _settings_menü(ui, config)
            config = _eval_config_laden()

        else:
            console.print(f"[red]Unbekanntes Kommando:[/red] {user_input}")


def _settings_menü(ui: UI, config: dict) -> None:
    commands = ["einkommen", "fixkosten", "back", "exit"]
    while True:
        console.print(Panel(
            Group(
                Text("einkommen  – Einkommen-Kategorien zuweisen",  style="#fa7ff6"),
                Text("fixkosten  – Fixkosten-Kategorien zuweisen",   style="#fa7ff6"),
                Text("back       – Zurück",                          style="#888888"),
            ),
            title="[bold green]Settings[/]",
            border_style="bold blue", box=box.ROUNDED,
        ))
        completer = WordCompleter(commands, ignore_case=True)
        try:
            raw = prompt("settings -- enter command: ",
                         completer=completer).strip().lower()
        except (KeyboardInterrupt, EOFError):
            ui.draw_exit_panel()

        if raw in ("back", ""):
            return
        elif raw == "exit":
            ui.draw_exit_panel()
        elif raw == "einkommen":
            config = _settings_kategorien_zuweisen(ui, config, "einkommen")
        elif raw == "fixkosten":
            config = _settings_kategorien_zuweisen(ui, config, "fixkosten")
        else:
            console.print(f"[red]Unbekanntes Kommando:[/red] {raw}")

