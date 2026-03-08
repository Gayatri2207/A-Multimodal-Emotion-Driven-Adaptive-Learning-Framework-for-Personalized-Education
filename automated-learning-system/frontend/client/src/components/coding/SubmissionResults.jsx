import React from "react";
import { T, Badge } from "./theme";

/* Map status → colour + label */
function statusInfo(d) {
  if (d.passed)      return { color: T.green,  bg: `${T.green}08`,  label: "✓ PASS"  };
  if (d.timed_out)   return { color: "#fbbf24", bg: "#fbbf2410",     label: "⏱ TLE"   };
  if (d.error_type)  return { color: T.purple,  bg: `${T.purple}0c`, label: "⚡ ERROR" };
  return               { color: T.red,    bg: `${T.red}08`,    label: "✗ FAIL"  };
}

/* Mini pill for progress bar segments */
function Segment({ d, index }) {
  const s = statusInfo(d);
  return (
    <div
      title={`#${d.test_case} ${s.label}`}
      style={{
        flex: 1, height: 6, borderRadius: 3,
        background: s.color, opacity: 0.85,
        minWidth: 4,
      }}
    />
  );
}

export default function SubmissionResults({ result, submissionHistory = [] }) {
  if (!result && submissionHistory.length === 0) return null;

  const allPassed = result && result.passed === result.total;

  return (
    <div style={{
      background: T.bg.base,
      borderTop: `1px solid ${T.border.default}`,
      flexShrink: 0,
    }}>

      {/* ── Submission error (500, no test cases) ─────────────────── */}
      {result?.error && (
        <div className="animate-fade" style={{
          padding: "10px 18px",
          color: T.red,
          background: `${T.red}10`,
          borderBottom: `1px solid ${T.red}30`,
          fontSize: 13,
        }}>
          ❌ {result.error}
        </div>
      )}

      {/* ── Test results panel ────────────────────────────────────── */}
      {result?.details && (
        <div className="animate-fade" style={{ maxHeight: 280, overflowY: "auto" }}>

          {/* Summary header */}
          <div style={{
            display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap",
            padding: "8px 18px",
            background: allPassed ? `${T.green}08` : `${T.red}0a`,
            borderBottom: `1px solid ${T.border.subtle}`,
          }}>
            <span style={{
              color: allPassed ? T.green : T.yellow,
              fontWeight: 700, fontSize: 13,
            }}>
              {allPassed ? "✅ All Tests Passed" : `⚠ ${result.passed} / ${result.total} Passed`}
            </span>

            {/* Progress bar */}
            <div style={{ display: "flex", gap: 2, flex: 1, minWidth: 60, maxWidth: 160 }}>
              {result.details.map((d, i) => <Segment key={i} d={d} index={i} />)}
            </div>

            <span style={{ color: T.text.muted, fontSize: 11 }}>
              {(result.score * 100).toFixed(0)}%
            </span>
            {result.recommended_difficulty && (
              <span style={{ color: T.text.muted, fontSize: 11, display: "flex", alignItems: "center", gap: 5 }}>
                Next: <Badge difficulty={result.recommended_difficulty} />
              </span>
            )}
            {result.adaptive_action && (
              <span style={{ color: T.text.secondary, fontSize: 11 }}>
                {result.adaptive_action === "challenge" ? "🚀 Push harder!"      :
                 result.adaptive_action === "relax"     ? "😮‍💨 Take a break"   :
                 result.adaptive_action === "hint"      ? "💡 Review the hints" : "🎯 Keep going"}
              </span>
            )}
          </div>

          {/* Test case table */}
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
            <thead>
              <tr style={{ background: T.bg.surface, position: "sticky", top: 0 }}>
                {["#", "STATUS", "INPUT", "EXPECTED", "ACTUAL OUTPUT", "TIME"].map((h, i) => (
                  <th key={h} style={{
                    padding: "5px 10px",
                    color: T.text.muted,
                    textAlign: i === 5 ? "right" : "left",
                    fontWeight: 600,
                    fontSize: 10,
                    letterSpacing: "0.05em",
                    width: i === 0 ? 36 : i === 1 ? 80 : i === 5 ? 60 : undefined,
                    borderBottom: `1px solid ${T.border.subtle}`,
                  }}>
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {result.details.map((d, i) => {
                const s          = statusInfo(d);
                const actualText = d.actual ?? (d.stdout || "").trim();
                const hasError   = !d.passed && (d.clean_stderr || d.error_type);

                return (
                  <React.Fragment key={i}>
                    <tr style={{
                      background: s.bg,
                      borderBottom: hasError ? "none" : `1px solid ${T.border.subtle}`,
                    }}>
                      <td style={{ padding: "5px 10px", color: T.text.muted, fontFamily: "monospace" }}>
                        {d.test_case}
                      </td>
                      <td style={{ padding: "5px 10px", color: s.color, fontWeight: 700 }}>
                        {s.label}
                      </td>
                      <td style={{ padding: "5px 10px" }}>
                        <code style={{
                          color: "#94a3b8", background: "#0d1117",
                          padding: "1px 6px", borderRadius: 3,
                        }}>
                          {d.stdin != null && d.stdin !== ""
                            ? d.stdin.substring(0, 40)
                            : <em style={{ color: T.text.dim }}>(none)</em>}
                        </code>
                      </td>
                      <td style={{ padding: "5px 10px" }}>
                        <code style={{
                          color: "#86efac", background: "#0a1a0a",
                          padding: "1px 6px", borderRadius: 3,
                        }}>
                          {(d.expected || "(empty)").substring(0, 50)}
                        </code>
                      </td>
                      <td style={{ padding: "5px 10px" }}>
                        {d.timed_out ? (
                          <span style={{ color: "#fbbf24", fontStyle: "italic" }}>— timed out —</span>
                        ) : (
                          <code style={{
                            color:      d.passed ? "#86efac" : d.error_type ? "#c4b5fd" : "#fca5a5",
                            background: d.passed ? "#0a1a0a"  : d.error_type ? "#1a0a2a"  : "#1a0a0a",
                            padding:    "1px 6px", borderRadius: 3,
                          }}>
                            {actualText
                              ? actualText.substring(0, 50)
                              : <em style={{ color: T.text.muted }}>(no output)</em>}
                          </code>
                        )}
                      </td>
                      <td style={{
                        padding: "5px 10px", color: T.text.muted,
                        textAlign: "right", fontFamily: "monospace",
                      }}>
                        {d.exec_time_ms != null ? `${d.exec_time_ms}ms` : "—"}
                      </td>
                    </tr>

                    {/* Error detail row */}
                    {hasError && (
                      <tr style={{ borderBottom: `1px solid ${T.border.subtle}` }}>
                        <td colSpan={5} style={{ padding: "3px 10px 7px 46px" }}>
                          <pre style={{
                            margin: 0,
                            color: "#c4b5fd",
                            fontSize: 11,
                            fontFamily: "monospace",
                            whiteSpace: "pre-wrap",
                            wordBreak: "break-word",
                            background: "#1a0a2a",
                            borderRadius: T.radius.sm,
                            padding: "5px 10px",
                            maxHeight: 90,
                            overflowY: "auto",
                            border: `1px solid ${T.purple}25`,
                          }}>
                            {(d.clean_stderr || d.error_type || "").trim()}
                          </pre>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* ── Submission history strip ──────────────────────────────── */}
      {submissionHistory.length > 0 && (
        <div style={{
          padding: "5px 18px",
          borderTop: `1px solid ${T.border.subtle}`,
          display: "flex",
          alignItems: "center",
          gap: 6,
          overflowX: "auto",
          background: "#0a0b10",
        }}>
          <span style={{ color: T.text.muted, fontSize: 10, flexShrink: 0, letterSpacing: "0.05em" }}>
            HISTORY
          </span>
          {submissionHistory.map((s) => {
            const allPass = s.passed === s.total;
            const partial = s.passed > 0 && s.passed < s.total;
            const col = allPass ? T.green : partial ? T.yellow : T.red;
            return (
              <div key={s.id} style={{
                fontSize: 10, flexShrink: 0,
                color: col,
                background: `${col}10`,
                border: `1px solid ${col}30`,
                padding: "2px 8px",
                borderRadius: 4,
              }}>
                #{s.id} {s.passed}/{s.total}
                <span style={{ color: T.text.muted, marginLeft: 4 }}>{s.time}</span>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
