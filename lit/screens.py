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

def show_log_screen(prefill_title=None):
    clear_and_header("log a film")
    console.print(" [dim]Fill in what you know. Press Enter to skip optional fields.[/dim]")
    console.print()


#lets collect some data
    while True:
        if prefill_title:
            console.print(f" [bold red]›[/bold red] Title[dim(pre-filled from watchlist)[/dim]]")
            console.print(f"    [white]{prefill_title}[/white] ")
            console.print("    [dim] press enter to keep, or type to change[/dim]")
            override = input("   ").strip()
            title = override if override else prefill_title
            break
        else:
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
    console.print(" [bold red][E][/bold red][dim] edit[/dim]")
    console.print(" [bold red][D][/bold red] [dim] delete[/dim]")
    console.print(" [bold red][Q][/bold red][dim] back to diary[/dim]")
    console.print()

    while True:
        key = readchar.readkey().lower()

        if key =="q":
            return "diary"
        elif key == "d":
            console.print()
            console.print(f" [dim]delete'[/dim][white] {entry.get('title')}[/white][dim]'? (y/n)[/dim]")
            confirm = readchar.readkey().lower()

            if confirm == "y":
                storage.delete_entry(entry["id"])
                console.print()
                console.print(" [bold red] ✓ [/bold red] [dim]entry deleted.[/dim]")
                console.print()
                console.print(" [dim] press any key to return to diary[/dim]")
                readchar.readkey()
                return "diary"
            else:
                console.print(" [dim]cancelled.[/dim]")
                console.print()

        elif key == "e":
            return show_edit_screen(entry)
        

#edit screen
def show_edit_screen(entry):
    clear_and_header("edit entry")

    console.print()
    console.print(" [dim] Press Enter to keep the current value. Type to replace it.[/dim]")
    console.print()

    def edit_prompt(label, current):
        console.print(f" [bold red]›[/bold red]{label}")
        console.print(f" [dim]current: {current if current else '-'}[/dim]")
        new_value = input("    new: ").strip()
        console.print()

        return new_value if new_value else current

    new_title = edit_prompt("Title", entry.get("Title"))
    new_director = edit_prompt("Director", entry.get("director", ""))


    #some validation
    while True:
        console.print(f" [bold red]›[/bold red] Year")
        console.print(f"     [dim]current: {entry.get('year') or '-'}[/dim]")
        new_year_raw = input("     new: ").strip()
        console.print()

        if new_year_raw == "":
            new_year = entry.get("year")
            break
        if new_year_raw.isdigit():
            y = int(new_year_raw)
            if 1888<= y <= 2030:
                new_year = y
                break
        console.print("  [dim red] Invalid year. Try again.[/dim red]")
        console.print()

    while True:
        console.print(f"   [bold red]›[/bold red] Rating (1-10)")
        console.print(f"   [dim]current: {entry.get('rating')or '-'}[/dim]")
        new_rating_raw = input("     new: ").strip()
        console.print()

        if new_rating_raw =="":
            new_rating = entry.get("rating")
            break
        if new_rating_raw.isdigit():
            r = int(new_rating_raw)
            if 1 <= r <= 10:
                new_rating = r
                break

        console.print(" [dim red] Please enter 1-10.[/dim red]")
        console.print()
    
    new_review = edit_prompt("Review", entry.get("review", ""))

#confirmation
    console.print(Rule(style="dim red"))
    console.print()
    console.print(" [bold white] Save changes[/bold white]")
    console.print()

    fields = [
        ("Title", new_title),
        ("Director", new_director or "-"),
        ("Year", str(new_year) if new_year else "-"),
        ("Rating", f"{new_rating}/10" if new_rating else "-"),
        ("Review", new_review or "-")
    ]
    for label , value in fields:
        console.print(f" [dim]{label:<12}[/dim][white]{value}[/white]")

    console.print()
    console.print(" [bold red]>[/bold red] Confirm[dim](y/n)[/dim]")
    confirm = readchar.readkey().lower()

    if confirm =="y":
        storage.update_entry(
            entry["id"],
            title = new_title,
            director = new_director,
            year = new_year,
            rating = new_rating,
            review = new_review
        )
        console.print()
        console.print(" [bold red]✓[/bold red] [dim]changes saved.[/dim]")
        console.print()
        console.print("  [dim]press any key to return to diary[/dim]")
        readchar.readkey()

    return "diary"

#stats screen

def show_stats_screen():
    from collections import Counter

    clear_and_header("stats")

    entries = storage.get_all_entries()

    if not entries:
        console.print()
        console.print(" [dim]No films logged yet. Nothing to compute.[/dim]")
        console.print()
        console.print(" [dim] press any key to go back[/dim]")
        readchar.readkey()
        return "menu"
    

# some deets computing
    total = len(entries)
    rated = [e for e in entries if e.get("rating") is not None]
    avg_rating = round(sum(e["rating"] for e in rated)/ len(rated), 1) if rated else None

    top_entry = max(rated, key=lambda e: e["rating"]) if rated else None
    low_entry = min(rated, key=lambda e: e["rating"]) if rated else None

    directors = [e["director"] for e in entries if e.get("director", "").strip()]
    fav_director = Counter(directors).most_common(1)[0] if directors else None


    months = []
    for e in entries:
        try:
            from datetime import datetime
            d = datetime.strptime(e["watched_date"], "%Y-%m-%d")
            months.append(d.strftime("%B %Y"))
        
        except Exception:
            pass

    top_month = Counter(months).most_common(1)[0] if months else None

    rating_counts = Counter(e["rating"] for e in rated)


    console.print()

    console.print(f" [bold red]›[/bold red] [white]Total logged[/white] [yellow]{total}[/yellow] film{'s' if total != 1 else ''}")
    console.print()

    if avg_rating:
        console.print(f"  [bold red]›[/bold red] [white]Highest rated[/white] [yellow]{avg_rating}[/yellow]/10")
        console.print()
    
    if top_entry:
        console.print(f" [bold red]›[/bold red] [white]Highest rated[/white] {top_entry['title']} [dim]({top_entry['rating']}/10[/dim])")
        console.print()

    if low_entry and low_entry["id"] != top_entry["id"]:
        console.print(f" [bold red]›[/bold red] [white]Lowest rated[/white] {low_entry['title']} [dim]({low_entry['rating']}/10[/dim])")
        console.print()

    if fav_director:
        name, count = fav_director
        console.print(f" [bold red]›[/bold red] [white]Top director[/white] {name} [dim]{count} film{'s' if count != 1 else ''}[/dim]")
        console.print()

    if rating_counts:
        console.print(Rule(style="dim red"))
        console.print()
        console.print(" [dim]rating distribution[/dim]")
        console.print()

        max_count = max(rating_counts.values())

        for star in range(1,11):
            count = rating_counts.get(star,0)

            bar_length = int( (count / max_count)* 20) if max_count > 0 else 0
            filled = "█" * bar_length
            empty = "░" * (20 - bar_length)


            if count > 0:
                console.print(
                    f" [dim] {star:>2}[/dim]"
                    f"[yellow] {filled}[/yellow][dim]{empty}[/dim] "
                    f"[dim]{count}[/dim]"
                )
            else:
                console.print(
                f"  [dim]{star:>2}  {filled}{empty}  {count}[/dim]"
                )

        console.print()
    console.print(Rule(style="dim red"))
    console.print()
    console.print(" [dim]press any key to go back[/dim]")
    readchar.readkey()
    return "menu"

def show_watchlist_screen():

    clear_and_header("watchlist")
    items = storage.get_watchlist()

    if not items:
        console.print()
        console.print(" [dim] Your watchlist is empty.[/dim]")
        console.print()
        console.print("  [bold red][A][/bold red][dim] add a film[/dim]")
        console.print(" [bold red][Q][bold red][dim] back to menu[/dim]")
        console.print()

        while True:
            key = readchar.readkey().lower()
            if key == "q":
                return "menu", None
            elif key == "a":
                show_add_to_watchlist()
                return show_watchlist_screen()
    console.print()
    console.print(f"  [dim] {len(items)} film{'s' if len(items) != 1 else ''} to watch[/dim]")
    console.print()

    for i, item in enumerate(items, start = 1):
        row = Text()
        row.append(f"  {i:02d} ", style ="dim white")
        row.append(f"{item['title']:<38}", style="bold white")

        if item.get("year"):
            row.append(f"{item['year']}", style ="dim white")

        console.print(row)

        meta_parts = []
        if item.get("director"):
            meta_parts.append(item["director"])
        if item.get("note"):
            meta_parts.append(f'" {item["note"]}"')
        if meta_parts:
            console.print(f"        [dim]{' · '.join(meta_parts)}[/dim]")

        console.print()
    
    console.print(Rule(style="dim red"))
    console.print()
    console.print(" [bold red][A][/bold red][dim] add a film[/dim]")
    console.print(" [bold red] [1-9][/bold red][dim] mark as watched[/dim]")
    console.print(" [bold red] [R] [/bold red][dim] remove a film[/dim]")
    console.print(" [bold red][Q][/bold red][dim] back to menu[/dim]")
    console.print()

    while True:
        key = readchar.readkey().lower()

        if key == "q":
            return "menu", None
        
        elif  key == "a":
            show_add_to_watchlist()
            return show_watchlist_screen()
        
        elif key == "r":
            show_add_to_watchlist(items)
            return show_watchlist_screen()
        
        elif key.isdigit():
            index = int(key)
            if 1 <= index <= len(items):
                item = item[index - 1]


                console.print()
                console.print(f"   [dim]mark '[/dim][white]{item['title']} [/white][dim]' as watched? (y/n)[/dim]")
                confirm = readchar.readkey().lower()

                if confirm == "y":

                    storage.remove_from_watchlist(item["id"])
                    console.print()
                    console.print(f" [bold red]✓[/bold red] [dim] moved to log screen - fill in your thoughts.[/dim]")
                    console.print()
                    console.print(" [dim] press any key to continue[/dim]")
                    readchar.readkey()

                    return "log", item["title"]
                

def show_add_to_watchlist():

    clear_and_header("add to watchlist")
    console.print()
    console.print(" [dim]Add a film you want to watch.[/dim]")
    console.print()

    while True:
        title = prompt("Title")
        if title:
            break
        console.print("   [dim red] Title is required.[/dim red]")
        console.print()
        console.print("   [dim] press any key to continue[/dim]")
        readchar.readkey()


def show_remove_from_watchlist(items):
    console.print()
    console.print(" [dim]Enter the number of the film to remove (or Q to cancel):[/dim]")
    console.print()

    while True:
        key = readchar.readkey().lower()

        if key == "q":
            return
        
        if key.isdigit():
            index = int(key)
            if 1 <= index <= len(items):
                item = items[index - 1]
                console.print(f"  [dim] remove '[/dim][white]{item['title']} [/white][dim]'? (y/n)[/dim]")
                confirm = readchar.readkey.lower()

                if confirm =="y":
                    storage.remove_from_watchlist(item["id"])
                    console.print()
                    console.print(f"  [bold red]✓[/bold red] [dim]removed.[/dim]")
                    console.print()
                    console.print("  [dim]press any key to continue[/dim]")
                    readchar.readkey()
                return
            
def show_search_screen():
    clear_and_header("search")

    console.print()
    console.print(" [bold red]›[/bold red] Search title or director [dim](or press Enter to skip)[/dim]")
    query = input("   ").strip()
    console.print()


    min_rating = None
    console.print(" [bold red] ›[/bold red] Minimum rating [dim](1-10, or press Enter to skip)[/dim]")
    min_raw = input("    ").strip()
    console.print()
    if min_raw.isdigit() and 1 <= int(min_raw) <= 10:
        min_rating = int(min_raw)


    if not query and min_rating is None:
        results = storage.get_all_entries()

    else:
        results = storage.search_entries(query=query, min_rating=min_rating)

    console.clear()
    clear_and_header("search results")
    console.print()

    if query and min_rating:
        console.print(f"  [dim]'{query}'  ·  rated {min_rating}+[/dim]")
    elif query:
        console.print(f"  [dim]'{query}'[/dim]")
    elif min_rating:
        console.print(f"  [dim]rated {min_rating} or above[/dim]")
    else:
        console.print(f"  [dim]all films[/dim]")

    console.print()