/**
 * OnboardingModal — shown once to first-time users.
 * Dismissed by clicking "Start Practicing", which sets localStorage flag.
 */
import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { T } from "./coding/theme";

const STORAGE_KEY = "emoticode_onboarded";

const FEATURES = [
  {
    icon: "🧠",
    title: "Adaptive Difficulty",
    desc: "Reinforcement learning adjusts problem difficulty in real time based on your performance.",
  },
  {
    icon: "😊",
    title: "Emotion Detection",
    desc: "Your webcam detects focus & frustration so the platform can respond to how you actually feel.",
  },
  {
    icon: "💻",
    title: "100 Coding Problems",
    desc: "Easy → Hard problems across algorithms, data structures, math, and more.",
  },
  {
    icon: "🤖",
    title: "AI Tutor",
    desc: "Get personalised hints, mistake analysis, and complexity feedback — without spoilers.",
  },
  {
    icon: "📊",
    title: "Analytics Dashboard",
    desc: "Track your emotion trends, performance over time, and difficulty progression.",
  },
];

export default function OnboardingModal() {
  const navigate  = useNavigate();
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (!localStorage.getItem(STORAGE_KEY)) setVisible(true);
  }, []);

  if (!visible) return null;

  const dismiss = (path = "/problems") => {
    localStorage.setItem(STORAGE_KEY, "1");
    setVisible(false);
    navigate(path);
  };

  return (
    /* Backdrop */
    <div
      onClick={() => dismiss()}
      style={{
        position: "fixed",
        inset: 0,
        background: "rgba(0,0,0,0.72)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        zIndex: 1000,
        padding: 24,
        backdropFilter: "blur(4px)",
      }}
    >
      {/* Modal card */}
      <div
        onClick={(e) => e.stopPropagation()}
        className="animate-fade"
        style={{
          background:   T.bg.surface,
          border:       `1px solid ${T.border.strong}`,
          borderRadius: T.radius.xl,
          maxWidth:     540,
          width:        "100%",
          padding:      "32px 36px",
          boxShadow:    "0 24px 80px rgba(0,0,0,0.6)",
        }}
      >
        {/* Header */}
        <div style={{ textAlign: "center", marginBottom: 28 }}>
          <div style={{ fontSize: 40, marginBottom: 10 }}>⚡</div>
          <h2 style={{ margin: 0, color: T.text.primary, fontSize: 22, fontWeight: 700, letterSpacing: "-0.02em" }}>
            Welcome to EmotiCode
          </h2>
          <p style={{ margin: "8px 0 0", color: T.text.secondary, fontSize: 13, lineHeight: 1.6 }}>
            An AI-powered coding practice platform that adapts to your emotions.
          </p>
        </div>

        {/* Feature grid */}
        <div style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: 12,
          marginBottom: 28,
        }}>
          {FEATURES.map((f) => (
            <div
              key={f.title}
              style={{
                background:   T.bg.elevated,
                border:       `1px solid ${T.border.default}`,
                borderRadius: T.radius.lg,
                padding:      "12px 14px",
                display:      "flex",
                gap:          10,
                alignItems:   "flex-start",
              }}
            >
              <span style={{ fontSize: 20, flexShrink: 0 }}>{f.icon}</span>
              <div>
                <div style={{ color: T.text.primary, fontSize: 12, fontWeight: 600, marginBottom: 3 }}>
                  {f.title}
                </div>
                <div style={{ color: T.text.muted, fontSize: 11, lineHeight: 1.5 }}>
                  {f.desc}
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Actions */}
        <div style={{ display: "flex", gap: 10, justifyContent: "center" }}>
          <button
            onClick={() => dismiss("/problems")}
            style={{
              background:   T.blue,
              border:       "none",
              borderRadius: T.radius.md,
              color:        "#fff",
              padding:      "10px 28px",
              fontSize:     14,
              fontWeight:   700,
              cursor:       "pointer",
              letterSpacing: "-0.01em",
            }}
          >
            Start Practising →
          </button>
          <button
            onClick={() => dismiss("/")}
            style={{
              background:   T.bg.elevated,
              border:       `1px solid ${T.border.default}`,
              borderRadius: T.radius.md,
              color:        T.text.secondary,
              padding:      "10px 20px",
              fontSize:     13,
              cursor:       "pointer",
            }}
          >
            View Dashboard
          </button>
        </div>

        <p style={{
          marginTop: 20, textAlign: "center",
          color: T.text.dim, fontSize: 10,
        }}>
          Click anywhere outside or press Escape to close
        </p>
      </div>
    </div>
  );
}
