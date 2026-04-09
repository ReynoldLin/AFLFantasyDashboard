import pandas as pd
import requests
import json
from datetime import date

PLAYERS_URL = "https://fantasy.afl.com.au/data/afl/players.json"

def calculate_age(dob_str):
    try:
        dob = date.fromisoformat(dob_str)
        today = date.today()
        return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
    except:
        return None

def age_factor(age):
    if age is None:
        return 1.0
    if age < 21:
        return 1.08
    elif age < 23:
        return 1.05
    elif age <= 29:
        return 1.0
    elif age <= 32:
        return 0.97
    else:
        return 0.94

def reliability_factor(games_played, total_games=23):
    if not games_played or games_played == 0:
        return 0.85
    ratio = games_played / total_games
    if ratio >= 0.9:
        return 1.0
    elif ratio >= 0.75:
        return 0.97
    elif ratio >= 0.5:
        return 0.93
    else:
        return 0.88

def fetch_dob_map():
    """Build DOB map directly from the players CSV."""
    try:
        df = pd.read_csv("data/players.csv")
        return dict(zip(df["id"].astype(str), df["dob"]))
    except:
        return {}

def project_player(row):
    avg_points = row.get("avg_points") or 0
    last_3_avg = row.get("last_3_avg") or 0
    last_5_avg = row.get("last_5_avg") or 0
    games_played = row.get("games_played") or 0

    if avg_points == 0:
        return None

    # Weight recent form more heavily if enough games played
    if games_played >= 10:
        # Enough data — weight last 3 heavily
        base = (avg_points * 0.4) + (last_3_avg * 0.4) + (last_5_avg * 0.2)
    elif games_played >= 5:
        # Some data — balance season avg and recent
        base = (avg_points * 0.5) + (last_3_avg * 0.3) + (last_5_avg * 0.2)
    else:
        # Very few games — rely mostly on season avg
        base = avg_points

    age = row.get("age")
    adj = base * age_factor(age) * reliability_factor(games_played)

    return round(adj, 1)

def build_projections(players_df, dob_map=None):
    df = players_df.copy()

    if dob_map:
        df["age"] = df["id"].map(lambda pid: calculate_age(dob_map.get(str(pid))))
    else:
        df["age"] = None

    df["projected_avg"] = df.apply(project_player, axis=1)
    df = df[df["projected_avg"].notna()]
    df = df.sort_values("projected_avg", ascending=False).reset_index(drop=True)
    df["rank"] = df.index + 1

    return df

if __name__ == "__main__":
    players_df = pd.read_csv("data/players.csv")

    print("Fetching DOB data for age calculations...")
    dob_map = fetch_dob_map()

    projections = build_projections(players_df, dob_map=dob_map)

    print(f"\nProjections generated for {len(projections)} players")
    print("\nTop 20 projected players:")
    cols = ["rank", "full_name", "position", "avg_points", "last_3_avg", "games_played", "projected_avg"]
    print(projections[cols].head(20).to_string(index=False))

    projections.to_csv("data/projections.csv", index=False)
    print("\nSaved to data/projections.csv")