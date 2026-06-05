import json
import uuid
from datetime import datetime, date
from pathlib import Path

#path setup
DATA_DIR = Path(__file__).parent.parent / "data"
ENTRIES_FILE= DATA_DIR / "entries.json"
WATCHLIST_FILE = DATA_DIR / "watchlist.json"
EXPORTS_DIR = Path(__file__).parent.parent / "exports"

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

def get_watchlist():
    items = load_watchlist()
    return sorted(items, key=lambda i: i["added_date"], reverse = True)

def remove_from_watchlist(item_id):
    items = load_watchlist
    original_count = len(items)
    items = [i for i in items if i["id"] != item_id]
    if len(items) == original_count:
        return False
    save_watchlist(items)
    return True

def search_entries(query= "", min_rating = None, max_rating = None, tag = None):
    entries = get_all_entries()
    results = []

    query = query.lower().strip()

    for entry in entries:
        if query:
            title = entry.get("title", "").lower()
            director = entry.get("director", "").lower()
            if query not in title and query not in director:
                continue

        rating = entry.get("rating")

        if min_rating is not None:
            if rating is None or rating < min_rating:
                continue

        if max_rating is not None:
            if rating is None or rating > max_rating:
                continue
        
        if tag is not None:
            entry_tags = entry.get("tags", [])
            if tag.strip().lower() not in entry_tags:
                continue

        results.append(entry)

    return results

def get_all_tags():
    from collections import Counter
    entries = load_entries()
    all_tags = []
    for entry in entries:
        all_tags.extend(entry.get("tags", []))
    return Counter(all_tags)

def search_by_tag(tag):

    tag = tag.strip().lower()
    entries = get_all_entries()
    return [e for e in entries if tag in e.get("tags", [])]


def export_to_letterboxd_csv():
    import csv
    from datetime import datetime

    entries = get_all_entries()

    if not entries:
        return None
    
    EXPORTS_DIR.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = EXPORTS_DIR / f"lit_export_{timestamp}.csv"

    from collections import Counter
    title_counts = Counter(
        e.get("title", "").strip().lower()
        for e in entries
    )

    with open(filename, "w", newline = "", encoding ="utf-8") as f:

        writer = csv.DictWriter(f, fieldnames = [
            "Title", "Year", "Rating10", "WatchedDate",
            "Rewatch", "Tags", "Review"
        ])

        writer.writeheader()

        chronological = sorted(entries, key = lambda e: e["watched_date"])

        for entry in chronological:
            title = entry.get("Title", "")

            is_rewatch = title_counts[title.strip().lower()] > 1
            tags = ", ".join(entry.get("tags", []))
            

            writer.writerow({
                "Title": title,
                "Year": entry.get("year") or "",
                "Rating10": entry.get("rating") or "",
                "WatchedDate": entry.get("watched_date", ""),
                "Rewatch": "Yes" if is_rewatch else "",
                "Tags": tags,
                "Review": entry.get("review", "")
            })

    return str(filename)

def get_random_watchlist_item():
    import random
    items = get_watchlist()
    return random.choice(items) if items else None

def get_entries_by_year(year):
    entries = get_all_entries()
    return [
        e for e in entries
        if e.get("watched_date", "").startswith(str(year))
    ]
def get_available_years():
    entries = load_entries()
    years = set()
    for e in entries:
        date = e.get("watched_date", "")
        if date:
            years.add(int(date[:4]))
    return sorted(years, reverse=True)
