import requests
import pandas as pd
import json
import os

URL = "https://fantasy.afl.com.au/json/fantasy/players.json"

def fetch_players():
    response = requests.get(URL)
    response.raise_for_status()
    return response.json()

def parse_players(raw):
    row = []
    for p in raw:
        scores = p.get("scores", {})

        sorted_rounds = sorted(scores.keys(), key=lambda x: int(x), reverse=True)
        recent_scores = [scores[r] for r in sorted_rounds[:5]]

        positions = p.get("position", [])
        position = "/".join(positions) if positions else "UNK"

        row.append({
            "id": p["id"],
            "first_name": p["firstName"],
            "last_name": p["lastName"],
            "full_name": f"{p['firstName']} {p['lastName']}",
            "team_id": p.get("squadId"),
            "position": position,
            "cost": p.get("price"),
            "status": p.get("status"),
            "dob": p.get("dob"),
            "avg_points": p.get("averagePoints"),
            "total_points": p.get("totalPoints"),
            "games_played": p.get("gamesPlayed"),
            "high_score": p.get("highScore"),
            "low_score": p.get("lowScore"),
            "last_3_avg": p.get("last3Avg"),
            "last_5_avg": p.get("last5Avg"),
            "last_round_score": p.get("lastRoundScore"),
            "recent_scores": json.dumps(recent_scores),
        })

    return pd.DataFrame(row)

def save_players(df):
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/players.csv", index=False)
    print(f"Saved {len(df)} players to data/players.csv")

if __name__ == "__main__":
    print("Fetching players...")
    raw = fetch_players()
    print(f"Found {len(raw)} players")
    df = parse_players(raw)
    save_players(df)

    top = df[df["games_played"] > 0].sort_values("avg_points", ascending=False).head(10)
    print("\nTop 10 players by 2026 average:")
    print(top[["full_name", "position", "avg_points", "last_3_avg", "cost"]].to_string(index=False))