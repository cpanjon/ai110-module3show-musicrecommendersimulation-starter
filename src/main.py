"""
Command line runner for the Music Recommender Simulation.

Run with:
    python -m src.main
"""

from src.recommender import load_songs, recommend_songs

DIVIDER = "=" * 60
THIN = "-" * 60


def print_results(label: str, user_prefs: dict, songs: list, k: int = 5, weights: dict = None) -> None:
    """Print a labelled recommendation block for one user profile."""
    genre  = user_prefs.get("genre", "?")
    mood   = user_prefs.get("mood", "?")
    energy = user_prefs.get("energy", "?")
    print(f"\n{DIVIDER}")
    print(f"  {label}")
    print(f"  Profile: genre={genre} | mood={mood} | energy={energy}")
    if weights:
        print(f"  Weights: genre={weights['genre']} | mood={weights['mood']} | energy={weights['energy']} | acoustic={weights['acoustic']}")
    print(THIN)
    results = recommend_songs(user_prefs, songs, k=k, weights=weights)
    max_score = sum(weights.values()) if weights else 4.5
    for rank, (song, score, explanation) in enumerate(results, start=1):
        print(f"  {rank}. {song['title']} by {song['artist']}")
        print(f"     Score : {score:.2f} / {max_score:.1f}")
        print(f"     Why   : {explanation}")
        print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"\nLoaded songs: {len(songs)}")

    # ------------------------------------------------------------------
    # Standard profiles
    # ------------------------------------------------------------------
    print_results(
        "PROFILE 1 — High-Energy Pop",
        {"genre": "pop", "mood": "happy", "energy": 0.85, "likes_acoustic": False},
        songs,
    )

    print_results(
        "PROFILE 2 — Chill Lofi",
        {"genre": "lofi", "mood": "chill", "energy": 0.38, "likes_acoustic": True},
        songs,
    )

    print_results(
        "PROFILE 3 — Deep Intense Rock",
        {"genre": "rock", "mood": "intense", "energy": 0.90, "likes_acoustic": False},
        songs,
    )

    # ------------------------------------------------------------------
    # Adversarial / edge-case profiles
    # ------------------------------------------------------------------
    print_results(
        "PROFILE 4 — ADVERSARIAL: High Energy + Sad (conflicting)",
        # High energy (0.90) but sad mood — tests whether energy pulls toward
        # metal/rock even though the user wants slow, sad blues.
        {"genre": "blues", "mood": "sad", "energy": 0.90, "likes_acoustic": False},
        songs,
    )

    print_results(
        "PROFILE 5 — ADVERSARIAL: Genre Not in Catalog (cold start)",
        # 'edm' does not exist in songs.csv — no song can earn genre points.
        # Exposes how the system degrades when the user's genre is unknown.
        {"genre": "edm", "mood": "chill", "energy": 0.50, "likes_acoustic": True},
        songs,
    )

    # ------------------------------------------------------------------
    # Experiment: double energy weight, halve genre weight
    # Hypothesis: energy-close songs from OTHER genres should rise in rank.
    # ------------------------------------------------------------------
    experimental_weights = {"genre": 1.0, "mood": 1.0, "energy": 2.0, "acoustic": 0.5}

    print_results(
        "EXPERIMENT — High-Energy Pop with doubled energy weight",
        {"genre": "pop", "mood": "happy", "energy": 0.85, "likes_acoustic": False},
        songs,
        weights=experimental_weights,
    )


if __name__ == "__main__":
    main()
