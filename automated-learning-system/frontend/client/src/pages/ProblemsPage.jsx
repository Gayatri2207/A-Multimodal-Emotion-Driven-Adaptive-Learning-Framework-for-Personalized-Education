import React, { useEffect, useState, useMemo } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { T, Badge } from "../components/coding/theme";

const API = process.env.REACT_APP_API_URL || "http://localhost:8000";

function SolvedBadge() {
  return (
    <span style={{
      background:   `${T.green}12`,
      color:        T.green,
      border:       `1px solid ${T.green}30`,
      borderRadius: T.radius.sm,
      padding:      "2px 8px",
      fontSize:     10,
      fontWeight:   700,
    }}>
      ✓ Solved
    </span>
  );
}

export default function ProblemsPage() {
  const navigate = useNavigate();
  const [problems, setProblems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState("");
  const [diffFilter, setDiffFilter] = useState("all");
  const [catFilter, setCatFilter] = useState("all");
  const [sortField, setSortField] = useState("id");
  const [sortDir, setSortDir] = useState("asc");

  // Track solved problems in localStorage (keyed by problem id)
  const [solved, setSolved] = useState(() => {
    try { return JSON.parse(localStorage.getItem("solvedProblems") || "{}"); }
    catch { return {}; }
  });

  useEffect(() => {
    axios.get(`${API}/coding/problems`)
      .then(({ data }) => { setProblems(data); setLoading(false); })
      .catch(() => { setError("Cannot reach backend. Is it running on :8000?"); setLoading(false); });
  }, []);

  // Also load progress from backend (uses authenticated user_id or guest=1)
  useEffect(() => {
    const userId = parseInt(localStorage.getItem("userId") || "1", 10) || 1;
    axios.get(`${API}/coding/progress/${userId}`)
      .then(({ data }) => {
        const s = {};
        (data.problems || []).forEach((p) => { if (p.solved) s[p.problem_id] = true; });
        setSolved((prev) => {
          const merged = { ...prev, ...s };
          localStorage.setItem("solvedProblems", JSON.stringify(merged));
          return merged;
        });
      })
      .catch(() => {});
  }, []);

  const categories = useMemo(() => {
    const cats = [...new Set(problems.map((p) => p.category).filter(Boolean))].sort();
    return cats;
  }, [problems]);

  const counts = useMemo(() => {
    const c = { easy: 0, medium: 0, hard: 0, total: 0 };
    problems.forEach((p) => { c[p.difficulty] = (c[p.difficulty] || 0) + 1; c.total += 1; });
    return c;
  }, [problems]);

  const filtered = useMemo(() => {
    let list = [...problems];
    if (diffFilter !== "all") list = list.filter((p) => p.difficulty === diffFilter);
    if (catFilter !== "all") list = list.filter((p) => p.category === catFilter);
    if (search.trim()) {
      const q = search.toLowerCase();
      list = list.filter((p) => p.title.toLowerCase().includes(q) || (p.category || "").toLowerCase().includes(q));
    }
    list.sort((a, b) => {
      let av = a[sortField], bv = b[sortField];
      if (typeof av === "string") av = av.toLowerCase();
      if (typeof bv === "string") bv = bv.toLowerCase();
      if (av < bv) return sortDir === "asc" ? -1 : 1;
      if (av > bv) return sortDir === "asc" ? 1 : -1;
      return 0;
    });
    return list;
  }, [problems, diffFilter, catFilter, search, sortField, sortDir]);

  const toggleSort = (field) => {
    if (sortField === field) setSortDir((d) => d === "asc" ? "desc" : "asc");
    else { setSortField(field); setSortDir("asc"); }
  };

  const sortIcon = (field) => sortField === field ? (sortDir === "asc" ? " ↑" : " ↓") : "";

  if (loading) return <div style={{ padding: 32, color: T.text.muted, fontSize: 13 }}>Loading problems…</div>;
  if (error)   return <div style={{ padding: 32, color: "#fca5a5", fontSize: 13 }}>{error}</div>;

  return (
    <div style={{ padding: "24px 32px", maxWidth: 1100, margin: "0 auto" }}>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "baseline", gap: 16, marginBottom: 20 }}>
        <h2 style={{ margin: 0, color: T.text.primary, fontSize: 20, fontWeight: 700 }}>📚 Problem Bank</h2>
        <span style={{ color: T.text.muted, fontSize: 13 }}>{counts.total} problems</span>
      </div>

      {/* Stats row */}
      <div style={{ display: "flex", gap: 12, marginBottom: 20 }}>
        {[
          { label: "Easy",   count: counts.easy,                  color: T.green  },
          { label: "Medium", count: counts.medium,                color: T.yellow },
          { label: "Hard",   count: counts.hard,                  color: T.red    },
          { label: "Solved", count: Object.keys(solved).length,   color: T.purple },
        ].map(({ label, count, color }) => (
          <div key={label} style={{
            background:   T.bg.surface,
            borderRadius: T.radius.lg,
            padding:      "10px 20px",
            border:       `1px solid ${color}25`,
            minWidth:     90,
            textAlign:    "center",
          }}>
            <div style={{ color: T.text.muted, fontSize: 10, marginBottom: 4 }}>{label.toUpperCase()}</div>
            <div style={{ color, fontSize: 22, fontWeight: 700 }}>{count}</div>
          </div>
        ))}
      </div>

      {/* Filters row */}
      <div style={{ display: "flex", gap: 10, marginBottom: 18, flexWrap: "wrap", alignItems: "center" }}>
        <input
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="🔍 Search problems…"
          style={{
            background:   T.bg.input,
            border:       `1px solid ${T.border.default}`,
            color:        T.text.primary,
            borderRadius: T.radius.md,
            padding:      "7px 14px",
            fontSize:     13,
            width:        240,
            outline:      "none",
          }}
        />

        <div style={{ display: "flex", gap: 6 }}>
          {["all", "easy", "medium", "hard"].map((d) => {
            const dc = T.diff[d] || {};
            const active = diffFilter === d;
            return (
              <button key={d} onClick={() => setDiffFilter(d)} style={{
                background:   active ? (dc.bg   || `${T.blue}15`)   : "transparent",
                border:       `1px solid ${active ? (dc.border || T.blue) : T.border.default}`,
                color:        active ? (dc.color || T.text.primary) : T.text.muted,
                borderRadius: 20,
                padding:      "5px 14px",
                cursor:       "pointer",
                fontSize:     12,
                fontWeight:   active ? 600 : 400,
              }}>
                {d === "all" ? "All" : d.charAt(0).toUpperCase() + d.slice(1)}
                {d !== "all" && (
                  <span style={{ marginLeft: 5, opacity: 0.6 }}>{counts[d]}</span>
                )}
              </button>
            );
          })}
        </div>

        <select
          value={catFilter}
          onChange={(e) => setCatFilter(e.target.value)}
          style={{
            background:   T.bg.input,
            border:       `1px solid ${T.border.default}`,
            color:        T.text.secondary,
            borderRadius: T.radius.md,
            padding:      "6px 12px",
            fontSize:     12,
            cursor:       "pointer",
            outline:      "none",
          }}
        >
          <option value="all">All Categories</option>
          {categories.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>

        <span style={{ color: T.text.dim, fontSize: 12, marginLeft: "auto" }}>
          {filtered.length} shown
        </span>
      </div>

      {/* Table */}
      <div style={{
        background:   T.bg.surface,
        borderRadius: T.radius.lg,
        border:       `1px solid ${T.border.default}`,
        overflow:     "hidden",
      }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
          <thead>
            <tr style={{
              background:   T.bg.elevated,
              borderBottom: `1px solid ${T.border.default}`,
            }}>
              {[
                { field: "id",         label: "#",          width: 50 },
                { field: "title",      label: "Title",      width: "auto" },
                { field: "difficulty", label: "Difficulty", width: 110 },
                { field: "category",   label: "Category",   width: 130 },
                { field: null,         label: "Status",     width: 90 },
              ].map(({ field, label, width }) => (
                <th
                  key={label}
                  onClick={field ? () => toggleSort(field) : undefined}
                  style={{
                    padding:      "9px 16px",
                    textAlign:    "left",
                    color:        T.text.muted,
                    fontSize:     10,
                    fontWeight:   700,
                    letterSpacing: "0.06em",
                    cursor:       field ? "pointer" : "default",
                    userSelect:   "none",
                    width,
                  }}
                >
                  {label.toUpperCase()}{field ? sortIcon(field) : ""}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 && (
              <tr>
                <td colSpan={5} style={{
                  padding: 28, textAlign: "center",
                  color: T.text.dim, fontSize: 13,
                }}>
                  No problems match your filters.
                </td>
              </tr>
            )}
            {filtered.map((p) => (
              <tr
                key={p.id}
                onClick={() => navigate(`/code/${p.id}`)}
                style={{
                  borderBottom: `1px solid ${T.border.subtle}`,
                  cursor:       "pointer",
                  transition:   "background 0.12s",
                }}
                onMouseEnter={(e) => e.currentTarget.style.background = T.bg.elevated}
                onMouseLeave={(e) => e.currentTarget.style.background = "transparent"}
              >
                <td style={{ padding: "10px 16px", color: T.text.dim }}>{p.id}</td>
                <td style={{ padding: "10px 16px", color: T.text.primary }}>{p.title}</td>
                <td style={{ padding: "10px 16px" }}><Badge difficulty={p.difficulty} /></td>
                <td style={{ padding: "10px 16px", color: T.text.muted, fontSize: 12 }}>
                  {p.category || "—"}
                </td>
                <td style={{ padding: "10px 16px" }}>
                  {solved[p.id]
                    ? <SolvedBadge />
                    : <span style={{ color: T.text.dim, fontSize: 11 }}>—</span>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div style={{ marginTop: 12, color: T.text.dim, fontSize: 11 }}>
        Click any problem to open it in the code editor.
      </div>
    </div>
  );
}
