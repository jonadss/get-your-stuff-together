
from ui_toolkit import *
from ui_styles import UI
import request
import calendar
from datetime import timedelta


# ──────────────────────────────────────────────
# PATHS
# ──────────────────────────────────────────────

from _paths import PROJEKT_DIR
EVAL_JSON   = PROJEKT_DIR / "db" / "evaluation.json"
CAT_JSON    = PROJEKT_DIR / "db" / "categories.json"
BUDGET_JSON = PROJEKT_DIR / "db" / "budget.json"


# ──────────────────────────────────────────────
# JSON HELPERS
# ──────────────────────────────────────────────

def _load_categories() -> dict:
    if not CAT_JSON.exists():
        return {}
    try:
        with open(CAT_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _load_budget() -> dict:
    if not BUDGET_JSON.exists():
        return {}
    try:
        with open(BUDGET_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}


def _load_eval_config() -> dict:
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


def _save_eval_config(config: dict) -> None:
    EVAL_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(EVAL_JSON, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)


# ──────────────────────────────────────────────
# PURE HELPERS
# ──────────────────────────────────────────────

def _last_n_month_keys(n: int) -> list:
    now    = datetime.now()
    months = []
    for i in range(n - 1, -1, -1):
        m = now.month - i
        y = now.year
        while m <= 0:
            m += 12
            y -= 1
        months.append(f"{y}-{m:02d}")
    return months


# ──────────────────────────────────────────────
# ANALYSIS 1 – COMPARISON
# ──────────────────────────────────────────────

def _analysis_comparison(ui: UI) -> None:
    all_cats = ["all"] + request.get_all_categories()
    if len(all_cats) == 1:
        ui.draw_header("[yellow]No categorized transactions found.[/yellow]")
        return

    cat_completer = WordCompleter(all_cats, ignore_case=True)
    try:
        cat = prompt("  Category (Tab = suggestions, 'all' = all): ",
                     completer=cat_completer).strip()
    except (KeyboardInterrupt, EOFError):
        return

    if cat not in all_cats:
        ui.draw_header(f"[red]Category '[bold]{cat}[/bold]' not found.[/red]")
        return

    p_completer = WordCompleter(["3", "6", "12"], ignore_case=True)
    try:
        n_raw = prompt("  Comparison period in months (3 / 6 / 12): ",
                       completer=p_completer).strip()
    except (KeyboardInterrupt, EOFError):
        return

    try:
        n = int(n_raw)
        if n <= 0:
            raise ValueError
    except ValueError:
        ui.draw_header(f"[red]Invalid input '[bold]{n_raw}[/bold]'.[/red]")
        return

    data        = request.get_expenses_by_month_category(cat if cat != "all" else None)
    month_keys  = _last_n_month_keys(n + 1)
    current_key = month_keys[-1]
    prev_keys   = month_keys[:-1]

    current_val = data.get(current_key, 0.0)
    prev_vals   = [data.get(k, 0.0) for k in prev_keys]
    average     = sum(prev_vals) / len(prev_vals) if prev_vals else 0.0
    diff        = current_val - average

    months_data = [(k, data.get(k, 0.0)) for k in month_keys]
    panel = ui.draw_comparison_panel(cat, months_data, current_key, average, diff)
    ui.less(panel)


# ──────────────────────────────────────────────
# ANALYSIS 2 – SEASONAL
# ──────────────────────────────────────────────

def _analysis_seasonal(ui: UI) -> None:
    all_cats = request.get_all_categories()
    if not all_cats:
        ui.draw_header("[yellow]No categorized transactions found.[/yellow]")
        return

    cat_completer = WordCompleter(all_cats, ignore_case=True)
    try:
        cat = prompt("  Category (Tab = suggestions): ",
                     completer=cat_completer).strip()
    except (KeyboardInterrupt, EOFError):
        return

    if cat not in all_cats:
        ui.draw_header(f"[red]Category '[bold]{cat}[/bold]' not found.[/red]")
        return

    data        = request.get_expenses_by_month_category(cat)
    month_keys  = _last_n_month_keys(12)
    months_data = [(k, data.get(k, 0.0)) for k in month_keys]
    panel = ui.draw_seasonal_panel(cat, months_data)
    ui.less(panel)


# ──────────────────────────────────────────────
# ANALYSIS 3 – RECURRING (merged abo + wiederkehrend)
# ──────────────────────────────────────────────

def _analysis_recurring(ui: UI) -> None:
    try:
        limit_raw = prompt("  Amount limit (€, Enter = no limit): ").strip()
    except (KeyboardInterrupt, EOFError):
        return

    amount_limit = None
    if limit_raw != "":
        limit_raw = limit_raw.replace(",", ".")
        try:
            amount_limit = float(limit_raw)
        except ValueError:
            ui.draw_header("[red]Invalid input.[/red]")
            return

    rows = request.get_recurring_transactions(amount_limit)
    if not rows:
        if amount_limit is not None:
            ui.draw_header(f"[yellow]No recurring transactions under {amount_limit:.2f} € found.[/yellow]")
        else:
            ui.draw_header("[yellow]No recurring transactions found.[/yellow]")
        return

    enriched       = []
    monthly_total  = 0.0
    yearly_total   = 0.0

    for zweck, betrag, anzahl, erstes, letztes in rows:
        try:
            e_m = int(erstes[3:5]) + int(erstes[6:10]) * 12
            l_m = int(letztes[3:5]) + int(letztes[6:10]) * 12
            month_gap = (l_m - e_m) / max(anzahl - 1, 1)
        except Exception:
            month_gap = 0

        if month_gap <= 2:
            rhythm = "monthly"
            monthly_total += abs(betrag)
        else:
            rhythm = "yearly"
            yearly_total  += abs(betrag)

        enriched.append((zweck, betrag, anzahl, erstes, letztes, rhythm))

    panel = ui.draw_recurring_panel(enriched, amount_limit, monthly_total, yearly_total)
    ui.less(panel)


# ──────────────────────────────────────────────
# ANALYSIS 4 – INCOME
# ──────────────────────────────────────────────

def _analysis_income(ui: UI, config: dict) -> None:
    income_cats = config.get("einkommen_kategorien", [])
    fixed_cats  = config.get("fixkosten_kategorien", [])

    if not income_cats:
        ui.draw_header("[yellow]No income categories configured.\n"
                       "Please assign them under 'settings → income'.[/yellow]")
        return
    if not fixed_cats:
        ui.draw_header("[yellow]No fixed cost categories configured.\n"
                       "Please assign them under 'settings → fixed'.[/yellow]")
        return

    now        = datetime.now()
    month      = f"{now.month:02d}"
    year       = str(now.year)
    prev_dt    = now.replace(day=1) - timedelta(days=1)
    prev_month = f"{prev_dt.month:02d}"
    prev_year  = str(prev_dt.year)

    income_detail = request.get_monthly_income(income_cats, month, year,
                                                prev_month, prev_year)
    fixed_detail  = request.get_monthly_fixed_costs(fixed_cats, month, year)

    total_income = sum(income_detail.values())
    total_fixed  = sum(fixed_detail.values())
    ratio        = (total_fixed / total_income * 100) if total_income > 0 else 0.0

    panel = ui.draw_income_panel(
        f"{month}/{year}", income_detail, fixed_detail,
        total_income, total_fixed, ratio
    )
    ui.less(panel)


# ──────────────────────────────────────────────
# ANALYSIS 5 – FORECAST
# ──────────────────────────────────────────────

def _analysis_forecast(ui: UI) -> None:
    budget   = _load_budget()
    all_cats = request.get_all_categories()

    cats_with_budget = [k for k in all_cats if k in budget]
    if not cats_with_budget:
        ui.draw_header("[yellow]No categories with a budget limit found.\n"
                       "Please set limits under 'budget' first.[/yellow]")
        return

    cat_completer = WordCompleter(cats_with_budget, ignore_case=True)
    try:
        cat_raw = prompt("  Category (Tab = suggestions, Enter = overview all): ",
                         completer=cat_completer).strip()
    except (KeyboardInterrupt, EOFError):
        return

    try:
        month_raw = prompt("  Month (MM/YYYY, Enter = current): ").strip()
    except (KeyboardInterrupt, EOFError):
        return

    now = datetime.now()
    if month_raw == "":
        target_month = now.month
        target_year  = now.year
        current_day  = now.day
    else:
        try:
            parts = month_raw.split("/")
            target_month = int(parts[0])
            target_year  = int(parts[1])
            if not (1 <= target_month <= 12):
                raise ValueError
        except (ValueError, IndexError):
            ui.draw_header(f"[red]Invalid month '[bold]{month_raw}[/bold]'. Use MM/YYYY.[/red]")
            return
        if (target_year, target_month) < (now.year, now.month):
            current_day = calendar.monthrange(target_year, target_month)[1]
        else:
            current_day = now.day

    days_in_month = calendar.monthrange(target_year, target_month)[1]
    month_str     = f"{target_month:02d}"
    year_str      = str(target_year)
    month_label   = f"{month_str}/{year_str}"

    if cat_raw == "" or cat_raw.lower() == "all":
        spending = request.get_all_monthly_spending(cats_with_budget, month_str, year_str)
        rows = []
        for cat in cats_with_budget:
            limit      = budget[cat]["limit"]
            spent      = spending.get(cat, 0.0)
            projection = (spent / current_day * days_in_month) if current_day > 0 else 0.0
            on_track   = projection <= limit
            rows.append((cat, limit, spent, projection, on_track))
        panel = ui.draw_forecast_overview(rows, month_label)
        ui.less(panel)
    else:
        if cat_raw not in budget:
            ui.draw_header(f"[red]No budget for '[bold]{cat_raw}[/bold]' found.[/red]")
            return
        limit      = budget[cat_raw]["limit"]
        spent      = request.get_monthly_category_spending(cat_raw, month_str, year_str)
        projection = (spent / current_day * days_in_month) if current_day > 0 else 0.0
        panel = ui.draw_forecast_single(cat_raw, limit, spent, projection,
                                         current_day, days_in_month)
        ui.less(panel)


# ──────────────────────────────────────────────
# SETTINGS
# ──────────────────────────────────────────────

def _settings_assign_categories(ui: UI, config: dict, cat_type: str) -> dict:
    key      = f"{cat_type}_kategorien"
    all_cats = list(_load_categories().keys())
    current  = config.get(key, [])
    label    = "Income" if cat_type == "einkommen" else "Fixed Costs"

    ui.draw_category_assign_panel(label, current)
    commands = ["add", "remove", "back", "exit"]

    while True:
        completer = WordCompleter(commands, ignore_case=True)
        try:
            raw = prompt(f"  settings ({cat_type}): ",
                         completer=completer).strip().lower()
        except (KeyboardInterrupt, EOFError):
            return config

        if raw in ("back", ""):
            return config
        elif raw == "exit":
            ui.draw_exit_panel()
        elif raw == "add":
            cat_completer = WordCompleter(
                [k for k in all_cats if k not in current], ignore_case=True
            )
            try:
                cat = prompt("  Add category: ", completer=cat_completer).strip()
            except (KeyboardInterrupt, EOFError):
                continue
            if cat not in all_cats:
                ui.draw_header(f"[red]Category '[bold]{cat}[/bold]' not found.[/red]")
                continue
            if cat in current:
                ui.draw_header(f"[yellow]'{cat}' is already in the list.[/yellow]")
                continue
            current.append(cat)
            config[key] = current
            _save_eval_config(config)
            ui.draw_header(f"[green]'{cat}' added as {label}.[/green]")
        elif raw == "remove":
            if not current:
                ui.draw_header("[yellow]List is empty.[/yellow]")
                continue
            rm_completer = WordCompleter(current, ignore_case=True)
            try:
                cat = prompt("  Remove category: ", completer=rm_completer).strip()
            except (KeyboardInterrupt, EOFError):
                continue
            if cat not in current:
                ui.draw_header(f"[red]'{cat}' not in the list.[/red]")
                continue
            current.remove(cat)
            config[key] = current
            _save_eval_config(config)
            ui.draw_header(f"[green]'{cat}' removed.[/green]")
        else:
            console.print(f"[red]Unknown command:[/red] {raw}")


def _settings_menu(ui: UI, config: dict) -> None:
    commands = ["income", "fixed", "back", "exit"]
    while True:
        ui.draw_settings_eval_panel(
            config.get("einkommen_kategorien", []),
            config.get("fixkosten_kategorien", []),
        )
        completer = WordCompleter(commands, ignore_case=True)
        try:
            raw = prompt("  settings: ", completer=completer).strip().lower()
        except (KeyboardInterrupt, EOFError):
            ui.draw_exit_panel()

        if raw in ("back", ""):
            return
        elif raw == "exit":
            ui.draw_exit_panel()
        elif raw == "income":
            config = _settings_assign_categories(ui, config, "einkommen")
        elif raw == "fixed":
            config = _settings_assign_categories(ui, config, "fixkosten")
        else:
            console.print(f"[red]Unknown command:[/red] {raw}")


# ──────────────────────────────────────────────
# MAIN LOOP
# ──────────────────────────────────────────────

def manage_evaluation() -> None:
    ui     = UI()
    config = _load_eval_config()

    commands = [
        "comparison", "seasonal", "recurring",
        "income", "forecast", "settings", "help", "back", "exit",
    ]
    
    ui.draw_eval_menu()

    while True:
        
        completer = WordCompleter(commands, ignore_case=True)

        try:
            user_input = prompt(
                "evaluation -- enter command: ",
                completer=completer,
            ).strip().lower()
        except (KeyboardInterrupt, EOFError):
            return

        if user_input == "":
            continue
        elif user_input == "back":
            return
        elif user_input == "exit":
            ui.draw_exit_panel()
        elif user_input == "help":
            ui.draw_header(
                "[bold #fa7ff6]comparison[/]   – Expenses vs. avg of last N months\n"
                "[bold #fa7ff6]seasonal[/]     – Seasonal trend over 12 months\n"
                "[bold #fa7ff6]recurring[/]    – Recurring transactions (optional amount limit)\n"
                "[bold #fa7ff6]income[/]       – Fixed costs as % of income (50% check)\n"
                "[bold #fa7ff6]forecast[/]     – Budget projection for a given month\n\n"
                "[bold #fa7ff6]settings[/]     – Configure income & fixed cost categories\n"
                "[bold #fa7ff6]back[/]         – Back to main menu"
            )
        elif user_input == "comparison":
            _analysis_comparison(ui)
            ui.draw_eval_menu()
        elif user_input == "seasonal":
            _analysis_seasonal(ui)
            ui.draw_eval_menu()
        elif user_input == "recurring":
            _analysis_recurring(ui)
            ui.draw_eval_menu()
        elif user_input == "income":
            config = _load_eval_config()
            _analysis_income(ui, config)
            ui.draw_eval_menu()
        elif user_input == "forecast":
            _analysis_forecast(ui)
            ui.draw_eval_menu()
        elif user_input == "settings":
            _settings_menu(ui, config)
            config = _load_eval_config()
            ui.draw_eval_menu()
        else:
            console.print(f"[red]Unknown command:[/red] {user_input}")
