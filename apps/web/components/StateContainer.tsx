"use client";

import React from "react";
import { useDemoState } from "../lib/StateContext";

interface StateContainerProps {
  children: React.ReactNode;
  emptyTitle?: string;
  emptyDescription?: string;
}

export function StateContainer({
  children,
  emptyTitle = "No items in this view yet",
  emptyDescription = "Get started by submitting a new company objective or reviewing proposed work items.",
}: StateContainerProps) {
  const { demoState, setDemoState } = useDemoState();

  if (demoState === "loading") {
    return (
      <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        <div className="skeleton" style={{ height: "140px", width: "100%" }} />
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(3, 1fr)",
            gap: "1rem",
          }}
        >
          <div className="skeleton" style={{ height: "200px" }} />
          <div className="skeleton" style={{ height: "200px" }} />
          <div className="skeleton" style={{ height: "200px" }} />
        </div>
        <div className="skeleton" style={{ height: "280px", width: "100%" }} />
      </div>
    );
  }

  if (demoState === "empty") {
    return (
      <div className="alert-box alert-empty">
        <div style={{ fontSize: "2.5rem", marginBottom: "0.5rem" }}>📭</div>
        <h3 style={{ marginBottom: "0.5rem", color: "var(--text-primary)" }}>
          {emptyTitle}
        </h3>
        <p
          style={{
            color: "var(--text-secondary)",
            maxWidth: "500px",
            marginBottom: "1.25rem",
            fontSize: "0.95rem",
          }}
        >
          {emptyDescription}
        </p>
        <button
          className="btn btn-primary"
          onClick={() => setDemoState("completed")}
        >
          Switch to Completed State
        </button>
      </div>
    );
  }

  if (demoState === "error") {
    return (
      <div className="alert-box alert-error">
        <div style={{ fontSize: "1.5rem" }}>⚠️</div>
        <div style={{ flex: 1 }}>
          <h4
            style={{
              color: "#ffe4e6",
              marginBottom: "0.25rem",
              fontWeight: 600,
            }}
          >
            ERR_SPECIALIST_TIMEOUT
          </h4>
          <p style={{ fontSize: "0.9rem", color: "#fecdd3" }}>
            The specialist agent execution timed out while attempting to contact
            the runtime model endpoint. Work item processing was halted safely.
          </p>
          <div style={{ marginTop: "1rem" }}>
            <button
              className="btn btn-sm btn-secondary"
              style={{
                backgroundColor: "rgba(255, 255, 255, 0.15)",
                color: "white",
              }}
              onClick={() => setDemoState("completed")}
            >
              Retry Execution
            </button>
          </div>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
