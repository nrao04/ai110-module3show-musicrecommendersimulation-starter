import csv
from dataclasses import asdict, dataclass
from typing import Dict, List, Tuple

# Scoring weights (tune here for experiments — see README “Experiments You Tried”).
WEIGHT_GENRE_MATCH = 2.0
WEIGHT_MOOD_MATCH = 1.0
WEIGHT_ENERGY_ALIGNMENT = 2.0  # max points when energy exactly matches target
WEIGHT_VALENCE_ALIGNMENT = 1.0
WEIGHT_DANCEABILITY_ALIGNMENT = 0.8
WEIGHT_ACOUSTIC_PREFERENCE = 1.2  # max when taste aligns with song acousticness


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """

    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """

    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """

    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Rank catalog songs for a user and return the top k."""
        prefs = user_profile_to_prefs(user)
        scored: List[Tuple[float, Song]] = []
        for song in self.songs:
            row = song_to_dict(song)
            score, _ = score_song(prefs, row)
            scored.append((score, song))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [song for _, song in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Human-readable explanation for one song and user."""
        prefs = user_profile_to_prefs(user)
        _, reasons = score_song(prefs, song_to_dict(song))
        return "; ".join(reasons) if reasons else "No strong matches to the stated preferences."


def user_profile_to_prefs(user: UserProfile) -> Dict:
    """Map a UserProfile into the dictionary shape used by score_song."""
    return {
        "genre": user.favorite_genre,
        "mood": user.favorite_mood,
        "energy": float(user.target_energy),
        "likes_acoustic": user.likes_acoustic,
    }


def song_to_dict(song: Song) -> Dict:
    """Convert a Song dataclass to a plain dict for CSV-style scoring."""
    return asdict(song)


def _normalize_str(value: str) -> str:
    return (value or "").strip().lower()


def _genre_matches(user_genre: str, song_genre: str) -> bool:
    u = _normalize_str(user_genre)
    s = _normalize_str(song_genre)
    if not u or not s:
        return False
    return u == s or u in s or s in u


def _mood_matches(user_mood: str, song_mood: str) -> bool:
    return _normalize_str(user_mood) == _normalize_str(song_mood)


def _alignment_bonus(weight: float, song_value: float, target: float) -> Tuple[float, float]:
    """Return (points, distance) where points are weight * (1 - distance), capped."""
    distance = abs(float(song_value) - float(target))
    distance = min(distance, 1.0)
    return weight * (1.0 - distance), distance


def load_songs(csv_path: str) -> List[Dict]:
    """Load song rows from CSV; coerce numeric fields for math."""
    print(f"Loading songs from {csv_path}...")
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append(
                {
                    "id": int(row["id"]),
                    "title": row["title"],
                    "artist": row["artist"],
                    "genre": row["genre"],
                    "mood": row["mood"],
                    "energy": float(row["energy"]),
                    "tempo_bpm": float(row["tempo_bpm"]),
                    "valence": float(row["valence"]),
                    "danceability": float(row["danceability"]),
                    "acousticness": float(row["acousticness"]),
                }
            )
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Returns total score and a list of short reason strings for transparency.
    """
    reasons: List[str] = []
    score = 0.0

    genre_key = user_prefs.get("genre") or user_prefs.get("favorite_genre")
    mood_key = user_prefs.get("mood") or user_prefs.get("favorite_mood")
    raw_energy = user_prefs.get("energy")
    if raw_energy is None:
        raw_energy = user_prefs.get("target_energy", 0.5)
    target_energy = float(raw_energy)

    if genre_key and _genre_matches(str(genre_key), str(song.get("genre", ""))):
        score += WEIGHT_GENRE_MATCH
        reasons.append(f"genre match (+{WEIGHT_GENRE_MATCH})")

    if mood_key and _mood_matches(str(mood_key), str(song.get("mood", ""))):
        score += WEIGHT_MOOD_MATCH
        reasons.append(f"mood match (+{WEIGHT_MOOD_MATCH})")

    energy_pts, energy_gap = _alignment_bonus(
        WEIGHT_ENERGY_ALIGNMENT, float(song["energy"]), target_energy
    )
    score += energy_pts
    reasons.append(
        f"energy alignment (+{energy_pts:.2f}; gap {energy_gap:.2f} from target {target_energy:.2f})"
    )

    if "target_valence" in user_prefs and user_prefs["target_valence"] is not None:
        tv = float(user_prefs["target_valence"])
        v_pts, v_gap = _alignment_bonus(WEIGHT_VALENCE_ALIGNMENT, float(song["valence"]), tv)
        score += v_pts
        reasons.append(
            f"valence alignment (+{v_pts:.2f}; gap {v_gap:.2f} from {tv:.2f})"
        )

    if "target_danceability" in user_prefs and user_prefs["target_danceability"] is not None:
        td = float(user_prefs["target_danceability"])
        d_pts, d_gap = _alignment_bonus(
            WEIGHT_DANCEABILITY_ALIGNMENT, float(song["danceability"]), td
        )
        score += d_pts
        reasons.append(
            f"danceability alignment (+{d_pts:.2f}; gap {d_gap:.2f} from {td:.2f})"
        )

    likes_acoustic = user_prefs.get("likes_acoustic")
    if likes_acoustic is not None:
        ac = float(song["acousticness"])
        if likes_acoustic:
            a_pts = WEIGHT_ACOUSTIC_PREFERENCE * ac
            reasons.append(f"prefers acoustic (+{a_pts:.2f})")
        else:
            a_pts = WEIGHT_ACOUSTIC_PREFERENCE * (1.0 - ac)
            reasons.append(f"prefers produced/electric (+{a_pts:.2f})")
        score += a_pts

    return score, reasons


def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5
) -> List[Tuple[Dict, float, str]]:
    """
    Score every song, sort high to low, return top k as (song, score, joined reasons).
    """
    ranked: List[Tuple[float, Dict, str]] = []
    for s in songs:
        sc, rs = score_song(user_prefs, s)
        ranked.append((sc, s, "; ".join(rs)))
    ranked.sort(key=lambda x: x[0], reverse=True)
    return [(song, sc, expl) for sc, song, expl in ranked[:k]]
