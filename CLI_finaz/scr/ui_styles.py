from ui_toolkit import *
import datetime
import time
import random


class UI:
    def __init__(self):
        self.console = Console()
        self.box_style = box.ROUNDED

    def draw_header(self, title):
        self.console.print(Panel(title, style="bold magenta", box=self.box_style))





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
        self.sytem_exit()
        




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




###########################################################
#####################Sytemfunktionen#######################
###########################################################

    def sytem_exit(self):
        sys.exit(1)
