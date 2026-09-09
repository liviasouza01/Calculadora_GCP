import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { DEFAULT_FLAGS } from "./flags";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App flags={DEFAULT_FLAGS} />
  </React.StrictMode>,
);
