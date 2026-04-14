# Model Card: Music Recommender Simulation

## 1. Model Name

**VibeFinder 1.0**

---

## 2. Intended Use

VibeFinder suggests the top 5 songs from an 18-song catalog that best match a user's stated taste profile. It is designed for classroom exploration of how rule-based recommender systems work — not for use with real users or in production. It assumes the user can describe their preferences in advance (favorite genre, mood, energy level, and whether they like acoustic music).

---

## 3. How the Model Works

Every song in the catalog is given a score by comparing it to the user's taste profile. The score is built from four checks:

- **Genre match** — worth the most points (2.0). If the song's genre matches the user's favorite, it gets a big boost.
- **Mood match** — worth 1.0 point. A chill user gets more credit for chill songs.
- **Energy closeness** — worth up to 1.0 point. Instead of rewarding high or low energy, the system rewards songs whose energy is *close* to the user's target. A song that is 0.02 away scores nearly 1.0; a song that is 0.50 away scores only 0.50.
- **Acousticness preference** — a 0.5 bonus when the song's texture (acoustic vs. produced) matches what the user likes.

Once every song has a score, they are sorted from highest to lowest and the top 5 are returned with a plain-language explanation of exactly which criteria contributed.

---

## 4. Data

The catalog contains **18 songs** in `data/songs.csv`. Each song has a genre, mood, energy (0.0–1.0), tempo in BPM, valence, danceability, and acousticness.

Genres represented: pop, lofi, rock, ambient, jazz, synthwave, indie pop, hip-hop, country, classical, r&b, metal, folk, blues, latin.

Moods represented: happy, chill, intense, relaxed, moody, focused, confident, nostalgic, peaceful, romantic, angry, melancholy, sad, energetic.

The starting catalog had 10 songs and was expanded to 18 to cover a broader range of genres and moods. The data is entirely synthetic — the artists and song titles are invented. Genre and mood diversity is roughly even by design, but energy skews toward mid-range values in several genres, which can affect scoring for extreme profiles.

---

## 5. Strengths

- **Perfect profile match works extremely well.** When a user's genre and mood both match a song, that song dominates the ranking (Storm Runner scored 4.49/4.5 for the Deep Intense Rock profile).
- **Energy proximity prevents nonsense results.** A lofi user (target energy 0.38) would never get a metal song in their top 5 even without a genre match — the energy gap penalizes it heavily.
- **Transparent explanations.** Every recommendation comes with a breakdown showing exactly which criteria contributed and how many points each was worth.
- **Adversarial profiles degrade gracefully.** When the user's genre is not in the catalog ("edm"), the system falls back to mood + energy + acoustic signals and still returns reasonable results (chill lofi songs for a chill EDM user).

---

## 6. Limitations and Bias

**Genre weight creates a filter bubble.** The +2.0 genre bonus is so dominant that a user with conflicting preferences — for example, blues/sad but energy 0.90 — still receives *Blue Porch Rain* (energy 0.44) as their top result, because genre+mood = 3.0 points overwhelms the energy gap penalty of 0.46. The system cannot distinguish "I want the sad *feeling* of blues at high intensity" from "give me exactly what the blues catalog sounds like."

**Catalog size amplifies genre bias.** With only 1–2 songs per genre, the genre weight locks in a predictable top pick with almost no competition. A real system with thousands of songs would have many genre matches and the energy/mood/acoustic signals would carry more relative weight.

**The system ignores tempo, valence, and danceability in scoring.** These features are stored in every song but are never consulted. A user who specifically wants high-danceability songs cannot express that preference — those dimensions are invisible to the recommender.

**Cold-start genre gap.** When the user's favorite genre does not exist in the catalog ("edm" in Profile 5), the maximum achievable score drops from 4.5 to 2.5, meaning that user's top result (2.42) would rank below any matched-genre user's bottom result. The system has no mechanism to tell the user their genre is unrepresented.

**Binary acousticness threshold.** The "is acoustic" check uses a hard cutoff of 0.6. A song with acousticness 0.59 and one with 0.61 are treated as completely opposite. A continuous proximity penalty (like energy uses) would be more accurate.

---

## 7. Evaluation

Five user profiles were tested against the 18-song catalog, plus one weight-shift experiment.

**Profile 1 — High-Energy Pop** (pop, happy, energy 0.85):
Top result: *Sunrise City* (4.47/4.5). The result felt right — it matches genre, mood, and energy almost exactly. The #4 and #5 picks (*Salsa Futura*, *Street Canvas*) were the most surprising: they ranked above many songs that feel more "pop-adjacent" simply because their energy was closest to 0.85. This exposed that non-genre songs compete on energy alone, and a score of ~1.5 feels like a weak recommendation.

**Profile 2 — Chill Lofi** (lofi, chill, energy 0.38):
Top results: *Library Rain* and *Midnight Coding* separated by only 0.01 points (4.47 vs 4.46), purely because Library Rain's energy (0.35) is 0.03 closer to the target than Midnight Coding (0.42). This surprised me — the two songs feel nearly identical in character, and energy proximity is acting as a tiebreaker at a scale too fine to mean anything musically.

**Profile 3 — Deep Intense Rock** (rock, intense, energy 0.90):
*Storm Runner* scored 4.49/4.5 — a near-perfect match. The #2 result (*Gym Hero*, pop/intense) makes sense: same mood, similar energy, no genre match. The #3–5 results are energy-close non-genre songs with little meaningful signal, which confirms the catalog is too small to provide real variety for rock listeners.

**Profile 4 — Adversarial: High Energy + Sad** (blues, sad, energy 0.90):
Most revealing test. *Blue Porch Rain* (energy 0.44) ranked #1 despite being 0.46 energy units away from the user's preference. Genre + mood totaled 3.0 points, which is larger than the maximum energy score (1.0). This showed the genre weight is strong enough to override a direct energy conflict — the system cannot honor "I want sad *and* intense" simultaneously.

**Profile 5 — Adversarial: Unknown Genre** (edm, chill, energy 0.50):
No genre points were ever awarded. The top three results were all chill/acoustic songs — reasonable by mood, but the scores (2.42, 2.35, 2.28) are much lower than any genre-matched profile. The system returns sensible fallback results but offers no signal to the user that their genre preference was completely ignored.

**Experiment — Doubled energy weight** (genre: 1.0, mood: 1.0, energy: 2.0, acoustic: 0.5):
Tested against the High-Energy Pop profile. The top result stayed the same, but *Rooftop Lights* rose from 2.41 to 3.32 and nearly tied *Gym Hero* (3.34). Cross-genre songs competitive on energy closed the gap significantly, which would improve result diversity. However, this change would hurt Profile 4 by giving energy-close metal songs undeserved authority over a sadness-oriented user.

---

## 8. Future Work

- Add tempo and danceability as scored features with their own proximity penalties, so users who care about those dimensions can express that preference.
- Replace the binary acousticness threshold with a continuous proximity penalty matching the energy formula.
- Add a diversity rule to the ranking step so the top-5 cannot all be from the same genre.
- Allow the user to specify multiple acceptable genres (e.g., `["rock", "metal"]`) rather than a single exact match.
- Surface a warning when the user's preferred genre has zero matches in the catalog.

---

## 9. Personal Reflection

Building this system made visible something that is easy to forget when using a real recommender: **the weights are a design choice, not a ground truth**. Choosing genre weight = 2.0 was an assumption about what matters most, and Profile 4 showed how that assumption breaks for a user with conflicting preferences. A "sad but intense" listener gets a quiet blues track as their top recommendation, which is exactly the wrong result — and the system has no way to know it made a mistake.

The experiment section was the most instructive part. Doubling the energy weight did not produce better results universally — it helped the pop profile but would hurt the adversarial sad profile. This is the core tension in any recommender: a weight that helps one kind of user hurts another, and without knowing what the user *actually* wanted (feedback, listening history, skips), there is no objective way to resolve it. Real systems like Spotify solve this by learning weights from behavior. Our system uses a fixed recipe, which is transparent and explainable but permanently biased toward the assumptions baked into those numbers.
