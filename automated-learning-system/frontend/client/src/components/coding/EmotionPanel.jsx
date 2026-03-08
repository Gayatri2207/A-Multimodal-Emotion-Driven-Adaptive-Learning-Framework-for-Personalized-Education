import React from "react";
import Webcam from "react-webcam";
import { T, SectionLabel } from "./theme";

/* Map emotion score → readable label + emoji */
function emotionLabel(score) {
  if (score === null || score === undefined) return { label: "Unknown",    emoji: "❓", color: T.text.muted };
  if (score < 0.20) return { label: "Frustrated",  emoji: "😤", color: T.red    };
  if (score < 0.35) return { label: "Struggling",  emoji: "😟", color: "#fb923c" };
  if (score < 0.50) return { label: "Neutral",     emoji: "😐", color: T.text.secondary };
  if (score < 0.65) return { label: "Focused",     emoji: "🎯", color: T.blue   };
  if (score < 0.80) return { label: "Engaged",     emoji: "😊", color: T.cyan   };
  return                    { label: "Excited",     emoji: "🤩", color: T.green  };
}

/* Recommendation text for each adaptive action */
function actionText(action) {
  const map = {
    challenge: { text: "Push yourself with a harder problem",   emoji: "🚀", color: T.red    },
    relax:     { text: "Take a short break and reset",          emoji: "😮‍💨", color: T.cyan },
    hint:      { text: "Review hints and try again",            emoji: "💡", color: T.yellow },
    practice:  { text: "Keep practising at this level",         emoji: "🎯", color: T.green  },
  };
  return map[action] || map.practice;
}

/* Animated metric bar */
function MetricBar({ label, value, color, max = 1 }) {
  const pct = Math.round(Math.min(1, Math.max(0, value / max)) * 100);
  return (
    <div style={{ marginBottom: 8 }}>
      <div style={{
        display: "flex", justifyContent: "space-between",
        color: T.text.muted, fontSize: 10, marginBottom: 3,
      }}>
        <span>{label}</span>
        <span style={{ color }}>{pct}%</span>
      </div>
      <div style={{ height: 4, background: T.border.subtle, borderRadius: 2 }}>
        <div style={{
          width: `${pct}%`, height: "100%",
          background: color, borderRadius: 2,
          transition: "width 0.8s cubic-bezier(0.4,0,0.2,1)",
        }} />
      </div>
    </div>
  );
}

/* Structured AI tutor feedback sections */
function TutorSection({ icon, title, items = [], color }) {
  if (!items || items.length === 0) return null;
  return (
    <div style={{ marginBottom: 10 }}>
      <div style={{ color, fontSize: 10, fontWeight: 700, letterSpacing: "0.07em", marginBottom: 4 }}>
        {icon} {title}
      </div>
      {items.map((item, i) => (
        <div key={i} style={{
          color: T.text.secondary, fontSize: 11, lineHeight: 1.55,
          paddingLeft: 10, marginBottom: 3,
          borderLeft: `2px solid ${color}40`,
        }}>
          {typeof item === "string" ? item : `${item.issue || item.suggestion || item}`}
        </div>
      ))}
    </div>
  );
}

export default function EmotionPanel({
  webcamRef,
  cameraOn,
  wsStatus,
  hint,
  result,
  problems = [],
  tutorFeedback,
  tutorLoading,
  showTutor,
  onToggleCamera,
  onCloseTutor,
}) {
  const easy   = problems.filter((p) => p.difficulty === "easy").length;
  const medium = problems.filter((p) => p.difficulty === "medium").length;
  const hard   = problems.filter((p) => p.difficulty === "hard").length;

  const emotionVal  = hint?.emotion_score   ?? null;
  const perfVal     = result?.score         ?? 0;
  const recDiff     = hint?.recommended_difficulty ?? result?.recommended_difficulty;
  const actionLabel = hint?.adaptive_action ?? result?.adaptive_action;

  const emotion  = emotionLabel(emotionVal);
  const rec      = actionLabel ? actionText(actionLabel) : null;

  return (
    <aside style={{
      width: 240,
      flexShrink: 0,
      background: T.bg.surface,
      borderLeft: `1px solid ${T.border.default}`,
      display: "flex",
      flexDirection: "column",
      overflowY: "auto",
    }}>

      {/* ── Webcam section ─────────────────────────────────────────── */}
      <div style={{ padding: "10px 12px", borderBottom: `1px solid ${T.border.subtle}` }}>
        <div style={{
          display: "flex", justifyContent: "space-between",
          alignItems: "center", marginBottom: 8,
        }}>
          <SectionLabel>EMOTION CAMERA</SectionLabel>
          <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
            <div title={`WebSocket: ${wsStatus}`} style={{
              width: 7, height: 7, borderRadius: "50%",
              background: wsStatus === "connected" ? T.green :
                          wsStatus === "error"     ? T.red   : T.yellow,
            }} />
            <button onClick={onToggleCamera} style={{
              background: T.bg.elevated, border: `1px solid ${T.border.default}`,
              borderRadius: T.radius.sm, color: T.text.muted, fontSize: 10,
              cursor: "pointer", padding: "2px 8px",
            }}>
              {cameraOn ? "OFF" : "ON"}
            </button>
          </div>
        </div>

        {cameraOn ? (
          <div style={{ borderRadius: T.radius.md, overflow: "hidden", background: "#000", aspectRatio: "4/3" }}>
            <Webcam
              ref={webcamRef} screenshotFormat="image/jpeg"
              width={216} height={162} mirrored
              style={{ display: "block", width: "100%" }}
            />
          </div>
        ) : (
          <div style={{
            background: T.bg.elevated, border: `1px dashed ${T.border.default}`,
            borderRadius: T.radius.md, height: 80,
            display: "flex", alignItems: "center", justifyContent: "center",
            color: T.text.dim, fontSize: 11,
          }}>
            📷 Camera off
          </div>
        )}

        {/* Detected emotion label */}
        {emotionVal !== null && (
          <div style={{
            marginTop: 8, padding: "6px 10px",
            background: `${emotion.color}10`,
            border: `1px solid ${emotion.color}30`,
            borderRadius: T.radius.md,
            display: "flex", alignItems: "center", gap: 8,
          }}>
            <span style={{ fontSize: 18 }}>{emotion.emoji}</span>
            <div>
              <div style={{ color: emotion.color, fontSize: 12, fontWeight: 700 }}>{emotion.label}</div>
              <div style={{ color: T.text.muted, fontSize: 9 }}>
                Intensity: {Math.max(10, Math.round(Math.abs(emotionVal - 0.5) * 200))}%
              </div>
            </div>
          </div>
        )}
      </div>

      {/* ── Adaptive engine metrics ─────────────────────────────────── */}
      <div style={{ padding: "10px 12px", borderBottom: `1px solid ${T.border.subtle}` }}>
        <SectionLabel style={{ marginBottom: 8 }}>ADAPTIVE ENGINE</SectionLabel>

        <MetricBar
          label="Emotion Score"
          value={emotionVal ?? 0}
          color={emotionVal !== null ? emotion.color : T.text.muted}
        />
        <MetricBar label="Performance" value={perfVal} color={T.green} />

        {rec && (
          <div style={{
            marginTop: 8, padding: "7px 10px",
            background: `${rec.color}10`,
            border: `1px solid ${rec.color}25`,
            borderRadius: T.radius.md,
          }}>
            <div style={{ fontSize: 13, marginBottom: 3 }}>{rec.emoji}</div>
            <div style={{ fontSize: 11, color: rec.color, fontWeight: 600, marginBottom: 2 }}>
              {actionLabel?.charAt(0).toUpperCase() + actionLabel?.slice(1) || ""}
            </div>
            <div style={{ fontSize: 10, color: T.text.muted, lineHeight: 1.5 }}>{rec.text}</div>
            {recDiff && (
              <div style={{ fontSize: 10, color: T.text.dim, marginTop: 5, display: "flex", gap: 5, alignItems: "center" }}>
                Next level:&nbsp;
                <span style={{
                  color: T.diff[recDiff]?.color || T.text.secondary,
                  fontWeight: 600, textTransform: "capitalize",
                }}>
                  {recDiff}
                </span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* ── Problem bank stats ─────────────────────────────────────── */}
      <div style={{ padding: "10px 12px", borderBottom: `1px solid ${T.border.subtle}` }}>
        <SectionLabel style={{ marginBottom: 8 }}>PROBLEM BANK</SectionLabel>
        <div style={{ display: "flex", gap: 6 }}>
          {[
            { diff: "easy",   count: easy,   color: T.green  },
            { diff: "medium", count: medium, color: T.yellow },
            { diff: "hard",   count: hard,   color: T.red    },
          ].map(({ diff, count, color }) => (
            <div key={diff} style={{
              flex: 1, textAlign: "center",
              background: T.bg.elevated, border: `1px solid ${T.border.default}`,
              borderRadius: T.radius.md, padding: "5px 0",
            }}>
              <div style={{ color, fontWeight: 700, fontSize: 15 }}>{count}</div>
              <div style={{ color: T.text.muted, fontSize: 9, textTransform: "capitalize" }}>{diff}</div>
            </div>
          ))}
        </div>
      </div>

      {/* ── AI Tutor panel ─────────────────────────────────────────── */}
      {(showTutor || tutorLoading) && (
        <div className="animate-fade" style={{ padding: "10px 12px" }}>
          <div style={{
            display: "flex", justifyContent: "space-between",
            alignItems: "center", marginBottom: 8,
          }}>
            <SectionLabel>AI TUTOR</SectionLabel>
            <button onClick={onCloseTutor} style={{
              background: "none", border: "none",
              color: T.text.dim, cursor: "pointer", fontSize: 14, padding: 0, lineHeight: 1,
            }}>×</button>
          </div>

          {tutorLoading && (
            <div style={{ color: T.text.muted, fontSize: 11, textAlign: "center", padding: "12px 0" }}>
              <span className="animate-pulse">🤖 Analysing your code…</span>
            </div>
          )}

          {tutorFeedback && !tutorLoading && (
            <div>
              {tutorFeedback.emotion_note && (
                <div style={{
                  color: "#fbbf24", fontSize: 11, marginBottom: 8,
                  fontStyle: "italic", lineHeight: 1.5,
                }}>
                  {tutorFeedback.emotion_note}
                </div>
              )}
              {tutorFeedback.summary && (
                <div style={{
                  color: T.text.secondary, fontSize: 11, marginBottom: 8, lineHeight: 1.55,
                  padding: "6px 10px", background: T.bg.elevated,
                  borderRadius: T.radius.md, border: `1px solid ${T.border.default}`,
                }}>
                  {tutorFeedback.summary}
                </div>
              )}
              <TutorSection icon="🔴" title="MISTAKES"      items={tutorFeedback.mistakes}    color={T.red}    />
              <TutorSection icon="🟡" title="IMPROVEMENTS"  items={tutorFeedback.improvements} color={T.yellow} />
              <TutorSection icon="🧠" title="ALGORITHM"
                items={tutorFeedback.algorithm_insight ? [tutorFeedback.algorithm_insight] : []}
                color={T.blue}
              />
              <TutorSection icon="💡" title="HINTS"         items={tutorFeedback.hints}        color={T.green}  />

              {(tutorFeedback.time_complexity || tutorFeedback.space_complexity) && (
                <div style={{
                  marginTop: 8, padding: "6px 10px",
                  background: T.bg.elevated, borderRadius: T.radius.md,
                  border: `1px solid ${T.border.default}`, fontSize: 11, color: T.text.secondary,
                }}>
                  {tutorFeedback.time_complexity && (
                    <div>⏱ Time: <code style={{ color: "#a5b4fc" }}>{tutorFeedback.time_complexity}</code></div>
                  )}
                  {tutorFeedback.space_complexity && (
                    <div>💾 Space: <code style={{ color: "#a5b4fc" }}>{tutorFeedback.space_complexity}</code></div>
                  )}
                  {tutorFeedback.readability_score != null && (
                    <div style={{ marginTop: 4 }}>
                      Readability: {tutorFeedback.readability_score}/100 · Efficiency: {tutorFeedback.efficiency_score}/100
                    </div>
                  )}
                </div>
              )}

              {tutorFeedback.source && (
                <div style={{ marginTop: 6, color: T.text.dim, fontSize: 9, textAlign: "right" }}>
                  source: {tutorFeedback.source}
                </div>
              )}
            </div>
          )}

          {tutorFeedback?.error && !tutorLoading && (
            <div style={{ color: T.red, fontSize: 11 }}>⚠ {tutorFeedback.error}</div>
          )}
        </div>
      )}
    </aside>
  );
}

/* Animated metric bar */
