import React, { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import { T } from "../components/coding/theme";

const API = process.env.REACT_APP_API_URL || "http://localhost:8000";

function Field({ label, type = "text", value, onChange, placeholder, autoComplete }) {
  return (
    <div style={{ marginBottom: 14 }}>
      <label style={{ display: "block", color: T.text.muted, fontSize: 11, marginBottom: 5, fontWeight: 600 }}>
        {label}
      </label>
      <input
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        autoComplete={autoComplete}
        style={{
          width: "100%", padding: "9px 14px",
          background: T.bg.input, border: `1px solid ${T.border.default}`,
          borderRadius: T.radius.md, color: T.text.primary,
          fontSize: 13, outline: "none", boxSizing: "border-box",
        }}
        onFocus={(e)  => e.target.style.borderColor = T.blue}
        onBlur={(e)   => e.target.style.borderColor = T.border.default}
      />
    </div>
  );
}

export default function LoginPage() {
  const navigate = useNavigate();
  const [mode, setMode]           = useState("login");   // "login" | "register"
  const [email, setEmail]         = useState("");
  const [password, setPassword]   = useState("");
  const [confirm, setConfirm]     = useState("");
  const [error, setError]         = useState("");
  const [loading, setLoading]     = useState(false);
  const [success, setSuccess]     = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(""); setSuccess("");

    if (mode === "register") {
      if (password !== confirm) { setError("Passwords do not match."); return; }
      if (password.length < 8)  { setError("Password must be at least 8 characters."); return; }
    }

    setLoading(true);
    try {
      if (mode === "login") {
        const { data } = await axios.post(`${API}/auth/login`, { email, password });
        localStorage.setItem("token", data.access_token);
        localStorage.setItem("userEmail", email);
        localStorage.setItem("userId", String(data.user_id ?? 1));
        navigate("/");
      } else {
        await axios.post(`${API}/auth/register`, { email, password });
        setSuccess("Account created! You can now sign in.");
        setMode("login");
      }
    } catch (err) {
      const detail = err.response?.data?.detail;
      setError(
        typeof detail === "string" ? detail :
        mode === "login" ? "Invalid email or password." : "Registration failed. Email may already be in use."
      );
    } finally {
      setLoading(false);
    }
  };

  const guestLogin = () => {
    localStorage.removeItem("token");
    localStorage.setItem("userEmail", "guest");
    navigate("/");
  };

  return (
    <div style={{
      minHeight: "calc(100vh - 48px)",
      display: "flex", alignItems: "center", justifyContent: "center",
      padding: 24,
    }}>
      <div style={{
        background: T.bg.surface, border: `1px solid ${T.border.default}`,
        borderRadius: T.radius.xl, padding: "36px 40px",
        width: "100%", maxWidth: 380,
        boxShadow: "0 24px 80px rgba(0,0,0,0.5)",
      }}>
        {/* Logo */}
        <div style={{ textAlign: "center", marginBottom: 28 }}>
          <div style={{ fontSize: 36, marginBottom: 8 }}>⚡</div>
          <h2 style={{ margin: 0, color: T.text.primary, fontSize: 20, fontWeight: 700, letterSpacing: "-0.02em" }}>
            EmotiCode
          </h2>
          <p style={{ margin: "6px 0 0", color: T.text.muted, fontSize: 12 }}>
            {mode === "login" ? "Sign in to your account" : "Create a new account"}
          </p>
        </div>

        {/* Tab switcher */}
        <div style={{
          display: "flex", background: T.bg.elevated,
          borderRadius: T.radius.md, padding: 3, marginBottom: 22,
        }}>
          {["login", "register"].map((m) => (
            <button key={m} onClick={() => { setMode(m); setError(""); setSuccess(""); }}
              style={{
                flex: 1, padding: "7px 0", borderRadius: T.radius.sm,
                background: mode === m ? T.bg.overlay : "transparent",
                border: mode === m ? `1px solid ${T.border.strong}` : "1px solid transparent",
                color: mode === m ? T.text.primary : T.text.muted,
                fontSize: 12, fontWeight: mode === m ? 600 : 400, cursor: "pointer",
              }}>
              {m === "login" ? "Sign In" : "Register"}
            </button>
          ))}
        </div>

        {/* Status messages */}
        {error && (
          <div style={{
            background: `${T.red}12`, border: `1px solid ${T.red}40`,
            borderRadius: T.radius.md, padding: "8px 12px",
            color: "#fca5a5", fontSize: 12, marginBottom: 14,
          }}>{error}</div>
        )}
        {success && (
          <div style={{
            background: `${T.green}12`, border: `1px solid ${T.green}40`,
            borderRadius: T.radius.md, padding: "8px 12px",
            color: "#86efac", fontSize: 12, marginBottom: 14,
          }}>{success}</div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit}>
          <Field
            label="Email Address" type="email" value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com" autoComplete="email"
          />
          <Field
            label="Password" type="password" value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder={mode === "register" ? "At least 8 characters" : "Your password"}
            autoComplete={mode === "login" ? "current-password" : "new-password"}
          />
          {mode === "register" && (
            <Field
              label="Confirm Password" type="password" value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
              placeholder="Repeat password" autoComplete="new-password"
            />
          )}

          <button type="submit" disabled={loading || !email || !password} style={{
            width: "100%", padding: "10px 0",
            background: loading ? `${T.blue}80` : T.blue,
            border: "none", borderRadius: T.radius.md,
            color: "#fff", fontSize: 14, fontWeight: 700,
            cursor: loading ? "wait" : (!email || !password ? "not-allowed" : "pointer"),
            opacity: !email || !password ? 0.6 : 1,
            marginTop: 4,
          }}>
            {loading ? "…" : mode === "login" ? "Sign In →" : "Create Account →"}
          </button>
        </form>

        {/* Divider */}
        <div style={{
          display: "flex", alignItems: "center", gap: 10, margin: "18px 0",
        }}>
          <div style={{ flex: 1, height: 1, background: T.border.subtle }} />
          <span style={{ color: T.text.dim, fontSize: 11 }}>or</span>
          <div style={{ flex: 1, height: 1, background: T.border.subtle }} />
        </div>

        {/* Guest access */}
        <button onClick={guestLogin} style={{
          width: "100%", padding: "9px 0",
          background: "transparent", border: `1px solid ${T.border.default}`,
          borderRadius: T.radius.md, color: T.text.secondary,
          fontSize: 13, cursor: "pointer",
        }}>
          Continue as Guest
        </button>

        <p style={{ textAlign: "center", color: T.text.dim, fontSize: 10, marginTop: 20 }}>
          Guest mode tracks progress locally in your browser.
        </p>
      </div>
    </div>
  );
}
