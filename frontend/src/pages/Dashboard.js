import React, { useEffect, useState } from "react";
import axios from "axios";

function Dashboard() {
  const [analytics, setAnalytics] = useState({});

  useEffect(() => {
    axios.get("http://localhost:8000/analytics")
      .then(res => setAnalytics(res.data))
      .catch(err => console.log(err));
  }, []);

  return (
    <div style={{ padding: 40, fontFamily: "Arial", background: "#111", minHeight: "100vh", color: "white" }}>
      <h2>Emotion Adaptive Learning Dashboard</h2>

      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(3, 1fr)",
        gap: 20,
        marginTop: 30
      }}>
        <Card title="Avg Emotion" value={analytics.average_emotion} />
        <Card title="Avg Performance" value={analytics.average_performance} />
        <Card title="Engagement Score" value={analytics.engagement_score} />
      </div>
    </div>
  );
}

function Card({ title, value }) {
  return (
    <div style={{
      padding: 20,
      background: "#222",
      borderRadius: 12,
      textAlign: "center",
      boxShadow: "0 0 20px #00ff88"
    }}>
      <h4>{title}</h4>
      <h2 style={{ color: "#00ff88" }}>{value}</h2>
    </div>
  );
}

export default Dashboard;
