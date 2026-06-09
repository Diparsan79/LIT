from datetime import date
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.rule import Rule
from rich.theme import Theme
from . import storage
import readchar
import os
from . import tmdb


custom_theme = Theme({
    "header": "bold white on #1e1e2e",
    "dim": "dim #888888",
    "prompt": "bold #ff79c6",
    "info": "dim #6272a4",
    "error": "bold red",
})
console = Console(theme=custom_theme)

def rich_safe(text: str):
    return text.replace("[", "(").replace("]",")")

def clear_and_header(title_text):
    console.clear()
    header= Text()
    header.append("LIT", style="bold red")
    header.append(f" | {title_text}", style="dim white")
    console.print(Panel(header, border_style="dim red", padding=(0,2)))
    console.print()

def prompt(label,optional=False):
# input prompt lol
    tag= " [dim](optional)[/dim]" if optional else ""
    console.print(f" [bold red],[/bold red] {label}{tag}")
    value=input("      ").strip()
    return value

def prompt_rating():

    while True:
        value = input(
            "Rating (0-10, blank to skip):"
        ).strip()

        if value =="":
            return None
        
        try:
            rating = float(value)

            if 0 <= rating <= 10:
                return rating
        except ValueError:
            pass

        console.print(
            "[red]Please enter a number between 0 and 10.[/red]"
        )

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

def multiliner_input(prompt_text=""):
    print(prompt_text)
    print("(Press ENTER twice to finish)")


    lines = []
    while True:
        line = input()
        if line.strip() == "":
            break
        lines.append(line)
    return "\n".join(lines)

def show_log_screen(prefill_title=None):
    clear_and_header("log a film")
    console.print(" [dim]Fill in what you know. Press Enter to skip optional fields.[/dim]")
    console.print()


#lets collect some data
    while True:
        if prefill_title:
            console.print(
                "[bold red]›[/bold red] Title [dim](pre-filled from watchlist if available)[/dim]"
            )
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
    tmdb_data = None

    poster_path = ""
    if TMDB_API_KEY := os.getenv("TMDB_API_KEY", ""):
        console.print()
        console.print(" [dim]searching TMDB...[/dim]")

        results = tmdb.search_film(title)

        if results:
            console.clear()
            clear_and_header("log a film")
            console.print()
            console.print(f" [dim]TMDB results for '[/dim][white]{title}[/white][dim]':[/dim]")
            console.print()

            for i,r in enumerate(results, start=1):
                year = r.get("release_date", "")[:4] or "-"
                console.print(
                    f" [bold red]{i}[/bold red] "
                    f"[white]{r['title']}[/white] "
                    f"[dim]{year}[/dim]"
                )
            console.print()
            director = ""
            year = None
            tags = []
            poster_path = ""
            console.print(f" [bold red]0[/bold red] [dim]none of these - enter manually[/dim]")
            console.print()
            console.print(" [dim]pick a result:[/dim]")

            while True:
                key = readchar.readkey()
                if key =="0":
                    break
                if key.isdigit():
                    idx = int(key)
                    if 1 <= idx <= len(results):

                        console.print()
                        console.print(" [dim]fetching details...[/dim]")
                        tmdb_data = tmdb.get_film_details(results[idx - 1]["id"])
                        if tmdb_data:
                            title = tmdb_data["title"]
                            director = tmdb_data["director"]
                            year = tmdb_data["year"]
                            tags = tmdb_data["tags"]
                            poster_path = tmdb_data.get("poster_path", "")

                            console.print()
                            console.print(" [bold red]✓[/bold red] [dim]details fetched from TMDB[/dim]")
                            console.print()
                            console.print(f" [dim]Title [/dim][white]{title}[/white]")
                            console.print(f" [dim]Director [/dim][white]{director}[/white]")
                            console.print(f" [dim]Tags [/dim][white]{','.join(tags)}[/white]")
                            console.print()
                            console.print(" [dim]press Enter to continue --- or type to override any field[/dim]")
                            input()
                        break
    if not tmdb_data:
        director = prompt("Director", optional=True)
        year = prompt_year()
    rating = prompt_rating()
    
    console.print(" [bold red]›[/bold red] Review [dim](optional) - press Enter twice when done)[/dim]")
    console.print(" [dim] for a single line review just type and hit enter)[/dim]")
    review = multiliner_input("Write review:")

    if not tmdb_data:
        console.print(" [bold red]›[/bold red] Tags [dim](optional - comma separated)[/dim]")
        tags_raw=input(" ").strip()
        tags = [t.strip().lower() for t in tags_raw.split(",") if t.strip()]
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
        ("Review", review or "-"),
        ("Tags", ",".join(tags) if tags else "-")
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

        previous_watches = storage.get_all_entries_by_title(title)
        entry = storage.create_entry(
            title=title,
            director=director,
            year=year,
            rating=rating,
            review=review,
            tags=tags,
            poster_path=poster_path
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
    if previous_watches:
        count = len(previous_watches)
        console.print()
        console.print(f"  [bold red]![/bold red] [white]You've logged this film {count} time{'s' if count != 1 else ''} before.[/white]")
        console.print()

        for i, prev in enumerate(previous_watches, start = 1):
            rating_str = f"{prev['rating']}/10" if prev.get('rating') else "unrated"
            date_str = format_date(prev.get("watched_date", ""))
            console.print(f"    [dim]watch {i}   ·  {date_str}   ·  {rating_str}[/dim]")

        console.print()
        console.print("  [dim]Logging as a new watch. Your previous entries are kept.[/dim]")
        console.print()

    return "menu"

def render_stars(rating: int | None) -> str:
    """Return a visual star rating or placeholder if None."""
    if rating is None:
        return "[dim]------------[/dim]"
    rating = int(rating)
    filled = "*" * rating
    empty = "o" * (10 - rating)
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

    raw_rating = entry.get("rating")
    try:
        rating = int(float(raw_rating)) if raw_rating is not None else 0
    except (ValueError, TypeError):
        rating = 0

    if rating:
        filled = "*" * (rating)
        empty = "o" * (10 - rating)
        row.append(filled, style = "yellow")
        row.append(empty, style="dim white")
    else:
        row.append("-----------", style = "dim white")

    date_str = format_date(entry.get("watched_date", " "))
    row.append(f"    {date_str}", style="dim white")

    director = entry.get("director", "")
    year = entry.get("year")

    meta_parts = [p for p in [director, str(year) if year else ""] if p]
    meta = "  ·  ".join(meta_parts) if meta_parts else ""

    if meta:
        row.append(f"\n     [dim] {meta} [/dim]")
    
    return row

# diary screen
def show_diary_screen():

    entries = storage.get_all_entries()

    if not entries:
        clear_and_header("diary")

        console.print()
        console.print(" [dim]No films logged yet.[/dim]")
        console.print()
        console.print(
            " [dim]Press [/dim] [bold red]L[/bold red] [dim] from the menu to log your first film.[/dim]"
        )
        console.print()
        console.print(
            " [dim]Press any key to go back[/dim]"
        )

        readchar.readkey()

        return "menu", None
    page = 0
    page_size = 10

    while True:
        clear_and_header("diary")

        total_pages = (
            len(entries) + page_size - 1
        ) // page_size

        start = page * page_size
        end = start + page_size

        visible_entries = entries[start:end]

        console.print()
        console.print(
            f" [dim]{len(entries)} films logged[/dim]"
        )

        console.print(
            f" [dim]Page {page + 1}/{total_pages}[/dim]"
        )

        console.print()
        start_number = start + 1

        for i, entry in enumerate(
            visible_entries,
            start=start_number
        ):
            row= render_entry_row(i, entry)
            console.print(row)
            console.print()

        console.print(
            Rule(style="dim red")
        )

        console.print(
            " [bold red]N[/bold red] Next Page"
        )

        console.print(
            " [bold red]P[/bold red] Previous Page"
        )

        console.print(
            " [bold red]Q[/bold red] Back"
        )
        console.print()

        choice = input(
            "Select Film number, N/P, or Q: "
        ).strip().lower()

        if choice =="q":
            return "menu", None
        elif choice =="n":
            
            if page < total_pages - 1:
                page+=1
        elif choice =="p":
            
            if page > 0:
                page -= 1

        elif choice.isdigit():
            index = int(choice)
            if 1 <= index <= len(entries):

                entry = entries[index - 1]

                return "detail", entry
                     
def show_detail_screen(entry):
    if not entry:
        return "menu"
    clear_and_header("entry detail")
    console.print()
    poster_path = entry.get("poster_path", "")

    if poster_path:
        console.print("Poster unavailable", style="dim")

    title_text = Text()
    title_text.append(entry.get("title", "Unknown"), style="bold white")
    console.print(f"  ", end = "")
    console.print(title_text)

    director = entry.get("director", "")
    year = entry.get("year")
    meta_parts = [p for p in [director, str(year) if year else ""]if p]
    meta = " · ".join(meta_parts) if meta_parts else ""
    if meta:
        console.print(f" [dim]{meta}[/dim]")

    console.print()

    all_watches = storage.get_all_entries_by_title(entry.get("title", ""))

    if len(all_watches) > 1:
        console.print()
        console.print(f"  [dim]watch hiustory  ·  {len(all_watches)} times[/dim]")
        console.print()

        for i, watch in enumerate(all_watches, start = 1):
            is_current = watch["id"] == entry["id"]

            rating_str = f"{watch['rating']}/10" if watch.get("rating") else "-"
            date_str = format_date(watch.get("watched_date", ""))

            if is_current:
                console.print(
                    f" [bold red]->[/bold red] "
                    f"[white] watch {i}[/white]"
                    f"[dim] {date_str}[/dim]"
                    f"[yellow]{rating_str}[/yellow]"
                    f"[dim](this entry)[/dim]"
                )
            else:
                console.print(
                    f"    [dim]watch {i}  ·  {date_str}  ·  {rating_str}[/dim] "
                )
        rated_watches = [w for w in all_watches if w.get("rating")]
        if len(rated_watches) > 1:
            first = rated_watches[0]["rating"]
            last = rated_watches[-1]["rating"]
            diff = last - first

            if diff > 0:
                arc = f"[green]+ {diff} since first watch[/green]"
            elif diff < 0:
                arc = f"[red]{diff} since first watch[/red]"
            else:
                arc = "[dim]No rating change[/dim]"

            console.print()
            console.print(f"   {arc}")

        console.print()
        console.print(Rule(style="dim red"))

    raw_rating = entry.get("rating")
    try:
        rating = int(float(raw_rating)) if raw_rating is not None else 0
    except (ValueError, TypeError):
        rating = 0

    if rating:
        filled = "*" * rating
        empty = "o" * (10 - rating)
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

    tags = entry.get("tags", [])
    if tags:
        console.print()
        tag_text = Text()
        tag_text.append(" ")
        for tag in tags:
            tag_text.append(f" {tag}", style="bold red")
            tag_text.append(" ", style = "")
        console.print(tag_text)


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

    new_title = edit_prompt("Title", entry.get("title"))
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

    current_tags = ",".join(str(t) for t in entry.get("tags", []))
    console.print(f" [bold red]›[/bold red] Tags [dim](comma separated)[/dim]")
    tags_raw = input("  new: ").strip()
    console.print()

    if tags_raw:
        new_tags = [t.strip().lower() for t in tags_raw.split(",") if t.strip()]
    else:
        new_tags = entry.get("tags", [])
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
            review = new_review,
            tags = new_tags
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
    rated_entries = [e for e in entries if isinstance(e.get("rating"), (int, float))]
    avg_rating = sum(e["rating"] for e in rated_entries) / len(rated_entries) if rated_entries else 0

    top_entry = max(rated_entries, key=lambda e: e["rating"]) if rated_entries else None
    low_entry = min(rated_entries, key=lambda e: e["rating"]) if rated_entries else None

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

#most rewatched
    from collections import Counter
    title_counts = Counter(
        e.get("title", "").strip().lower()
        for e in entries
    )
    rewatched = [(t,c) for t,c in title_counts.most_common() if c > 1]

    rating_counts = Counter(e["rating"] for e in rated_entries)


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

    if rewatched:
        top_title_lower, top_count = rewatched[0]
        display_title = next(
            (e["title"] for e in entries
            if e["title"].strip().lower() == top_title_lower),
            top_title_lower
        )
        console.print(
            f" [bold red]›[/bold red] "
            f"[white]Most rewatched[/white] "
            f"{display_title} "
            f"[dim]({top_count} watches[/dim])"
        )
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
    tag_counts = storage.get_all_tags()

    if tag_counts:
        console.print(Rule(style="dim red"))
        console.print()
        console.print(" [dim]your tags[/dim]")
        console.print()

        tag_line = Text(" ")
        for tag, count in tag_counts.most_common(10):

            style = "bold red" if count >= 3 else "red" if count >= 2 else "dim red"
            tag_line.append(f" {tag}", style = f"bold black on red")
            tag_line.append(f" x{count} ", style = "dim white")

        console.print(tag_line)
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
        choice = input("Select a command/key:").strip()

        if choice == "q":
            return "menu", None
        
        elif  choice == "a":
            show_add_to_watchlist()
            return show_watchlist_screen()
        
        elif choice == "r":
            show_remove_from_watchlist(items)
            return show_watchlist_screen()
        
        elif choice.isdigit():
            index = int(choice)
            if 1 <= index <= len(items):
                item = items[index - 1]


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
    clear_and_header("Add to Watchlist")

    console.print()
    console.print(" [dim]Add a film you want to watch.[/dim]")
    console.print()

    title = prompt("Title")

    director = prompt(
        "Director",
        optional = True
    )

    year = prompt_year()

    note = prompt(
        "Note",
        optional=True
    )

    result = storage.add_to_watchlist(
        title,
        director,
        year,
        note
    )

    console.print()

    if result:
        console.print(
            " [bold green]✓ Added to watchlist.[/bold green]"
        )
    else:
        console.print(
            " [bold yellow] ! Film already exists in watchlist.[/bold yellow]"
        )
    console.print()
    console.print(
        " [dim]Press any key to continue[/dim]"
    )

    readchar.readkey()
    return "watchlist"


def show_remove_from_watchlist(items):
    console.print()
    console.print(" [dim]Enter the number of the film to remove (or Q to cancel):[/dim]")
    console.print()

    while True:
        choice = input(" enter the movie id:")

        if choice == "q":
            return
        
        if choice.isdigit():
            index = int(choice)
            if 1 <= index <= len(items):
                item = items[index - 1]
                console.print(f"  [dim] remove '[/dim][white]{item['title']} [/white][dim]'? (y/n)[/dim]")
                confirm = readchar.readkey().lower()

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
    console.print(" [bold red]›[/bold red] Minimum rating [dim](1-10, or press Enter to skip)[/dim]")
    min_raw = input("    ").strip()
    console.print()
    if min_raw.isdigit() and 1 <= int(min_raw) <= 10:
        min_rating = int(min_raw)

    console.print(" [bold red]›[/bold red] Filter by tag [dim](or press Enter to skip)[/dim]")
    tag_filter = input(" ").strip().lower() or None
    console.print()

    if not query and min_rating is None and tag_filter is None:
        results = storage.get_all_entries()

    else:
        results = storage.search_entries(query=query, min_rating=min_rating, tag = tag_filter)

    console.clear()
    clear_and_header("search results")
    console.print()

    filters = []
    if query:    filters.append(query)
    if min_rating: filters.append(f" rated {min_rating}+")
    if tag_filter: filters.append(f"#{tag_filter}")
    console.print(f"  [dim]{' · '.join(filters) if filters else 'all films'}[/dim]")
    console.print()

    if not results:
        console.print(" [dim] No films match your search.[/dim]")
        console.print()
        console.print(" [dim] press any key to search again ·  [/dim][bold red]Q[/bold red][dim] to go back[/dim]")
        key = readchar.readkey().lower()
        if key == "q":
            return "menu"
        return show_search_screen()
    
# results
    console.print(f"   [dim]{len(results)} result{'s' if len(results) != 1 else ''}[/dim]")
    console.print()

    for i , entry in enumerate(results, start=1):
        row = render_entry_row(i, entry)
        console.print(row)
        console.print()

    console.print(Rule(style="dim red"))
    console.print()
    console.print( " [bold red][1-9][/bold red][dim] open entry[/dim]")
    console.print(f"  [bold red]\\[/][/bold red][dim] search again[/dim]")
    console.print("  [bold red][Q][/bold red][dim] back to menu[/dim]")
    console.print()

    while True:
        key = readchar.readkey().lower()

        if key == "q":
            return "menu"

        elif key == "/":
            return show_search_screen()

        elif key.isdigit():
            index = int(key)
            if 1 <= index <= len(results):
                entry = results[index - 1]

                next_screen = show_detail_screen(entry)
                if next_screen == "diary":

                    return show_search_screen()
                return next_screen

#Export screen
def show_export_screen():
    clear_and_header("export to letterboxd")

    entries = storage.get_all_entries()

    if not entries:
        console.print()
        console.print(" [dim]Nothing to export. Log some films first.[/dim]")
        console.print()
        console.print(" [dim]press any key to go back[/dim]")
        readchar.readkey()
        return "menu"
    
# preview
    console.print()
    console.print(f"  [white]Ready to export {len(entries)}"
                  f"film{'s' if len(entries) != 1 else ''} to letterboxd CSV.[/white]")
    console.print()
    
    console.print(" preview (first 5 entries):")
    console.print()

    for entry in entries[:5]:
        rating_str = f"{entry['rating']}/10" if entry.get("rating") else "unrated"
        date_str = format_date(entry.get("watched_date", ""))
        tags_str = ", ".join(entry.get("tags", [])) or "-"

        console.print(f" [bold white]{entry['title']}[/bold white]")
        console.print(f" [dim] {date_str}  ·  {rating_str}  {tags_str}[/dim]")
        console.print()

    if len(entries) > 5:
        console.print(f"  [dim]  ... and {len(entries) - 5} more [/dim]")
        console.print()

    console.print(Rule(style="dim red"))
    console.print()
    

    console.print(" [dim]Format Letterboxd CSV import [/dim]")
    console.print("[dim]Columns  Title  ·  Year  ·  Rating  ·  Date  ·  Rewatch  ·  Tags  ·  Review[/dim]")
    console.print("[dim]Saved to exports/folder with timestamp[/dim]")
    console.print(Rule(style="dim red"))
    console.print()

    console.print("  [bold red]›[/bold red] Export now?[dim](y/n)[/dim]")
    confirm=readchar.readkey().lower()

    if confirm != "y":
        console.print()
        console.print(" [dim]export cancelled.[/dim]")
        console.print()
        console.print(" [dim]press any key to go back[/dim]")
        readchar.readkey()
        return "menu"
    
    console.print()
    console.print(" [dim]exporting...[/dim]")

    filepath = storage.export_to_letterboxd_csv()
    if filepath:
        console.print()
        console.print(" [bold red]✓[/bold red] [white]Export complete.[/white]")
        console.print()
        console.print(f" [dim]saved to:[/dim]")
        console.print(f" [white]{filepath}[/white]")
        console.print()
        console.print(f" [dim]Upload this file at:[/dim]")
        console.print(f"[white]Letterboxd.com/import[/white]")
    else:
        console.print()
        console.print(" [dim red]Export failed. No entries found.[/dim red]")

    console.print()
    console.print(Rule(style="dim red"))
    console.print()
    console.print(" [dim]press any key to go back.[/dim]")
    readchar.readkey()
    return "menu"

def show_surprise_screen():
    clear_and_header("Surprise Me")
    console.print()

    item = storage.get_random_watchlist_item()

    if not item:
        console.print(" [dim]Your watchlist is empty.[/dim]")
        console.print()
        console.print(" [dim]Add films to your watchlist first - press [/dim][bold red]W[/bold red][dim] from the menu.[/dim]")
        console.print()
        console.print()
        return "menu"
    title_text = Text()
    title_text.append(f" {item['title']}", style ="bold white")
    console.print(title_text)

    meta_parts = []
    if item.get("director"): meta_parts.append(item["director"])
    if item.get("year"): meta_parts.append(str(item["year"]))
    if meta_parts:
        console.print(f" [dim] {' · '.join(meta_parts)}[/dim]")

    if item.get("note"):
        console.print()
        console.print(f" [dim]\"{item['note']}\"[/dim]")

    console.print()
    console.print(Rule(style="dim red"))
    console.print()
    console.print(" [bold red][W][/bold red][dim] mark as watched now[/dim]")
    console.print(" [bold red][R][/bold red][dim] pick another [/dim]")
    console.print(" [bold red][Q][/bold red][dim] back to menu[/dim]")
    console.print()
    
    while True:
        key= readchar.readkey().lower()

        if key== "q":
            return "menu"
        elif key =="r":
            return show_surprise_screen()
        elif key == "w":
            storage.remove_from_watchlist(item["id"])
            return "log", item["title"]
            
def show_year_in_review():
    from collections import Counter

    clear_and_header("year in review")
    console.print()
    
    years = storage.get_available_years()

    if not years:
        console.print(" [dim]No films logged yet.[/dim]")
        console.print()
        console.print(" [dim]press any key to go back[/dim]")
        readchar.readkey()
        return "menu"
    console.print(" [dim]Select a year:[/dim]")
    console.print()

    for i, year in enumerate(years, start=1):
        count = len(storage.get_entries_by_year(year))
        console.print(
            f" [bold red]{i}[/bold red] "
            f"[white]{year}[/white] "
            f"[dim]{count} film{'s' if count != 1 else ''}[/dim]"
        )
    console.print()

    while True:
        key= readchar.readkey()
        if key =="q":
            return "menu"
        if key.isdigit():
            idx = int(key)
            if 1 <= idx <= len(years):
                selected_year = years[idx - 1]
                break
    
    entries = storage.get_entries_by_year(selected_year)
    rated= [e for e in entries if e.get("rating")]

    total = len(entries)
    avg_rating = round(sum(e["rating"] for e in rated) / len(rated), 1) if rated else None
    top_entry = max(rated,key=lambda e: e["rating"]) if rated else None

    directors = [e["director"] for e in entries if e.get("director", "").strip()]
    fav_director = Counter(directors).most_common(1)[0] if directors else None

    all_tags = []
    for e in entries:
        all_tags.extend(e.get("tags", []))
    top_tags = Counter(all_tags).most_common(3)
    
    rating_counts = Counter(e["rating"] for e in rated)

    console.clear()
    clear_and_header(f"{selected_year} in review")
    console.print()

    console.print(f" [bold red]{selected_year}[/bold red]")
    console.print()

    console.print(f" [bold red]›[/bold red] [white]Films watched[/white] [yellow]{total}[/yellow]")
    console.print()

    if avg_rating:
        console.print(f" [bold red]›[/bold red] [white]Average rating[/white] [yellow]{avg_rating}[/yellow]/ 10")
        console.print()
    
    if top_entry:
        console.print(f" [bold red]›[/bold red] [white]Best film[/white] {top_entry['title']} [dim]({top_entry['rating']}/10)[/dim]")
        console.print()

    if fav_director:
        name, count = fav_director
        console.print(f" [bold red]›[/bold red] [white]Top director[/white] {name} [dim]({count} film{'s' if count != 1 else ''})[/dim]")
        console.print()

    if top_tags:
        tags_str = "  ".join(f"[bold red] {t} [/bold red]"for t, _ in top_tags)
        console.print(f" [bold red]›[/bold red] [white]Top tags[/white]")
        console.print()
        console.print(f" {tags_str}")
        console.print()

#top 5 films of the year
    console.print(Rule(style="dim red"))
    console.print()
    console.print(f" [dim]top films of {selected_year}[/dim]")
    console.print()

    top_5 = sorted(rated, key=lambda e: e["rating"], reverse =True)[:5]

    for i, entry in enumerate(top_5,start=1):
        try:
            rating_val = int(float(entry.get("rating", 0)))
        except (ValueError, TypeError):
            rating_val = 0
            
        filled = "*" * rating_val
        empty = "o" * (10 - rating_val)
        console.print(
            f" [bold red]{i}[/bold red] "
            f"[white]{entry['title']:<35}[/white] "
            f"[yellow]{filled}[/yellow][dim]{empty}[/dim]"
        )
        console.print()
        
    if rating_counts:
        console.print(Rule(style="dim red"))
        console.print()
        console.print(" [dim]rating distribution[/dim]")
        console.print()

        max_count = max(rating_counts.values())
        for star in range(1,11):
            count = rating_counts.get(star, 0)
            bar_length = int((count / max_count) * 20) if max_count > 0 else 0
            filled = "█" * bar_length
            empty = "░" * (20 - bar_length)
            if count > 0:
                console.print(f" [dim]{star:>2}[/dim] [yellow]{filled}[/yellow][dim]{empty} {count:>2}[/dim]")
            else:
                console.print(f" [dim]{star:>2}[/dim] [dim]{filled}{empty} {count:>2}[/dim]")
            
        console.print()

    console.print(Rule(style="dim red"))
    console.print()
    console.print()
    console.print(" [dim]press any key to go back [/dim]")
    readchar.readkey()
    return "menu"

        