import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css";

const container = document.getElementById("root") || document.createElement("div");
if (!container.id) document.body.appendChild(container);
createRoot(container).render(<App />);
