# Music Recommender Simulation

## What this is

It’s a fake recommender: songs live in a CSV, your “user” is a small dict of preferences, and the program just adds points and sorts. No training step, no API. I like that because you can read `score_song` and actually see why something ranked where it did.

Spotify-style apps mix **collaborative** stuff (people like you) with **content** stuff (tempo, mood, etc.). This project is content-only, so it’s more like “match my tags” than “learn from the crowd.”

---

## How it works (quick version)

**What’s in each song row:** the usual suspects (genre, mood, energy, tempo, valence, danceability, acousticness) plus a few extras I added for the stretch goals: popularity 0–100, release decade, mood tags separated with `|`, a rough `lyric_theme`, and `language`. If your prefs dict includes things like `target_popularity` or `favorite_mood_tags`, those columns start affecting the score too. All the nitty-gritty is in `src/recommender.py`.

**How we represent a user:**  
Either a plain dict (what `main.py` uses) or the `UserProfile` class the tests use. Same scoring underneath.

**Rough scoring idea:** points if genre lines up (I allow substring stuff so “pop” can still hit “indie pop”), points if mood matches exactly, more points if energy is *close* to what you asked for (not just “higher = better”). There’s optional valence/danceability if you add those keys. `likes_acoustic` nudges scores toward acoustic vs produced tracks.

After scoring, we sort. There’s also an optional **diversity** step so the top K doesn’t fill up with the same artist or genre over and over. The CLI prints **tables** (using `tabulate`) with a Reasons column so you’re not guessing.

### Stretch / optional pieces

I bundled four extras: extra CSV fields + math for them, a few **modes** (`balanced`, `genre_first`, `mood_first`, `energy_focused`) that scale how much each kind of signal matters, the diversity penalty above, and the table output. First profile in `main.py` runs all four modes so you can compare; the other profiles just use balanced so the terminal doesn’t go forever.

### Flow (Mermaid)

```mermaid
flowchart LR
  CSV[data/songs.csv] --> LOAD[load_songs]
  LOAD --> CATALOG[List of song dicts]
  PREFS[User preferences] --> SCORE[score_song per song]
  CATALOG --> SCORE
  SCORE --> PAIRS[(song, score, reasons)]
  PAIRS --> SORT[Sort by score desc]
  SORT --> TOP[Top K recommendations]
```

**One bias to keep in mind:** genre still carries a lot of weight. If the CSV is mostly one style, that style will keep winning even when mood or energy would have pointed somewhere else.

---

## Setup

```bash
cd ai110-module3show-musicrecommendersimulation-starter
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Run from the repo root (folder that has `data/` and `src/`):

```bash
python -m src.main
```

You should see something like `Loaded songs: 18`, then tables for different profiles.

Tests:

```bash
pytest
```

---

## What the output looks like

The app prints GitHub-style tables now, not the old bullet list. Roughly like:

```
| # | Title        | Artist    | Score | Reasons |
|---|--------------|-----------|-------|---------|
| 1 | Sunrise City | Neon Echo | 9.82  | genre match; mood match; energy alignment; ... |
```

Your numbers will depend on the exact weights and prefs. If a rubric wants a screenshot, grab one from your own terminal after a run.

---

## Stuff I tried

I temporarily changed the constants in `recommender.py`: lower genre weight, higher energy weight, ran again. The list shifted toward whoever sat near the target energy, even when another song was a “truer” genre match. Kind of what I expected.

I also mentally removed the mood line (didn’t leave it commented out in the repo) and noticed happy vs intense pop would blur together more. So mood was doing real work for those cases.

---

## Honest limitations

Eighteen fake songs is not a catalog. No lyrics, no social signals, no “you listened to this last week.” Genre substring matching is handy for a tiny dataset but could get weird if someone names genres carelessly.

More detail in [`model_card.md`](model_card.md) and the informal notes in [`reflection.md`](reflection.md).

---

## Tiny reflection

Before this, recommenders felt like a black box. After, it’s mostly: define features, pick weights, sort. The part that still feels “AI-ish” to people is really just which weights and which data someone chose. I used tests to catch dumb mistakes; for whether the rankings “feel right,” I still had to use my own judgment on the fake profiles.
