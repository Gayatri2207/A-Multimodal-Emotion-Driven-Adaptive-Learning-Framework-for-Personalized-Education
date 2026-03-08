import React, { useEffect, useRef, useState, useCallback } from "react";
import Editor from "@monaco-editor/react";
import axios from "axios";
import { useParams } from "react-router-dom";
import { T } from "../components/coding/theme";
import ProblemSidebar     from "../components/coding/ProblemSidebar";
import ProblemDescription from "../components/coding/ProblemDescription";
import SubmissionResults  from "../components/coding/SubmissionResults";
import EmotionPanel       from "../components/coding/EmotionPanel";

const API            = process.env.REACT_APP_API_URL || "http://localhost:8000";
const WS_URL         = process.env.REACT_APP_WS_URL  || "ws://localhost:8000/ws/emotion";
const FRAME_INTERVAL = 2000;

export default function CodingInterface() {
  const { problemId } = useParams();
  const webcamRef = useRef(null);
  const wsRef = useRef(null);
  const keystrokeLog = useRef({ intervals: [], lastTime: null, mistakes: 0, totalChars: 0 });

  const [problems, setProblems] = useState([]);
  const [filteredProblems, setFilteredProblems] = useState([]);
  const [diffFilter, setDiffFilter] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedId, setSelectedId] = useState(problemId ? Number(problemId) : null);
  const [problem, setProblem] = useState(null);
  const [code, setCode] = useState("# Write your solution here\n");
  const [result, setResult] = useState(null);
  const [running, setRunning] = useState(false);
  const [hint, setHint] = useState(null);
  const [wsStatus, setWsStatus] = useState("disconnected");
  const [cameraOn, setCameraOn] = useState(true);
  const [showHints, setShowHints] = useState(false);
  const [showExamples, setShowExamples] = useState(true);
  const [submissionHistory, setSubmissionHistory] = useState([]);
  const [tutorFeedback, setTutorFeedback] = useState(null);
  const [tutorLoading, setTutorLoading] = useState(false);
  const [showTutor, setShowTutor] = useState(false);
  const [solvedSet, setSolvedSet] = useState(() => {
    try {
      const stored = JSON.parse(localStorage.getItem("solvedProblems") || "{}");
      return new Set(Object.keys(stored).filter((k) => stored[k]));
    } catch {
      return new Set();
    }
  });

  useEffect(() => {
    axios.get(`${API}/coding/problems`)
      .then(({ data }) => {
        setProblems(data);
        setFilteredProblems(data);
        if (!selectedId && data.length) setSelectedId(data[0].id);
      })
      .catch((err) => console.error("[CodingInterface] Failed to load problems:", err));
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    let filtered = problems;
    if (diffFilter !== "all") filtered = filtered.filter((p) => p.difficulty === diffFilter);
    if (searchQuery.trim()) {
      const q = searchQuery.trim().toLowerCase();
      filtered = filtered.filter(
        (p) => p.title.toLowerCase().includes(q) || (p.category || "").toLowerCase().includes(q)
      );
    }
    setFilteredProblems(filtered);
  }, [diffFilter, searchQuery, problems]);

  useEffect(() => {
    if (!selectedId) return;
    axios.get(`${API}/coding/problems/${selectedId}`)
      .then(({ data }) => {
        setProblem(data);
        setCode(data.starter_code || "# Write your solution here\n");
        setResult(null);
        setShowHints(false);
      })
      .catch((err) => console.error("[CodingInterface] Failed to load problem:", err));
  }, [selectedId]);

  useEffect(() => {
    let ws;
    try {
      ws = new WebSocket(WS_URL);
      ws.onopen = () => { wsRef.current = ws; setWsStatus("connected"); };
      ws.onclose = () => { wsRef.current = null; setWsStatus("disconnected"); };
      ws.onerror = () => setWsStatus("error");
      ws.onmessage = (evt) => {
        try {
          const d = JSON.parse(evt.data);
          if (d.adaptive_action) setHint(d);
        } catch {}
      };
    } catch {}
    return () => ws && ws.close();
  }, []);

  useEffect(() => {
    const interval = setInterval(() => {
      if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
      const log = keystrokeLog.current;
      const userId = parseInt(localStorage.getItem("userId") || "1", 10);
      const payload = {
        user_id: userId,
        typing_data: { intervals: log.intervals.slice(-50), mistakes: log.mistakes, total_chars: log.totalChars },
      };
      if (cameraOn && webcamRef.current) {
        try {
          const shot = webcamRef.current.getScreenshot();
          if (shot) payload.facial_frame = shot.split(",")[1];
        } catch {}
      }
      wsRef.current.send(JSON.stringify(payload));
      log.intervals = [];
    }, FRAME_INTERVAL);
    return () => clearInterval(interval);
  }, [cameraOn]);

  const handleKeyDown = useCallback((e) => {
    const now = Date.now();
    const log = keystrokeLog.current;
    if (log.lastTime !== null) log.intervals.push((now - log.lastTime) / 1000);
    log.lastTime = now;
    log.totalChars += 1;
    if (e.key === "Backspace") log.mistakes += 1;
  }, []);

  const handleCodeChange = useCallback((value) => setCode(value || ""), []);

  const runCode = async () => {
    if (!problem) return;
    setRunning(true);
    setResult(null);
    const userId = parseInt(localStorage.getItem("userId") || "1", 10);
    try {
      const { data } = await axios.post(`${API}/coding/submit`, {
        user_id: userId,
        problem_id: problem.id,
        code,
        emotion_score: hint?.emotion_score ?? 0.5,
        performance_score: hint?.performance_score ?? 0.5,
      });
      setResult(data);
      if (data.adaptive_action) setHint((prev) => ({ ...(prev || {}), ...data }));
      // Mark problem as solved in localStorage if all tests pass
      if (data.score === 1.0 && problem?.id) {
        const existing = JSON.parse(localStorage.getItem("solvedProblems") || "{}");
        existing[problem.id] = true;
        localStorage.setItem("solvedProblems", JSON.stringify(existing));
        setSolvedSet((prev) => new Set([...prev, String(problem.id)]));
      }
      setSubmissionHistory((prev) => [
        { id: data.submission_id, score: data.score, passed: data.passed, total: data.total, time: new Date().toLocaleTimeString() },
        ...prev.slice(0, 4),
      ]);
    } catch (err) {
      setResult({ error: err.response?.data?.detail || "Submission failed" });
    } finally {
      setRunning(false);
    }
  };

  const askTutor = async () => {
    if (!problem || !code.trim()) return;
    setTutorLoading(true);
    setShowTutor(true);
    setTutorFeedback(null);
    const userId = parseInt(localStorage.getItem("userId") || "1", 10);
    try {
      const { data } = await axios.post(`${API}/ai-tutor`, {
        problem: `${problem.title}\n\n${problem.description}`,
        code,
        emotion_score: hint?.emotion_score ?? 0.5,
        user_id: userId,
      });
      setTutorFeedback(data);
    } catch (err) {
      setTutorFeedback({ error: err.response?.data?.detail || "Tutor unavailable" });
    } finally {
      setTutorLoading(false);
    }
  };

  const examples = (() => { try { return JSON.parse(problem?.examples || "[]"); } catch { return []; } })();
  const hints    = (() => { try { return JSON.parse(problem?.hints    || "[]"); } catch { return []; } })();

  return (
    <div style={{ display: "flex", height: "calc(100vh - 48px)", overflow: "hidden" }}>

      {/* LEFT: searchable problem list */}
      <ProblemSidebar
        problems={problems}
        filteredProblems={filteredProblems}
        selectedId={selectedId}
        diffFilter={diffFilter}
        searchQuery={searchQuery}
        solvedSet={solvedSet}
        hint={hint}
        onSelect={setSelectedId}
        onDiffFilter={setDiffFilter}
        onSearch={setSearchQuery}
      />

      {/* CENTER: description + editor + results */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden", minWidth: 0 }}>

        <ProblemDescription
          problem={problem}
          examples={examples}
          hints={hints}
          showHints={showHints}
          showExamples={showExamples}
          onToggleHints={() => setShowHints((v) => !v)}
          onToggleExamples={() => setShowExamples((v) => !v)}
        />

        {/* Monaco editor */}
        <div style={{ flex: 1, minHeight: 0 }} onKeyDown={handleKeyDown}>
          <Editor
            height="100%"
            defaultLanguage="python"
            value={code}
            onChange={handleCodeChange}
            theme="vs-dark"
            options={{ fontSize: 14, minimap: { enabled: false }, scrollBeyondLastLine: false, fontFamily: "JetBrains Mono, Fira Code, monospace" }}
          />
        </div>

        {/* Action toolbar */}
        <div style={{
          padding: "8px 16px",
          background: T.bg.base,
          borderTop: `1px solid ${T.border.default}`,
          display: "flex", alignItems: "center", gap: 10, flexWrap: "wrap",
        }}>
          <button
            onClick={runCode}
            disabled={running || !problem}
            style={{
              background: running ? `${T.green}10` : `${T.green}18`,
              border:     `1px solid ${running ? T.green + "50" : T.green}`,
              color:      T.green,
              padding:    "7px 22px", borderRadius: T.radius.md,
              cursor:     running ? "wait" : (problem ? "pointer" : "not-allowed"),
              fontSize:   13, fontWeight: 600,
              opacity:    problem ? 1 : 0.4,
            }}
          >
            {running ? "⏳ Running…" : "▶  Run & Submit"}
          </button>

          <button
            onClick={askTutor}
            disabled={tutorLoading || !problem}
            style={{
              background: showTutor ? `${T.purple}18` : `${T.purple}0a`,
              border:     `1px solid ${showTutor ? T.purple : T.purple + "55"}`,
              color:      T.purple,
              padding:    "7px 14px", borderRadius: T.radius.md,
              cursor:     tutorLoading ? "wait" : (problem ? "pointer" : "not-allowed"),
              fontSize:   13, opacity: problem ? 1 : 0.4,
            }}
          >
            {tutorLoading ? "🤖 Analysing…" : "🤖 Ask AI Tutor"}
          </button>
        </div>

        {/* Test results + history */}
        <SubmissionResults result={result} submissionHistory={submissionHistory} />
      </div>

      {/* RIGHT: emotion camera + adaptive engine + AI tutor */}
      <EmotionPanel
        webcamRef={webcamRef}
        cameraOn={cameraOn}
        wsStatus={wsStatus}
        hint={hint}
        result={result}
        problems={problems}
        tutorFeedback={tutorFeedback}
        tutorLoading={tutorLoading}
        showTutor={showTutor}
        onToggleCamera={() => setCameraOn((v) => !v)}
        onCloseTutor={() => setShowTutor(false)}
      />
    </div>
  );
}
