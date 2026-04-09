import { useState, useEffect } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";

const POSITION_COLORS = {
  DEF: "#F38182",
  MID: "#EBF19F",
  RUC: "#A8A8FB",
  FWD: "#ABF5CA",
};

function getPositionColor(position) {
  const primary = position?.split("/")[0];
  return POSITION_COLORS[primary] || "#888780";
}

function StatBadge({ label, value }) {
  return (
    <div style={{
      textAlign: "center", padding: "8px 16px",
      background: "#f1efe8", borderRadius: 8, minWidth: 80
    }}>
      <div style={{ fontSize: 11, color: "#5f5e5a", marginBottom: 2 }}>{label}</div>
      <div style={{ fontSize: 16, fontWeight: 500 }}>{value ?? "—"}</div>
    </div>
  );
}

function PositionBadges({ position }) {
  const parts = position?.split("/") || [];
  if (parts.length === 1) {
    return (
      <span style={{
        background: getPositionColor(parts[0]),
        color: "black", borderRadius: 4, padding: "1px 6px", fontSize: 11
      }}>
        {parts[0]}
      </span>
    );
  }
  const color1 = getPositionColor(parts[0]);
  const color2 = getPositionColor(parts[1]);
  return (
    <span style={{
      background: `linear-gradient(125deg, ${color1} 50%, ${color2} 50%)`,
      color: "black", borderRadius: 4, padding: "1px 6px", fontSize: 11
    }}>
      {parts.join("/")}
    </span>
  );
}

function PlayerCard({ player }) {
  return (
    <div style={{
      background: "white", borderRadius: 12, padding: 16,
      border: "1px solid #d3d1c7", marginBottom: 8,
      display: "flex", alignItems: "center", gap: 16
    }}>
      <div style={{ width: 36, textAlign: "center", fontSize: 13, color: "#888780", fontWeight: 500 }}>
        #{player.rank}
      </div>
      <div style={{ flex: 1 }}>
        <div style={{ fontWeight: 500, fontSize: 15 }}>{player.full_name}</div>
        <div style={{ fontSize: 12, marginTop: 2, display: "flex", alignItems: "center", gap: 6 }}>
          <PositionBadges position={player.position} />
          <span style={{ color: "#888780" }}>${player.cost?.toLocaleString()}</span>
        </div>
      </div>
      <div style={{ display: "flex", gap: 8 }}>
        <StatBadge label="2025 Avg" value={player.avg_points} />
        <StatBadge label="Career Avg" value={player.career_avg?.toFixed(1)} />
        <StatBadge label="Projected" value={player.projected_avg} />
      </div>
    </div>
  );
}

export default function App() {
  const [players, setPlayers] = useState([]);
  const [search, setSearch] = useState("");
  const [posFilter, setPosFilter] = useState("ALL");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/projections.json")
      .then(res => res.json())
      .then(data => {
        setPlayers(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const positions = ["ALL", "DEF", "MID", "RUC", "FWD"];

  const filtered = players.filter(p => {
    const matchSearch = p.full_name?.toLowerCase().includes(search.toLowerCase());
    const matchPos = posFilter === "ALL" || p.position?.includes(posFilter);
    return matchSearch && matchPos;
  });

  const top10 = filtered.slice(0, 10);

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: "32px 16px", fontFamily: "sans-serif" }}>
      <h1 style={{ fontSize: 24, fontWeight: 500, marginBottom: 4 }}>AFL Fantasy Projector</h1>
      <p style={{ color: "#888780", marginBottom: 24 }}>2026 Season Projections Based on 2025 Data</p>

      {/* Filters */}
      <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
        <input
          placeholder="Search player..."
          value={search}
          onChange={e => setSearch(e.target.value)}
          style={{
            flex: 1, padding: "8px 12px", borderRadius: 8,
            border: "1px solid #d3d1c7", fontSize: 14, outline: "none"
          }}
        />
        {positions.map(pos => (
          <button key={pos} onClick={() => setPosFilter(pos)} style={{
            padding: "8px 14px", borderRadius: 8, fontSize: 13, cursor: "pointer",
            border: "1px solid #d3d1c7",
            background: posFilter === pos ? "#1D9E75" : "white",
            color: posFilter === pos ? "white" : "#3d3d3a",
            fontWeight: posFilter === pos ? 500 : 400,
          }}>
            {pos}
          </button>
        ))}
      </div>

      {/* Player List */}
      {loading ? (
        <div style={{ color: "#888780", textAlign: "center", padding: 40 }}>Loading projections...</div>
      ) : filtered.length === 0 ? (
        <div style={{ color: "#888780", textAlign: "center", padding: 40 }}>No players found</div>
      ) : (
        filtered.map(p => <PlayerCard key={p.id} player={p} />)
      )}
    </div>
  );
}