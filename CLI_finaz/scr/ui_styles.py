from ui_toolkit import *
import datetime
import time
import random
import sys



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



    def play_loading(self, text="Lade Daten...", length=18):
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
    def _build_grid_panel(self, wink=False, middle_title = "Welcome!!"):

        current_date, current_time, app_status, app_title = self.get_context()
        
        frog_img = self.frog(wink=wink)

        grid = Table.grid(expand=True)
        grid.add_column(ratio=1)
        grid.add_column(ratio=3)
        grid.add_column(ratio=1)
        text_middle_text = Text(middle_title,style= "#fa7ff6")
       

        grid.add_row(
            frog_img,
            Align.center(text_middle_text, vertical="middle"),
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




### ── In ui_styles.py einfügen (neue Methode in der UI-Klasse) ───────────────

    def draw_file_browser(self, aktueller_pfad, eintraege):

        current_date, current_time, app_status, app_title = self.get_context()

        table = Table(
            box=box.SIMPLE,
            show_header=True,
            header_style="bold #fa7ff6",
            expand=True,
            padding=(0, 1),
        )
        table.add_column("Typ",  width=10)
        table.add_column("Name", ratio=1)

        

        for e in eintraege:
            if e.is_dir():
                icon = Text("📁 Ordner", style="blue")
                name = Text(e.name,      style="bold white")
            elif e.suffix.lower() == ".csv":
                icon = Text("📄 CSV",    style="bold green")
                name = Text(e.name,      style="bold green")
            else:
                icon = Text("   Datei",  style="#555555")
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


###########################################################
#####################Sytemfunktionen#######################
###########################################################

    def sytem_exit(self):
        sys.exit(1)
