"""
Command line runner for the Music Recommender Simulation.

Run with:
    python -m src.main
"""

from src.recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")
    print(f"Loaded songs: {len(songs)}")

    # User taste profile — all features the scoring rule uses
    user_prefs = {
        "genre": "rock",          # favorite genre
        "mood": "intense",        # favorite mood
        "energy": 0.85,           # target energy (0.0 = very calm, 1.0 = very intense)
        "tempo_bpm": 140,         # target tempo in bpm
        "valence": 0.50,          # target positivity (0.0 = dark, 1.0 = upbeat)
        "danceability": 0.65,     # target danceability
        "acousticness": 0.10,     # target acousticness
        "likes_acoustic": False,  # acoustic preference flag
    }

    print(f"\nProfile: genre={user_prefs['genre']} | mood={user_prefs['mood']} | energy={user_prefs['energy']}\n")
    print("-" * 55)

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print(f"\nTop {len(recommendations)} Recommendations\n")
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"  {rank}. {song['title']} by {song['artist']}")
        print(f"     Score : {score:.2f} / 4.50")
        print(f"     Why   : {explanation}")
        print()


if __name__ == "__main__":
    main()
