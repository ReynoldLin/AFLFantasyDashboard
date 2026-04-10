import requests
import pandas as pd
import json
import os
import time
import math

PLAYERS_URL = "https://fantasy.afl.com.au/json/fantasy/players.json"
STATS_URL = "https://fantasy.afl.com.au/json/fantasy/players_game_stats/{year}/{player_id}.json"

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

def fetch_season_stats(player_id, year):
    url = STATS_URL.format(year=year, player_id=player_id)
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            return r.json()
    except:
        pass
    return []

def build_player_history(player, min_year=2014):
    player_id = player["id"]
    seasons = player.get("seasons", [])
    seasons = [s for s in seasons if s >= min_year]

    history = []
    for year in seasons:
        games = fetch_season_stats(player_id, year)
        if not games:
            continue

        def season_avg(key):
            vals = [g.get(key, 0) for g in games]
            return round(sum(vals) / len(vals), 1) if vals else 0

        scores = [calculate_fantasy_score(g) for g in games]
        games_played = len(scores)
        avg = round(sum(scores) / games_played, 1) if games_played > 0 else 0

        history.append({
            "year": year,
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
        })

        time.sleep(0.05)

    return history

if __name__ == "__main__":
    print("Fetching player list...")
    players = requests.get(PLAYERS_URL).json()
    print(f"Building history for {len(players)} players...")

    all_history = {}
    for i, p in enumerate(players):
        player_id = p["id"]
        history = build_player_history(p)
        if history:
            all_history[str(player_id)] = history

        if (i + 1) % 25 == 0:
            print(f"  {i + 1}/{len(players)} done...")

    os.makedirs("data", exist_ok=True)
    with open("data/player_history.json", "w") as f:
        json.dump(all_history, f)

    print(f"\nSaved history for {len(all_history)} players to data/player_history.json")

    # Preview Nick Daicos
    daicos = next((p for p in players if p["lastName"] == "Daicos" and p["firstName"] == "Nick"), None)
    if daicos:
        history = all_history.get(str(daicos["id"]), [])
        print("\nNick Daicos career history:")
        for season in history:
            print(f"  {season['year']}: {season['games_played']} games, avg {season['avg']}, high {season['high']}, low {season['low']}")