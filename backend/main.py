from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler
import json
import os
import sys
import time
import requests
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AFL Fantasy Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../data")

# In-memory cache
cache = {}
CACHE_TTL = 3600  # 1 hour in seconds

def get_cached(key, fetch_fn):
    now = time.time()
    if key in cache:
        data, timestamp = cache[key]
        if now - timestamp < CACHE_TTL:
            return data
    data = fetch_fn()
    cache[key] = (data, now)
    return data

def fetch_projections():
    path = os.path.join(DATA_DIR, "projections.json")
    with open(path) as f:
        return json.load(f)

def fetch_history():
    path = os.path.join(DATA_DIR, "player_history.json")
    with open(path) as f:
        return json.load(f)

def fetch_rounds():
    r = requests.get("https://fantasy.afl.com.au/json/fantasy/rounds.json")
    data = r.json()
    rounds_info = {}
    for rd in data:
        games = rd.get("games", [])
        teams_played = []
        fixture = {}
        for g in games:
            home = g["homeId"]
            away = g["awayId"]
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
    return rounds_info

def fetch_bye_rounds():
    path = os.path.join(DATA_DIR, "bye_rounds_all.json")
    with open(path) as f:
        return json.load(f)

def run_refresh():
    logger.info("Running scheduled refresh...")
    subprocess.run([sys.executable, "backend/refresh.py"], check=True)
    # Clear cache after refresh
    cache.clear()
    logger.info("Refresh complete")

@app.get("/")
def root():
    return {"message": "AFL Fantasy Dashboard API"}

@app.get("/projections")
def get_projections():
    try:
        return get_cached("projections", fetch_projections)
    except Exception as e:
        return {"error": str(e)}

@app.get("/history")
def get_history():
    try:
        return get_cached("history", fetch_history)
    except Exception as e:
        return {"error": str(e)}

@app.get("/history/{player_id}")
def get_player_history(player_id: str):
    try:
        history = get_cached("history", fetch_history)
        return history.get(player_id, [])
    except Exception as e:
        return {"error": str(e)}

@app.get("/rounds")
def get_rounds():
    try:
        return get_cached("rounds", fetch_rounds)
    except Exception as e:
        return {"error": str(e)}

@app.get("/bye-rounds-all")
def get_bye_rounds_all():
    try:
        return get_cached("bye_rounds", fetch_bye_rounds)
    except Exception as e:
        return {"error": str(e)}

@app.post("/refresh")
def manual_refresh():
    try:
        run_refresh()
        return {"status": "success", "message": "Refresh complete"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

scheduler = BackgroundScheduler()

@app.on_event("startup")
def start_scheduler():
    scheduler.add_job(run_refresh, "cron", day_of_week="thu,fri", hour=6)
    scheduler.start()
    logger.info("Scheduler started")

@app.on_event("shutdown")
def stop_scheduler():
    scheduler.shutdown()