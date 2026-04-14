import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass


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

    def _score(self, user: UserProfile, song: Song) -> Tuple[float, List[str]]:
        """Score a single Song against a UserProfile. Returns (score, reasons)."""
        score = 0.0
        reasons = []

        # Genre match: +2.0 (strongest signal)
        if song.genre == user.favorite_genre:
            score += 2.0
            reasons.append(f"genre match ({song.genre})")

        # Mood match: +1.0
        if song.mood == user.favorite_mood:
            score += 1.0
            reasons.append(f"mood match ({song.mood})")

        # Energy proximity: up to +1.0 — rewards closeness, not just high/low
        energy_sim = 1.0 - abs(song.energy - user.target_energy)
        score += energy_sim
        reasons.append(f"energy similarity {energy_sim:.2f}")

        # Acousticness preference: +0.5 bonus when the song matches the user's acoustic taste
        song_is_acoustic = song.acousticness >= 0.6
        if song_is_acoustic == user.likes_acoustic:
            score += 0.5
            reasons.append("acousticness preference match")

        return score, reasons

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        scored = sorted(self.songs, key=lambda s: self._score(user, s)[0], reverse=True)
        return scored[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        _, reasons = self._score(user, song)
        return ", ".join(reasons)


# ---------------------------------------------------------------------------
# Functional API — used by src/main.py
# ---------------------------------------------------------------------------

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file and casts numeric columns to float/int.
    Required by src/main.py
    """
    songs = []
    with open(csv_path, newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row['id'] = int(row['id'])
            row['energy'] = float(row['energy'])
            row['tempo_bpm'] = float(row['tempo_bpm'])
            row['valence'] = float(row['valence'])
            row['danceability'] = float(row['danceability'])
            row['acousticness'] = float(row['acousticness'])
            songs.append(row)
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song dict against user preference dict.

    Algorithm Recipe
    ----------------
    +2.0  genre match        (strongest categorical signal)
    +1.0  mood match         (situational signal)
    +0–1.0 energy proximity  (1.0 - |song.energy - target_energy|)
    +0.5  acousticness match (bonus when acoustic preference aligns)

    Max possible score: 4.5

    Required by recommend_songs() and src/main.py
    """
    score = 0.0
    reasons = []

    # Genre match: +2.0
    if song['genre'] == user_prefs.get('genre', ''):
        score += 2.0
        reasons.append(f"genre match ({song['genre']})")

    # Mood match: +1.0
    if song['mood'] == user_prefs.get('mood', ''):
        score += 1.0
        reasons.append(f"mood match ({song['mood']})")

    # Energy proximity: up to +1.0
    target_energy = user_prefs.get('energy', 0.5)
    energy_sim = 1.0 - abs(song['energy'] - target_energy)
    score += energy_sim
    reasons.append(f"energy similarity {energy_sim:.2f}")

    # Acousticness preference: +0.5
    likes_acoustic = user_prefs.get('likes_acoustic', False)
    song_is_acoustic = song['acousticness'] >= 0.6
    if song_is_acoustic == likes_acoustic:
        score += 0.5
        reasons.append("acousticness preference match")

    return score, reasons


def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """
    Scores every song, sorts by score descending, returns the top-k.
    Required by src/main.py
    """
    scored = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        explanation = ", ".join(reasons)
        scored.append((song, score, explanation))

    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:k]
