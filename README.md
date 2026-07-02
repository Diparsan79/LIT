# LIT — Letterboxd in Terminal

> A retro-inspired, local movie logging app for the terminal.

```
    L I T
    Letterboxd in Terminal

    [L] log a film
    [D] diary
    [W] watchlist
    [S] search
    [T] stats
    [E] export
    [X] surprise me
    [Y] Year in review
    [Q] quit
```

---

# What is LIT?
LIT is a personal movie logging app that lives entirely in your terminal. Its almost exactly like Letterboxd (well in some ways) if you exclude the multi users and the internet thing. 


 I wanted to combine my love for movies and my thirst for becoming a better programmer so I decided to start this project. This whole journey turned out to be a complete roller coaster of emotions. I am soooo happy that finally the project ended but now i won't have any other project to maintain my streak for :(

---

#Features
**Logging**
- Log films with title, director, year, rating, review , and tags
- Auto-fill metadata from TMDB with a single keypress (makes the whole process SOOOOOOO COOOLLLLL)
- Rewatch detection - see your previous ratings when logging the same movie again aswell


**Diary**
- chronological list of everything you watched
- detailed well formatted data
- entry detail well shown like review , tags , watch history with edit or delete any entry feature


**Watchlist**
- separate list of films you want/have to watch
- add specific notes to each movies like " recommended by Tyler (durden) "
-  mark as watched -> goes to log screen and fetches data from tmdb -> select the one you chose so as to fix the spelling errors and directors
- easy and effifient

**Search @ Filter**
- Search by Title or Director
- Filter using minimum rating , tags , combine all filters (all are optional)

**Stats**
- Total films, average rating, top director
- Rating distribution bar chart
- Tag cloud weighted by frequency

**Export**
- Export to Letterboxd's official CSV import format
- Upload directly at `letterboxd.com/import`
- easy and convenient movie logging feature

**Surprise Me
- Press `X` -> LIT picks a random film from your watchlist
- Press `R` to pick another random film , `W` to mark it as watched that day , you get into the logging section

**Requirements:** Python 3.10+

```bash
# Clone the Project
git clone `https://github.com/Diparsan79/LIT`
cd LIT

# Create and activate virtual environment in mac/linux
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

** setting up TMDB api**
1. Create a free account at [themoviedb.org] (https://themoviedb.org/signup)
2. Go to sSettings -> API -> Request an API key
3. Create a `.env` file in the project root:

```
TMDB_API=your_key_here
```

ps: LIT works fully without a TMDB api but it is recommended for easy logging of proper info of movies also for letterboxd exporting so as to avoid errors


## Run
``` bash
python -m lit.main
```

---
**File structure**
lit/
├── lit/
│   ├── main.py      
│   ├── screens.py  
│   ├── storage.py    
│   ├── tmdb.py       
│   └── ascii_art.py  
├── data/
│   ├── entries.json   
│   └── watchlist.json 
├── exports/          
├── .env              
└── requirements.txt

All your data lives in `data/`. It's plain JSON . Open it in any text editor. Back it up anywhere.


## ai clarification
This project is an original creation of mine and undoubtedly my biggest project yet. I've had a lot of debugging errors for which i used gemini to fix my errors and used claude for some features ideas generation. the two features that claude suggested me was of the surprise me feature and the Year in Review but i implemented all of that myself.