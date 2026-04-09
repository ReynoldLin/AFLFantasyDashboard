import requests
import pandas as pd
import json
import os

URL = "https://fantasy.afl.com.au/data/afl/players.json"

POSITION_MAP = {
    1: "DEF",
    2: "MID",
    3: "RUC",
    4: "FWD"
}

def fetch_players():
    response = requests.get(URL)
    response.raise_for_status()
    return response.json()

def parse_players(raw):
    row = []
    for p in raw:
        stats = p.get("stats", {})
        scores = stats.get("scores", {})

        #Get last 3 and 5 round scores
        sorted_rounds = sorted(scores.keys(), key=lambda x: int(x), reverse=True)
        recent_scores = [scores[r] for r in sorted_rounds[:5]]

        positions = [POSITION_MAP.get(pos, "UNK") for pos in p.get("positions", [])]

        row.append({
            "id": p["id"],
            "first_name": p["first_name"],
            "last_name": p["last_name"],
            "full_name": f"{p['first_name']} {p['last_name']}",
            "team_id": p.get("squad_id"),
            "position": "/".join(positions),
            "cost": p.get("cost"),
            "status": p.get("status"),
            "avg_points": stats.get("avg_points"),
            "total_points": stats.get("total_points"),
            "games_played": stats.get("games_played"),
            "high_score": stats.get("high_score"),
            "low_score": stats.get("low_score"),
            "last_3_avg": stats.get("last_3_avg"),
            "last_5_avg": stats.get("last_5_avg"),
            "career_avg": stats.get("career_avg"),
            "proj_avg": stats.get("proj_avg"),
            "owned_by": stats.get("owned_by"),
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
    df = parse_players(raw)
    save_players(df)

    # Preview top 10 by average
    top = df[df["games_played"] > 5].sort_values("avg_points", ascending=False).head(10)
    print("\nTop 10 players by average:")
    print(top[["full_name", "position", "avg_points", "last_3_avg", "cost"]].to_string(index=False))