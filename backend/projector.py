import pandas as pd
import json
from datetime import date

def calculate_age(dob_str):
    try:
        dob = date.fromisoformat(dob_str)
        today = date.today()
        return today.year - dob.year ((today.month, today.day) < (dob.month, dob.day))
    except:
        return None

def age_factor(age):
    """
    Adjust projection based on age.
    Young players (< 23) trending up, peak (23-29), older (30+) trending down.
    """
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
    """
    Penalise players who miss a lot of games
    Full season = 23 games. Less games = less reliable
    """
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

def project_player(row):
    """
    Weighted projection combining career avg and last season avg.
    Last season weighted more heavily than career avg.
    """
    career_avg = row.get("career_avg") or 0
    last_season_avg = row.get("avg_points") or 0
    games_played = row.get("games_played") or 0

    # Need at least some data to project
    if last_season_avg == 0 and career_avg == 0:
        return None

    # If they barely played, lean more on career avg
    if games_played < 8:
        base = (career_avg * 0.7) + (last_season_avg * 0.3)
    else:
        base = (career_avg * 0.35) + (last_season_avg * 0.65)

    # Apply age and reliability adjustments
    age = row.get("age")
    adj = base * age_factor(age) * reliability_factor(games_played)

    return round(adj, 1)

def build_projections(players_df, dob_map=None):
    """
    Takes the players DataFrame and returns projections.
    dob_map: optional dict of {player_id: dob_string} for age calculations.
    """
    df = players_df.copy()

    # Add age if dob_map provided
    if dob_map:
        df["age"] = df["id"].map(lambda pid: calculate_age(dob_map.get(str(pid))))
    else:
        df["age"] = None

    # Generate projection
    df["projected_avg"] = df.apply(project_player, axis=1)

    # Drop players with no projection
    df = df[df["projected_avg"].notna()]

    # Rank by projected average
    df = df.sort_values("projected_avg", ascending=False).reset_index(drop=True)
    df["rank"] = df.index + 1

    return df

if __name__ == "__main__":
    # Load saved player data
    players_df = pd.read_csv("data/players.csv")

    projections = build_projections(players_df)

    print(f"\nProjections generated for {len(projections)} players")
    print("\nTop 20 projected players for next season:")
    cols = ["rank", "full_name", "position", "avg_points", "career_avg", "games_played", "projected_avg"]
    print(projections[cols].head(20).to_string(index=False))

    # Save projections
    projections.to_csv("data/projections.csv", index=False)
    print("\nSaved to data/projections.csv")
