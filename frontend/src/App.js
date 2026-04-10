import { useState, useEffect } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { TEAM_MAP } from "./constants/teams";

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

function PlayerCard({ player, onClick }) {
  return (
    <div style={{
      background: "white", borderRadius: 12, padding: 16,
      border: "1px solid #d3d1c7", marginBottom: 8,
      display: "flex", alignItems: "center", gap: 16
    }}>
      <div style={{ width: 36, textAlign: "center", fontSize: 13, color: "#888780", fontWeight: 500 }}>
        #{player.rank}
      </div>
      <img
        src={`/logos/${player.team_id}.svg`}
        alt=""
        style={{ width: 42, height: 42, objectFit: "contain" }}
      />
      <img
        src={`https://fantasy.afl.com.au/media/fantasy/players/${player.id}_100.webp?v=3`}
        alt={player.full_name}
        onClick={onClick}
        style={{ width: 64, height: 64, objectFit: "contain", borderRadius: "50%", cursor: "pointer" }}
        onError={e => e.target.style.display = 'none'}
      />
      <div style={{ flex: 1 }}>
        <div
          onClick={onClick}
          style={{ fontWeight: 500, fontSize: 15, cursor: "pointer", textDecoration: "underline" }}
        >
          {player.full_name}
        </div>
        <div style={{ fontSize: 12, marginTop: 2, display: "flex", alignItems: "center", gap: 6 }}>
          <PositionBadges position={player.position} />
          <span style={{ color: "#888780" }}>${player.cost?.toLocaleString()}</span>
        </div>
      </div>
      <div style={{ display: "flex", gap: 8 }}>
        <StatBadge label="Current 2026 Avg" value={player.avg_points} />
        <StatBadge label="Career Avg" value={player.career_avg?.toFixed(1)} />
        <StatBadge label="Projected 2026 Avg" value={player.projected_avg} />
      </div>
    </div>
  );
}

function CareerHistoryTable({ playerId, history }) {
  if (!history || history.length === 0) {
    return <p style={{ color: "#888780", fontSize: 13 }}>No career history available.</p>;
  }

  return (
    <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13, marginTop: 8 }}>
      <thead>
        <tr style={{ borderBottom: "2px solid #d3d1c7" }}>
          <th style={{ textAlign: "left", padding: "6px 8px", color: "#5f5e5a", fontWeight: 500 }}>Year</th>
          <th style={{ textAlign: "center", padding: "6px 8px", color: "#5f5e5a", fontWeight: 500 }}>Games</th>
          <th style={{ textAlign: "center", padding: "6px 8px", color: "#5f5e5a", fontWeight: 500 }}>Avg</th>
          <th style={{ textAlign: "center", padding: "6px 8px", color: "#5f5e5a", fontWeight: 500 }}>High</th>
          <th style={{ textAlign: "center", padding: "6px 8px", color: "#5f5e5a", fontWeight: 500 }}>Low</th>
          <th style={{ textAlign: "center", padding: "6px 8px", color: "#5f5e5a", fontWeight: 500 }}>Total</th>
        </tr>
      </thead>
      <tbody>
        {[...history].reverse().map((season, i) => (
          <tr
            key={season.year}
            style={{
              background: i % 2 === 0 ? "#fafaf8" : "white",
              borderBottom: "1px solid #f1efe8"
            }}
          >
            <td style={{ padding: "8px 8px", fontWeight: season.year === 2026 ? 600 : 400 }}>
              {season.year}
              {season.year === 2026 && (
                <span style={{
                  marginLeft: 6, fontSize: 10, background: "#1D9E75",
                  color: "white", borderRadius: 4, padding: "1px 5px"
                }}>
                  LIVE
                </span>
              )}
            </td>
            <td style={{ textAlign: "center", padding: "8px 8px" }}>{season.games_played}</td>
            <td style={{ textAlign: "center", padding: "8px 8px", fontWeight: 500 }}>{season.avg}</td>
            <td style={{ textAlign: "center", padding: "8px 8px", color: "#1D9E75" }}>{season.high}</td>
            <td style={{ textAlign: "center", padding: "8px 8px", color: "#D85A30" }}>{season.low}</td>
            <td style={{ textAlign: "center", padding: "8px 8px", color: "#888780" }}>{season.total}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default function App() {
  const [players, setPlayers] = useState([]);
  const [history, setHistory] = useState({});
  const [search, setSearch] = useState("");
  const [posFilter, setPosFilter] = useState("ALL");
  const [loading, setLoading] = useState(true);
  const [selectedPlayer, setSelectedPlayer] = useState(null);

  useEffect(() => {
    fetch("/projections.json")
      .then(res => res.json())
      .then(data => {
        setPlayers(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));

    fetch("/player_history.json")
      .then(res => res.json())
      .then(data => setHistory(data))
      .catch(() => {});
  }, []);

  const positions = ["ALL", "DEF", "MID", "RUC", "FWD"];

  const filtered = players.filter(p => {
    const matchSearch = p.full_name?.toLowerCase().includes(search.toLowerCase());
    const matchPos = posFilter === "ALL" || p.position?.includes(posFilter);
    return matchSearch && matchPos;
  });

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: "32px 16px", fontFamily: "'Open Sans', sans-serif" }}>
      <h1 style={{ fontSize: 24, fontWeight: 500, marginBottom: 4 }}>AFL Fantasy Projector</h1>
      <p style={{ color: "#888780", marginBottom: 24 }}>2026 Season AFL Fantasy Projections</p>

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
        filtered.map(p => (
          <PlayerCard
            key={p.id}
            player={p}
            onClick={() => setSelectedPlayer(p)}
          />
        ))
      )}

      {/* Modal */}
      {selectedPlayer && (
        <div
          onClick={() => setSelectedPlayer(null)}
          style={{
            position: "fixed", top: 0, left: 0,
            width: "100%", height: "100%",
            background: "rgba(0,0,0,0.5)",
            display: "flex", justifyContent: "center", alignItems: "center",
            zIndex: 1000
          }}
        >
          <div
            onClick={e => e.stopPropagation()}
            style={{
              background: "white", padding: 24, borderRadius: 12,
              width: "90%", maxWidth: 560,
              maxHeight: "85vh", overflowY: "auto"
            }}
          >
            <button
              onClick={() => setSelectedPlayer(null)}
              style={{ float: "right", border: "none", background: "transparent", cursor: "pointer", fontSize: 16 }}
            >
              ✕
            </button>

            {/* Header */}
            <div style={{ display: "flex", alignItems: "center", gap: 16, marginBottom: 16 }}>
              <img
                src={`https://fantasy.afl.com.au/media/fantasy/players/${selectedPlayer.id}_100.webp?v=3`}
                alt={selectedPlayer.full_name}
                style={{ width: 80, height: 80, objectFit: "contain", borderRadius: "50%" }}
                onError={e => e.target.style.display = 'none'}
              />
              <div>
                <h2 style={{ margin: 0 }}>{selectedPlayer.full_name}</h2>
                <div style={{ marginTop: 4, fontSize: 14, color: "#5f5e5a" }}>
                  {TEAM_MAP[selectedPlayer.team_id]}
                </div>
                <div style={{ marginTop: 4 }}>
                  <PositionBadges position={selectedPlayer.position} />
                </div>
              </div>
              <img
                src={`/logos/${selectedPlayer.team_id}.svg`}
                alt=""
                style={{ width: 48, height: 48, objectFit: "contain", marginLeft: "auto" }}
              />
            </div>

            <p style={{ margin: "0 0 16px", fontSize: 13, color: "#5f5e5a" }}>
              <strong>Price:</strong> ${selectedPlayer.cost?.toLocaleString()}
            </p>

            {/* Stat badges */}
            <div style={{ display: "flex", gap: 8, marginBottom: 24 }}>
              <StatBadge label="2026 Avg" value={selectedPlayer.avg_points} />
              <StatBadge label="Career Avg" value={selectedPlayer.career_avg?.toFixed(1)} />
              <StatBadge label="Projected" value={selectedPlayer.projected_avg} />
            </div>

            {/* Career History */}
            <div style={{ borderTop: "1px solid #d3d1c7", paddingTop: 16 }}>
              <div style={{ fontWeight: 500, fontSize: 14, marginBottom: 8 }}>Career History</div>
              <CareerHistoryTable
                playerId={selectedPlayer.id}
                history={history[String(selectedPlayer.id)]}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}