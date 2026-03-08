import React, { useEffect, useState, useCallback } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import {
  XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer, AreaChart, Area,
} from "recharts";
import { T, Badge } from "../components/coding/theme";

const API    = process.env.REACT_APP_API_URL || "http://localhost:8000";
const WS_URL = process.env.REACT_APP_WS_URL  || "ws://localhost:8000/ws/emotion";

/* ── Tiny metric card ───────────────────────────────────────────── */
function MetricCard({ icon, label, value, color, sub }) {
  return (
    <div style={{
      background:   T.bg.surface,
      border:       `1px solid ${color}25`,
      borderRadius: T.radius.lg,
      padding:      "18px 22px",
      minWidth:     140,
      flex:         "1 1 140px",
    }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
        <span style={{ fontSize: 18 }}>{icon}</span>
        <span style={{ color: T.text.muted, fontSize: 11 }}>{label}</span>
      </div>
      <div style={{ color, fontSize: 28, fontWeight: 700, lineHeight: 1 }}>{value}</div>
      {sub && <div style={{ color: T.text.dim, fontSize: 10, marginTop: 4 }}>{sub}</div>}
    </div>
  );
}

/* ── Section header ─────────────────────────────────────────────── */
function SectionHead({ title, action }) {
  return (
    <div style={{
      display:        "flex",
      justifyContent: "space-between",
      alignItems:     "center",
      marginBottom:   14,
    }}>
      <h3 style={{ margin: 0, color: T.text.primary, fontSize: 14, fontWeight: 600 }}>{title}</h3>
      {action}
    </div>
  );
}

/* ── Custom recharts tooltip ────────────────────────────────────── */
const DarkTooltip = {
  contentStyle: {
    background: T.bg.elevated,
    border:     `1px solid ${T.border.default}`,
    borderRadius: 6,
    color:       T.text.primary,
    fontSize:    11,
  },
};

export default function Dashboard() {
  const navigate   = useNavigate();
  const [analytics,    setAnalytics]    = useState(null);
  const [codingStats,  setCodingStats]  = useState(null);
  const [problems,     setProblems]     = useState([]);
  const [recentSubs,   setRecentSubs]   = useState([]);
  const [history,      setHistory]      = useState([]);
  const [error,        setError]        = useState(null);
  const [loading,      setLoading]      = useState(true);
  const [wsStatus,     setWsStatus]     = useState("disconnected");
  const [liveEmotion,  setLiveEmotion]  = useState(null);

  /* Solved set from localStorage */
  const solved = (() => {
    try { return JSON.parse(localStorage.getItem("solvedProblems") || "{}"); }
    catch { return {}; }
  })();
  const solvedCount = Object.keys(solved).length;

  /* ── Data fetching ─────────────────────────────────────────────── */
  const fetchAll = useCallback(async () => {
    try {
      setError(null);
      const userId = parseInt(localStorage.getItem("userId") || "1", 10) || 1;
      const [anaRes, codingRes, probRes, subRes] = await Promise.allSettled([
        axios.get(`${API}/analytics/summary`),
        axios.get(`${API}/coding/stats`),
        axios.get(`${API}/coding/problems`),
        axios.get(`${API}/coding/submissions/${userId}`),
      ]);
      if (anaRes.status    === "fulfilled") setAnalytics(anaRes.value.data);
      if (codingRes.status === "fulfilled") setCodingStats(codingRes.value.data);
      if (probRes.status   === "fulfilled") setProblems(probRes.value.data);
      if (subRes.status    === "fulfilled") setRecentSubs((subRes.value.data || []).slice(0, 8));
    } catch {
      setError("Could not load analytics — is the backend running on :8000?");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAll();
    const t = setInterval(fetchAll, 15000);
    return () => clearInterval(t);
  }, [fetchAll]);

  /* ── Live WebSocket emotion feed ───────────────────────────────── */
  useEffect(() => {
    let ws;
    try {
      ws = new WebSocket(WS_URL);
      ws.onopen  = () => setWsStatus("connected");
      ws.onclose = () => setWsStatus("disconnected");
      ws.onerror = () => setWsStatus("error");
      ws.onmessage = (evt) => {
        try {
          const d = JSON.parse(evt.data);
          if (d.emotion_score !== undefined) {
            setLiveEmotion(d.emotion_score);
            setHistory((prev) => [
              ...prev.slice(-59),
              {
                t:           new Date().toLocaleTimeString("en", { hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit" }),
                emotion:     +d.emotion_score.toFixed(3),
                performance: +( d.performance_score ?? 0).toFixed(3),
              },
            ]);
          }
        } catch {}
      };
    } catch {}
    return () => ws && ws.close();
  }, []);

  /* ── Derived stats ─────────────────────────────────────────────── */
  const totalProblems  = problems.length;
  const easyCount      = problems.filter((p) => p.difficulty === "easy").length;
  const medCount       = problems.filter((p) => p.difficulty === "medium").length;
  const hardCount      = problems.filter((p) => p.difficulty === "hard").length;
  const avgScore       = codingStats ? (codingStats.overall_avg_score * 100).toFixed(1) : null;
  const totalSubs      = codingStats?.total_submissions ?? 0;

  /* ── WS dot colour ─────────────────────────────────────────────── */
  const wsDot = wsStatus === "connected" ? T.green : wsStatus === "error" ? T.red : T.text.dim;

  return (
    <div style={{
      padding:  "24px 32px",
      maxWidth: 1100,
      margin:   "0 auto",
    }}>

      {/* ── Page header ──────────────────────────────────────────── */}
      <div style={{
        display:        "flex",
        justifyContent: "space-between",
        alignItems:     "flex-start",
        marginBottom:   24,
        flexWrap:       "wrap",
        gap:            12,
      }}>
        <div>
          <h2 style={{ margin: 0, color: T.text.primary, fontSize: 20, fontWeight: 700 }}>
            📊 Learning Dashboard
          </h2>
          <div style={{ display: "flex", alignItems: "center", gap: 6, marginTop: 5 }}>
            <span style={{ width: 7, height: 7, borderRadius: "50%", background: wsDot, display: "inline-block" }} />
            <span style={{ color: T.text.muted, fontSize: 11 }}>
              Emotion feed: {wsStatus}
              {liveEmotion !== null && (
                <span style={{ color: T.green, marginLeft: 8 }}>
                  ● {(liveEmotion * 100).toFixed(0)}%
                </span>
              )}
            </span>
          </div>
        </div>

        <div style={{ display: "flex", gap: 8 }}>
          <button
            onClick={() => navigate("/problems")}
            style={{
              background:   `${T.blue}18`,
              border:       `1px solid ${T.blue}50`,
              color:        T.blue,
              padding:      "7px 16px",
              borderRadius: T.radius.md,
              cursor:       "pointer",
              fontSize:     13,
            }}
          >
            📚 Problem Bank
          </button>
          <button
            onClick={() => navigate("/code")}
            style={{
              background:   `${T.green}15`,
              border:       `1px solid ${T.green}50`,
              color:        T.green,
              padding:      "7px 16px",
              borderRadius: T.radius.md,
              cursor:       "pointer",
              fontSize:     13,
            }}
          >
            💻 Start Coding
          </button>
          <button
            onClick={fetchAll}
            style={{
              background:   T.bg.elevated,
              border:       `1px solid ${T.border.default}`,
              color:        T.text.muted,
              padding:      "7px 12px",
              borderRadius: T.radius.md,
              cursor:       "pointer",
              fontSize:     12,
            }}
          >
            ↺ Refresh
          </button>
        </div>
      </div>

      {/* ── Error banner ─────────────────────────────────────────── */}
      {error && (
        <div style={{
          background:   `${T.red}12`,
          border:       `1px solid ${T.red}40`,
          borderRadius: T.radius.lg,
          padding:      "10px 16px",
          color:        "#fca5a5",
          fontSize:     13,
          marginBottom: 20,
        }}>
          ⚠ {error}
        </div>
      )}

      {/* ── Emotion / performance metric cards ───────────────────── */}
      {loading ? (
        <div style={{ color: T.text.muted, fontSize: 13, padding: "20px 0" }}>Loading analytics…</div>
      ) : (
        <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 24 }}>
          <MetricCard
            icon="😊" label="Avg Emotion"
            value={analytics ? (analytics.average_emotion * 100).toFixed(1) + "%" : "—"}
            color={T.green}
          />
          <MetricCard
            icon="🎯" label="Avg Performance"
            value={analytics ? (analytics.average_performance * 100).toFixed(1) + "%" : "—"}
            color={T.blue}
          />
          <MetricCard
            icon="⚡" label="Engagement"
            value={analytics ? (analytics.engagement_score * 100).toFixed(1) + "%" : "—"}
            color={T.orange}
          />
          <MetricCard
            icon="✅" label="Problems Solved"
            value={solvedCount}
            color={T.purple}
            sub={`out of ${totalProblems}`}
          />
          <MetricCard
            icon="📬" label="Total Submissions"
            value={totalSubs}
            color={T.cyan}
            sub={avgScore ? `avg score ${avgScore}%` : undefined}
          />
        </div>
      )}

      {/* ── Learning Insights ────────────────────────────────────── */}
      <div style={{
        background:   T.bg.surface,
        border:       `1px solid ${T.border.default}`,
        borderRadius: T.radius.lg,
        padding:      "18px 22px",
        marginBottom: 20,
      }}>
        <SectionHead title="🎓 Learning Insights" />
        <div style={{ display: "flex", gap: 20, flexWrap: "wrap" }}>

          {/* Progress bar per difficulty */}
          {[
            { diff: "easy",   label: "Easy",   count: easyCount,  color: T.green,  solved: 0 },
            { diff: "medium", label: "Medium", count: medCount,   color: T.yellow, solved: 0 },
            { diff: "hard",   label: "Hard",   count: hardCount,  color: T.red,    solved: 0 },
          ].map(({ diff, label, count, color }) => {
            /* Count solved per difficulty from problems list */
            const diffSolved = problems
              .filter((p) => p.difficulty === diff && solved[p.id])
              .length;
            const pct = count > 0 ? Math.round((diffSolved / count) * 100) : 0;
            return (
              <div key={diff} style={{ flex: "1 1 140px" }}>
                <div style={{
                  display:        "flex",
                  justifyContent: "space-between",
                  marginBottom:   5,
                }}>
                  <span style={{ color, fontSize: 12, fontWeight: 600 }}>{label}</span>
                  <span style={{ color: T.text.muted, fontSize: 11 }}>
                    {diffSolved} / {count}
                  </span>
                </div>
                <div style={{ height: 6, background: T.border.subtle, borderRadius: 3 }}>
                  <div style={{
                    width:      `${pct}%`,
                    height:     "100%",
                    background: color,
                    borderRadius: 3,
                    transition: "width 0.8s ease",
                  }} />
                </div>
                <div style={{ color: T.text.muted, fontSize: 10, marginTop: 3 }}>{pct}% complete</div>
              </div>
            );
          })}

          {/* Coding stats summary */}
          {codingStats && (
            <div style={{
              flex:         "1 1 160px",
              background:   T.bg.elevated,
              borderRadius: T.radius.md,
              padding:      "10px 14px",
              border:       `1px solid ${T.border.default}`,
            }}>
              <div style={{ color: T.text.muted, fontSize: 10, marginBottom: 8 }}>PERFORMANCE BY DIFFICULTY</div>
              {codingStats.by_difficulty?.map((d) => (
                <div key={d.difficulty} style={{
                  display:        "flex",
                  justifyContent: "space-between",
                  marginBottom:   5,
                  fontSize:       11,
                }}>
                  <span style={{
                    color: T.diff[d.difficulty]?.color || T.text.secondary,
                    textTransform: "capitalize",
                    fontWeight: 500,
                  }}>
                    {d.difficulty}
                  </span>
                  <span style={{ color: T.text.secondary }}>
                    {(d.avg_score * 100).toFixed(0)}%
                    <span style={{ color: T.text.dim, marginLeft: 5 }}>
                      ({d.submissions} subs)
                    </span>
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* ── Live Emotion Timeline chart ───────────────────────────── */}
      {history.length > 2 && (
        <div style={{
          background:   T.bg.surface,
          border:       `1px solid ${T.border.default}`,
          borderRadius: T.radius.lg,
          padding:      "18px 22px",
          marginBottom: 20,
        }}>
          <SectionHead
            title="📈 Live Emotion & Performance"
            action={
              <span style={{
                color:     T.text.muted,
                fontSize:  10,
                background: T.bg.elevated,
                padding:   "2px 8px",
                borderRadius: T.radius.sm,
                border:    `1px solid ${T.border.default}`,
              }}>
                {history.length} data points
              </span>
            }
          />
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={history} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="gEmotion" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor={T.green}  stopOpacity={0.25} />
                  <stop offset="95%" stopColor={T.green}  stopOpacity={0} />
                </linearGradient>
                <linearGradient id="gPerf" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor={T.blue}   stopOpacity={0.25} />
                  <stop offset="95%" stopColor={T.blue}   stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke={T.border.subtle} />
              <XAxis dataKey="t"  tick={{ fontSize: 9, fill: T.text.muted }} tickLine={false} />
              <YAxis domain={[0, 1]} tick={{ fontSize: 9, fill: T.text.muted }} tickLine={false} />
              <Tooltip {...DarkTooltip} />
              <Legend wrapperStyle={{ fontSize: 11, color: T.text.secondary }} />
              <Area type="monotone" dataKey="emotion"     stroke={T.green} fill="url(#gEmotion)" dot={false} name="Emotion"     strokeWidth={2} />
              <Area type="monotone" dataKey="performance" stroke={T.blue}  fill="url(#gPerf)"    dot={false} name="Performance" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* ── Quick Start (no data state) ───────────────────────────── */}
      {!loading && history.length === 0 && (
        <div style={{
          background:   T.bg.surface,
          border:       `1px dashed ${T.border.strong}`,
          borderRadius: T.radius.lg,
          padding:      "32px 24px",
          textAlign:    "center",
          marginBottom: 20,
        }}>
          <div style={{ fontSize: 40, marginBottom: 12 }}>🚀</div>
          <div style={{ color: T.text.primary, fontSize: 15, fontWeight: 600, marginBottom: 8 }}>
            Ready to start?
          </div>
          <div style={{ color: T.text.muted, fontSize: 13, marginBottom: 20 }}>
            The emotion timeline will appear here once you start a coding session with webcam enabled.
          </div>
          <button
            onClick={() => navigate("/problems")}
            style={{
              background:   T.blue,
              border:       "none",
              color:        "#fff",
              padding:      "9px 24px",
              borderRadius: T.radius.md,
              cursor:       "pointer",
              fontSize:     13,
              fontWeight:   600,
            }}
          >
            Browse Problems →
          </button>
        </div>
      )}

      {/* ── Recent Submissions ────────────────────────────────────── */}
      {recentSubs.length > 0 && (
        <div style={{
          background:   T.bg.surface,
          border:       `1px solid ${T.border.default}`,
          borderRadius: T.radius.lg,
          padding:      "18px 22px",
          marginBottom: 20,
        }}>
          <SectionHead title="🕒 Recent Submissions" />
          <div style={{ display: "flex", flexDirection: "column", gap: 5 }}>
            {recentSubs.map((s) => {
              const prob = problems.find((p) => p.id === s.problem_id);
              const allPass = s.passed === s.total;
              const partial = s.passed > 0 && s.passed < s.total;
              const col = allPass ? T.green : partial ? T.yellow : T.red;
              const label = allPass ? "✅ PASS" : partial ? `⚠ ${s.passed}/${s.total}` : "✗ FAIL";
              return (
                <div
                  key={s.id}
                  onClick={() => prob && navigate(`/code/${prob.id}`)}
                  style={{
                    display:      "flex",
                    alignItems:   "center",
                    gap:          12,
                    padding:      "7px 12px",
                    background:   T.bg.elevated,
                    border:       `1px solid ${T.border.subtle}`,
                    borderRadius: T.radius.md,
                    cursor:       prob ? "pointer" : "default",
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.borderColor = T.border.strong}
                  onMouseLeave={(e) => e.currentTarget.style.borderColor = T.border.subtle}
                >
                  <span style={{ color: col, fontWeight: 700, fontSize: 11, minWidth: 70 }}>{label}</span>
                  {prob && <Badge difficulty={prob.difficulty} />}
                  <span style={{ color: T.text.secondary, fontSize: 13, flex: 1 }}>
                    {prob?.title || `Problem #${s.problem_id}`}
                  </span>
                  <span style={{ color: T.text.dim, fontSize: 10 }}>
                    {new Date(s.created_at).toLocaleString()}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* ── Problem Bank summary ──────────────────────────────────── */}
      {problems.length > 0 && (
        <div style={{
          background:   T.bg.surface,
          border:       `1px solid ${T.border.default}`,
          borderRadius: T.radius.lg,
          padding:      "18px 22px",
        }}>
          <SectionHead
            title="📚 Problem Bank"
            action={
              <button
                onClick={() => navigate("/problems")}
                style={{
                  background:   "none",
                  border:       `1px solid ${T.border.default}`,
                  color:        T.text.muted,
                  padding:      "4px 12px",
                  borderRadius: T.radius.sm,
                  cursor:       "pointer",
                  fontSize:     11,
                }}
              >
                View All →
              </button>
            }
          />
          {/* Recently unsolved problems as a preview */}
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            {problems
              .filter((p) => !solved[p.id])
              .slice(0, 5)
              .map((p) => (
                <div
                  key={p.id}
                  onClick={() => navigate(`/code/${p.id}`)}
                  style={{
                    display:      "flex",
                    alignItems:   "center",
                    gap:          12,
                    padding:      "8px 12px",
                    background:   T.bg.elevated,
                    border:       `1px solid ${T.border.subtle}`,
                    borderRadius: T.radius.md,
                    cursor:       "pointer",
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.borderColor = T.border.strong}
                  onMouseLeave={(e) => e.currentTarget.style.borderColor = T.border.subtle}
                >
                  <Badge difficulty={p.difficulty} />
                  <span style={{ color: T.text.secondary, fontSize: 13, flex: 1 }}>{p.title}</span>
                  <span style={{ color: T.text.dim, fontSize: 11 }}>{p.category || ""}</span>
                  <span style={{ color: T.text.muted, fontSize: 11 }}>→</span>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  );
}
