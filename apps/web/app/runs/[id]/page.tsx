"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { StateContainer } from "../../../components/StateContainer";
import { RunTimeline } from "../../../components/RunTimeline";
import {
  sampleRuns,
  sampleRunEvents,
  sampleArtifacts,
  sampleObjectives,
  Artifact,
} from "../../../lib/fixtures";

export default function RunInspectionPage() {
  const params = useParams();
  const runId = params?.id as string;

  const run =
    sampleRuns.find((r) => r.id === runId) || sampleRuns[0];
  const objective =
    sampleObjectives.find((o) => o.id === run.objective_id) ||
    sampleObjectives[0];

  const [selectedArtifact, setSelectedArtifact] = useState<Artifact | null>(
    null
  );

  return (
    <StateContainer
      emptyTitle="No events recorded for this run ID"
      emptyDescription="The execution graph has not emitted any durable events for this run."
    >
      <div style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
        {/* Header section */}
        <div>
          <Link
            href="/"
            style={{
              fontSize: "0.85rem",
              color: "var(--text-accent)",
              display: "inline-flex",
              alignItems: "center",
              gap: "0.35rem",
              marginBottom: "0.5rem",
            }}
          >
            ← Back to Dashboard
          </Link>

          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              flexWrap: "wrap",
              gap: "1rem",
            }}
          >
            <div>
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "0.6rem",
                  marginBottom: "0.35rem",
                }}
              >
                <span
                  className={`badge ${
                    run.status === "completed"
                      ? "badge-done"
                      : run.status === "running"
                      ? "badge-running"
                      : "badge-failed"
                  }`}
                >
                  Run: {run.status}
                </span>
                <span
                  style={{
                    fontSize: "0.75rem",
                    color: "var(--text-tertiary)",
                    fontFamily: "monospace",
                  }}
                >
                  Run ID: {run.id}
                </span>
              </div>
              <h1 style={{ fontSize: "1.75rem" }}>Run Inspection Timeline</h1>
              <p
                style={{
                  fontSize: "0.95rem",
                  color: "var(--text-secondary)",
                }}
              >
                Objective: <strong>{objective.title}</strong>
              </p>
            </div>

            <div style={{ display: "flex", gap: "0.75rem" }}>
              <Link
                href={`/objectives/${objective.id}/plan`}
                className="btn btn-secondary"
              >
                Inspect Plan
              </Link>
              {run.status === "failed" && (
                <button className="btn btn-primary">🔄 Retry Run</button>
              )}
            </div>
          </div>
        </div>

        {/* Runtime Model & Metadata Cards */}
        <div className="grid-cols-3">
          <div className="card">
            <div
              style={{
                fontSize: "0.75rem",
                color: "var(--text-tertiary)",
                textTransform: "uppercase",
                marginBottom: "0.25rem",
              }}
            >
              Runtime Model
            </div>
            <div
              style={{
                fontSize: "1.25rem",
                fontWeight: 600,
                color: "var(--text-accent)",
              }}
            >
              gemini-3.1-pro
            </div>
            <div
              style={{
                fontSize: "0.8rem",
                color: "var(--text-secondary)",
                marginTop: "0.2rem",
              }}
            >
              Configured frontier runtime model
            </div>
          </div>

          <div className="card">
            <div
              style={{
                fontSize: "0.75rem",
                color: "var(--text-tertiary)",
                textTransform: "uppercase",
                marginBottom: "0.25rem",
              }}
            >
              Graph Execution Version
            </div>
            <div
              style={{
                fontSize: "1.25rem",
                fontWeight: 600,
                color: "var(--text-primary)",
              }}
            >
              {run.graph_version}
            </div>
            <div
              style={{
                fontSize: "0.8rem",
                color: "var(--text-secondary)",
                marginTop: "0.2rem",
              }}
            >
              Idempotent state transitions
            </div>
          </div>

          <div className="card">
            <div
              style={{
                fontSize: "0.75rem",
                color: "var(--text-tertiary)",
                textTransform: "uppercase",
                marginBottom: "0.25rem",
              }}
            >
              Produced Artifacts
            </div>
            <div
              style={{
                fontSize: "1.25rem",
                fontWeight: 600,
                color: "var(--accent-emerald)",
              }}
            >
              {sampleArtifacts.length} Artifact Records
            </div>
            <div
              style={{
                fontSize: "0.8rem",
                color: "var(--text-secondary)",
                marginTop: "0.2rem",
              }}
            >
              Persistent Markdown records
            </div>
          </div>
        </div>

        {/* Error Callout if failed */}
        {run.status === "failed" && (
          <div className="alert-box alert-error">
            <div style={{ fontSize: "1.5rem" }}>❌</div>
            <div>
              <h4
                style={{
                  color: "#ffe4e6",
                  marginBottom: "0.25rem",
                  fontWeight: 600,
                }}
              >
                Execution Error: {run.error_code || "ERR_SPECIALIST_TIMEOUT"}
              </h4>
              <p style={{ fontSize: "0.9rem", color: "#fecdd3" }}>
                Specialist execution halted after failure on Step #6. No
                subsequent work items will execute until the error is resolved.
              </p>
            </div>
          </div>
        )}

        {/* Event Timeline and Artifacts Split View */}
        <div
          style={{
            display: "grid",
            gridTemplateColumns: "2fr 1fr",
            gap: "2rem",
          }}
        >
          {/* Timeline Column */}
          <div className="card">
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                marginBottom: "1.5rem",
                borderBottom: "1px solid var(--border-color)",
                paddingBottom: "0.75rem",
              }}
            >
              <div>
                <h3 style={{ fontSize: "1.15rem" }}>Event Sequence Timeline</h3>
                <p
                  style={{
                    fontSize: "0.825rem",
                    color: "var(--text-secondary)",
                  }}
                >
                  Plain summaries without private model reasoning
                </p>
              </div>
              <span className="badge badge-running">
                {sampleRunEvents.length} Events
              </span>
            </div>

            <RunTimeline events={sampleRunEvents} />
          </div>

          {/* Artifacts Column */}
          <div className="card" style={{ height: "fit-content" }}>
            <div
              style={{
                marginBottom: "1.25rem",
                borderBottom: "1px solid var(--border-color)",
                paddingBottom: "0.75rem",
              }}
            >
              <h3 style={{ fontSize: "1.15rem" }}>Run Artifacts</h3>
              <p
                style={{
                  fontSize: "0.825rem",
                  color: "var(--text-secondary)",
                }}
              >
                Persistent outputs generated during this run
              </p>
            </div>

            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "1rem",
              }}
            >
              {sampleArtifacts.map((artifact) => (
                <div
                  key={artifact.id}
                  style={{
                    backgroundColor: "var(--bg-tertiary)",
                    border: "1px solid var(--border-color)",
                    borderRadius: "var(--radius-sm)",
                    padding: "1rem",
                    cursor: "pointer",
                  }}
                  onClick={() => setSelectedArtifact(artifact)}
                >
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      justifyContent: "space-between",
                      marginBottom: "0.35rem",
                    }}
                  >
                    <span
                      style={{
                        fontSize: "0.7rem",
                        textTransform: "uppercase",
                        color: "var(--text-accent)",
                        fontWeight: 600,
                      }}
                    >
                      {artifact.artifact_type}
                    </span>
                    <span
                      style={{
                        fontSize: "0.7rem",
                        color: "var(--text-tertiary)",
                      }}
                    >
                      v{artifact.version}
                    </span>
                  </div>

                  <h4 style={{ fontSize: "0.95rem", marginBottom: "0.4rem" }}>
                    {artifact.title}
                  </h4>
                  <div
                    style={{
                      fontSize: "0.775rem",
                      color: "var(--text-secondary)",
                      display: "-webkit-box",
                      WebkitLineClamp: 2,
                      WebkitBoxOrient: "vertical",
                      overflow: "hidden",
                    }}
                  >
                    {artifact.content_markdown}
                  </div>

                  <div
                    style={{
                      marginTop: "0.75rem",
                      fontSize: "0.8rem",
                      color: "var(--accent-primary)",
                    }}
                  >
                    Click to inspect full markdown →
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Artifact Modal */}
        {selectedArtifact && (
          <div
            style={{
              position: "fixed",
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: "rgba(0, 0, 0, 0.75)",
              backdropFilter: "blur(4px)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              zIndex: 100,
              padding: "2rem",
            }}
            onClick={() => setSelectedArtifact(null)}
          >
            <div
              className="card"
              style={{
                maxWidth: "800px",
                width: "100%",
                maxHeight: "80vh",
                overflowY: "auto",
              }}
              onClick={(e) => e.stopPropagation()}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  marginBottom: "1rem",
                  borderBottom: "1px solid var(--border-color)",
                  paddingBottom: "0.75rem",
                }}
              >
                <div>
                  <span
                    className="badge badge-approved"
                    style={{ marginRight: "0.5rem" }}
                  >
                    {selectedArtifact.artifact_type}
                  </span>
                  <h3 style={{ marginTop: "0.25rem" }}>
                    {selectedArtifact.title}
                  </h3>
                </div>
                <button
                  className="btn btn-sm btn-secondary"
                  onClick={() => setSelectedArtifact(null)}
                >
                  ✕ Close
                </button>
              </div>

              <pre
                style={{
                  whiteSpace: "pre-wrap",
                  fontFamily: "inherit",
                  fontSize: "0.9rem",
                  lineHeight: 1.6,
                  color: "var(--text-primary)",
                  backgroundColor: "var(--bg-primary)",
                  padding: "1.25rem",
                  borderRadius: "var(--radius-sm)",
                  border: "1px solid var(--border-color)",
                }}
              >
                {selectedArtifact.content_markdown}
              </pre>
            </div>
          </div>
        )}
      </div>
    </StateContainer>
  );
}
