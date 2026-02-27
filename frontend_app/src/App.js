import React, { useState } from "react";
import Login from "./components/Login";
import Dashboard from "./components/Dashboard";

export default function App() {
  const [token, setToken] = useState(localStorage.getItem("token"));

  return token ? (
    <Dashboard token={token} onLogout={() => { localStorage.removeItem("token"); setToken(null); }} />
  ) : (
    <Login onLogin={(t) => { localStorage.setItem("token", t); setToken(t); }} />
  );
}
