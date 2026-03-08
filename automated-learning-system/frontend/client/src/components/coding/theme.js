/**
 * Design tokens for the Emotion-Aware Coding Platform.
 * Import this in any component that needs consistent colours/spacing.
 */

export const T = {
  // ── Backgrounds ──────────────────────────────────────────────────────
  bg: {
    base:     "#0c0e14",
    surface:  "#111318",
    elevated: "#161b24",
    overlay:  "#1c2132",
    input:    "#131720",
  },
  // ── Borders ───────────────────────────────────────────────────────────
  border: {
    subtle:  "#1a2035",
    default: "#1e2535",
    strong:  "#2a3347",
  },
  // ── Text ──────────────────────────────────────────────────────────────
  text: {
    primary:   "#e2e8f0",
    secondary: "#8892a4",
    muted:     "#4a5568",
    dim:       "#2a3347",
  },
  // ── Accent colours ────────────────────────────────────────────────────
  green:  "#22c55e",
  blue:   "#3b82f6",
  yellow: "#f59e0b",
  red:    "#ef4444",
  purple: "#a855f7",
  cyan:   "#06b6d4",
  orange: "#f97316",

  // ── Difficulty ─────────────────────────────────────────────────────────
  diff: {
    easy:   { color: "#22c55e", bg: "#22c55e12", border: "#22c55e30" },
    medium: { color: "#f59e0b", bg: "#f59e0b12", border: "#f59e0b30" },
    hard:   { color: "#ef4444", bg: "#ef444412", border: "#ef444430" },
  },

  // ── Common radii ──────────────────────────────────────────────────────
  radius: { sm: 4, md: 6, lg: 10, xl: 14 },
};

/** Shared Badge component used across all coding pages. */
export function Badge({ difficulty, size = "sm" }) {
  const d = T.diff[difficulty] || { color: "#8892a4", bg: "#ffffff0a", border: "#ffffff15" };
  const label = difficulty
    ? difficulty.charAt(0).toUpperCase() + difficulty.slice(1)
    : "?";
  return (
    <span style={{
      display: "inline-block",
      color: d.color,
      background: d.bg,
      border: `1px solid ${d.border}`,
      borderRadius: T.radius.sm,
      padding: size === "sm" ? "1px 7px" : "3px 10px",
      fontSize: size === "sm" ? 10 : 12,
      fontWeight: 600,
      letterSpacing: "0.04em",
      lineHeight: 1.6,
    }}>
      {label.toUpperCase()}
    </span>
  );
}

/** Pill button (filter, tag). */
export function Pill({ label, active, color, bg, border, onClick }) {
  return (
    <button
      onClick={onClick}
      style={{
        background:   active ? (bg   || "#ffffff12") : "transparent",
        border:       `1px solid ${active ? (border || "#ffffff30") : T.border.default}`,
        color:        active ? (color || T.text.primary) : T.text.muted,
        borderRadius: T.radius.sm,
        padding:      "3px 10px",
        fontSize:     11,
        fontWeight:   active ? 600 : 400,
        cursor:       "pointer",
      }}
    >
      {label}
    </button>
  );
}

/** Section label (uppercase, spaced). */
export function SectionLabel({ children, style }) {
  return (
    <div style={{
      color: T.text.muted,
      fontSize: 9,
      fontWeight: 700,
      letterSpacing: "0.09em",
      textTransform: "uppercase",
      marginBottom: 6,
      ...style,
    }}>
      {children}
    </div>
  );
}

/** Card wrapper. */
export function Card({ children, style }) {
  return (
    <div style={{
      background: T.bg.surface,
      border: `1px solid ${T.border.default}`,
      borderRadius: T.radius.lg,
      padding: 12,
      ...style,
    }}>
      {children}
    </div>
  );
}
