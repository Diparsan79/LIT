from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.console import Group
import readchar
from . import screens
from . import storage
import os

console = Console()

APP_STATE = {
    "running": True,
    "screen": "menu",
    "selected_entry": None,
    "prefill_title": None,
    "page": 0
}


def render_header():
    title = Text()
    title.append("L", style="bold red")
    title.append(" ")
    title.append("I", style="bold white")
    title.append(" ")
    title.append("T", style="bold red")
    title.append(" Letterboxd in terminal", style="dim white")
    return Align.center(title)

def render_menu():
    menu=Text()
    menu.append("\n")

    options=[
        ("L", "log a film"),
        ("D", "diary"),
        ("w", "watchlist"),
        ("S", "search"),
        ("T", "Stats"),
        ("E", "export"),
        ("X", "surprise me"),
        ("Y", "year in review"),
        ("Q", "quit")
    ]

    for key, label in options:
        menu.append(f" [{key}]", style="bold red")
        menu.append(f"{label}\n", style="white")
    
    return Align.center(menu)

def show_main_menu():
    console.clear()

    console.print(
        Panel(
            Group(
                render_header(),
                render_menu(),
            ),
            padding=(1, 4),
            border_style="dim white",
        )
    )

def show_placeholder(screen_name):
    console.clear()
    console.print(
        Panel(
            Align.center(
                Text(f"\n[ {screen_name.upper()}]\n\ncoming soon..... \n\npress any key to go back",
                     style="dim white", justify="center")
            ),
            border_style="dim red",
            padding=(1,4),
        )
    )
    readchar.readkey()
    APP_STATE["screen"]="menu"

#input handling
def handle_menu_input(key):

    key = key.lower()
    if key =="l":
        APP_STATE["screen"]= "log"
    elif key =="d":
        APP_STATE["screen"]= "diary"
    elif key=="w":
        APP_STATE["screen"]="watchlist"
    elif key=="s":
        APP_STATE["screen"]="search"
    elif key =="t":
        APP_STATE["screen"]="stats"
    elif key=="e":
        APP_STATE["screen"]="export"
    elif key =="x":
        APP_STATE["screen"] ="surprise"
    elif key =="y":
        APP_STATE["screen"] = "year"
    elif key =="q":
        APP_STATE["running"]= False


# LOOPY loop
def main():
    while APP_STATE["running"]:
        if APP_STATE["screen"]== "menu":
            show_main_menu()
            key = readchar.readkey()
            handle_menu_input(key)

        elif APP_STATE["screen"] =="log":
            next_screen = screens.show_log_screen(
                APP_STATE["prefill_title"]
            )
            APP_STATE["prefill_title"] = None
            APP_STATE["screen"]= next_screen

        elif APP_STATE["screen"] =="diary":
            next_screen, entry = screens.show_diary_screen()
            APP_STATE["screen"] = next_screen
            APP_STATE["selected_entry"] = entry

        elif APP_STATE["screen"] == "detail":
            next_screen = screens.show_detail_screen(APP_STATE["selected_entry"])
            APP_STATE["screen"] = next_screen
            APP_STATE["selected_entry"]= None

        elif APP_STATE["screen"]== "watchlist":
            result = screens.show_watchlist_screen()

            next_screen, prefill = result
            APP_STATE["screen"] = next_screen
            APP_STATE["prefill_title"] = prefill

        elif APP_STATE["screen"] == "search":
            next_screen = screens.show_search_screen()
            APP_STATE["screen"] = next_screen
        elif APP_STATE["screen"] =="stats":
            next_screen = screens.show_stats_screen()
            APP_STATE["screen"] = next_screen
        elif APP_STATE["screen"] =="export":
            next_screen = screens.show_export_screen()
            APP_STATE["screen"] = next_screen
        elif APP_STATE["screen"] == "surprise":
            result = screens.show_surprise_screen()
            if isinstance(result, tuple):
                next_screen, prefill = result
                APP_STATE["prefill_title"] = prefill
            else:
                APP_STATE["screen"] = result
        
        elif APP_STATE["screen"] =="year":
            next_screen = screens.show_year_in_review()
            APP_STATE["screen"] = next_screen
    
    console.clear()
    console.print("\n[dim red] goodbye ,  beloved cinephile. [/dim red]")

if __name__ == "__main__":
    main()
