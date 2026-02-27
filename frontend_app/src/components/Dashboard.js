import React, { useEffect, useState, useRef } from "react";
import axios from "axios";
import Card from "./Card";

export default function Dashboard({ token, onLogout }) {
  const [adaptiveAction, setAdaptiveAction] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const wsRef = useRef(null);

  useEffect(() => {
    fetchAnalytics();
    const ws = new WebSocket("ws://localhost:8000/ws/emotion");
    ws.onopen = () => console.log("ws open");
    ws.onmessage = (ev) => {
      try {
        const data = JSON.parse(ev.data);
        setAdaptiveAction(data.adaptive_action || null);
      } catch (e) {
        console.error(e);
      }
    };
    ws.onclose = () => console.log("ws closed");
    wsRef.current = ws;
    return () => ws.close();
  }, []);

  async function fetchAnalytics() {
    try {
      const res = await axios.get("http://localhost:8000/analytics/summary");
      setAnalytics(res.data);
    } catch (e) {
      console.error(e);
    }
  }

  function sendSample() {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
    // sample payload
    const payload = { emotion_score: Math.random().toFixed(2), performance_score: Math.random().toFixed(2) };
    wsRef.current.send(JSON.stringify(payload));
  }

  return (
    <div className="layout">
      <header className="topbar">
        <h1>Emotion-Adaptive Dashboard</h1>
        <div>
          <button onClick={sendSample}>Send Sample</button>
          <button onClick={onLogout}>Logout</button>
        </div>
      </header>
      <main>
        <div className="grid">
          <Card title="Real-time Adaptive Action">
            <div className="action">{adaptiveAction || "—"}</div>
          </Card>
          <Card title="Analytics">
            {analytics ? (
              <div>
                <div>Average Emotion: {analytics.average_emotion.toFixed(2)}</div>
                <div>Average Performance: {analytics.average_performance.toFixed(2)}</div>
                <div>Engagement Score: {analytics.engagement_score.toFixed(2)}</div>
              </div>
            ) : (
              <div>Loading...</div>
            )}
          </Card>
        </div>
      </main>
    </div>
  );
}
