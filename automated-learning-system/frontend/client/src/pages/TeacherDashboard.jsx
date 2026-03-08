import React, { useEffect, useState, useCallback } from "react";
import axios from "axios";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
  AreaChart, Area,
} from "recharts";
import { T } from "../components/coding/theme";

const API = process.env.REACT_APP_API_URL || "http://localhost:8000";

function MetricCard({ label, value, color, sub }) {
  return (
    <div style={{
      background: T.bg.surface, border: `1px solid ${color}25`,
      borderRadius: T.radius.lg, padding: "16px 22px", minWidth: 140, flex: "1 1 140px",
    }}>
      <div style={{ color: T.text.muted, fontSize: 10, marginBottom: 5 }}>{label}</div>
      <div style={{ color, fontSize: 24, fontWeight: 700, lineHeight: 1 }}>{value}</div>
      {sub && <div style={{ color: T.text.dim, fontSize: 10, marginTop: 4 }}>{sub}</div>}
    </div>
  );
}

function SectionCard({ title, children }) {
  return (
    <div style={{
      background: T.bg.surface, border: `1px solid ${T.border.default}`,
      borderRadius: T.radius.lg, padding: "18px 22px",
    }}>
      <h3 style={{ margin: "0 0 16px", color: T.text.primary, fontSize: 14, fontWeight: 600 }}>{title}</h3>
      {children}
    </div>
  );
}

const ChartTooltip = {
  contentStyle: { background: T.bg.elevated, border: `1px solid ${T.border.default}`, borderRadius: 6, color: T.text.primary, fontSize: 11 },
};

function exportCSV(rows) {
  const headers = ["user_id", "avg_emotion", "avg_performance", "engagement_score", "sessions", "last_active"];
  const lines = [headers.join(","), ...rows.map((r) => headers.map((h) => r[h] ?? "").join(","))];
  const blob = new Blob([lines.join("\n")], { type: "text/csv" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = "emoticode_dashboard.csv"; a.click();
  URL.revokeObjectURL(url);
}

export default function TeacherDashboard() {
  const [data, setData] = useState([]);
  const [summary, setSummary] = useState(null);
  const [codingStats, setCodingStats] = useState(null);
  const [emotionTrends, setEmotionTrends] = useState([]);
  const [actionDist, setActionDist] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selected, setSelected] = useState(null);

  const fetchData = useCallback(async () => {
    try {
      setError(null);
      const [dashRes, sumRes, codingRes, trendsRes, actRes] = await Promise.allSettled([
        axios.get(`${API}/analytics/dashboard`),
        axios.get(`${API}/analytics/summary`),
        axios.get(`${API}/coding/stats`),
        axios.get(`${API}/analytics/emotion-trends?hours=24`),
        axios.get(`${API}/analytics/action-distribution`),
      ]);
      if (dashRes.status   === "fulfilled") setData(dashRes.value.data);
      if (sumRes.status    === "fulfilled") setSummary(sumRes.value.data);
      if (codingRes.status === "fulfilled") setCodingStats(codingRes.value.data);
      if (trendsRes.status === "fulfilled") setEmotionTrends(trendsRes.value.data);
      if (actRes.status    === "fulfilled") setActionDist(actRes.value.data);
    } catch {
      setError("Failed to load dashboard. Is the backend running on :8000?");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
    const t = setInterval(fetchData, 20000);
    return () => clearInterval(t);
  }, [fetchData]);

  const radarData = selected ? [
    { metric: "Emotion",     value: Math.round((selected.avg_emotion     ?? 0) * 100) },
    { metric: "Performance", value: Math.round((selected.avg_performance ?? 0) * 100) },
    { metric: "Engagement",  value: Math.round((selected.engagement_score ?? 0) * 100) },
  ] : [];

  const actionChartData = Object.entries(actionDist).map(([action, count]) => ({
    action: action.charAt(0).toUpperCase() + action.slice(1),
    count,
    fill: action === "challenge" ? T.red : action === "hint" ? T.yellow : action === "relax" ? T.cyan : T.green,
  }));

  return (
    <div style={{ padding: "24px 32px", maxWidth: 1200, margin: "0 auto" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
        <div>
          <h2 style={{ margin: 0, color: T.text.primary, fontSize: 20, fontWeight: 700 }}>🎓 Teacher Dashboard</h2>
          <p style={{ margin: "4px 0 0", color: T.text.muted, fontSize: 12 }}>
            Real-time class analytics & emotion monitoring · auto-refreshes every 20s
          </p>
        </div>
        <div style={{ display: "flex", gap: 10 }}>
          <button onClick={fetchData} style={{
            background: T.bg.elevated, border: `1px solid ${T.border.default}`,
            color: T.text.muted, padding: "7px 14px", borderRadius: T.radius.md, fontSize: 12,
          }}>
            ↺ Refresh
          </button>
          <button onClick={() => exportCSV(data)} disabled={!data.length} style={{
            background: `${T.green}15`, border: `1px solid ${T.green}50`,
            color: T.green, padding: "7px 14px", borderRadius: T.radius.md, fontSize: 12,
            opacity: data.length ? 1 : 0.4,
          }}>
            ⬇ Export CSV
          </button>
        </div>
      </div>

      {error && (
        <div style={{
          background: `${T.red}12`, border: `1px solid ${T.red}40`,
          borderRadius: T.radius.lg, padding: "10px 16px", color: "#fca5a5",
          fontSize: 13, marginBottom: 20,
        }}>{error}</div>
      )}

      {/* Summary metric cards */}
      {summary && (
        <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 20 }}>
          <MetricCard label="CLASS AVG EMOTION"      value={(summary.average_emotion * 100).toFixed(1) + "%"}     color={T.green}  />
          <MetricCard label="CLASS AVG PERFORMANCE"  value={(summary.average_performance * 100).toFixed(1) + "%"} color={T.blue}   />
          <MetricCard label="CLASS ENGAGEMENT"       value={(summary.engagement_score * 100).toFixed(1) + "%"}    color={T.orange} />
          <MetricCard label="TOTAL SESSIONS"         value={summary.total_sessions ?? 0}                color={T.purple} />
          {codingStats && <>
            <MetricCard label="TOTAL SUBMISSIONS"   value={codingStats.total_submissions} color={T.cyan}   sub={`avg ${(codingStats.overall_avg_score * 100).toFixed(0)}%`} />
            <MetricCard label="PROBLEM BANK"        value={codingStats.total_problems}    color={T.yellow} />
          </>}
        </div>
      )}

      {/* Charts row */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 16 }}>

        {/* Emotion trends over 24h */}
        <SectionCard title="📈 Emotion & Performance Trends (24h)">
          {emotionTrends.length === 0 ? (
            <div style={{ color: T.text.dim, fontSize: 12, textAlign: "center", padding: "24px 0" }}>
              No emotion data yet — start a coding session to see trends.
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={180}>
              <AreaChart data={emotionTrends}>
                <defs>
                  <linearGradient id="gEmotion" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor={T.green} stopOpacity={0.3} />
                    <stop offset="95%" stopColor={T.green} stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="gPerf" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%"  stopColor={T.blue} stopOpacity={0.3} />
                    <stop offset="95%" stopColor={T.blue} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke={T.border.subtle} />
                <XAxis dataKey="hour" tick={{ fill: T.text.muted, fontSize: 9 }} tickFormatter={(v) => v.slice(11)} />
                <YAxis domain={[0, 1]} tick={{ fill: T.text.muted, fontSize: 9 }} />
                <Tooltip {...ChartTooltip} />
                <Legend wrapperStyle={{ fontSize: 11, color: T.text.muted }} />
                <Area type="monotone" dataKey="avg_emotion"     name="Emotion"     stroke={T.green} fill="url(#gEmotion)" strokeWidth={2} dot={false} />
                <Area type="monotone" dataKey="avg_performance" name="Performance" stroke={T.blue}  fill="url(#gPerf)"    strokeWidth={2} dot={false} />
              </AreaChart>
            </ResponsiveContainer>
          )}
        </SectionCard>

        {/* Adaptive action distribution */}
        <SectionCard title="🎯 Adaptive Action Distribution">
          {actionChartData.length === 0 ? (
            <div style={{ color: T.text.dim, fontSize: 12, textAlign: "center", padding: "24px 0" }}>
              No adaptive actions recorded yet.
            </div>
          ) : (
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={actionChartData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke={T.border.subtle} horizontal={false} />
                <XAxis type="number" tick={{ fill: T.text.muted, fontSize: 10 }} />
                <YAxis type="category" dataKey="action" tick={{ fill: T.text.secondary, fontSize: 11 }} width={70} />
                <Tooltip {...ChartTooltip} />
                <Bar dataKey="count" name="Count" fill={T.blue} radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </SectionCard>

        {/* Performance by difficulty */}
        {codingStats?.by_difficulty?.length > 0 && (
          <SectionCard title="📊 Performance by Difficulty">
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={codingStats.by_difficulty.map((d) => ({
                name: d.difficulty.charAt(0).toUpperCase() + d.difficulty.slice(1),
                "Avg Score": +(d.avg_score * 100).toFixed(1),
                Submissions: d.submissions,
              }))}>
                <CartesianGrid strokeDasharray="3 3" stroke={T.border.subtle} />
                <XAxis dataKey="name" tick={{ fill: T.text.muted, fontSize: 11 }} />
                <YAxis yAxisId="left" tick={{ fill: T.text.muted, fontSize: 10 }} />
                <YAxis yAxisId="right" orientation="right" tick={{ fill: T.text.muted, fontSize: 10 }} />
                <Tooltip {...ChartTooltip} />
                <Legend wrapperStyle={{ fontSize: 11, color: T.text.muted }} />
                <Bar yAxisId="left"  dataKey="Avg Score"   fill={T.green}  radius={[3,3,0,0]} />
                <Bar yAxisId="right" dataKey="Submissions" fill={T.blue}   radius={[3,3,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </SectionCard>
        )}

        {/* Student engagement bar */}
        {data.length > 0 && (
          <SectionCard title="👥 Engagement by Student">
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={data.map((r) => ({
                name: r.user_id ? `U${r.user_id}` : "Guest",
                Emotion:     +(r.avg_emotion * 100).toFixed(1),
                Performance: +(r.avg_performance * 100).toFixed(1),
                Engagement:  +(r.engagement_score * 100).toFixed(1),
              }))}>
                <CartesianGrid strokeDasharray="3 3" stroke={T.border.subtle} />
                <XAxis dataKey="name" tick={{ fill: T.text.muted, fontSize: 11 }} />
                <YAxis domain={[0, 100]} tick={{ fill: T.text.muted, fontSize: 10 }} />
                <Tooltip {...ChartTooltip} />
                <Legend wrapperStyle={{ fontSize: 11, color: T.text.muted }} />
                <Bar dataKey="Emotion"     fill={T.green}  radius={[2,2,0,0]} />
                <Bar dataKey="Performance" fill={T.blue}   radius={[2,2,0,0]} />
                <Bar dataKey="Engagement"  fill={T.orange} radius={[2,2,0,0]} />
              </BarChart>
            </ResponsiveContainer>
          </SectionCard>
        )}
      </div>

      {/* Student detail: list + radar */}
      {data.length > 0 && (
        <SectionCard title="🔍 Student Detail">
          <div style={{ display: "flex", gap: 20 }}>
            {/* Student list */}
            <div style={{ flex: 1, overflowY: "auto", maxHeight: 220 }}>
              {data.map((row) => {
                const active = selected?.user_id === row.user_id;
                const eng = row.engagement_score;
                const engColor = eng >= 0.7 ? T.green : eng >= 0.4 ? T.yellow : T.red;
                return (
                  <div key={row.user_id} onClick={() => setSelected(active ? null : row)} style={{
                    padding: "8px 12px", borderRadius: T.radius.md, cursor: "pointer",
                    marginBottom: 4, display: "flex", justifyContent: "space-between", alignItems: "center",
                    background: active ? T.bg.overlay : "transparent",
                    border: `1px solid ${active ? T.border.strong : T.border.subtle}`,
                  }}>
                    <span style={{ color: T.text.primary, fontSize: 13 }}>
                      {row.user_id ? `User ${row.user_id}` : "Guest"}
                    </span>
                    <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
                      <span style={{ color: T.text.muted, fontSize: 11 }}>{row.sessions} sessions</span>
                      <span style={{ color: engColor, fontSize: 11, fontWeight: 600 }}>
                        {(eng * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
            {/* Radar chart for selected student */}
            {selected ? (
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center" }}>
                <div style={{ color: T.text.muted, fontSize: 11, marginBottom: 8 }}>
                  {selected.user_id ? `User ${selected.user_id}` : "Guest"} profile
                </div>
                <RadarChart width={200} height={180} data={radarData}>
                  <PolarGrid stroke={T.border.default} />
                  <PolarAngleAxis dataKey="metric" tick={{ fill: T.text.muted, fontSize: 10 }} />
                  <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: T.text.dim, fontSize: 8 }} />
                  <Radar name="Student" dataKey="value" stroke={T.green} fill={T.green} fillOpacity={0.25} />
                </RadarChart>
              </div>
            ) : (
              <div style={{
                width: 200, display: "flex", alignItems: "center", justifyContent: "center",
                color: T.text.dim, fontSize: 12, textAlign: "center",
              }}>
                Click a student to see their radar profile
              </div>
            )}
          </div>
        </SectionCard>
      )}

      {/* Full student table */}
      {data.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <SectionCard title="📋 Student Summary Table">
            <div style={{ overflowX: "auto" }}>
              <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
                <thead>
                  <tr style={{ background: T.bg.elevated }}>
                    {["Student", "Sessions", "Last Active", "Avg Emotion", "Avg Performance", "Engagement", "Status"].map((h) => (
                      <th key={h} style={{
                        padding: "8px 14px", color: T.text.muted, textAlign: "left",
                        fontSize: 10, fontWeight: 700, letterSpacing: "0.06em",
                        borderBottom: `1px solid ${T.border.default}`,
                      }}>{h.toUpperCase()}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {data.map((row) => {
                    const eng = row.engagement_score;
                    const engColor = eng >= 0.7 ? T.green : eng >= 0.4 ? T.yellow : T.red;
                    const status = eng >= 0.7 ? { label: "Engaged", color: T.green } :
                                   eng >= 0.4 ? { label: "Neutral",  color: T.yellow } :
                                                { label: "Struggling", color: T.red };
                    return (
                      <tr key={row.user_id} style={{ borderBottom: `1px solid ${T.border.subtle}` }}
                          onMouseEnter={(e) => e.currentTarget.style.background = T.bg.elevated}
                          onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}>
                        <td style={{ padding: "8px 14px", color: T.text.primary }}>
                          {row.user_id ? `User ${row.user_id}` : "Guest"}
                        </td>
                        <td style={{ padding: "8px 14px", color: T.text.secondary }}>{row.sessions}</td>
                        <td style={{ padding: "8px 14px", color: T.text.muted, fontSize: 11 }}>
                          {row.last_active ? new Date(row.last_active).toLocaleString() : "—"}
                        </td>
                        <td style={{ padding: "8px 14px", color: T.green  }}>{(row.avg_emotion * 100).toFixed(1)}%</td>
                        <td style={{ padding: "8px 14px", color: T.blue   }}>{(row.avg_performance * 100).toFixed(1)}%</td>
                        <td style={{ padding: "8px 14px", color: engColor, fontWeight: 600 }}>
                          {(eng * 100).toFixed(1)}%
                        </td>
                        <td style={{ padding: "8px 14px" }}>
                          <span style={{
                            color: status.color, background: `${status.color}12`,
                            border: `1px solid ${status.color}30`,
                            borderRadius: 4, padding: "1px 8px", fontSize: 10, fontWeight: 700,
                          }}>
                            {status.label}
                          </span>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </SectionCard>
        </div>
      )}

      {!loading && data.length === 0 && (
        <div style={{
          textAlign: "center", padding: "48px 24px",
          color: T.text.muted, fontSize: 13,
          background: T.bg.surface, borderRadius: T.radius.lg,
          border: `1px solid ${T.border.subtle}`,
        }}>
          <div style={{ fontSize: 36, marginBottom: 12 }}>📊</div>
          No student data yet. Students need to use the coding platform to generate analytics.
        </div>
      )}
    </div>
  );
}
