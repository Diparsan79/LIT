import json
import uuid
from datetime import datetime, date
from pathlib import Path
import os

#path setup
DATA_DIR = Path(__file__).parent.parent / "data"
ENTRIES_FILE= DATA_DIR / "entries.json"
WATCHLIST_FILE = DATA_DIR / "watchlist.json"
EXPORTS_DIR = Path(__file__).parent.parent / "exports"

# storage functions

def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

def load_entries():
    if not ENTRIES_FILE.exists():
        return []
    try:
        content = ENTRIES_FILE.read_text(encoding="utf-8").strip()
        if not content:
            return []
        return json.loads(content)
    except Exception:
        return []

    
def save_entries(entries):
    ensure_data_dir()
    tmp_file = ENTRIES_FILE.with_suffix(".tmp")

    with open(tmp_file, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)

    os.replace(tmp_file, ENTRIES_FILE)

#creating entry setup

def create_entry(title, director="", year=None, rating=None, review="", watched_date=None, tags=None, poster_path=""):
    ensure_data_dir()
    entries= load_entries()

    if rating is not None:

        try:
            rating = float(rating)

            if not (0 <= rating <= 10):
                rating = None
        
        except(TypeError, ValueError):
            rating = None

    if isinstance(tags, str):
        tags = [tags]

    new_entry= {
        "id": str(uuid.uuid4())[:8],
        "title": str(title).strip(),
        "director": str(director).strip() if director else "",
        "year": year,
        "rating": rating,
        "review": str(review).strip() if review else "",
        "watched_date": str(watched_date) if watched_date else date.today().isoformat(),
        "created_at": datetime.now().isoformat(),
        "tags": [str(t).strip().lower() for t in (tags or []) if str(t).strip()],
        "poster_path": str(poster_path) if poster_path else ""
    }
    entries.append(new_entry)
    save_entries(entries)

    return new_entry

def get_all_entries():
    entries= load_entries()
    return sorted(entries, key=lambda e: str(e.get("watched_date", "")), reverse=True)

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
        if entry["id"] == entry_id:
            for field, value in kwargs.items():
                if field in entry:
                    entry[field] = value
            save_entries(entries)
            return entry
        
    return None


def load_watchlist():
    if not WATCHLIST_FILE.exists():
        return []
    try:
        content = WATCHLIST_FILE.read_text(encoding="utf-8").strip()
        if not content:
            return []
        return json.loads(content)
    except Exception:
        return []

def save_watchlist(items):
    ensure_data_dir()
    tmp_file = WATCHLIST_FILE.with_suffix(".tmp")

    with open(tmp_file, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)


    os.replace(tmp_file, WATCHLIST_FILE)

def add_to_watchlist(title, director="", year=None, note=""):

    items = load_watchlist()

    normalized_title = title.strip().lower()

    for item in items:
        existing_title = item.get("title", "").strip().lower()

        if existing_title == normalized_title:
            return None
    new_item = {
        "id": str(uuid.uuid4())[:8],
        "title": title.strip(),
        "director": director.strip(),
        "year": year,
        "note": note.strip(),
        "added_date": date.today().isoformat()
    }

    items.append(new_item)
    save_watchlist(items)

    return new_item

def get_watchlist():
    items = load_watchlist()

    def safe_date(item):
        return item.get("added_date") or ""
    
    return sorted(items, key=safe_date, reverse=True)

def remove_from_watchlist(item_id):
    items = load_watchlist()
    original_count = len(items)
    items = [i for i in items if i["id"] != item_id]
    if len(items) == original_count:
        return False
    save_watchlist(items)
    return True

def search_entries(query="", min_rating=None, max_rating=None, tag=None):
    entries=get_all_entries()
    results = []

    query = query.lower().strip()
    
    for entry in entries:
        title = entry.get("title", "").lower()
        director = entry.get("director", "").lower()
        tags = [t.lower() for t in entry.get("tags", [])]

        if query:
            if query not in title and query not in director and query not in " ".join(tags):
                continue

        if tag:
            if tag.strip().lower() not in tags:
                continue
        rating = entry.get("rating")

        try:
            if rating is not None:
                rating = float(rating)
        except (TypeError, ValueError):
            rating = None
        
        if min_rating is not None:
            if rating is None or rating < min_rating:
                continue
        
        if max_rating is not None:
            if rating is None or rating > max_rating:
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

def get_all_entries_by_title(title):
    title = title.strip().lower()

    return [
        e for e in load_entries()
        if e.get("title", "").strip().lower() ==title
    ]


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

        chronological = sorted(entries, key = lambda e: str(e.get("watched_date", "")))

        for entry in chronological:
            title = entry.get("title", "")

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
    console_message = str(filename.resolve())
    return console_message

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
        d = e.get("watched_date", "")
        if isinstance(d, str) and len(d) >= 4 and d[:4].isdigit():
            years.add(int(d[:4]))
    return sorted(years, reverse = True)

def paginate(items, page, page_size =10):
    start = page * page_size
    end = start + page_size
    return items[start:end]