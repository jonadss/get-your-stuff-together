from ui_toolkit import *

class UI:
    def __init__(self):
        self.console = Console()
        self.box_style = box.ROUNDED

    def draw_header(self, title):
        self.console.print(Panel(title, style="bold magenta", box=self.box_style))




frog_text = """
  @..@
 (----)
( >__< )
^^    ^^
"""

console = Console()  

frog_green = Text(frog_text, style="bold green")
frog_green.highlight_regex(r"@",        "bold red")
frog_green.highlight_regex(r"-+",       "black")
frog_green.highlight_regex(r"[\(\)]",   "#248a3f")
frog_green.highlight_regex(r"\^",       "black")

console.print(frog_green)

title  = "[bold cyan]Finanz-App[/]"
status = "[bold green]● Online[/]"



grid = Table.grid(expand=True)
grid.add_column(ratio=1)   # 25 % → Frosch
grid.add_column(ratio=3)   # 75 % → Text



title  = "[bold cyan]Finanz-App[/]"
status = "[bold green]● Online[/]"
grid.add_row(
    frog_green,
    Align.center(
        "[bold]Welcome![/]\n",
        vertical="middle",
    ),
)


console.print(Panel(grid, title="[blue]finanz_frog[/]", border_style="magenta"))
