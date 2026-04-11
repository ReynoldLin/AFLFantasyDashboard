# AFL Fantasy Dashboard

A tool to project AFL Fantasy scores for the 2026 season, built with Python and React.

## Features

- 2026 player projections based on career averages and recent form
- Player cards with headshots, team logos and position badges
- Search and filter by position
- Player modal with full career history (2014 onwards)
- Game-by-game breakdown per season with stats and opponent logos
- Colour-coded averages and games played

## Prerequisites

- Python 3.9+
- Node.js 18+
- npm 9+

## Getting Started

### Backend

```bash
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r backend/requirements.txt
```

Run the initial data pipeline:

```bash
python backend/collector.py
python backend/projector.py
python backend/generate_json.py
python backend/fetch_history.py
```

Start the API server:

```bash
uvicorn backend.main:app --reload
```

API runs on http://localhost:8000. Docs available at http://localhost:8000/docs.

### Frontend

```bash
cd frontend
npm install --legacy-peer-deps
npm start
```

Frontend runs on http://localhost:3000.

## Data Sources

- **AFL Fantasy API** — player data, 2026 scores, pricing, status and historical data

## Updating Data

To refresh player data and projections manually:

```bash
python backend/refresh.py
```

## Notes

- Career history data goes back to 2014.
- Projections are currently updated manually by re-running the data pipeline.