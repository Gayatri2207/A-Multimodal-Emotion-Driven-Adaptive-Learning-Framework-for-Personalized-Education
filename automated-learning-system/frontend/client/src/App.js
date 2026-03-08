import React from "react";
import { BrowserRouter, Routes, Route, NavLink, useNavigate } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import CodingInterface from "./pages/CodingInterface";
import TeacherDashboard from "./pages/TeacherDashboard";
import ProblemsPage from "./pages/ProblemsPage";
import LoginPage from "./pages/LoginPage";
import OnboardingModal from "./components/OnboardingModal";
import "./App.css";

const NAV_LINKS = [
  { to: "/",        label: "Dashboard", end: true },
  { to: "/problems",label: "Problems" },
  { to: "/code",    label: "Editor" },
  { to: "/teacher", label: "Teacher" },
];

function NavUser() {
  const navigate = useNavigate();
  const email = localStorage.getItem("userEmail");
  const token = localStorage.getItem("token");

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("userEmail");
    navigate("/login");
  };

  if (!email) return (
    <button onClick={() => navigate("/login")} style={{
      background: "transparent", border: "1px solid #2a3347",
      color: "#4a5568", padding: "3px 12px", borderRadius: 6,
      cursor: "pointer", fontSize: 12, marginLeft: "auto",
    }}>
      Sign In
    </button>
  );

  return (
    <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 10 }}>
      <span style={{ color: "#4a5568", fontSize: 11 }}>
        {token ? "🔒" : "👤"} {email.length > 20 ? email.slice(0, 20) + "…" : email}
      </span>
      <button onClick={logout} style={{
        background: "transparent", border: "1px solid #2a3347",
        color: "#4a5568", padding: "3px 10px", borderRadius: 6,
        cursor: "pointer", fontSize: 11,
      }}>
        Sign Out
      </button>
    </div>
  );
}

function Nav() {
  return (
    <nav style={{
      background: "#0f1117",
      borderBottom: "1px solid #1e2535",
      padding: "0 20px",
      height: 48,
      display: "flex",
      alignItems: "center",
      gap: 4,
      position: "sticky",
      top: 0,
      zIndex: 100,
    }}>
      {/* Logo */}
      <NavLink to="/" style={{ textDecoration: "none", display: "flex", alignItems: "center", gap: 8, marginRight: 20 }}>
        <span style={{ fontSize: 18 }}>⚡</span>
        <span style={{ color: "#e2e8f0", fontWeight: 700, fontSize: 14, letterSpacing: "-0.02em" }}>
          EmotiCode
        </span>
      </NavLink>

      {/* Nav links */}
      {NAV_LINKS.map(({ to, label, end }) => (
        <NavLink key={to} to={to} end={end} style={({ isActive }) => ({
          color:          isActive ? "#e2e8f0" : "#4a5568",
          textDecoration: "none",
          padding:        "4px 12px",
          borderRadius:   6,
          fontSize:       13,
          fontWeight:     isActive ? 600 : 400,
          background:     isActive ? "#1e2535" : "transparent",
          border:         `1px solid ${isActive ? "#2a3347" : "transparent"}`,
        })}>
          {label}
        </NavLink>
      ))}

      <NavUser />
    </nav>
  );
}

function App() {
  return (
    <BrowserRouter>
      <div style={{ minHeight: "100vh", background: "#0c0e14", color: "#e2e8f0" }}>
        <Nav />
        <OnboardingModal />
        <Routes>
          <Route path="/"                element={<Dashboard />} />
          <Route path="/problems"        element={<ProblemsPage />} />
          <Route path="/code"            element={<CodingInterface />} />
          <Route path="/code/:problemId" element={<CodingInterface />} />
          <Route path="/teacher"         element={<TeacherDashboard />} />
          <Route path="/login"           element={<LoginPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
