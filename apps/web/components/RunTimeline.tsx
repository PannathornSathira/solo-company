"use client";

import React, { useState } from "react";
import { RunEvent, sampleArtifacts, Artifact } from "../lib/fixtures";

interface RunTimelineProps {
  events: RunEvent[];
}

export function RunTimeline({ events }: RunTimelineProps) {
  const [selectedArtifact, setSelectedArtifact] = useState<Artifact | null>(
    null
  );

  const getEventBadgeColor = (eventType: string) => {
    if (eventType.includes("approved") || eventType.includes("completed")) {
      return "badge-done";
    }
    if (eventType.includes("failed")) {
      return "badge-failed";
    }
    if (eventType.includes("artifact") || eventType.includes("brief")) {
      return "badge-approved";
    }
    if (eventType.includes("started") || eventType.includes("progress")) {
      return "badge-running";
    }
    return "badge-proposed";
  };

  const getArtifactForEvent = (event: RunEvent) => {
    if (!event.payload_json?.artifact_id) return null;
    return (
      sampleArtifacts.find(
        (a) => a.id === (event.payload_json.artifact_id as string)
      ) || null
    );
  };

  return (
    <div>
      <div className="timeline">
        {events.map((event) => {
          const artifact = getArtifactForEvent(event);
          return (
            <div key={event.id} className="timeline-item">
              <div className="timeline-dot" />
              <div className="timeline-content">
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    marginBottom: "0.5rem",
                  }}
                >
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "0.6rem",
                    }}
                  >
                    <span
                      style={{
                        fontSize: "0.75rem",
                        fontWeight: 700,
                        color: "var(--text-tertiary)",
                      }}
                    >
                      #{event.sequence}
                    </span>
                    <span
                      className={`badge ${getEventBadgeColor(
                        event.event_type
                      )}`}
                    >
                      {event.event_type}
                    </span>
                  </div>
                  <span
                    style={{
                      fontSize: "0.75rem",
                      color: "var(--text-tertiary)",
                    }}
                  >
                    {new Date(event.created_at).toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                      second: "2-digit",
                    })}
                  </span>
                </div>

                <div
                  style={{
                    fontSize: "0.95rem",
                    fontWeight: 500,
                    color: "var(--text-primary)",
                    marginBottom: "0.5rem",
                  }}
                >
                  {event.summary}
                </div>

                {event.payload_json &&
                  Object.keys(event.payload_json).length > 0 && (
                    <div
                      style={{
                        fontSize: "0.75rem",
                        backgroundColor: "rgba(0, 0, 0, 0.25)",
                        padding: "0.5rem 0.75rem",
                        borderRadius: "var(--radius-sm)",
                        color: "var(--text-secondary)",
                        fontFamily: "monospace",
                        marginBottom: artifact ? "0.75rem" : 0,
                      }}
                    >
                      {JSON.stringify(event.payload_json)}
                    </div>
                  )}

                {artifact && (
                  <button
                    className="btn btn-sm btn-secondary"
                    style={{ marginTop: "0.5rem" }}
                    onClick={() => setSelectedArtifact(artifact)}
                  >
                    📄 View Artifact: {artifact.title}
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Artifact Viewer Modal */}
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
              position: "relative",
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
                <span className="badge badge-approved" style={{ marginRight: "0.5rem" }}>
                  {selectedArtifact.artifact_type}
                </span>
                <span style={{ fontSize: "0.8rem", color: "var(--text-tertiary)" }}>
                  v{selectedArtifact.version}
                </span>
                <h3 style={{ marginTop: "0.25rem" }}>{selectedArtifact.title}</h3>
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
  );
}
