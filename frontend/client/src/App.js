import React, { useRef, useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import 'chart.js/auto';

function App() {

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [emotion, setEmotion] = useState("Waiting...");
  const [history, setHistory] = useState([]);

  useEffect(() => {

    navigator.mediaDevices.getUserMedia({ video: true })
      .then(stream => {
        videoRef.current.srcObject = stream;
      });

    const ws = new WebSocket("ws://localhost:8000/ws/realtime");

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setEmotion(data.final);
      setHistory(prev => [...prev.slice(-20), data.final]);
    };

    const interval = setInterval(() => {
      const canvas = canvasRef.current;
      const ctx = canvas.getContext("2d");

      ctx.drawImage(videoRef.current, 0, 0, 320, 240);
      const image = canvas.toDataURL("image/jpeg");

      ws.send(image);
    }, 500);

    return () => clearInterval(interval);

  }, []);

  const chartData = {
    labels: history.map((_, i) => i),
    datasets: [{
      label: "Emotion Timeline",
      data: history.map(e => e === "happy" ? 1 : 0),
      borderColor: "blue"
    }]
  };

  return (
    <div style={{ padding: 30 }}>
      <h2>Real-Time Emotion Dashboard</h2>
      <video ref={videoRef} autoPlay width="320" height="240"/>
      <canvas ref={canvasRef} width="320" height="240" style={{display:"none"}}/>
      <h3>Current Emotion: {emotion}</h3>
      <Line data={chartData}/>
    </div>
  );
}

export default App;
