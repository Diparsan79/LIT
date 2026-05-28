import readchar
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

console = Console()

# ── App State ─────────────────────────────────────────────────────────────────
#
# This dictionary holds the current "mood" of the app.
# Right now it only tracks which screen we're on and whether we're running.
#
# Why a dictionary instead of plain variables?
# We could write: current_screen = "menu" and running = True
# That works fine now. But a dict groups related state together,
# makes it easier to pass around, and easier to expand later.
# It's a small habit that pays off as complexity grows.
#
APP_STATE = {
    "running": True,
    "screen": "menu",
}


# ── Render Functions ───────────────────────────────────────────────────────────
#
# These haven't changed from Milestone 1.
# They build content but never print it directly.
# This discipline becomes very important once we have multiple screens.

def render_header():
    title = Text()
    title.append("L ", style="bold red")
    title.append("I ", style="bold white")
    title.append("T\n", style="bold red")
    title.append("Letterboxd in Terminal", style="dim white")
    return title


def render_menu():
    menu = Text()
    menu.append("\n")

    options = [
        ("L", "log a film"),
        ("D", "diary"),
        ("W", "watchlist"),
        ("S", "search"),
        ("Q", "quit"),
    ]

    for key, label in options:
        menu.append(f"  [{key}]", style="bold red")
        menu.append(f"  {label}\n", style="white")

    return menu


def render_footer():
    footer = Text()
    footer.append("\nv0.1.0  ·  local-first movie diary", style="dim white")
    return footer


# ── Screen Functions ───────────────────────────────────────────────────────────
#
# Each "screen" is a function that draws something.
# Right now only the menu screen is real — the others are placeholders.
# Placeholders are not laziness. They're intentional scaffolding.
# They let you test navigation before the destination exists.

def show_main_menu():
    console.clear()

    content = Text()
    content.append_text(render_header())
    content.append_text(render_menu())
    content.append_text(render_footer())

    console.print(
        Panel(
            Align.center(content),
            border_style="red",
            padding=(1, 4),
        )
    )


def show_placeholder(screen_name):
    """
    Temporary stand-in for screens that don't exist yet.

    Instead of crashing or doing nothing when you press L/D/W/S,
    we show a friendly message and wait for a keypress to go back.

    This is called a "stub" — a placeholder with just enough
    behavior to be useful during development.
    """
    console.clear()
    console.print(
        Panel(
            Align.center(
                Text(f"\n[ {screen_name.upper()} ]\n\ncoming soon...\n\npress any key to go back", 
                     style="dim white", justify="center")
            ),
            border_style="dim red",
            padding=(1, 4),
        )
    )
    readchar.readkey()  # wait for any key, then return
    APP_STATE["screen"] = "menu"


# ── Input Handlers ─────────────────────────────────────────────────────────────
#
# These functions decide what a keypress MEANS on a given screen.
# Notice they don't draw anything — they just update APP_STATE.
# Drawing is handled separately in the main loop.
#
# Why separate "what does this key mean" from "what do we draw"?
# Because the same key can mean different things on different screens.
# 'Q' on the menu means quit. 'Q' while typing a review means the letter Q.
# Keeping input logic separate from display logic makes this manageable.

def handle_menu_input(key):
    """Processes a keypress when we're on the main menu."""

    # .lower() means L and l both work — small UX kindness
    key = key.lower()

    if key == "l":
        APP_STATE["screen"] = "log"
    elif key == "d":
        APP_STATE["screen"] = "diary"
    elif key == "w":
        APP_STATE["screen"] = "watchlist"
    elif key == "s":
        APP_STATE["screen"] = "search"
    elif key == "q":
        APP_STATE["running"] = False


# ── Main Loop ──────────────────────────────────────────────────────────────────
#
# This is the heartbeat of the entire application.
# It runs forever (until running = False) and does three things each cycle:
#   1. Draw whatever screen we're on
#   2. Read a keypress
#   3. Handle that keypress (which may change the screen)
#
# This pattern — draw → read → handle → repeat — is the foundation
# of every interactive terminal app. Learn its shape. You'll see it everywhere.

def main():
    while APP_STATE["running"]:

        # ── Draw phase ──
        # Look at what screen we're on and display it
        if APP_STATE["screen"] == "menu":
            show_main_menu()
            # ── Read phase ──
            # Wait here, frozen, until the user presses a key
            key = readchar.readkey()
            # ── Handle phase ──
            handle_menu_input(key)

        elif APP_STATE["screen"] == "log":
            show_placeholder("log a film")

        elif APP_STATE["screen"] == "diary":
            show_placeholder("diary")

        elif APP_STATE["screen"] == "watchlist":
            show_placeholder("watchlist")

        elif APP_STATE["screen"] == "search":
            show_placeholder("search")

    # ── Exit ──
    # Only reached when running = False (user pressed Q)
    console.clear()
    console.print("\n[dim red]  goodbye, cinephile.[/dim red]\n")


if __name__ == "__main__":
    main()