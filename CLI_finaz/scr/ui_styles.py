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



    def play_loading(self,text="Lade Daten...",lenght=30):

        frames = self.get_cachy_frames(lenght)
        try:

            self.console.show_cursor(False)

            for f in frames:
                
                ani_text = Text(f)
                ani_text.highlight_regex(r"C","bold green")
                ani_text.highlight_regex(r"c","bold green")
                ani_text.highlight_regex(r"•","white")
                self.console.print(text,ani_text,, end="\r")
                
                time.sleep(0.1) 

            self.console.print(" " * (lenght+1), end="\r") 

        finally:
            self.console.show_cursor(True)


    def draw_exit_panel(self):

        with Live(self._build_grid_panel(middle_title = "Good byeeee"), console=self.console, refresh_per_second=10) as live:
          start_time = time.time()
          
        while time.time() - start_time < duration:
            is_winking = int(time.time() * 2) % 2 == 0
            live.update(self._build_grid_panel(wink=is_winking, middle_title = "Good byeeee"))
            time.sleep(0.1)
        live.update(self._build_grid_panel(wink=False, middle_title = "Good byeeee"))
        




###########################################################
#######################Hilffunktion########################
###########################################################



    #get loiading animation UNCOLORIERT
    def get_cachy_frames(self,width):
        frame = []
        for i in range(width + 1):
            if i % 2 == 0:
                cachy = "C"
                eaten = "-" * i
                remaining = " " * (width - i)
            else:
                cachy = "c"
                eaten = "-" * i
                remaining = "⚬" * (width - i)
            
            prozent_int = i/width * 100
            prozent_char = "%"
            frame.append(f"[{eaten}{cachy}{remaining}{prozent_int}{prozent_char}]")
        return frame




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
        frog_green.highlight_regex(r"(@|-)",    "bold red")
        frog_green.highlight_regex(r"-+",       "black")
        frog_green.highlight_regex(r"[\(\)]",   "#248a3f")
        frog_green.highlight_regex(r"\^",       "black")
        return frog_green

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