from datetime import date
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.rule import Rule
from . import storage
import readchar


console = Console()

def clear_and_header(title_text):
    console.clear()
    header= Text()
    header.append("LIT", style="bold red")
    header.append(f" | {title_text}", style="dim white")
    console.print(Panel(header, border_style="dim red", padding=(0,2)))
    console.print()

def prompt(label,optional=False):
# its a input prompt lol
    tag= " [dim](optional)[/dim]" if optional else ""
    console.print(f" [bold red],[/bold red] {label}{tag}")
    value=input("      ").strip()
    return value

def prompt_rating():
    while True:
        console.print(" [bold red],[/bold red] Rating [dim](1-10, or skip[/dim]")
        value=input("     ").strip()

        if value == "": # if input is empty then js dont add thats it hah
            return None
        
        if value.isdigit():
            rating= int(value)
            if 1<= rating <=10:
                return rating
            
        console.print(" [dim red] Please enter a number between 1 and 10, or press Enter or skip.[/dim red]")
        console.print()

def prompt_year():
    while True:
        console.print(" [bold red],[/bold red] Year [dim])optional)[/dim]")
        value=input("      ").strip()

        if value=="":
            return None
        if value.isdigit():
            year=int(value)
            if 1888 <= year <=date.today().year:
                return year
            
        console.print(f" [dim red] Please enter a valid year (1888-{date.today().year}).[/dim red]")
        console.print()

def show_log_screen():
    clear_and_header("log a film")
    console.print(" [dim]Fill in what you know. Press Enter to skip optional fields.[/dim]")
    console.print()


#lets collect some data
    while True:
        title= prompt("Title")
        if title:
            break
        console.print(" [dim red] Title is required.[/dim red]")
        console.print()

    director = prompt("Director", optional=True)
    year = prompt_year()
    rating = prompt_rating()
    
    console.print(" [bold red]›[/bold red] Review [dim](optional) - press Enter twice when done)[/dim]")
    console.print(" [dim] for a single line review just type and hit enter)[/dim]")
    review= input("       ").strip()

# confirming ig?
    console.print()
    console.print(Rule(style="dim red"))
    console.print()
    console.print("[bold white] Ready to save:[/bold white]")
    console.print()

    fields= [
        ("Title", title),
        ("Director", director or "-"),
        ("Year", str(year) if year else "-"),
        ("Rating", f"{rating}/10" if rating else "-"),
        ("Review", review or "-")
    ]

    for label, value in fields:
        console.print(f" [dim] {label:<12} [/dim][white]{value}[/white]")

    console.print()
    console.print(Rule(style="dim red"))
    console.print()

# save the entry or cancel
    console.print(" [bold red]›[/bold red] Save? [dim](y/n)[/dim]")
    confirm= input("    ").strip().lower()

    if confirm =="y":
        entry = storage.create_entry(
            title=title,
            director=director,
            year=year,
            rating=rating,
            review=review
        )
        console.print()
        console.print(f" [bold red] Done[/bold red] [white]'{entry['title']}' [/white] [dim]saved.[/dim]")
        console.print()
        console.print(" [dim]press any key to return to menu[/dim]")
        readchar.readkey()

    else:
        console.print()
        console.print(" [dim]cancelled. Nothing was saved :( [/dim])")
        console.print()
        console.print(" [dim]press Enter to return to menu[/dim]")
        readchar.readkey()

    return "menu"

def render_stars(rating):

    if rating is None:
        return "[dim]------------[/dim]"
    
    filled = "*" * rating
    empty = "O" (10-rating)
    return f"[yellow]{filled}[/yellow][dim]{empty}[/dim]"

def format_date(iso_date_string):
    try:
        from datetime import datetime
        d = datetime.strptime(iso_date_string, "%Y-%m-%d")
        return d.strftime(" %d %b %Y")
    except Exception:
        return iso_date_string
    
def render_entry_row(index, entry):
    row = Text()

    row.append(f"{index:02d} ", style="dim white")

    title = entry.get("title", "unknown")
    row.append(f"{title:<38}", style="bold white")

    rating = entry.get("rating")
    if rating:
        filled = "*" * rating
        empty = "O" * (10 - rating)
        row.append(filled, style = "yellow")
        row.append(empty, style="dim white")
    else:
        row.append("-----------", style = "dim white")

    date_str = format_date(entry.get("watched_date", " "))
    row.append(f"    {date_str}", style="dim white")

    director = entry.get("director", "")
    year = entry.get("year")

    meta_parts = [p for p in [director , str(year) if year else ""]if p]
    meta = "  ·  ".join(meta_parts) if meta_parts else ""

    if meta:
        row.append(f"\n     [dim] {meta} [/dim]")
        return row

# diary screen
def show_diary_screen():
    clear_and_header("diary")
    entries = storage.get_all_entries()

    if not entries:
        console.print()
        console.print("  [dim]No films logged yet.[/dim]")
        console.print()
        console.print(" [dim] Press [/dim][bold red]L[/bold red][dim] from the menu to log your first film. [/dim]")
        console.print()
        console.print(" [dim]press any key to go back[/dim]")
        readchar.readkey()
        return "menu", None
    
    console.print()
    console.print(f" [dim] {len(entries)} film{'s' if len(entries) != 1 else ''} logged[/dim]")
    console.print()

    for i, entry in enumerate(entries, start=1):
        row = render_entry_row(i,entry)
        console.print(row)
        console.print()

    console.print(Rule(style="dim red"))
    console.print(" [dim] press [/dim] [bold red]Q[/bold red][dim] to go back[/dim]")
    console.print()

    while True:
        key = readchar.readkey().lower()

        if key =="q":
            return "menu", None
        
        if key.isdigit():
            index = int(key)
            if 1 <= index <= len(entries):
                entry = entries[index -1]
                return "detail", entry
            
def show_detail_screen(entry):
    if not entry:
        return "menu"
    clear_and_header("entry detail")
    console.print()

    title_text = Text()
    title_text.append(entry.get("title", "Unknown"), style="bold white")
    console.print(f"  ", end = "")
    console.print(title_text)

    director = entry.get("director", "")
    year = entry.get("year")
    meta_parts = [p for p in [director, str(year), str(year) if year else ""]if p]
    meta = "  ·  ".join(meta_parts) if meta_parts else ""
    if meta:
        console.print(f" [dim] {meta}[/dim]")

    console.print()

    rating = entry.get("rating")
    if rating:
        filled = "*" * rating
        empty = "O" * (10 - rating)
        console.print(f" [yellow] {filled}[/yellow][dim white] {empty}[/dim white] [dim] {rating}/10[/dim]")
    else:
        console.print(" [dim]no rating[/dim]")
    
    console.print()
    console.print(Rule(style="dim red"))
    console.print()

    review = entry.get("review", "").strip()
    if review:
        console.print(" [dim red]review [/dim red]")
        console.print()
        console.print(f" [white]{review}[/white]")
    else:
        console.print(" [dim]no review written.[/dim]")

    console.print()
    console.print(Rule(style="dim red"))
    console.print()


    watched = format_date(entry.get("watched_date", ""))
    created = entry.get("created_at", "")[:10]
    entry_id = entry.get("id", "")
    console.print(f" [dim] watched {watched}[/dim]")
    console.print(f" [dim]logged {created}[/dim]")
    console.print(f" [dim] id{entry_id}[/dim]")

    console.print()
    console.print(Rule(style="dim red"))
    console.print()

# some random ahh actions

    console.print(" [bold red][Q][/bold red][dim] back to diary[/dim]")
    console.print()

    while True:
        key = readchar.readkey().lower()
        if key =="q":
            return "diary"