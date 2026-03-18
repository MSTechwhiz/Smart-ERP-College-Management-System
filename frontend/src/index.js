/**
 * Startup Instructions:
 * 1. Open a terminal and navigate to the 'frontend' directory.
 * 2. Install dependencies (if not already done): npm install
 * 3. Start the application: npm start
 */

import React from "react";
import ReactDOM from "react-dom/client";
import "@/index.css";
import App from "@/App";
import { ThemeProvider } from "./context/ThemeContext";

const root = ReactDOM.createRoot(document.getElementById("root"));

root.render(
  <React.StrictMode>
    <ThemeProvider>
      <App />
    </ThemeProvider>
  </React.StrictMode>,
);
