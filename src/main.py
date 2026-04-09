"""
Command line runner for the Music Recommender Simulation.

Run from the project root:

    python -m src.main
"""

from __future__ import annotations

from typing import Dict, List

from .recommender import load_songs, recommend_songs


def format_block(title: str, recs: List, width: int = 72) -> str:
    """Build a readable multi-line block for stdout."""
    lines = [title, "=" * min(width, len(title) + 4)]
    for song, score, explanation in recs:
        lines.append(f"  • {song['title']}  |  score {score:.2f}")
        lines.append(f"    {explanation}")
        lines.append("")
    return "\n".join(lines).rstrip()


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}\n")

    # Several hand-picked taste profiles for evaluation (Phase 4).
    profiles: Dict[str, Dict] = {
        "High-energy pop (default)": {
            "genre": "pop",
            "mood": "happy",
            "energy": 0.8,
            "likes_acoustic": False,
        },
        "Chill lofi room": {
            "genre": "lofi",
            "mood": "chill",
            "energy": 0.35,
            "likes_acoustic": True,
        },
        "Deep intense rock": {
            "genre": "rock",
            "mood": "intense",
            "energy": 0.9,
            "likes_acoustic": False,
        },
        # Edge-style: conflicting signals — sad mood but wants rave-level energy.
        "Adversarial — sad but max energy": {
            "genre": "pop",
            "mood": "moody",
            "energy": 0.95,
            "likes_acoustic": False,
        },
    }

    for label, user_prefs in profiles.items():
        recommendations = recommend_songs(user_prefs, songs, k=5)
        print(format_block(f"{label}", recommendations))
        print()


if __name__ == "__main__":
    main()
