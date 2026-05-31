import json
import uuid
from datetime import datetime, date
from pathlib import Path

#path setup
DATA_DIR = Path(__file__).parent.parent / "data"
ENTRIES_FILE= DATA_DIR / "entries.json"
WATCHLIST_FILE = DATA_DIR / "watchlist.json"

# storage functions

def ensure_data_dir():
    DATA_DIR.mkdir(exist_ok=True)

def load_entries():
    if not ENTRIES_FILE.exists():
        return []
    content = ENTRIES_FILE.read_text(encoding="utf-8").strip()
    if not content:
        return[]
    return json.loads(content)
    
def save_entries(entries):
    with open(ENTRIES_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)

#creating entry setup

def create_entry(title, director="", year=None, rating=None, review="", watched_date=None, tags=None):
    entries= load_entries()

    new_entry= {
        "id": str(uuid.uuid4())[:8],
        "title": title.strip(),
        "director": director.strip(),
        "year": year,
        "rating": rating,
        "review": review.strip(),
        "year": year,
        "rating": rating,
        "review": review.strip(),
        "watched_date": watched_date or date.today().isoformat(),
        "created_at": datetime.now().isoformat(),
        "tags": tags or []
    }
    entries.append(new_entry)
    save_entries(entries)

    return new_entry

def get_all_entries():
    entries= load_entries()
    return sorted(entries, key=lambda e: e["watched_date"], reverse=True)

def get_entry_by_id(entry_id):
    entries= load_entries()
    for entry in entries:
        if entry["id"] == entry_id:
            return entry
    return None

def delete_entry(entry_id):
    entries = load_entries()
    original_count = len(entries)
    entries =[e for e in entries if e["id"] != entry_id]

    if len(entries) ==original_count:
        return False
    save_entries(entries)
    return True

def update_entry(entry_id, **kwargs):
# im using kwargs to make partial updates so that user doesnt have to update each value every time
    entries = load_entries()
    for entry in entries:
        for field,value in kwargs.items():

            if field in entry:
                entry[field]= value
        save_entries(entries)
        return entry
    return None


def load_watchlist():
    if not WATCHLIST_FILE.exists():
        return []
    content = WATCHLIST_FILE.read_text(encoding = "utf-8").strip()
    if not content:
        return []
    return json.loads(content)

def save_watchlist(items):
    ensure_data_dir()
    with open(WATCHLIST_FILE, "w", encoding = "utf-8") as f:
        json.dump(items,f, indent = 2, ensure_ascii = False)

def add_to_watchlist(title, director="", year = None, note = ""):

    items = load_watchlist()

    new_item = {
        "id":  str(uuid.uuid())[:8],
        "title": title.strip(),
        "director": director.strip(),
        "year": year,
        "note": note.strip(),
        "added_note": date.today().isoformat()
    }
    items.append(new_item)
    save_watchlist(items)
    return new_item

