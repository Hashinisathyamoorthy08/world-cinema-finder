"""
🎬 Movie Recommendation System
Using User-Based Collaborative Filtering
"""

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# ──────────────────────────────────────────────
# STEP 1: Sample Dataset (User-Movie Ratings)
# Ratings are on a scale of 1 to 5 (0 = not watched)
# ──────────────────────────────────────────────

data = {
    'User':        ['Alice', 'Bob', 'Carol', 'David', 'Eve'],
    'Inception':   [5, 4, 0, 2, 4],
    'Interstellar':[4, 5, 4, 0, 3],
    'The Matrix':  [3, 0, 5, 4, 2],
    'Avatar':      [0, 3, 4, 5, 1],
    'Titanic':     [2, 1, 0, 3, 5],
    'Avengers':    [4, 4, 3, 0, 4],
}

df = pd.DataFrame(data).set_index('User')

print("📊 User-Movie Rating Matrix:")
print(df)
print()

# ──────────────────────────────────────────────
# STEP 2: Compute User Similarity
# ──────────────────────────────────────────────

similarity_matrix = cosine_similarity(df)
similarity_df = pd.DataFrame(similarity_matrix, index=df.index, columns=df.index)

print("🔗 User Similarity Matrix:")
print(similarity_df.round(2))
print()

# ──────────────────────────────────────────────
# STEP 3: Recommend Movies for a Target User
# ──────────────────────────────────────────────

def recommend_movies(target_user, df, similarity_df, top_n=3):
    similar_users = similarity_df[target_user].drop(target_user).sort_values(ascending=False)
    unwatched = df.loc[target_user][df.loc[target_user] == 0].index.tolist()

    if not unwatched:
        return "🎉 This user has watched all movies!"

    scores = {}
    for movie in unwatched:
        weighted_sum = 0
        similarity_sum = 0
        for user, sim_score in similar_users.items():
            rating = df.loc[user, movie]
            if rating > 0:
                weighted_sum += sim_score * rating
                similarity_sum += sim_score
        if similarity_sum > 0:
            scores[movie] = weighted_sum / similarity_sum

    if not scores:
        return "❌ Not enough data to make recommendations."

    recommendations = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return recommendations

# ──────────────────────────────────────────────
# STEP 4: Print Recommendations
# ──────────────────────────────────────────────

for user in df.index:
    print(f"🎬 Top movie recommendations for {user}:")
    recs = recommend_movies(user, df, similarity_df)
    if isinstance(recs, str):
        print(f"   {recs}")
    else:
        for i, (movie, score) in enumerate(recs, 1):
            print(f"   {i}. {movie} (Predicted Rating: {score:.2f})")
    print()
    