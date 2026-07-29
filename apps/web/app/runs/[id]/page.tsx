"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { StateContainer } from "../../../components/StateContainer";
import { RunTimeline } from "../../../components/RunTimeline";
import {
  sampleRuns,
  sampleRunEvents,
  sampleArtifacts,
  sampleObjectives,
} from "../../../lib/fixtures";
import {
  getRun,
  listRunEvents,
  listRunArtifacts,
  retryRun,
  getObjective,
  generateIdempotencyKey,
  getApiBaseUrl,
  AgentRun,
  RunEvent,
  Artifact,
  Objective,
} from "../../../lib/api-client";

export default function RunInspectionPage() {
  const params = useParams();
  const runId = params?.id as string;

  const [run, setRun] = useState<AgentRun>(
    (sampleRuns.find((r) => r.id === runId) || sampleRuns[0]) as unknown as AgentRun
  );
  const [objective, setObjective] = useState<Objective>(
    (sampleObjectives.find((o) => o.id === (run ? run.objective_id : "")) ||
      sampleObjectives[0]) as unknown as Objective
  );
  const [events, setEvents] = useState<RunEvent[]>(
    (sampleRunEvents.filter((e) => e.run_id === runId).length > 0
      ? sampleRunEvents.filter((e) => e.run_id === runId)
      : sampleRunEvents) as unknown as RunEvent[]
  );
  const [artifacts, setArtifacts] = useState<Artifact[]>(
    (sampleArtifacts.filter((a) => a.run_id === runId).length > 0
      ? sampleArtifacts.filter((a) => a.run_id === runId)
      : sampleArtifacts) as unknown as Artifact[]
  );
  const [selectedArtifact, setSelectedArtifact] = useState<Artifact | null>(
    null
  );
  const [isRetrying, setIsRetrying] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    Promise.all([
      getRun(runId),
      listRunEvents(runId),
      listRunArtifacts(runId),
    ])
      .then(([runData, evData, artData]) => {
        if (!mounted) return;
        setRun(runData);
        if (evData.length > 0) setEvents(evData);
        if (artData.length > 0) setArtifacts(artData);
        return getObjective(runData.objective_id)
          .then((objData) => {
            if (mounted) setObjective(objData);
          })
          .catch(() => {});
      })
      .catch((err) => {
        if (!mounted) return;
        console.warn("API offline or error fetching run data, using fixtures:", err);
      });
    return () => {
      mounted = false;
    };
  }, [runId]);

  useEffect(() => {
    let es: EventSource | null = null;
    try {
      const maxSequence =
        events.length > 0
          ? Math.max(...events.map((e) => e.sequence || 0))
          : 0;
      const url = `${getApiBaseUrl()}/api/runs/${encodeURIComponent(
        runId
      )}/stream?after_sequence=${maxSequence}`;
      es = new EventSource(url);

      const eventTypes = [
        "run.created",
        "plan.proposed",
        "plan.revision_requested",
        "plan.approved",
        "work.started",
        "work.progress",
        "artifact.created",
        "work.completed",
        "work.failed",
        "brief.created",
        "run.completed",
        "run.failed",
      ];

      const handler = (msg: MessageEvent) => {
        try {
          const newEv = JSON.parse(msg.data) as RunEvent;
          setEvents((prev) => {
            if (prev.some((e) => e.sequence === newEv.sequence)) {
              return prev;
            }
            return [...prev, newEv].sort((a, b) => a.sequence - b.sequence);
          });
          if (newEv.event_type === "artifact.created") {
            listRunArtifacts(runId)
              .then((arts) => setArtifacts(arts))
              .catch(() => {});
          } else if (
            newEv.event_type === "run.completed" ||
            newEv.event_type === "run.failed"
          ) {
            getRun(runId)
              .then((r) => setRun(r))
              .catch(() => {});
            listRunArtifacts(runId)
              .then((arts) => setArtifacts(arts))
              .catch(() => {});
            if (es) es.close();
          }
        } catch (err) {
          // ignore parse errors
        }
      };

      eventTypes.forEach((type) => {
        es?.addEventListener(type, handler);
      });
    } catch (err) {
      console.warn("EventSource stream not available:", err);
    }

    return () => {
      if (es) es.close();
    };
  }, [runId]);

  const handleRetry = async () => {
    setIsRetrying(true);
    setError(null);
    const key = generateIdempotencyKey();
    try {
      const updatedRun = await retryRun(runId, key);
      setRun(updatedRun);
    } catch (err) {
      console.warn("API offline or retryRun failed:", err);
      // fallback in offline mode
      setRun((prev) => ({ ...prev, status: "running" as const, retryable: false }));
    } finally {
      setIsRetrying(false);
    }
  };

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
              {(run.retryable || run.status === "failed") && (
                <button
                  className="btn btn-primary"
                  onClick={handleRetry}
                  disabled={isRetrying}
                >
                  {isRetrying ? "Retrying..." : "🔄 Retry Run"}
                </button>
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
                {events.length} Events
              </span>
            </div>

            <RunTimeline events={events} artifacts={artifacts} />
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
              {artifacts.map((artifact) => (
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
