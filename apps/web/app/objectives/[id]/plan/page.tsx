"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";
import {
  sampleObjectives,
  sampleWorkItems,
  sampleAgents,
} from "../../../../lib/fixtures";
import { StateContainer } from "../../../../components/StateContainer";

export default function PlanReviewPage() {
  const params = useParams();
  const router = useRouter();
  const objectiveId = params?.id as string;

  const objective =
    sampleObjectives.find((o) => o.id === objectiveId) ||
    sampleObjectives[0];

  const planWorkItems = sampleWorkItems.filter(
    (w) => w.objective_id === objective.id || sampleWorkItems.slice(0, 3)
  );

  const [planStatus, setPlanStatus] = useState<"proposed" | "approved">(
    "proposed"
  );
  const [revisionNote, setRevisionNote] = useState("");
  const [showRevisionModal, setShowRevisionModal] = useState(false);

  const getAgentName = (agentId: string) => {
    const found = sampleAgents.find((a) => a.id === agentId);
    return found ? found.name : "Specialist Agent";
  };

  const handleApprove = () => {
    setPlanStatus("approved");
    setTimeout(() => {
      router.push("/work");
    }, 800);
  };

  const handleRevise = (e: React.FormEvent) => {
    e.preventDefault();
    setShowRevisionModal(false);
    alert("Revision request recorded. Chief of Staff will re-generate plan.");
  };

  return (
    <StateContainer
      emptyTitle="No proposed plan for this objective"
      emptyDescription="The Chief of Staff has not generated a work plan for this objective ID yet."
    >
      <div style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
        {/* Header and Back Link */}
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
                    planStatus === "approved"
                      ? "badge-approved"
                      : "badge-proposed"
                  }`}
                >
                  {planStatus === "approved" ? "Plan Approved" : "Plan Proposed"}
                </span>
                <span
                  style={{
                    fontSize: "0.75rem",
                    color: "var(--text-tertiary)",
                    fontFamily: "monospace",
                  }}
                >
                  Objective ID: {objective.id}
                </span>
              </div>
              <h1 style={{ fontSize: "1.75rem" }}>{objective.title}</h1>
              <p
                style={{
                  fontSize: "0.95rem",
                  color: "var(--text-secondary)",
                  maxWidth: "800px",
                }}
              >
                {objective.desired_outcome}
              </p>
            </div>

            <div style={{ display: "flex", gap: "0.75rem" }}>
              <button
                className="btn btn-secondary"
                onClick={() => setShowRevisionModal(true)}
                disabled={planStatus === "approved"}
              >
                ✏️ Request Revision
              </button>
              <button
                className="btn btn-primary"
                onClick={handleApprove}
                disabled={planStatus === "approved"}
              >
                {planStatus === "approved"
                  ? "✓ Approved (Redirecting...)"
                  : "✓ Approve Plan & Execute"}
              </button>
            </div>
          </div>
        </div>

        {/* Chief of Staff Summary Card */}
        <div
          className="card"
          style={{
            borderLeft: "4px solid var(--accent-purple)",
            backgroundColor: "rgba(139, 92, 246, 0.08)",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "0.6rem",
              marginBottom: "0.5rem",
            }}
          >
            <span
              style={{
                fontSize: "0.75rem",
                textTransform: "uppercase",
                fontWeight: 600,
                color: "var(--text-accent)",
              }}
            >
              Chief of Staff Synthesis
            </span>
            <span
              style={{ fontSize: "0.75rem", color: "var(--text-tertiary)" }}
            >
              • Model: gemini-3.1-pro
            </span>
          </div>

          <p style={{ fontSize: "0.95rem", color: "var(--text-primary)" }}>
            “I have structured this objective into <strong>3 sequential work items</strong> assigned across our specialist workforce. Each item defines a validated deliverable required before the next step begins.”
          </p>
        </div>

        {/* Work Items Table */}
        <div className="card">
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              marginBottom: "1.25rem",
            }}
          >
            <div>
              <h3 style={{ fontSize: "1.15rem" }}>Proposed Work Items</h3>
              <p
                style={{
                  fontSize: "0.85rem",
                  color: "var(--text-secondary)",
                }}
              >
                Specialist work is sequential. Every deliverable must be
                validated before the next item begins.
              </p>
            </div>
            <span
              className="badge badge-proposed"
              style={{ fontSize: "0.75rem" }}
            >
              {planWorkItems.length} Sequential Items
            </span>
          </div>

          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "1rem",
            }}
          >
            {planWorkItems.map((item, index) => (
              <div
                key={item.id}
                style={{
                  border: "1px solid var(--border-color)",
                  borderRadius: "var(--radius-md)",
                  padding: "1.25rem",
                  backgroundColor: "var(--bg-tertiary)",
                  display: "flex",
                  alignItems: "flex-start",
                  justifyContent: "space-between",
                  flexWrap: "wrap",
                  gap: "1rem",
                }}
              >
                <div style={{ flex: "1 1 500px" }}>
                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "0.6rem",
                      marginBottom: "0.4rem",
                    }}
                  >
                    <span
                      style={{
                        fontSize: "0.85rem",
                        fontWeight: 700,
                        color: "var(--accent-primary)",
                      }}
                    >
                      Step #{item.position}
                    </span>
                    <span className="badge badge-proposed">
                      {item.deliverable_type}
                    </span>
                    {index > 0 && (
                      <span
                        style={{
                          fontSize: "0.725rem",
                          color: "var(--text-tertiary)",
                          backgroundColor: "rgba(0,0,0,0.25)",
                          padding: "0.15rem 0.5rem",
                          borderRadius: "var(--radius-full)",
                        }}
                      >
                        Dependency: Step #{index}
                      </span>
                    )}
                  </div>

                  <h4 style={{ fontSize: "1.05rem", marginBottom: "0.35rem" }}>
                    {item.title}
                  </h4>
                  <p
                    style={{
                      fontSize: "0.875rem",
                      color: "var(--text-secondary)",
                      marginBottom: "0.75rem",
                    }}
                  >
                    {item.instructions}
                  </p>

                  <div
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "1rem",
                      fontSize: "0.8rem",
                      color: "var(--text-tertiary)",
                    }}
                  >
                    <span>
                      Owner:{" "}
                      <strong style={{ color: "var(--text-primary)" }}>
                        {getAgentName(item.assigned_agent_id)}
                      </strong>
                    </span>
                    <span>•</span>
                    <span>Status: {item.status}</span>
                  </div>
                </div>

                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "flex-end",
                    gap: "0.5rem",
                  }}
                >
                  <Link
                    href={`/agents/${
                      item.assigned_agent_id === sampleAgents[1].id
                        ? "marketing-specialist"
                        : item.assigned_agent_id === sampleAgents[2].id
                        ? "operations-manager"
                        : "chief-of-staff"
                    }`}
                    className="btn btn-sm btn-secondary"
                  >
                    Inspect Owner
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Request Revision Modal */}
      {showRevisionModal && (
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
          onClick={() => setShowRevisionModal(false)}
        >
          <div
            className="card"
            style={{ maxWidth: "550px", width: "100%" }}
            onClick={(e) => e.stopPropagation()}
          >
            <h3 style={{ marginBottom: "0.5rem" }}>Request Plan Revision</h3>
            <p
              style={{
                fontSize: "0.875rem",
                color: "var(--text-secondary)",
                marginBottom: "1rem",
              }}
            >
              Provide feedback to the Chief of Staff agent. It will revise the
              work items, owners, or deliverables accordingly.
            </p>

            <form onSubmit={handleRevise}>
              <div className="form-group">
                <label className="form-label">Revision Instructions</label>
                <textarea
                  className="form-textarea"
                  rows={4}
                  placeholder="e.g., Please add a step to audit existing competitor pricing before creating the marketing brief."
                  value={revisionNote}
                  onChange={(e) => setRevisionNote(e.target.value)}
                  required
                />
              </div>

              <div
                style={{
                  display: "flex",
                  justifyContent: "flex-end",
                  gap: "0.75rem",
                  marginTop: "1.25rem",
                }}
              >
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => setShowRevisionModal(false)}
                >
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Submit Revision Request
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </StateContainer>
  );
}
