from ui_toolkit import *
import datetime
import time
import random
import sys
import os


class UI:
    def __init__(self):
        self.console = Console()
        self.box_style = box.ROUNDED

    def draw_header(self, title):
        self.console.print(Panel(title, style="bold magenta", box=box.MINIMAL))





    def draw_welcom_panel(self,duration = 5):

        with Live(self._build_grid_panel(), console=self.console, refresh_per_second=10) as live:
            start_time = time.time()
            

            while time.time() - start_time < duration:

                is_winking = int(time.time() * 2) % 2 == 0

                live.update(self._build_grid_panel(wink=is_winking))
                time.sleep(0.1)

            live.update(self._build_grid_panel(wink=False))



    def draw_menu_panel(self,middle_title):


        current_date, current_time, app_status, app_title = self.get_context()
        
        frog_img = self.small_frog()

        grid = Table.grid(expand=True)
        grid.add_column(ratio=1)
        grid.add_column(ratio=3)
        grid.add_column(ratio=1)
        text_middle_text = Text(middle_title,style= "#fa7ff6")
       

        grid.add_row(
            frog_img,
            Align.center(text_middle_text, vertical="middle"),
            Align.right(
                Group( current_date, current_time), 
                vertical="top"
            )
        )

        panel = Panel(
                    grid, 
                    title=app_title,
                    border_style="bold blue", 
    
        )



        self.console.print(panel)


    def draw_balance_overview_panel(self,middle_title="balance_overview",saldo = None):


        current_date, current_time, app_status, app_title = self.get_context()
        
        frog_img = self.small_frog()

        grid = Table.grid(expand=True)
        grid.add_column(ratio=1)
        grid.add_column(ratio=3)
        grid.add_column(ratio=1)
        text_middle_text = Text(middle_title,style= "#fa7ff6")
        
        text_saldo_text = Text(f"{saldo:.2f} €" if saldo is not None else "–", style="#fa7ff6")

        grid.add_row(
            frog_img,
            Align.center(Group(text_middle_text, text_saldo_text), vertical="middle"),
            Align.right(
                Group( current_date, current_time), 
                vertical="top"
            )
        )

        panel = Panel(
                    grid, 
                    title=app_title, 
                    border_style="bold blue", 
    
        )
    
    
    
        self.console.print(panel)
    
    def draw_overview_table(self, transaktionen: list):
    
        breite = self.console.width
        zeige_saldo    = breite >= 80
        zeige_zweck    = breite >= 60
        zeige_category = breite >= 100

        table = Table(
            box=box.SIMPLE,
            show_header=True,
            header_style="bold #fa7ff6",
            expand=True,
            padding=(0, 1),
        )

        table.add_column("Date",       width=12, justify="center")
        table.add_column("Amount (€)", width=14, justify="right")
        if zeige_saldo:
            table.add_column("Balance (€)", width=14, justify="right")
        if zeige_zweck:
            table.add_column("Description", ratio=1)
        if zeige_category:
            table.add_column("Category", width=16, justify="left")

        for row in transaktionen:
            buchungs_id, datum, betrag, saldo, zweck, category = row

            betrag_style = "bold green" if betrag >= 0 else "bold red"

            zeile = [
                Text(str(datum)  if datum  else "–", style="italic white"),
                Text(f"{betrag:>+.2f}" if betrag is not None else "–", style=betrag_style),
            ]

            if zeige_saldo:
                zeile.append(Text(f"{saldo:.2f}" if saldo is not None else "–", style="white"))

            if zeige_zweck:
                max_len  = max(20, breite - 60)
                zweck_roh  = str(zweck or "–")
                zweck_kurz = zweck_roh[:max_len] + "…" if len(zweck_roh) > max_len else zweck_roh
                zeile.append(Text(zweck_kurz, style="#888888"))

            if zeige_category:
                cat_text  = str(category) if category else "–"
                cat_style = "#aaaaaa" if not category else "bold #fa7ff6"
                zeile.append(Text(cat_text, style=cat_style))

            table.add_row(*zeile)
    
        titel_text = Text(
            f"Transaction Overview  –  {len(transaktionen)} entries  (newest first)",
            style="#fa7ff6"
        )
    
        panel = Panel(
            Group(Align.center(titel_text), table),
            title="[bold green]Finanz-App[/]",
            border_style="bold blue",
            box=self.box_style,
            subtitle="[bold #808080] 'q' = back [/]",

        )
    
        # In String rendern (mit Farben als ANSI-Codes)
        import io
        from rich.console import Console as RichConsole
        buf = io.StringIO()
        tmp = RichConsole(file=buf, width=breite, highlight=False, force_terminal=True)
        tmp.print(panel)
        inhalt = buf.getvalue()
    
        # Über less ausgeben – bleibt am Anfang, q zum Beenden
        import subprocess
        subprocess.run(["less", "-R", "-S", "--prompt= Scroll: arrow keys | q = back"],
                       input=inhalt, text=True)

    def draw_importer_panel(self,middle_title,path=None):


        current_date, current_time, app_status, app_title = self.get_context()
        
        frog_img = self.small_frog()


  

        grid = Table.grid(expand=True)
        grid.add_column(ratio=1)
        grid.add_column(ratio=3)
        grid.add_column(ratio=1)


        text_middle_text = Text(middle_title,style= "#fa7ff6")
        text_path        = Text(str(path), style="italic #808080") 

        grid.add_row(
        frog_img,
        Align.center(Group(text_middle_text, text_path), vertical="middle"),  # ← korrekt
        Align.right(
            Group(current_date, current_time),
            vertical="top"
        )
    )

        panel = Panel(
                    grid, 
                    title=app_title, 
                    border_style="bold blue", 
    
        )



        self.console.print(panel)



    def play_loading(self, text="Loading...", length=18):
        frames = self.get_cachy_frames(length)

        try:
            self.console.show_cursor(False)

            # Wir nutzen Live für ein flackerfreies Grid-Layout
            with Live(console=self.console, refresh_per_second=10) as live:
                for f in frames:
                  
                    grid = Table.grid(expand=True)
                    grid.add_column(justify="left")  
                    grid.add_column(justify="right") #
                    # Highlighting Logik
                    ani_text = Text(f, style="white") 
                 
                    ani_text.highlight_regex(r"[Cc]", "bold green")

                    grid.add_row(text, ani_text)

                    live.update(grid)
                    time.sleep(0.05)

          
            self.console.print(" " * (length * 3 + len(text)), end="\r")

        finally:
            self.console.show_cursor(True)

    def draw_exit_panel(self):

        with Live(self._build_grid_panel(middle_title="Good byeeee"), 
                  console=self.console, 
                  refresh_per_second=10) as live:
            start_time = time.time()
            while time.time() - start_time < 1:

                is_winking = int(time.time() * 2) % 2 == 0

                live.update(self._build_grid_panel(wink=is_winking, middle_title="Good byeeee"))
                time.sleep(0.1)
            live.update(self._build_grid_panel(wink=False, middle_title="Good byeeee"))
        sys.exit(1)
        




###########################################################
#######################Hilffunktion########################
###########################################################



        #get loiading animation UNCOLORIERT
    def get_cachy_frames(self, width):
        frames = []
        for i in range(width + 1):
            # C/c Logik für den "Mund"
            cachy = "C" if i % 2 == 0 else "c"

            # Wegstrecke: Bindestriche mit Leerzeichen
            eaten = "- " * i
            # Verbleibend: Punkte mit Leerzeichen (join sorgt für Abstände dazwischen)
            remaining = " ".join(["⚬"] * (width - i))

            # Prozent berechnen (gerundet)
            prozent = int((i / width) * 100)

            # Das f-string Layout: [ Animation ] Prozent%
            # Wenn noch Punkte da sind, fügen wir ein Leerzeichen vor den Punkten ein
            space = " " if width - i > 0 else ""
            frames.append(f"[{eaten}{cachy}{space}{remaining}] {prozent}%")
        return frames



    #build grid for welcome panel 
    def _build_grid_panel(self, wink=False, middle_title = "Welcome", username= ""):

        current_date, current_time, app_status, app_title = self.get_context()
        
        frog_img = self.frog(wink=wink)

        grid = Table.grid(expand=True)
        grid.add_column(ratio=1)
        grid.add_column(ratio=3)
        grid.add_column(ratio=1)
        text_middle_text = Text(middle_title,style= "#fa7ff6")
        text_username = Text(username,style= "bold blue")

        # Logo-Banner
        banner = Text()
        banner.append("\n")
        banner.append("  ██████╗ ██╗███╗   ██╗ █████╗  ██████╗\n", "bold #00d7ff")
        banner.append("  ██╔═══╝ ██║████╗  ██║██╔══██╗██╔════╝\n", "bold #00d7ff")
        banner.append("  █████╗  ██║██╔██╗ ██║███████║██║     \n", "bold #fa7ff6")
        banner.append("  ██╔══╝  ██║██║╚██╗██║██╔══██║██║     \n", "bold #fa7ff6")
        banner.append("  ██║     ██║██║ ╚████║██║  ██║╚██████╗\n", "bold #ff79c6")
        banner.append("  ╚═╝     ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝\n", "bold #ff79c6")
        banner.append("        Your personal finance companion\n", "#808080")
 



        grid.add_row(
            Align.center(
                frog_img,vertical="middle"
            ),
            Align.center(
                Group(banner), vertical="middle"),
            Align.right(
                Group(app_status, "", current_date, current_time), 
                vertical="top"
            )
        )
        return Panel(grid, title=app_title, border_style="magenta" ,box=box.ROUNDED )




    #give frog as text objekt with colour back
    def frog(self, wink=False):
        eyes = "-..-" if wink else "@..@"
        
        frog_text = f"""
  {eyes}
 (----)
( >__< )
^^    ^^
"""
        frog_green = Text(frog_text, style="bold green")
        frog_green.highlight_regex(r"(@|-)","bold red")
        frog_green.highlight_regex(r"-+","black")
        frog_green.highlight_regex(r"[\(\)]","#248a3f")
        frog_green.highlight_regex(r"\^","black")
        return frog_green



    def small_frog(self):
        frog_text = " @,-,@ \n(—————)"
        small_frog_green = Text(frog_text, style="bold green")
        small_frog_green.highlight_regex(r"(@|-)","bold red")
        small_frog_green.highlight_regex(r"—+", "bold white")
        small_frog_green.highlight_regex(r",-,", "bold #808080")

        return small_frog_green




    def get_context(self):
        now = datetime.datetime.now()
        date = now.strftime("%d.%m.%Y")
        time_now = now.strftime("%H:%M")
        status = "[bold green]● Online[/]"
        title_text = "[bold green]Finanz-App[/]" 
        
        return date,time_now,status,title_text



###########################################################
#########################Importer##########################
###########################################################

    def draw_file_browser(self, aktueller_pfad, eintraege):

        current_date, current_time, app_status, app_title = self.get_context()

        table = Table(
            box=box.SIMPLE,
            show_header=True,
            header_style="bold #fa7ff6",
            expand=True,
            padding=(0, 1),
        )
        table.add_column("Type", width=10)
        table.add_column("Name", ratio=1)

        

        for e in eintraege:
            if e.is_dir():
                icon = Text("📁 Folder", style="blue")
                name = Text(e.name,      style="bold white")
            elif e.suffix.lower() == ".csv":
                icon = Text("📄 CSV",    style="bold green")
                name = Text(e.name,      style="bold green")
            else:

                icon = Text("   File",   style="#555555")
                name = Text(e.name,      style="#888888")
            table.add_row(icon, name)

        
        path_text = Text(str(aktueller_pfad), style="italic #fa7ff6")


        frog_with_padding = self.small_frog()



        grid = Table.grid(expand=True)
        grid.add_column(justify="left", vertical="middle", ratio=1)
        grid.add_column(ratio=8)
       

        grid.add_row(
            Align.left(frog_with_padding),
            Group(Align.center(path_text), table)#,
            #Align.right(Group("", current_date, current_time)),
        )

        self.console.print(
            Panel(
                grid,
                title=app_title,
                subtitle="[bold #808080]Enter = back | exit = quit[/]",
                border_style="bold blue",
                box=self.box_style,
            )
        )


    def draw_import_start(self, csv_pfad, db_pfad):
        grid = Table.grid(expand=True)
        grid.add_column()
        grid.add_row(Text("Starting import...", style="bold #fa7ff6"))
        grid.add_row(Text(f"Source : {csv_pfad}", style="italic white"))
        grid.add_row(Text(f"Target : {db_pfad}", style="italic white"))

        self.console.print(Panel(grid, border_style="bold blue", box=box.MINIMAL))


    def draw_import_bericht(self, csv_pfad, db_pfad, gesamt, neu, start):
        duplikate  = gesamt - neu
        db_groesse = os.path.getsize(db_pfad) / 1024

        grid = Table.grid(expand=True, padding=(0, 1))
        grid.add_column(style="bold #808080")
        grid.add_column(style="white")

        grid.add_row("CSV",                   str(csv_pfad))
        grid.add_row("Database",              f"{db_pfad}  ({db_groesse:.1f} KB)")
        grid.add_row("",                      "")
        grid.add_row("CSV rows total",        f"{gesamt:>6}")
        grid.add_row("Newly imported",        Text(f"{neu:>6}",       style="bold green"))
        grid.add_row("Duplicates ignored",    Text(f"{duplikate:>6}", style="bold yellow"))

        self.console.print(Panel(
            grid,
            title="[bold green]Import complete[/]",
            border_style="green",
            box=self.box_style,
        ))



###########################################################
#####################Sytemfunktionen#######################
###########################################################

    def sytem_exit(self):
        sys.exit(1)




###########################################################
########################Easter_Egg#########################
###########################################################





    def crazy_frog(self):

            frog_text = r"""
                                __--~~--_     _--~~--__
                             _-~         \---/         ~-_
                           /~     __--~~\     /~~--__     ~\
                          /   _-~~       |   |       ~~-_   \
                         |  /~            | |            ~\  |
                         | /      o       | |       o      \ |
                         | |             |   |             | |
                          \ \_         _/     \_         _/ /
                           ~-_~--___--~  b   d  ~--___--~_-~
                            / ~~---    _________    ---~~ \
                            / ~~---    _________    ---~~ \
                           /  __---~~~~         ~~~~---__  \
                          _-~~                           ~~-_
                        /~                                   ~\
                       (_-~                                 ~-_)
                         \                                   /
                        _-~-_                             _-~-_
                       /     ~~--___               ___--~~     \
                      /             ~~~~-------~~~~             \
                     |                                           |
                    |                                             |
             ___    |                                             |    ___
         _-~~   ~~~-|       /                             \       |-~~~   ~~-_
        /            |     |                               |     |            \
       (    ,--~~--_ |    |                                 |    | _--~~--,    )
        \           ~-|   |                                 |   |-~           /
         ~-_           |   |                               |   |           _-~
            ~-_         \   \                             /   /         _-~
               ~-__     /    )                           (    \     __-~
               _--_~~_-~    (~-_                       _-~)    ~-_~~_--_
      _-------(    ~~_-      \  ~~--___   _-_   ___--~~  /      -_~~    )-------_
     ( ,---~~~~~-__-~         ~-_     )~~~   ~~~(     _-~~-      __ -~~~~~---, )
      ( __---~~~(    _-~/   |\   )--~~           ~~--(   /|   \~-_)  ~~~---__ )
       (    _-~~~~--~  (   |  ~-~                     ~-~  |   )~--~~~~-_    )
    """

            frog_green = Text(frog_text, style="bold green")
            self.console.print(frog_green)
