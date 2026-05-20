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

        if zeige_category:
            table.add_column("Category",   width=16, justify="left")
        table.add_column("Date",       width=12, justify="center")
        table.add_column("Amount (€)", width=14, justify="right")
        if zeige_saldo:
            table.add_column("Balance (€)", width=14, justify="right")
        if zeige_zweck:
            table.add_column("Description", ratio=1)

        for row in transaktionen:
            buchungs_id, datum, betrag, saldo, zweck, category = row

            betrag_style = "bold green" if betrag >= 0 else "bold red"

            zeile = []

            if zeige_category:
                cat_text  = str(category) if category else "–"
                cat_style = "#aaaaaa" if not category else "bold #fa7ff6"
                zeile.append(Text(cat_text, style=cat_style))

            zeile.append(Text(str(datum) if datum else "–", style="italic white"))
            zeile.append(Text(f"{betrag:>+.2f}" if betrag is not None else "–", style=betrag_style))

            if zeige_saldo:
                zeile.append(Text(f"{saldo:.2f}" if saldo is not None else "–", style="white"))

            if zeige_zweck:
                max_len    = max(20, breite - 60)
                zweck_roh  = str(zweck or "–")
                zweck_kurz = zweck_roh[:max_len] + "…" if len(zweck_roh) > max_len else zweck_roh
                zeile.append(Text(zweck_kurz, style="#888888"))

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
        try:
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
        except KeyboardInterrupt:
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





    # ──────────────────────────────────────────────
    # EVALUATION PANELS
    # ──────────────────────────────────────────────

    def less(self, panel) -> None:
        breite = self.console.width
        buf    = io.StringIO()
        tmp    = RichConsole(file=buf, width=breite, highlight=False, force_terminal=True)
        tmp.print(panel)
        subprocess.run(
            ["less", "-R", "-S", "--prompt= Arrow keys to scroll | q = back"],
            input=buf.getvalue(), text=True
        )

    def draw_eval_menu(self) -> None:
        table = Table(box=box.SIMPLE, show_header=False, expand=True, padding=(0, 1))
        table.add_column(width=4,  style="#808080")
        table.add_column(width=22, style="bold #fa7ff6")
        table.add_column(ratio=1,  style="#888888")

        rows = [
            ("1", "comparison", "Expenses of a category vs. avg of last N months"),
            ("2", "seasonal",   "Monthly trend of a category over 12 months"),
            ("3", "recurring",  "Recurring transactions (optional limit for subscription traps)"),
            ("4", "income",     "Fixed costs as % of income (50% check)"),
            ("5", "forecast",   "Budget projection for a given month"),
            ("",  "",           ""),
            ("",  "settings",   "Configure income & fixed cost categories"),
        ]
        for nr, cmd, desc in rows:
            table.add_row(nr, cmd, desc)

        self.console.print(Panel(
            table,
            title="[bold green]Evaluation – Analysis[/]",
            border_style="bold blue", box=box.ROUNDED,
        ))

    def draw_comparison_panel(self, category, months_data, current_key, average, diff):
        vals    = [v for _, v in months_data]
        max_val = max(vals + [0.01])
        bar_len = 35
        diff_style = "bold red" if diff > 0 else "bold green"

        table = Table(box=box.SIMPLE, show_header=True,
                      header_style="bold #fa7ff6", expand=True, padding=(0, 1))
        table.add_column("Month",      width=10)
        table.add_column("Expenses €", width=12, justify="right")
        table.add_column("Trend",      ratio=1)

        for key, val in months_data[:-1]:
            filled = int((val / max_val) * bar_len)
            table.add_row(key, f"{val:.2f}", Text("█" * filled, style="#888888"))

        cur_val  = months_data[-1][1]
        filled_c = int((cur_val / max_val) * bar_len)
        table.add_row(
            Text(current_key + " ◀", style="bold white"),
            Text(f"{cur_val:.2f}",   style="bold white"),
            Text("█" * filled_c,     style="bold #fa7ff6"),
        )

        n = len(months_data) - 1
        summary = Table.grid(expand=True, padding=(0, 2))
        summary.add_column(ratio=1)
        summary.add_column(ratio=1)
        summary.add_column(ratio=1)
        summary.add_row(
            Text(f"Current month:  {cur_val:.2f} €",        style="bold white"),
            Text(f"Avg last {n} months:  {average:.2f} €",  style="#aaaaaa"),
            Text(f"Difference:  {diff:+.2f} €",              style=diff_style),
        )

        cat_label = category if category != "all" else "All Categories"
        return Panel(
            Group(Align.center(summary), Text(""), table),
            title=f"[bold green]Comparison – {cat_label}[/]",
            border_style="bold blue", box=box.ROUNDED,
        )

    def draw_seasonal_panel(self, category, months_data):
        vals    = [v for _, v in months_data]
        max_val = max(vals + [0.01])
        bar_len = 40
        sorted_d = sorted(months_data, key=lambda x: x[1], reverse=True)
        spikes   = {k for k, _ in sorted_d[:3]}

        table = Table(box=box.SIMPLE, show_header=True,
                      header_style="bold #fa7ff6", expand=True, padding=(0, 1))
        table.add_column("Month",      width=10)
        table.add_column("Expenses €", width=12, justify="right")
        table.add_column("Trend",      ratio=1)

        for key, val in months_data:
            filled   = int((val / max_val) * bar_len) if max_val > 0 else 0
            is_spike = key in spikes and val > 0
            color    = "bold red" if is_spike else "bold #4a9eff"
            bar      = Text()
            bar.append("█" * filled, style=color)
            if is_spike:
                bar.append("  ▲ spike", style="bold red")
            table.add_row(
                Text(key, style="bold white" if is_spike else "white"),
                Text(f"{val:.2f}", style="bold white" if is_spike else "white"),
                bar,
            )

        return Panel(
            table,
            title=f"[bold green]Seasonal Trend – {category} (last 12 months)[/]",
            border_style="bold blue", box=box.ROUNDED,
        )

    def draw_recurring_panel(self, rows, amount_limit=None,
                              monthly_total=0.0, yearly_total=0.0):
        breite = self.console.width
        table  = Table(box=box.SIMPLE, show_header=True,
                       header_style="bold #fa7ff6", expand=True, padding=(0, 1))
        table.add_column("Amount €",    width=10, justify="right")
        table.add_column("Count",       width=8,  justify="right", style="#888888")
        table.add_column("Rhythm",      width=10, style="bold")
        table.add_column("First",       width=12, style="#888888")
        table.add_column("Last",        width=12, style="#888888")
        table.add_column("Description", ratio=1,  style="#aaaaaa")

        for zweck, betrag, anzahl, erstes, letztes, rhythm in rows:
            r_text = (Text("monthly", style="bold #fa7ff6")
                      if rhythm == "monthly"
                      else Text("yearly", style="bold yellow"))
            max_len = max(20, breite - 70)
            desc    = str(zweck or "–")[:max_len]
            table.add_row(
                Text(f"{abs(betrag):.2f}", style="bold red"),
                str(anzahl), r_text,
                str(erstes), str(letztes), desc,
            )

        footer = Table.grid(expand=True, padding=(0, 2))
        footer.add_column(ratio=1)
        footer.add_column(ratio=1)
        footer.add_row(
            Text(f"Monthly total:  {monthly_total:.2f} €", style="bold #fa7ff6"),
            Text(f"Yearly total:   {yearly_total:.2f} €",  style="bold yellow"),
        )

        limit_label = f"≤ {amount_limit:.2f} €" if amount_limit is not None else "all amounts"
        return Panel(
            Group(table, Text(""), Align.center(footer)),
            title=f"[bold green]Recurring Transactions – {limit_label}[/]",
            border_style="bold blue", box=box.ROUNDED,
        )

    def draw_income_panel(self, month_label, income_detail, fixed_detail,
                           total_income, total_fixed, ratio):
        t_income = Table(box=box.SIMPLE, show_header=True,
                         header_style="bold #fa7ff6", expand=True, padding=(0, 1))
        t_income.add_column("Category", width=20, style="bold white")
        t_income.add_column("Income €", width=14, justify="right", style="bold green")
        for cat, s in income_detail.items():
            t_income.add_row(cat, f"{s:.2f}")
        t_income.add_row(Text("TOTAL", style="bold #fa7ff6"),
                         Text(f"{total_income:.2f}", style="bold #fa7ff6"))

        t_fixed = Table(box=box.SIMPLE, show_header=True,
                        header_style="bold #fa7ff6", expand=True, padding=(0, 1))
        t_fixed.add_column("Category",      width=20, style="bold white")
        t_fixed.add_column("Fixed Costs €", width=14, justify="right", style="bold red")
        for cat, s in fixed_detail.items():
            t_fixed.add_row(cat, f"{s:.2f}")
        t_fixed.add_row(Text("TOTAL", style="bold #fa7ff6"),
                        Text(f"{total_fixed:.2f}", style="bold #fa7ff6"))

        warning     = ratio > 50
        ratio_style = "bold red" if warning else "bold green"
        result_text = Text()
        result_text.append("Fixed cost ratio: ", style="bold white")
        result_text.append(f"{ratio:.1f}%", style=ratio_style)
        if warning:
            result_text.append("  ⚠  Above the 50% threshold!", style="bold red")
        else:
            result_text.append("  ✓  Below the 50% threshold",  style="bold green")

        return Panel(
            Group(
                Align.center(Text(f"Month: {month_label}", style="#888888")),
                Text(""),
                t_income, Text(""),
                t_fixed,  Text(""),
                Align.center(result_text),
            ),
            title="[bold green]Fixed Costs as % of Income[/]",
            border_style="bold blue", box=box.ROUNDED,
        )

    def draw_forecast_single(self, category, limit, spent, projection,
                              day, days_in_month):
        bar_len     = 40
        over_budget = projection > limit
        diff        = projection - limit
        prog_style  = "bold red" if over_budget else "bold yellow"

        ist_pct  = min(spent / limit, 1.0)      if limit > 0 else 0.0
        prog_pct = min(projection / limit, 1.0) if limit > 0 else 0.0

        bar_ist = Text()
        bar_ist.append("█" * int(ist_pct * bar_len),
                        style="bold #4a9eff")
        bar_ist.append("░" * (bar_len - int(ist_pct * bar_len)),
                        style="#444444")
        bar_ist.append(f"  {ist_pct*100:.0f}%", style="bold #4a9eff")

        bar_prog = Text()
        bar_prog.append("█" * int(prog_pct * bar_len),             style=prog_style)
        bar_prog.append("░" * (bar_len - int(prog_pct * bar_len)), style="#444444")
        bar_prog.append(f"  {prog_pct*100:.0f}%",                  style=prog_style)

        warn = Text()
        if over_budget:
            warn.append(f"  ⚠  Projection exceeds budget by {diff:+.2f} €!", style="bold red")
        else:
            warn.append(f"  ✓  Budget on track  ({abs(diff):.2f} € remaining buffer)",
                        style="bold green")

        rest_budget = limit - spent
        rest_days   = days_in_month - day
        pro_day     = spent / day if day > 0 else 0.0

        info = Table.grid(expand=True, padding=(0, 2))
        info.add_column(ratio=1)
        info.add_column(ratio=1)
        info.add_column(ratio=1)
        info.add_row(
            Text(f"Limit:        {limit:.2f} €",        style="bold white"),
            Text(f"Spent (day {day}):  {spent:.2f} €",  style="bold #4a9eff"),
            Text(f"Projection:   {projection:.2f} €",   style=prog_style),
        )
        info.add_row(
            Text(f"Avg/day:      {pro_day:.2f} €",      style="#888888"),
            Text(f"Remaining:    {rest_budget:.2f} €",  style="#888888"),
            Text(f"Days left:    {rest_days}",           style="#888888"),
        )

        return Panel(
            Group(
                Align.center(Text(
                    f"Category: {category}  |  Budget: {limit:.2f} €  |  "
                    f"Month: {days_in_month} days",
                    style="bold #fa7ff6"
                )),
                Text(""),
                info, Text(""),
                Text("  Current:    ", style="#888888"), bar_ist,
                Text("  Projection: ", style="#888888"), bar_prog,
                Text(""),
                Align.center(warn),
            ),
            title="[bold green]Budget Forecast[/]",
            border_style="bold blue", box=box.ROUNDED,
        )

    def draw_forecast_overview(self, rows, month_label):
        table = Table(box=box.SIMPLE, show_header=True,
                      header_style="bold #fa7ff6", expand=True, padding=(0, 1))
        table.add_column("Category",    ratio=1,  style="bold white")
        table.add_column("Limit €",     width=12, justify="right")
        table.add_column("Spent €",     width=16, justify="right")
        table.add_column("Projected €", width=16, justify="right")
        table.add_column("Status",      width=12)

        for cat, limit, spent, projection, on_track in rows:
            pct      = (spent / limit * 100)      if limit > 0 else 0.0
            proj_pct = (projection / limit * 100) if limit > 0 else 0.0
            status   = (Text("✓ on track", style="bold green")
                        if on_track else Text("⚠ over", style="bold red"))
            table.add_row(
                cat,
                f"{limit:.2f}",
                Text(f"{spent:.2f} ({pct:.0f}%)",      style="bold #4a9eff"),
                Text(f"{projection:.2f} ({proj_pct:.0f}%)",
                     style="bold green" if on_track else "bold red"),
                status,
            )

        return Panel(
            table,
            title=f"[bold green]Budget Forecast – Overview – {month_label}[/]",
            border_style="bold blue", box=box.ROUNDED,
        )

    def draw_settings_eval_panel(self, income_cats, fixed_cats):
        self.console.print(Panel(
            Group(
                Text("income  – Assign income categories",      style="#fa7ff6"),
                Text("fixed   – Assign fixed cost categories",  style="#fa7ff6"),
                Text("back    – Back",                           style="#888888"),
                Text(""),
                Text("Income categories:     " +
                     (", ".join(income_cats) if income_cats else "– none –"),
                     style="#aaaaaa"),
                Text("Fixed cost categories: " +
                     (", ".join(fixed_cats) if fixed_cats else "– none –"),
                     style="#aaaaaa"),
            ),
            title="[bold green]Settings – Evaluation[/]",
            border_style="bold blue", box=box.ROUNDED,
        ))

    def draw_category_assign_panel(self, label, current):
        self.console.print(Panel(
            Group(
                Text(f"Currently marked as {label}:", style="bold #fa7ff6"),
                Text(", ".join(current) if current else "– none –", style="#888888"),
                Text(""),
                Text("add <category>    – add",    style="#aaaaaa"),
                Text("remove <category> – remove", style="#aaaaaa"),
                Text("back              – back",   style="#aaaaaa"),
            ),
            title=f"[bold green]{label} Categories[/]",
            border_style="bold blue", box=box.ROUNDED,
        ))

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
