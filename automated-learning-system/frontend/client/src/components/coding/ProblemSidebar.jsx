import React from "react";
import { T, Badge, Pill } from "./theme";

export default function ProblemSidebar({
  problems = [],
  filteredProblems = [],
  selectedId,
  diffFilter,
  searchQuery,
  solvedSet = new Set(),
  hint,
  onSelect,
  onDiffFilter,
  onSearch,
}) {
  const solvedCount = problems.filter((p) => solvedSet.has(String(p.id))).length;

  return (
    <aside style={{
      width: 240,
      flexShrink: 0,
      background: T.bg.surface,
      borderRight: `1px solid ${T.border.default}`,
      display: "flex",
      flexDirection: "column",
      overflow: "hidden",
    }}>

      {/* ── Header ─────────────────────────────────────────────────── */}
      <div style={{ padding: "12px 14px", borderBottom: `1px solid ${T.border.subtle}` }}>

        {/* Title + solved count */}
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 }}>
          <span style={{ color: T.text.primary, fontSize: 13, fontWeight: 600 }}>Problems</span>
          <span style={{
            color: T.text.muted, fontSize: 10, background: "#ffffff08",
            border: `1px solid ${T.border.default}`, borderRadius: 10, padding: "1px 8px",
          }}>
            {solvedCount} / {problems.length} solved
          </span>
        </div>

        {/* Search input */}
        <div style={{ position: "relative", marginBottom: 8 }}>
          <span style={{
            position: "absolute", left: 9, top: "50%", transform: "translateY(-50%)",
            color: T.text.muted, fontSize: 12, pointerEvents: "none",
          }}>
            🔍
          </span>
          <input
            type="text"
            placeholder="Search problems…"
            value={searchQuery}
            onChange={(e) => onSearch(e.target.value)}
            style={{
              width: "100%",
              background: T.bg.input,
              border: `1px solid ${T.border.default}`,
              borderRadius: T.radius.md,
              color: T.text.primary,
              fontSize: 12,
              padding: "6px 8px 6px 28px",
              outline: "none",
            }}
          />
        </div>

        {/* Difficulty filter pills */}
        <div style={{ display: "flex", gap: 4 }}>
          {["all", "easy", "medium", "hard"].map((d) => {
            const dConf = T.diff[d] || {};
            const active = diffFilter === d;
            return (
              <Pill
                key={d}
                label={d === "all" ? "All" : d.charAt(0).toUpperCase() + d.slice(1)}
                active={active}
                color={dConf.color}
                bg={dConf.bg}
                border={dConf.border}
                onClick={() => onDiffFilter(d)}
              />
            );
          })}
        </div>
      </div>

      {/* ── Problem list ────────────────────────────────────────────── */}
      <div style={{ flex: 1, overflowY: "auto" }}>
        {filteredProblems.length === 0 && (
          <div style={{ padding: "24px 14px", color: T.text.muted, fontSize: 12, textAlign: "center" }}>
            No problems match.
          </div>
        )}

        {filteredProblems.map((p) => {
          const isSolved   = solvedSet.has(String(p.id));
          const isSelected = p.id === selectedId;
          const dConf      = T.diff[p.difficulty] || {};

          return (
            <div
              key={p.id}
              onClick={() => onSelect(p.id)}
              role="button"
              style={{
                padding: "9px 14px",
                cursor: "pointer",
                background: isSelected ? T.bg.elevated : "transparent",
                borderLeft: `3px solid ${isSelected ? (dConf.color || T.blue) : "transparent"}`,
              }}
            >
              <div style={{ display: "flex", alignItems: "flex-start", gap: 7 }}>
                {/* Solved indicator */}
                <span style={{
                  color:    isSolved ? T.green : T.text.dim,
                  fontSize: 10,
                  marginTop: 2,
                  flexShrink: 0,
                  fontWeight: isSolved ? 700 : 400,
                }}>
                  {isSolved ? "✓" : "○"}
                </span>

                <div style={{ minWidth: 0 }}>
                  {/* Problem title */}
                  <div style={{
                    color:     isSelected ? T.text.primary : T.text.secondary,
                    fontSize:  12,
                    fontWeight: isSelected ? 500 : 400,
                    lineHeight: 1.35,
                    marginBottom: 4,
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "nowrap",
                  }}>
                    {p.title}
                  </div>

                  {/* Difficulty + category */}
                  <div style={{ display: "flex", gap: 5, alignItems: "center" }}>
                    <Badge difficulty={p.difficulty} size="sm" />
                    {p.category && (
                      <span style={{
                        color: T.text.muted, fontSize: 9,
                        overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap",
                        maxWidth: 100,
                      }}>
                        {p.category}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* ── Adaptive recommendation footer ──────────────────────────── */}
      {hint?.adaptive_action && (
        <div style={{
          padding: "8px 14px",
          borderTop: `1px solid ${T.border.subtle}`,
          background: T.bg.base,
        }}>
          <div style={{ color: T.text.muted, fontSize: 9, letterSpacing: "0.07em", marginBottom: 3 }}>
            RECOMMENDED NEXT
          </div>
          <div style={{ color: T.text.secondary, fontSize: 11 }}>
            {hint.adaptive_action === "challenge" ? "🔴 Hard — push yourself"  :
             hint.adaptive_action === "practice"  ? "🟡 Medium — keep going"   :
             hint.adaptive_action === "hint"      ? "💡 Review this problem"   :
                                                    "🟢 Easy — take a breather"}
          </div>
        </div>
      )}
    </aside>
  );
}
