import pandas as pd
import json
import os
import math

df = pd.read_csv("data/projections.csv")

players = []
for record in df.to_dict(orient="records"):
    cleaned = {}
    for k, v in record.items():
        if isinstance(v, float) and math.isnan(v):
            cleaned[k] = None
        else:
            cleaned[k] = v
    players.append(cleaned)

out_path = os.path.join("frontend", "public", "projections.json")
with open(out_path, "w") as f:
    json.dump(players, f)

print(f"Written {len(players)} players to {out_path}")