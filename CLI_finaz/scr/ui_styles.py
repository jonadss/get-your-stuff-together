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


# ══════════════════════════════════════════════════════════════════════════════
# TEXTUAL TUI
# ══════════════════════════════════════════════════════════════════════════════

_FROG_W = 14

_FROG_FRAMES = {
    "normal": [" @    @ ", "(------)", "(>____<)", "^^    ^^"],
    "blink":  [" -    - ", "(------)", "(>____<)", "^^    ^^"],
    "jump":   [" @    @ ", "(------)", "(>____<)", " /    \\ "],
    "squat":  [" @    @ ", "(------)", "(______)", " ^^  ^^ "],
}

TABS_DEF = [
    ("balance",    "Balance"),
    ("history",    "History"),
    ("importer",   "Importer"),
    ("evaluation", "Evaluation"),
    ("debts",      "Debts"),
    ("categories", "Categories"),
    ("budget",     "Budget"),
]

TAB_COMMANDS: dict = {
    "balance":    ["show history", "importer", "evaluation", "debts",
                   "categories", "budget", "help", "exit"],
    "history":    ["refresh", "help", "exit"],
    "importer":   ["import", "undo import", "delete csv", "delete db", "help", "exit"],
    "evaluation": ["comparison", "seasonal", "recurring", "income", "forecast",
                   "settings income", "settings fixed", "help", "exit"],
    "debts":      ["show debts", "new list", "add entry", "remove entry",
                   "delete list", "help", "exit"],
    "categories": ["list", "new", "delete", "wordpool add", "wordpool remove",
                   "apply", "help", "exit"],
    "budget":     ["show budget", "set budget", "remove budget", "period", "help", "exit"],
}


@dataclass
class FlowStep:
    label: str
    key: str
    choices: list = field(default_factory=list)
    optional: bool = False
    validate_fn: Callable = field(default=lambda v: None)


def _is_positive_float(s: str) -> bool:
    try:
        return float(s.replace(",", ".")) > 0
    except ValueError:
        return False


def _is_any_float(s: str) -> bool:
    try:
        float(s.replace(",", "."))
        return True
    except ValueError:
        return False


# ─── FrogPanel ────────────────────────────────────────────────────────────────

class FrogPanel(Static):
    def on_mount(self) -> None:
        self._f = 0
        rng = random.Random(7)
        self._stars = [
            (rng.randint(0, _FROG_W - 1), rng.uniform(0, 24),
             rng.choice("✦✧·*"), rng.uniform(0, math.pi * 2),
             rng.uniform(0.4, 1.2))
            for _ in range(28)
        ]
        self.set_interval(0.13, self._tick)

    def _tick(self) -> None:
        self._f += 1
        H = self.size.height if self.size.height > 0 else 24
        W = _FROG_W
        t = self._f * 0.13
        grid = [[(" ", "#111100")] * W for _ in range(H)]

        for sx, sy0, ch, phase, spd in self._stars:
            sy = (sy0 + self._f * spd * 0.09) % H
            iy = int(sy)
            bri = (math.sin(t * 1.8 + phase) + 1) / 2
            if bri > 0.75:   col, sc = "bold yellow", "✦"
            elif bri > 0.5:  col, sc = "#ccaa00",     "✧"
            elif bri > 0.25: col, sc = "#665500",     "·"
            else:             col, sc = "#221100",     " "
            if 0 <= iy < H:
                grid[iy][sx] = (sc, col)

        total  = H + 8
        base_y = (self._f * 0.28) % total - 4
        hop_sin = math.sin(self._f * 0.55)
        hop_off = -int(abs(hop_sin) * 3)

        if   abs(hop_sin) > 0.7:  fname = "jump"
        elif abs(hop_sin) < 0.12: fname = "squat"
        elif self._f % 40 < 3:   fname = "blink"
        else:                      fname = "normal"

        frog_lines = _FROG_FRAMES[fname]
        gy = int(base_y) + hop_off
        gx = (W - 8) // 2
        grn = int(110 + 70 * abs(math.sin(t * 0.4)))
        er  = int(200 + 55 * abs(math.sin(t * 1.1)))

        for li, line in enumerate(frog_lines):
            for ci, fc in enumerate(line):
                giy, gix = gy + li, gx + ci
                if 0 <= giy < H and 0 <= gix < W:
                    if fc == " ":
                        grid[giy][gix] = (" ", "#0a1a0a")
                    elif fc in "@-" and li == 0:
                        grid[giy][gix] = (fc, f"bold rgb({er},60,60)")
                    elif fc in "^/\\":
                        grid[giy][gix] = (fc, "#1a5c1a")
                    else:
                        grid[giy][gix] = (fc, f"bold rgb(40,{grn},40)")

        title = "Finanz-App"
        r2 = int(200 + 55 * abs(math.sin(t * 0.6)))
        g2 = int(100 + 55 * abs(math.sin(t * 0.6 + 2)))
        b2 = int(150 + 80 * abs(math.sin(t * 0.6 + 4)))
        tx = max(0, (W - len(title)) // 2)
        for i, c in enumerate(title):
            xi = tx + i
            if xi < W:
                grid[0][xi] = (c, f"bold rgb({r2},{g2},{b2})")

        out = Text()
        for row in grid:
            for fc, col in row:
                out.append(fc, style=col)
            out.append("\n")
        self.update(out)


# ─── CommandCompleter ─────────────────────────────────────────────────────────

class CommandCompleter(OptionList):
    def show_for(self, query: str, commands: list) -> None:
        self.clear_options()
        q = query.lower()
        matches = [c for c in commands if c.startswith(q)] if query else list(commands)
        if not matches:
            self.display = False
            return
        for m in matches:
            n = len(query)
            lbl = Text.from_markup(
                f"[bold cyan]{m[:n]}[/bold cyan][dim]{m[n:]}[/dim]"
            )
            self.add_option(Option(lbl, id=m))
        self.highlighted = 0
        self.display = True

    def pick_highlighted(self) -> str | None:
        if not self.display or self.highlighted is None:
            return None
        val = str(self.get_option_at_index(self.highlighted).id)
        inp = self.app.query_one("#cmd-input", Input)
        inp.value = val
        inp.cursor_position = len(val)
        self.display = False
        inp.focus()
        return val

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        val = str(event.option.id)
        inp = self.app.query_one("#cmd-input", Input)
        inp.value = val
        inp.cursor_position = len(val)
        self.display = False
        inp.focus()


# ─── Content Views ────────────────────────────────────────────────────────────

class BalanceView(Static):
    def on_mount(self) -> None:
        self.refresh_content()

    def refresh_content(self) -> None:
        try:
            from request import start_saldo_request
            saldo = start_saldo_request()
            t = Text()
            t.append("\n\n  Current Balance\n\n", style="#888888")
            style = "bold #fa7ff6" if (saldo is None or saldo >= 0) else "bold red"
            val = f"{saldo:+.2f} €" if saldo is not None else "–"
            t.append(f"  {val}\n", style=style)
            t.append(
                "\n  [dim]Commands: show history  importer  evaluation[/dim]\n"
                "  [dim]           debts  categories  budget  help  exit[/dim]\n",
            )
            self.update(t)
        except Exception:
            self.update(Text("  [dim]No database found. Import a CSV first.[/dim]"))


class HistoryView(VerticalScroll):
    def compose(self) -> ComposeResult:
        yield Static(id="history-content")

    def refresh_content(self) -> None:
        from request import overview, DB_PFAD as REQ_DB
        content = self.query_one("#history-content", Static)
        try:
            rows = overview(sqlite3.connect(REQ_DB))
            tbl = Table(box=box.SIMPLE, show_header=True,
                        header_style="bold #fa7ff6", expand=True, padding=(0, 1))
            tbl.add_column("Category",    width=16)
            tbl.add_column("Date",        width=12, justify="center")
            tbl.add_column("Amount (€)",  width=14, justify="right")
            tbl.add_column("Balance (€)", width=14, justify="right")
            tbl.add_column("Description", ratio=1)
            for _, datum, betrag, saldo, zweck, category in rows:
                bs = "bold green" if betrag >= 0 else "bold red"
                cs = "#aaaaaa" if not category else "bold #fa7ff6"
                tbl.add_row(
                    Text(str(category) if category else "–", style=cs),
                    Text(str(datum) if datum else "–", style="italic white"),
                    Text(f"{betrag:>+.2f}" if betrag is not None else "–", style=bs),
                    Text(f"{saldo:.2f}" if saldo is not None else "–", style="white"),
                    Text(str(zweck or "–")[:80], style="#888888"),
                )
            content.update(Panel(tbl,
                title="[bold green]Transaction History[/]",
                border_style="bold blue", box=box.ROUNDED))
        except sqlite3.OperationalError:
            content.update(Text("[yellow]No transactions yet. Import a CSV first.[/yellow]"))
        except Exception as e:
            content.update(Text(f"[red]Error: {e}[/red]"))


class BudgetView(Static):
    def on_mount(self) -> None:
        self._zeitraum = "monat"
        self.refresh_content()

    def refresh_content(self, zeitraum: str | None = None) -> None:
        if zeitraum:
            self._zeitraum = zeitraum
        try:
            from budget import _budget_laden, _draw_budget_panel
            panel = _draw_budget_panel(None, _budget_laden(), self._zeitraum)
            self.update(panel if panel is not None else
                        Text("[yellow]No budget data. Use 'set budget' first.[/yellow]"))
        except Exception as e:
            self.update(Text(f"[red]Error: {e}[/red]"))


class DebtsView(Static):
    def on_mount(self) -> None:
        self.refresh_content()

    def refresh_content(self) -> None:
        try:
            from debts import _db_connect, _draw_debts_panel, _tabellen_erstellen
            with _db_connect() as conn:
                cur = conn.cursor()
                _tabellen_erstellen(cur)
                conn.commit()
                panel = _draw_debts_panel(None, cur)
            self.update(panel if panel is not None else Text(""))
        except Exception as e:
            self.update(Text(f"[red]Error: {e}[/red]"))


class CategoriesView(Static):
    def on_mount(self) -> None:
        self.refresh_content()

    def refresh_content(self) -> None:
        try:
            from categories import _kategorien_laden, _draw_kategorien_panel
            panel = _draw_kategorien_panel(None, _kategorien_laden())
            self.update(panel if panel is not None else
                        Text("[yellow]No categories yet. Use 'new' to create one.[/yellow]"))
        except Exception as e:
            self.update(Text(f"[red]Error: {e}[/red]"))


class EvaluationView(Static):
    def on_mount(self) -> None:
        self.show_menu()

    def show_menu(self) -> None:
        tbl = Table(box=box.SIMPLE, show_header=False, expand=True, padding=(0, 1))
        tbl.add_column(width=4,  style="#808080")
        tbl.add_column(width=22, style="bold #fa7ff6")
        tbl.add_column(ratio=1,  style="#888888")
        for nr, cmd, desc in [
            ("1", "comparison",      "Expenses vs. avg of last N months"),
            ("2", "seasonal",        "Monthly trend over 12 months"),
            ("3", "recurring",       "Recurring transactions"),
            ("4", "income",          "Fixed costs as % of income"),
            ("5", "forecast",        "Budget projection for a given month"),
            ("",  "",                ""),
            ("",  "settings income", "Configure income categories"),
            ("",  "settings fixed",  "Configure fixed cost categories"),
        ]:
            tbl.add_row(nr, cmd, desc)
        self.update(Panel(tbl, title="[bold green]Evaluation[/]",
                          border_style="bold blue", box=box.ROUNDED))

    def show_result(self, panel) -> None:
        self.update(panel)


class ImporterView(Static):
    def on_mount(self) -> None:
        self.refresh_content()

    def refresh_content(self) -> None:
        try:
            from import_csv import DB_PFAD as IMP_DB, LOG_PFAD
            tbl = Table(box=box.SIMPLE, show_header=False, expand=True, padding=(0, 1))
            tbl.add_column(style="bold #808080")
            tbl.add_column(style="white")
            tbl.add_row("Database", str(IMP_DB))
            tbl.add_row("Status",
                        "[green]exists[/green]" if IMP_DB.exists() else "[yellow]not found[/yellow]")
            if LOG_PFAD.exists():
                try:
                    import json as _j
                    with open(LOG_PFAD) as f:
                        log = _j.load(f)
                    last = next((e for e in reversed(log) if not e["rueckgaengig"]), None)
                    if last:
                        tbl.add_row("Last import",
                                    f"{last['zeitstempel']} – {last['anzahl_neu']} rows")
                except Exception:
                    pass
            self.update(Panel(tbl, title="[bold green]Importer[/]",
                              subtitle="[dim]import | undo import | delete csv | delete db[/dim]",
                              border_style="bold blue", box=box.ROUNDED))
        except Exception as e:
            self.update(Text(f"[red]Error: {e}[/red]"))


# ─── FinanzApp ────────────────────────────────────────────────────────────────

class FinanzApp(App):
    CSS = """
    Screen { background: #0d0d0d; }
    #main-row { height: 1fr; }
    #sidebar { width: 16; height: 100%; }
    #right { width: 1fr; margin-left: 1; }
    Tabs { height: 3; }
    Tab { color: #555; }
    Tab.-active { color: #fa7ff6; }
    #content-area { height: 1fr; border: round #2a2a2a; }
    BalanceView, BudgetView, DebtsView, CategoriesView,
    EvaluationView, ImporterView { height: 1fr; padding: 1 2; }
    HistoryView { height: 1fr; }
    #input-area { height: auto; margin: 1 1 0 1; }
    #cmd-input  { border: round cyan; }
    #statusbar  { height: 1; background: #111; color: #888; padding: 0 2; }
    #completer  { display: none; height: auto; max-height: 8;
                  border: round #333; background: #0d0d1a; }
    #completer > .option-list--option             { padding: 0 2; }
    #completer > .option-list--option-highlighted { background: #1a1a3a; }
    """

    BINDINGS = []

    def compose(self) -> ComposeResult:
        with Horizontal(id="main-row"):
            yield FrogPanel(id="sidebar")
            with Vertical(id="right"):
                yield Tabs(*[Tab(label, id=tid) for tid, label in TABS_DEF])
                with ContentSwitcher(id="content-area", initial="balance"):
                    yield BalanceView(id="balance")
                    yield HistoryView(id="history")
                    yield ImporterView(id="importer")
                    yield EvaluationView(id="evaluation")
                    yield DebtsView(id="debts")
                    yield CategoriesView(id="categories")
                    yield BudgetView(id="budget")
                with Vertical(id="input-area"):
                    yield CommandCompleter(id="completer")
                    yield Input(placeholder="Befehl  (Tab = Menü  |  Esc = abbrechen)", id="cmd-input")
                yield Static(id="statusbar")

    def on_mount(self) -> None:
        self._tab_id = "balance"
        self._flow_steps = None
        self._flow_data: dict = {}
        self._flow_done = None
        self._flow_step_idx = 0
        self.query_one("#cmd-input", Input).focus()
        self._log("[dim]Tab = open menu  |  Enter = confirm  |  Esc = cancel  |  exit = quit[/dim]")

    # ── Tab handling ──────────────────────────────────────────────────────────

    def on_tabs_tab_activated(self, event: Tabs.TabActivated) -> None:
        tab_id = str(event.tab.id)
        self._tab_id = tab_id
        self.query_one(ContentSwitcher).current = tab_id

    def _switch_tab(self, tab_id: str) -> None:
        self._tab_id = tab_id
        self.query_one(Tabs).active = tab_id

    # ── Logging ───────────────────────────────────────────────────────────────

    def _log(self, msg: str) -> None:
        try:
            self.query_one("#statusbar", Static).update(Text.from_markup(msg))
        except Exception:
            pass

    # ── Key handling ──────────────────────────────────────────────────────────

    def on_key(self, event) -> None:
        completer = self.query_one("#completer", CommandCompleter)
        inp = self.query_one("#cmd-input", Input)

        if event.key == "escape":
            if self._flow_steps is not None:
                self._flow_steps = None
                self._flow_data = {}
                self._flow_done = None
                self._flow_step_idx = 0
                completer.display = False
                self._log("[dim]Cancelled.[/dim]")
                event.stop()
                return
            if completer.display:
                completer.display = False
                inp.focus()
                event.stop()
                return

        if event.key == "tab" and self.focused == inp:
            event.prevent_default()
            event.stop()
            if completer.display:
                count = completer.option_count
                completer.highlighted = ((completer.highlighted or 0) + 1) % count
            else:
                if self._flow_steps is not None:
                    step = self._flow_steps[self._flow_step_idx]
                    completer.show_for(inp.value, step.choices)
                else:
                    completer.show_for(inp.value, TAB_COMMANDS.get(self._tab_id, []))
            return

        if event.key == "backspace" and completer.display and inp.value == "":
            completer.display = False
            event.stop()
            return

        if not completer.display:
            return

        if event.key == "enter":
            if completer.pick_highlighted():
                event.stop()
        elif event.key == "escape":
            completer.display = False
            inp.focus()
            event.stop()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id != "cmd-input":
            return
        completer = self.query_one("#completer", CommandCompleter)
        if not completer.display:
            return
        if self._flow_steps is not None:
            step = self._flow_steps[self._flow_step_idx]
            completer.show_for(event.value, step.choices)
        else:
            completer.show_for(event.value, TAB_COMMANDS.get(self._tab_id, []))

    def on_input_submitted(self, event: Input.Submitted) -> None:
        completer = self.query_one("#completer", CommandCompleter)
        if completer.display:
            completer.pick_highlighted()
            return
        value = event.value.strip()
        event.input.clear()
        completer.display = False
        if not value:
            return
        if self._flow_steps is not None:
            self._advance_flow(value)
        else:
            self._dispatch(value)

    # ── Flow engine ───────────────────────────────────────────────────────────

    def _start_flow(self, steps: list, callback) -> None:
        self._flow_steps = list(steps)
        self._flow_data = {}
        self._flow_done = callback
        self._flow_step_idx = 0
        self._show_flow_step()

    def _show_flow_step(self) -> None:
        if not self._flow_steps:
            return
        step = self._flow_steps[self._flow_step_idx]
        self._log(f"[cyan]{step.label}[/cyan]  [dim](Esc = cancel)[/dim]")
        completer = self.query_one("#completer", CommandCompleter)
        if step.choices:
            completer.show_for("", step.choices)
        else:
            completer.display = False

    def _advance_flow(self, value: str) -> None:
        step = self._flow_steps[self._flow_step_idx]
        if step.optional and value == "":
            self._flow_data[step.key] = ""
        else:
            err = step.validate_fn(value)
            if err:
                self._log(f"[red]{err}[/red]")
                return
            self._flow_data[step.key] = value
        self._flow_step_idx += 1
        if self._flow_step_idx >= len(self._flow_steps):
            done = self._flow_done
            data = dict(self._flow_data)
            self._flow_steps = None
            self._flow_data = {}
            self._flow_done = None
            self._flow_step_idx = 0
            self._log("")
            done(data)
        else:
            self._show_flow_step()

    # ── Command dispatch ──────────────────────────────────────────────────────

    def _dispatch(self, cmd: str) -> None:
        c = cmd.lower()
        tab = self._tab_id

        if c == "exit":
            self.exit()
            return
        if c == "help":
            self._log("[cyan]Commands:[/cyan] " + "  ".join(TAB_COMMANDS.get(tab, [])))
            return

        if tab == "balance":
            nav = {
                "show history": "history", "importer": "importer",
                "evaluation": "evaluation", "debts": "debts",
                "categories": "categories", "budget": "budget",
            }
            if c in nav:
                self._switch_tab(nav[c])
                return
            self._log(f"[red]Unknown command:[/red] {cmd}")
            return

        if tab == "history":
            if c == "refresh":
                self.query_one("#history", HistoryView).refresh_content()
                self._log("[green]History refreshed.[/green]")
            else:
                self._log(f"[red]Unknown command:[/red] {cmd}")
            return

        if tab == "budget":
            if   c == "show budget":   self.query_one("#budget", BudgetView).refresh_content()
            elif c == "set budget":    self._flow_set_budget()
            elif c == "remove budget": self._flow_remove_budget()
            elif c == "period":        self._flow_period()
            else: self._log(f"[red]Unknown command:[/red] {cmd}")
            return

        if tab == "debts":
            if   c == "show debts":   self.query_one("#debts", DebtsView).refresh_content()
            elif c == "new list":     self._flow_new_debt_list()
            elif c == "add entry":    self._flow_add_debt_entry()
            elif c == "remove entry": self._flow_remove_debt_entry()
            elif c == "delete list":  self._flow_delete_debt_list()
            else: self._log(f"[red]Unknown command:[/red] {cmd}")
            return

        if tab == "categories":
            if   c == "list":          self.query_one("#categories", CategoriesView).refresh_content()
            elif c == "new":           self._flow_new_category()
            elif c == "delete":        self._flow_delete_category()
            elif c == "wordpool add":  self._flow_wordpool_add()
            elif c == "wordpool remove": self._flow_wordpool_remove()
            elif c == "apply":         self._apply_categories()
            else: self._log(f"[red]Unknown command:[/red] {cmd}")
            return

        if tab == "importer":
            if   c == "import":      self._flow_import()
            elif c == "undo import": self._undo_import()
            elif c == "delete csv":  self._flow_delete_csv()
            elif c == "delete db":   self._flow_delete_db()
            else: self._log(f"[red]Unknown command:[/red] {cmd}")
            return

        if tab == "evaluation":
            if   c == "comparison":       self._flow_eval_comparison()
            elif c == "seasonal":         self._flow_eval_seasonal()
            elif c == "recurring":        self._flow_eval_recurring()
            elif c == "income":           self._eval_income()
            elif c == "forecast":         self._flow_eval_forecast()
            elif c == "settings income":  self._flow_eval_settings("einkommen")
            elif c == "settings fixed":   self._flow_eval_settings("fixkosten")
            else: self._log(f"[red]Unknown command:[/red] {cmd}")
            return

        self._log(f"[red]Unknown command:[/red] {cmd}")

    # ── Budget flows ──────────────────────────────────────────────────────────

    def _flow_set_budget(self) -> None:
        from categories import _kategorien_laden
        kats = sorted(_kategorien_laden().keys())
        if not kats:
            self._log("[yellow]No categories. Create categories first.[/yellow]")
            return

        def done(data):
            from budget import _budget_laden, _budget_speichern
            b = _budget_laden()
            b[data["kat"]] = {"limit": float(data["limit"].replace(",", ".")),
                              "zeitraum": data["zeitraum"]}
            _budget_speichern(b)
            self._log(f"[green]Budget set:[/green] {data['kat']} → {data['limit']} € / {data['zeitraum']}")
            self.query_one("#budget", BudgetView).refresh_content()

        self._start_flow([
            FlowStep("Category:", "kat", choices=kats,
                     validate_fn=lambda v: None if v in kats else f"Category '{v}' not found"),
            FlowStep("Limit (€):", "limit",
                     validate_fn=lambda v: None if _is_positive_float(v) else "Enter a number > 0"),
            FlowStep("Period (monat/jahr/gesamt):", "zeitraum",
                     choices=["monat", "jahr", "gesamt"],
                     validate_fn=lambda v: None if v in ("monat", "jahr", "gesamt") else "Enter monat, jahr, or gesamt"),
        ], done)

    def _flow_remove_budget(self) -> None:
        from budget import _budget_laden
        kats = list(_budget_laden().keys())
        if not kats:
            self._log("[yellow]No budget limits set.[/yellow]")
            return

        def done(data):
            from budget import _budget_laden, _budget_speichern
            b = _budget_laden()
            if data["kat"] in b:
                del b[data["kat"]]
                _budget_speichern(b)
                self._log(f"[green]Budget for '{data['kat']}' removed.[/green]")
                self.query_one("#budget", BudgetView).refresh_content()
            else:
                self._log(f"[red]Category '{data['kat']}' not found.[/red]")

        self._start_flow([
            FlowStep("Category to remove:", "kat", choices=kats,
                     validate_fn=lambda v: None if v in kats else f"Category '{v}' not found"),
        ], done)

    def _flow_period(self) -> None:
        def done(data):
            self.query_one("#budget", BudgetView).refresh_content(zeitraum=data["zr"])
            self._log(f"[green]Period: {data['zr']}[/green]")

        self._start_flow([
            FlowStep("Period (monat/jahr/gesamt):", "zr",
                     choices=["monat", "jahr", "gesamt"],
                     validate_fn=lambda v: None if v in ("monat", "jahr", "gesamt") else "Enter monat, jahr, or gesamt"),
        ], done)

    # ── Debts flows ───────────────────────────────────────────────────────────

    def _flow_new_debt_list(self) -> None:
        def done(data):
            from debts import _db_connect, _tabellen_erstellen
            datum = datetime.now().strftime("%d.%m.%Y")
            try:
                with _db_connect() as conn:
                    cur = conn.cursor()
                    _tabellen_erstellen(cur)
                    conn.execute(
                        "INSERT INTO schulden_listen (person, erstellt_am) VALUES (?, ?)",
                        (data["person"], datum))
                    conn.commit()
                self._log(f"[green]List for '{data['person']}' created.[/green]")
                self.query_one("#debts", DebtsView).refresh_content()
            except sqlite3.IntegrityError:
                self._log(f"[yellow]Person '{data['person']}' already exists.[/yellow]")

        self._start_flow([
            FlowStep("Person's name:", "person",
                     validate_fn=lambda v: None if v.strip() else "Name cannot be empty"),
        ], done)

    def _flow_add_debt_entry(self) -> None:
        from debts import _db_connect, _alle_personen, _tabellen_erstellen
        try:
            with _db_connect() as conn:
                cur = conn.cursor()
                _tabellen_erstellen(cur)
                persons = _alle_personen(cur)
        except Exception as e:
            self._log(f"[red]Error: {e}[/red]")
            return
        if not persons:
            self._log("[yellow]No lists. Use 'new list' first.[/yellow]")
            return
        names = [p[1] for p in persons]

        def done(data):
            from debts import _db_connect, _alle_personen
            try:
                with _db_connect() as conn:
                    cur = conn.cursor()
                    pers = [(lid, p) for lid, p in _alle_personen(cur)
                            if p.lower() == data["person"].lower()]
                    if not pers:
                        self._log(f"[red]Person not found.[/red]")
                        return
                    betrag = float(data["betrag"].replace(",", "."))
                    grund = data.get("grund") or None
                    datum = datetime.now().strftime("%d.%m.%Y")
                    conn.execute(
                        "INSERT INTO schulden_eintraege (listen_id, betrag, grund, datum) VALUES (?,?,?,?)",
                        (pers[0][0], betrag, grund, datum))
                    conn.commit()
                self._log(f"[green]Entry added:[/green] {betrag:+.2f} €" +
                          (f"  – {grund}" if grund else ""))
                self.query_one("#debts", DebtsView).refresh_content()
            except Exception as e:
                self._log(f"[red]Error: {e}[/red]")

        self._start_flow([
            FlowStep("Person:", "person", choices=names,
                     validate_fn=lambda v: None if v in names else f"Person '{v}' not found"),
            FlowStep("Amount (€) – negative=I owe, positive=I am owed:", "betrag",
                     validate_fn=lambda v: None if _is_any_float(v) else "Enter a number"),
            FlowStep("Reason (optional, Enter = skip):", "grund", optional=True),
        ], done)

    def _flow_remove_debt_entry(self) -> None:
        from debts import _db_connect, _alle_personen, _tabellen_erstellen
        try:
            with _db_connect() as conn:
                cur = conn.cursor()
                _tabellen_erstellen(cur)
                persons = _alle_personen(cur)
        except Exception as e:
            self._log(f"[red]Error: {e}[/red]")
            return
        if not persons:
            self._log("[yellow]No debt lists.[/yellow]")
            return
        names = [p[1] for p in persons]

        def done(data):
            from debts import _db_connect, _alle_personen
            try:
                with _db_connect() as conn:
                    cur = conn.cursor()
                    pers = [(lid, p) for lid, p in _alle_personen(cur)
                            if p.lower() == data["person"].lower()]
                    if not pers:
                        self._log(f"[red]Person not found.[/red]")
                        return
                    eid = data["entry_id"]
                    if not eid.isdigit():
                        self._log("[red]Invalid entry ID.[/red]")
                        return
                    conn.execute("DELETE FROM schulden_eintraege WHERE eintrag_id = ?",
                                 (int(eid),))
                    conn.commit()
                self._log(f"[green]Entry {eid} deleted.[/green]")
                self.query_one("#debts", DebtsView).refresh_content()
            except Exception as e:
                self._log(f"[red]Error: {e}[/red]")

        self._start_flow([
            FlowStep("Person:", "person", choices=names),
            FlowStep("Entry ID to delete:", "entry_id",
                     validate_fn=lambda v: None if v.isdigit() else "Enter a valid entry ID"),
        ], done)

    def _flow_delete_debt_list(self) -> None:
        from debts import _db_connect, _alle_personen, _tabellen_erstellen
        try:
            with _db_connect() as conn:
                cur = conn.cursor()
                _tabellen_erstellen(cur)
                persons = _alle_personen(cur)
        except Exception as e:
            self._log(f"[red]Error: {e}[/red]")
            return
        if not persons:
            self._log("[yellow]No debt lists.[/yellow]")
            return
        names = [p[1] for p in persons]

        def done(data):
            from debts import _db_connect, _alle_personen
            try:
                with _db_connect() as conn:
                    cur = conn.cursor()
                    pers = [(lid, p) for lid, p in _alle_personen(cur)
                            if p.lower() == data["person"].lower()]
                    if not pers:
                        self._log(f"[red]Person not found.[/red]")
                        return
                    conn.execute("DELETE FROM schulden_listen WHERE listen_id = ?",
                                 (pers[0][0],))
                    conn.commit()
                self._log(f"[green]List for '{data['person']}' deleted.[/green]")
                self.query_one("#debts", DebtsView).refresh_content()
            except Exception as e:
                self._log(f"[red]Error: {e}[/red]")

        self._start_flow([
            FlowStep("Person to delete:", "person", choices=names,
                     validate_fn=lambda v: None if v in names else f"Person '{v}' not found"),
        ], done)

    # ── Categories flows ──────────────────────────────────────────────────────

    def _flow_new_category(self) -> None:
        def done(data):
            from categories import _kategorien_laden, _kategorien_speichern
            k = _kategorien_laden()
            name = data["name"]
            if name in k:
                self._log(f"[yellow]Category '{name}' already exists.[/yellow]")
                return
            k[name] = []
            _kategorien_speichern(k)
            self._log(f"[green]Category '{name}' created.[/green]")
            self.query_one("#categories", CategoriesView).refresh_content()

        self._start_flow([
            FlowStep("New category name:", "name",
                     validate_fn=lambda v: None if v.strip() else "Name cannot be empty"),
        ], done)

    def _flow_delete_category(self) -> None:
        from categories import _kategorien_laden
        k = _kategorien_laden()
        if not k:
            self._log("[yellow]No categories.[/yellow]")
            return
        names = list(k.keys())

        def done(data):
            from categories import _kategorien_laden, _kategorien_speichern
            k2 = _kategorien_laden()
            n = data["name"]
            if n not in k2:
                self._log(f"[red]Category '{n}' not found.[/red]")
                return
            del k2[n]
            _kategorien_speichern(k2)
            self._log(f"[green]Category '{n}' deleted.[/green]")
            self.query_one("#categories", CategoriesView).refresh_content()

        self._start_flow([
            FlowStep("Category to delete:", "name", choices=names,
                     validate_fn=lambda v: None if v in names else f"Category '{v}' not found"),
        ], done)

    def _flow_wordpool_add(self) -> None:
        from categories import _kategorien_laden
        k = _kategorien_laden()
        if not k:
            self._log("[yellow]No categories.[/yellow]")
            return
        cat_names = list(k.keys())

        def done(data):
            from categories import _kategorien_laden, _kategorien_speichern
            k2 = _kategorien_laden()
            cat, word = data["cat"], data["word"]
            if cat not in k2:
                self._log(f"[red]Category '{cat}' not found.[/red]")
                return
            if word in k2[cat]:
                self._log(f"[yellow]'{word}' already in word pool.[/yellow]")
                return
            k2[cat].append(word)
            _kategorien_speichern(k2)
            self._log(f"[green]'{word}' added to '{cat}'.[/green]")
            self.query_one("#categories", CategoriesView).refresh_content()

        self._start_flow([
            FlowStep("Category:", "cat", choices=cat_names,
                     validate_fn=lambda v: None if v in cat_names else f"Category '{v}' not found"),
            FlowStep("New keyword:", "word",
                     validate_fn=lambda v: None if v.strip() else "Keyword cannot be empty"),
        ], done)

    def _flow_wordpool_remove(self) -> None:
        from categories import _kategorien_laden
        k = _kategorien_laden()
        if not k:
            self._log("[yellow]No categories.[/yellow]")
            return
        cat_names = list(k.keys())

        def done(data):
            from categories import _kategorien_laden, _kategorien_speichern
            k2 = _kategorien_laden()
            cat, word = data["cat"], data["word"]
            if cat not in k2 or word not in k2[cat]:
                self._log(f"[red]'{word}' not in word pool of '{cat}'.[/red]")
                return
            k2[cat].remove(word)
            _kategorien_speichern(k2)
            self._log(f"[green]'{word}' removed from '{cat}'.[/green]")
            self.query_one("#categories", CategoriesView).refresh_content()

        self._start_flow([
            FlowStep("Category:", "cat", choices=cat_names,
                     validate_fn=lambda v: None if v in cat_names else f"Category '{v}' not found"),
            FlowStep("Keyword to remove:", "word",
                     validate_fn=lambda v: None if v.strip() else "Keyword cannot be empty"),
        ], done)

    def _apply_categories(self) -> None:
        self._log("[#fa7ff6]Applying categories...[/]")

        def worker():
            from categories import update_category_on_database
            from import_csv import DB_PFAD as IMP_DB
            try:
                if not IMP_DB.exists():
                    self.call_from_thread(self._log, "[yellow]Database not found.[/yellow]")
                    return
                with sqlite3.connect(IMP_DB) as conn:
                    count = update_category_on_database(conn)
                self.call_from_thread(
                    self._log, f"[green]Done – {count} transactions updated.[/green]")
                self.call_from_thread(
                    lambda: self.query_one("#history", HistoryView).refresh_content())
            except Exception as e:
                self.call_from_thread(self._log, f"[red]Error: {e}[/red]")

        threading.Thread(target=worker, daemon=True).start()

    # ── Importer flows ────────────────────────────────────────────────────────

    def _flow_import(self) -> None:
        def done(data):
            path_str = data["path"]
            self._log(f"[#fa7ff6]Importing {path_str}...[/]")

            def worker():
                import import_csv as _ic
                _ic.CSV_PFAD = Path(path_str)
                try:
                    _ic.main_import()
                    self.call_from_thread(self._log, "[green]Import complete.[/green]")
                except Exception as e:
                    self.call_from_thread(self._log, f"[red]Import error: {e}[/red]")
                self.call_from_thread(
                    lambda: self.query_one("#history", HistoryView).refresh_content())
                self.call_from_thread(
                    lambda: self.query_one("#importer", ImporterView).refresh_content())

            threading.Thread(target=worker, daemon=True).start()

        self._start_flow([
            FlowStep("CSV file path:", "path",
                     validate_fn=lambda v: None if Path(v).exists() else f"File not found: {v}"),
        ], done)

    def _undo_import(self) -> None:
        try:
            from import_csv import _undo_last_import_logik, DB_PFAD as IMP_DB
            if not IMP_DB.exists():
                self._log("[yellow]Database not found.[/yellow]")
                return
            with sqlite3.connect(IMP_DB) as conn:
                success, msg = _undo_last_import_logik(conn)
            self._log(msg if success else f"[yellow]{msg}[/yellow]")
            self.query_one("#history", HistoryView).refresh_content()
            self.query_one("#importer", ImporterView).refresh_content()
        except Exception as e:
            self._log(f"[red]Error: {e}[/red]")

    def _flow_delete_csv(self) -> None:
        def done(data):
            from import_csv import _delete_csv_logik, DB_PFAD as IMP_DB
            try:
                pfad = Path(data["path"])
                with sqlite3.connect(IMP_DB) as conn:
                    _, msg = _delete_csv_logik(conn, pfad)
                self._log(msg)
                self.query_one("#history", HistoryView).refresh_content()
            except Exception as e:
                self._log(f"[red]Error: {e}[/red]")

        self._start_flow([
            FlowStep("CSV path to remove from DB:", "path",
                     validate_fn=lambda v: None if Path(v).exists() else f"File not found: {v}"),
        ], done)

    def _flow_delete_db(self) -> None:
        def done(data):
            if data["confirm"].lower() != "yes":
                self._log("[dim]Cancelled.[/dim]")
                return
            try:
                from import_csv import DB_PFAD as IMP_DB
                if not IMP_DB.exists():
                    self._log("[yellow]Database not found.[/yellow]")
                    return
                with sqlite3.connect(IMP_DB) as conn:
                    cur = conn.cursor()
                    cur.execute("DELETE FROM transaktionen")
                    cur.execute(
                        "DELETE FROM sqlite_sequence WHERE name='transaktionen'")
                    conn.commit()
                self._log("[green]Database cleared.[/green]")
                self.query_one("#balance", BalanceView).refresh_content()
                self.query_one("#importer", ImporterView).refresh_content()
            except Exception as e:
                self._log(f"[red]Error: {e}[/red]")

        self._start_flow([
            FlowStep("Type 'yes' to confirm deleting the entire database:", "confirm",
                     choices=["yes", "no"]),
        ], done)

    # ── Evaluation flows ──────────────────────────────────────────────────────

    def _flow_eval_comparison(self) -> None:
        import request as req
        all_cats = ["all"] + req.get_all_categories()

        def done(data):
            import request as req
            from evaluation import _last_n_month_keys
            cat = data["cat"]
            n = int(data["n"])
            month_keys = _last_n_month_keys(n + 1)
            current_key = month_keys[-1]
            prev_keys = month_keys[:-1]
            db_data = req.get_expenses_by_month_category(cat if cat != "all" else None)
            current_val = db_data.get(current_key, 0.0)
            prev_vals = [db_data.get(k, 0.0) for k in prev_keys]
            average = sum(prev_vals) / len(prev_vals) if prev_vals else 0.0
            months_data = [(k, db_data.get(k, 0.0)) for k in month_keys]
            panel = UI().draw_comparison_panel(
                cat, months_data, current_key, average, current_val - average)
            self.query_one("#evaluation", EvaluationView).show_result(panel)

        self._start_flow([
            FlowStep("Category (or 'all'):", "cat", choices=all_cats,
                     validate_fn=lambda v: None if v in all_cats else f"Category '{v}' not found"),
            FlowStep("Months to compare (3/6/12):", "n", choices=["3", "6", "12"],
                     validate_fn=lambda v: None if v.isdigit() and int(v) > 0 else "Enter 3, 6, or 12"),
        ], done)

    def _flow_eval_seasonal(self) -> None:
        import request as req
        all_cats = req.get_all_categories()
        if not all_cats:
            self._log("[yellow]No categorized transactions found.[/yellow]")
            return

        def done(data):
            import request as req
            from evaluation import _last_n_month_keys
            cat = data["cat"]
            db_data = req.get_expenses_by_month_category(cat)
            months_data = [(k, db_data.get(k, 0.0)) for k in _last_n_month_keys(12)]
            self.query_one("#evaluation", EvaluationView).show_result(
                UI().draw_seasonal_panel(cat, months_data))

        self._start_flow([
            FlowStep("Category:", "cat", choices=all_cats,
                     validate_fn=lambda v: None if v in all_cats else f"Category '{v}' not found"),
        ], done)

    def _flow_eval_recurring(self) -> None:
        def done(data):
            import request as req
            limit_str = data["limit"]
            amount_limit = None
            if limit_str:
                try:
                    amount_limit = float(limit_str.replace(",", "."))
                except ValueError:
                    self._log("[red]Invalid amount.[/red]")
                    return
            rows = req.get_recurring_transactions(amount_limit)
            if not rows:
                self._log("[yellow]No recurring transactions found.[/yellow]")
                return
            enriched, monthly_total, yearly_total = [], 0.0, 0.0
            for zweck, betrag, anzahl, erstes, letztes in rows:
                try:
                    e_m = int(erstes[3:5]) + int(erstes[6:10]) * 12
                    l_m = int(letztes[3:5]) + int(letztes[6:10]) * 12
                    gap = (l_m - e_m) / max(anzahl - 1, 1)
                except Exception:
                    gap = 0
                rhythm = "monthly" if gap <= 2 else "yearly"
                if rhythm == "monthly":
                    monthly_total += abs(betrag)
                else:
                    yearly_total += abs(betrag)
                enriched.append((zweck, betrag, anzahl, erstes, letztes, rhythm))
            self.query_one("#evaluation", EvaluationView).show_result(
                UI().draw_recurring_panel(enriched, amount_limit, monthly_total, yearly_total))

        self._start_flow([
            FlowStep("Amount limit € (optional, Enter = no limit):", "limit", optional=True),
        ], done)

    def _eval_income(self) -> None:
        from evaluation import _load_eval_config
        import request as req
        from datetime import timedelta
        config = _load_eval_config()
        income_cats = config.get("einkommen_kategorien", [])
        fixed_cats = config.get("fixkosten_kategorien", [])
        if not income_cats:
            self._log("[yellow]No income categories. Use 'settings income'.[/yellow]")
            return
        if not fixed_cats:
            self._log("[yellow]No fixed cost categories. Use 'settings fixed'.[/yellow]")
            return
        now = datetime.now()
        month = f"{now.month:02d}"
        year = str(now.year)
        prev_dt = now.replace(day=1) - timedelta(days=1)
        income_detail = req.get_monthly_income(
            income_cats, month, year, f"{prev_dt.month:02d}", str(prev_dt.year))
        fixed_detail = req.get_monthly_fixed_costs(fixed_cats, month, year)
        total_income = sum(income_detail.values())
        total_fixed = sum(fixed_detail.values())
        ratio = (total_fixed / total_income * 100) if total_income > 0 else 0.0
        self.query_one("#evaluation", EvaluationView).show_result(
            UI().draw_income_panel(f"{month}/{year}", income_detail, fixed_detail,
                                   total_income, total_fixed, ratio))

    def _flow_eval_forecast(self) -> None:
        import request as req
        from evaluation import _load_budget
        budget = _load_budget()
        cats_with_budget = [k for k in req.get_all_categories() if k in budget]
        if not cats_with_budget:
            self._log("[yellow]No categories with budget. Use 'set budget' first.[/yellow]")
            return

        def done(data):
            import calendar, request as req
            from evaluation import _load_budget
            budget = _load_budget()
            cat_raw = data["cat"]
            month_raw = data["month"]
            now = datetime.now()
            if not month_raw:
                tm, ty, cd = now.month, now.year, now.day
            else:
                try:
                    parts = month_raw.split("/")
                    tm, ty = int(parts[0]), int(parts[1])
                    if not (1 <= tm <= 12):
                        raise ValueError
                    cd = (calendar.monthrange(ty, tm)[1]
                          if (ty, tm) < (now.year, now.month) else now.day)
                except (ValueError, IndexError):
                    self._log(f"[red]Invalid month '{month_raw}'. Use MM/YYYY.[/red]")
                    return
            dim = calendar.monthrange(ty, tm)[1]
            ms, ys = f"{tm:02d}", str(ty)
            cats_wb = [k for k in req.get_all_categories() if k in budget]
            if not cat_raw or cat_raw.lower() == "all":
                spending = req.get_all_monthly_spending(cats_wb, ms, ys)
                rows = [(cat, budget[cat]["limit"], spending.get(cat, 0.0),
                         (spending.get(cat, 0.0) / cd * dim) if cd > 0 else 0.0,
                         (spending.get(cat, 0.0) / cd * dim) <= budget[cat]["limit"] if cd > 0 else True)
                        for cat in cats_wb]
                panel = UI().draw_forecast_overview(rows, f"{ms}/{ys}")
            else:
                if cat_raw not in budget:
                    self._log(f"[red]No budget for '{cat_raw}'.[/red]")
                    return
                limit = budget[cat_raw]["limit"]
                spent = req.get_monthly_category_spending(cat_raw, ms, ys)
                proj = (spent / cd * dim) if cd > 0 else 0.0
                panel = UI().draw_forecast_single(cat_raw, limit, spent, proj, cd, dim)
            self.query_one("#evaluation", EvaluationView).show_result(panel)

        self._start_flow([
            FlowStep("Category (Enter = all):", "cat",
                     choices=cats_with_budget + ["all"], optional=True),
            FlowStep("Month MM/YYYY (Enter = current):", "month", optional=True),
        ], done)

    def _flow_eval_settings(self, cat_type: str) -> None:
        from evaluation import _load_eval_config
        key = f"{cat_type}_kategorien"
        label = "Income" if cat_type == "einkommen" else "Fixed Costs"
        config = _load_eval_config()
        current = config.get(key, [])
        self._log(f"[cyan]{label}:[/cyan] {', '.join(current) or '–'}  |  add / remove / back")

        def done(data):
            action = data["action"]
            if action == "back":
                self._log("[dim]Back.[/dim]")
            elif action == "add":
                self._flow_eval_settings_add(cat_type)
            elif action == "remove":
                self._flow_eval_settings_remove(cat_type)

        self._start_flow([
            FlowStep(f"Settings {label} (add/remove/back):", "action",
                     choices=["add", "remove", "back"],
                     validate_fn=lambda v: None if v in ("add", "remove", "back") else "Enter add, remove, or back"),
        ], done)

    def _flow_eval_settings_add(self, cat_type: str) -> None:
        from evaluation import _load_eval_config
        from categories import _kategorien_laden
        key = f"{cat_type}_kategorien"
        label = "Income" if cat_type == "einkommen" else "Fixed Costs"
        config = _load_eval_config()
        all_cats = list(_kategorien_laden().keys())
        available = [k for k in all_cats if k not in config.get(key, [])]
        if not available:
            self._log("[yellow]All categories already assigned.[/yellow]")
            return

        def done(data):
            from evaluation import _load_eval_config, _save_eval_config
            conf = _load_eval_config()
            lst = conf.get(f"{cat_type}_kategorien", [])
            cat = data["cat"]
            if cat in lst:
                self._log(f"[yellow]'{cat}' already assigned.[/yellow]")
                return
            lst.append(cat)
            conf[f"{cat_type}_kategorien"] = lst
            _save_eval_config(conf)
            self._log(f"[green]'{cat}' added as {label}.[/green]")

        self._start_flow([
            FlowStep(f"Add category as {label}:", "cat", choices=available,
                     validate_fn=lambda v: None if v in all_cats else f"Category '{v}' not found"),
        ], done)

    def _flow_eval_settings_remove(self, cat_type: str) -> None:
        from evaluation import _load_eval_config
        key = f"{cat_type}_kategorien"
        label = "Income" if cat_type == "einkommen" else "Fixed Costs"
        config = _load_eval_config()
        current = config.get(key, [])
        if not current:
            self._log("[yellow]No categories assigned.[/yellow]")
            return

        def done(data):
            from evaluation import _load_eval_config, _save_eval_config
            conf = _load_eval_config()
            lst = conf.get(f"{cat_type}_kategorien", [])
            cat = data["cat"]
            if cat not in lst:
                self._log(f"[red]'{cat}' not in list.[/red]")
                return
            lst.remove(cat)
            conf[f"{cat_type}_kategorien"] = lst
            _save_eval_config(conf)
            self._log(f"[green]'{cat}' removed from {label}.[/green]")

        self._start_flow([
            FlowStep(f"Remove category from {label}:", "cat", choices=current,
                     validate_fn=lambda v: None if v in current else f"'{v}' not in list"),
        ], done)
