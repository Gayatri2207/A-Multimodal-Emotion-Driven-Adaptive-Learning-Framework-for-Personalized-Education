import React from "react";
import { T, Badge } from "./theme";

export default function ProblemDescription({
  problem,
  examples = [],
  hints    = [],
  showHints,
  showExamples,
  onToggleHints,
  onToggleExamples,
}) {
  if (!problem) {
    return (
      <div style={{
        padding: "20px", color: T.text.muted, fontSize: 13, textAlign: "center",
        background: T.bg.surface, borderBottom: `1px solid ${T.border.default}`,
      }}>
        ← Select a problem from the list to begin
      </div>
    );
  }

  return (
    <div style={{
      background: T.bg.surface,
      borderBottom: `1px solid ${T.border.default}`,
      maxHeight: 220,
      overflowY: "auto",
      flexShrink: 0,
    }}>
      <div style={{ padding: "14px 18px" }}>

        {/* ── Title row ──────────────────────────────────────────────── */}
        <div style={{
          display: "flex", alignItems: "center",
          gap: 10, marginBottom: 8, flexWrap: "wrap",
        }}>
          <h3 style={{ margin: 0, color: T.text.primary, fontSize: 15, fontWeight: 600 }}>
            {problem.title}
          </h3>
          <Badge difficulty={problem.difficulty} size="md" />
          {problem.category && (
            <span style={{
              color: T.text.muted, fontSize: 11,
              background: "#ffffff06", border: `1px solid ${T.border.default}`,
              borderRadius: T.radius.sm, padding: "2px 8px",
            }}>
              {problem.category}
            </span>
          )}
        </div>

        {/* ── Description ────────────────────────────────────────────── */}
        <p style={{ margin: "0 0 10px", color: T.text.secondary, fontSize: 13, lineHeight: 1.65 }}>
          {problem.description}
        </p>

        {/* ── Examples ───────────────────────────────────────────────── */}
        {examples.length > 0 && (
          <div style={{ marginBottom: 6 }}>
            <button
              onClick={onToggleExamples}
              style={{
                background: "none", border: "none", padding: "0 0 6px 0",
                color: T.blue, cursor: "pointer", fontSize: 12,
                display: "flex", alignItems: "center", gap: 5,
              }}
            >
              <span style={{ fontSize: 9 }}>{showExamples ? "▾" : "▸"}</span>
              Examples ({examples.length})
            </button>

            {showExamples && (
              <div className="animate-fade" style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                {examples.map((ex, i) => (
                  <div key={i} style={{
                    background: T.bg.base,
                    border: `1px solid ${T.border.default}`,
                    borderRadius: T.radius.md,
                    padding: "6px 12px",
                    fontSize: 12,
                  }}>
                    <span style={{ color: T.text.muted }}>Input: </span>
                    <code style={{ color: "#a5b4fc" }}>{ex.input}</code>
                    <span style={{ color: T.text.muted, marginLeft: 12 }}>Output: </span>
                    <code style={{ color: "#86efac" }}>{ex.output}</code>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ── Hints ──────────────────────────────────────────────────── */}
        {hints.length > 0 && (
          <div>
            <button
              onClick={onToggleHints}
              style={{
                background: "none", border: "none", padding: "0 0 6px 0",
                color: T.yellow, cursor: "pointer", fontSize: 12,
                display: "flex", alignItems: "center", gap: 5,
              }}
            >
              <span style={{ fontSize: 9 }}>{showHints ? "▾" : "▸"}</span>
              💡 Hints ({hints.length})
            </button>

            {showHints && (
              <div className="animate-fade">
                {hints.map((h, i) => (
                  <div key={i} style={{
                    color: "#fcd34d", fontSize: 12, marginBottom: 6,
                    paddingLeft: 10,
                    borderLeft: `2px solid ${T.yellow}40`,
                    lineHeight: 1.5,
                  }}>
                    <strong>Hint {i + 1}:</strong> {h}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
