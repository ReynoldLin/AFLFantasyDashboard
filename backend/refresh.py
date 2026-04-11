import subprocess
import requests
import json
import os
import time
import shutil
import sys

PLAYERS_URL = "https://fantasy.afl.com.au/json/fantasy/players.json"
STATS_URL = "https://fantasy.afl.com.au/json/fantasy/players_game_stats/2026/{player_id}.json"

def calculate_fantasy_score(game):
    return (
        game.get("kicks", 0) * 3 +
        game.get("handballs", 0) * 2 +
        game.get("marks", 0) * 3 +
        game.get("tackles", 0) * 4 +
        game.get("freesFor", 0) * 1 +
        game.get("freesAgainst", 0) * -3 +
        game.get("hitouts", 0) * 1 +
        game.get("goals", 0) * 6 +
        game.get("behinds", 0) * 1
    )

def fetch_2026_stats(player_id):
    url = STATS_URL.format(player_id=player_id)
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []

def refresh_2026_history():
    print("Fetching player list...")
    players = requests.get(PLAYERS_URL).json()
    active = [p for p in players if p.get("status") != "not-playing"]

    # Load existing history
    history_path = "data/player_history.json"
    if os.path.exists(history_path):
        with open(history_path) as f:
            all_history = json.load(f)
        print(f"Loaded existing history for {len(all_history)} players")
    else:
        all_history = {}
        print("No existing history found, starting fresh")

    print(f"Refreshing 2026 stats for {len(active)} players...")

    for i, p in enumerate(active):
        player_id = str(p["id"])
        games = fetch_2026_stats(p["id"])

        if not games:
            # Remove 2026 entry if no games
            if player_id in all_history:
                all_history[player_id] = [s for s in all_history[player_id] if s["year"] != 2026]
            continue

        scores = [calculate_fantasy_score(g) for g in games]
        games_played = len(scores)
        avg = round(sum(scores) / games_played, 1) if games_played > 0 else 0

        def season_avg(key):
            vals = [g.get(key, 0) for g in games]
            return round(sum(vals) / len(vals), 1) if vals else 0

        season_2026 = {
            "year": 2026,
            "games_played": games_played,
            "avg": avg,
            "high": max(scores),
            "low": min(scores),
            "total": sum(scores),
            "scores": scores,
            "disposals": season_avg("disposals"),
            "kicks": season_avg("kicks"),
            "handballs": season_avg("handballs"),
            "marks": season_avg("marks"),
            "tackles": season_avg("tackles"),
            "goals": season_avg("goals"),
            "behinds": season_avg("behinds"),
            "hitouts": season_avg("hitouts"),
            "frees_for": season_avg("freesFor"),
            "frees_against": season_avg("freesAgainst"),
            "games": [
                {
                    "round": g.get("roundNumber"),
                    "score": calculate_fantasy_score(g),
                    "kicks": g.get("kicks"),
                    "handballs": g.get("handballs"),
                    "disposals": g.get("disposals"),
                    "marks": g.get("marks"),
                    "tackles": g.get("tackles"),
                    "goals": g.get("goals"),
                    "behinds": g.get("behinds"),
                    "hitouts": g.get("hitouts"),
                    "frees_for": g.get("freesFor"),
                    "frees_against": g.get("freesAgainst"),
                    "opponent_id": g.get("opponentSquadId"),
                    "time_on_ground": g.get("timeOnGround"),
                }
                for g in games
            ]
        }

        if player_id in all_history:
            # Replace 2026 entry
            all_history[player_id] = [s for s in all_history[player_id] if s["year"] != 2026]
            all_history[player_id].append(season_2026)
            # Sort by year
            all_history[player_id].sort(key=lambda x: x["year"])
        else:
            all_history[player_id] = [season_2026]

        if (i + 1) % 50 == 0:
            print(f"  {i + 1}/{len(active)} done...")

        time.sleep(0.05)

    with open(history_path, "w") as f:
        json.dump(all_history, f)
    print(f"Saved updated history for {len(all_history)} players")

def refresh_rounds_info():
    print("Fetching rounds info...")
    r = requests.get("https://fantasy.afl.com.au/json/fantasy/rounds.json")
    data = r.json()

    rounds_info = {}
    for rd in data:
        games = rd.get("games", [])
        teams_played = []
        fixture = {}  # team_id -> opponent_id for this round

        for g in games:
            home = g["homeId"]
            away = g["awayId"]
            # Map each team to their opponent
            fixture[str(home)] = away
            fixture[str(away)] = home
            if g.get("status") == "completed":
                teams_played.append(home)
                teams_played.append(away)

        rounds_info[str(rd["roundNumber"])] = {
            "name": rd["name"],
            "status": rd["status"],
            "isByeRound": rd["isByeRound"],
            "isEarlyByeRound": rd["isEarlyByeRound"],
            "teamsPlayed": teams_played,
            "fixture": fixture
        }

    with open("data/rounds_info.json", "w") as f:
        json.dump(rounds_info, f)
    print("Saved rounds info")

def copy_to_frontend():
    print("Copying files to frontend...")
    files = [
        ("data/player_history.json", "frontend/public/player_history.json"),
        ("data/projections.json", "frontend/public/projections.json"),
        ("data/rounds_info.json", "frontend/public/rounds_info.json"),
    ]
    for src, dst in files:
        if os.path.exists(src):
            shutil.copy(src, dst)
            print(f"  Copied {src} → {dst}")

if __name__ == "__main__":
    print("=== AFL Fantasy Dashboard Refresh ===\n")

    print("Step 1: Fetching player data...")
    subprocess.run([sys.executable, "backend/collector.py"], check=True)
    print()

    print("Step 2: Generating projections...")
    subprocess.run([sys.executable, "backend/projector.py"], check=True)
    print()

    print("Step 3: Exporting projections to JSON...")
    subprocess.run([sys.executable, "backend/generate_json.py"], check=True)
    print()

    print("Step 4: Refreshing 2026 history...")
    refresh_2026_history()
    print()

    print("Step 5: Refreshing rounds info...")
    refresh_rounds_info()
    print()

    print("Step 6: Copying files to frontend...")
    copy_to_frontend()
    print()

    print("=== Refresh complete ===")