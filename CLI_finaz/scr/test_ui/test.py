from rich.text import Text
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from rich import box

console = Console()

def make_frog():
    t = Text("""
  @..@
 (----)
( >__< )
^^ ~~ ^^
""", style="green")
    t.highlight_regex(r"@",      "bold red")
    t.highlight_regex(r"\^",     "black")
    t.highlight_regex(r"-+",     "white")
    t.highlight_regex(r"[\(\)]", "yellow")
    return t

title  = "[bold cyan]Finanz-App[/]"
status = "[bold green]● Online[/]"
info   = "[yellow]Kontostand: 1.234 €[/]"
warn   = "[bold red]⚠ Warnung![/]"


# ════════════════════════════════════════════════════════════════════
# 1) Frosch links – Titel rechts  (2 Spalten)
# ════════════════════════════════════════════════════════════════════
grid1 = Table.grid(expand=True)
grid1.add_column(justify="left")
grid1.add_column(justify="right")
grid1.add_row(make_frog(), Align.right(title))

console.print(Panel(grid1, title="Beispiel 1 · links / rechts", border_style="cyan"))


# ════════════════════════════════════════════════════════════════════
# 2) 3 Spalten  – Frosch mitte zentriert
# ════════════════════════════════════════════════════════════════════
grid2 = Table.grid(expand=True)
grid2.add_column(justify="left")
grid2.add_column(justify="center")   # ← Frosch kommt hier rein
grid2.add_column(justify="right")
grid2.add_row(status, make_frog(), info)

console.print(Panel(grid2, title="Beispiel 2 · 3 Spalten", border_style="green"))


# ════════════════════════════════════════════════════════════════════
# 3) Mehrere Zeilen  – Frosch fix in Zeile 2, Spalte 1
#
#   [ Titel         ] [ Status ]
#   [ Frosch 🐸     ] [ Info   ]
#   [ Warnung       ] [ leer   ]
# ════════════════════════════════════════════════════════════════════
grid3 = Table.grid(expand=True)
grid3.add_column(justify="left",  ratio=2)
grid3.add_column(justify="right", ratio=1)

grid3.add_row(title,       status)   # Zeile 1
grid3.add_row(make_frog(), info)     # Zeile 2  ← Frosch
grid3.add_row(warn,        "")       # Zeile 3

console.print(Panel(grid3, title="Beispiel 3 · mehrere Zeilen", border_style="yellow"))


# ════════════════════════════════════════════════════════════════════
# 4) ratio – Spaltenbreite prozentual steuern
#    Frosch bekommt 1/4, Rest-Info 3/4
# ════════════════════════════════════════════════════════════════════
grid4 = Table.grid(expand=True)
grid4.add_column(ratio=1)   # 25 % → Frosch
grid4.add_column(ratio=3)   # 75 % → Text

grid4.add_row(
    make_frog(),
    Align.center(
        "[bold]Willkommen![/]\n\nDein Kontostand beträgt\n[bold green]1.234 €[/]",
        vertical="middle",
    ),
)

console.print(Panel(grid4, title="Beispiel 4 · ratio (25/75)", border_style="magenta"))


# ════════════════════════════════════════════════════════════════════
# 5) Grid im Grid  – Header + Body getrennt aufgebaut
#
#   ┌─────────────────────────────────────┐
#   │  [Frosch]   App-Titel    [Status]   │  ← Header-Grid
#   ├─────────────────────────────────────┤
#   │  Info links  │  Warnung rechts      │  ← Body-Grid
#   └─────────────────────────────────────┘
# ════════════════════════════════════════════════════════════════════
header = Table.grid(expand=True)
header.add_column(justify="left")
header.add_column(justify="center")
header.add_column(justify="right")
header.add_row(make_frog(), title, status)

body = Table.grid(expand=True)
body.add_column(justify="left",  ratio=1)
body.add_column(justify="right", ratio=1)
body.add_row(info, warn)

outer = Table.grid(expand=True)
outer.add_column()
outer.add_row(Panel(header, border_style="cyan"))
outer.add_row(Panel(body,   border_style="yellow"))

console.print(Panel(outer, title="Beispiel 5 · Grid im Grid", border_style="white"))