"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { StateContainer } from "../../../components/StateContainer";
import { sampleObjectives } from "../../../lib/fixtures";
import { createObjective, createPlan } from "../../../lib/api-client";

export default function NewObjectivePage() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [desiredOutcome, setDesiredOutcome] = useState("");
  const [context, setContext] = useState("");
  const [constraintInput, setConstraintInput] = useState("");
  const [constraints, setConstraints] = useState<string[]>([
    "Budget must remain under $5,000 for launch tooling",
    "Onboarding time must be under 3 business days per client",
  ]);
  const [submitted, setSubmitted] = useState(false);
  const [statusText, setStatusText] = useState("");
  const [error, setError] = useState<string | null>(null);

  const handleAddConstraint = () => {
    if (constraintInput.trim()) {
      setConstraints([...constraints, constraintInput.trim()]);
      setConstraintInput("");
    }
  };

  const handleRemoveConstraint = (index: number) => {
    setConstraints(constraints.filter((_, i) => i !== index));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
    setError(null);
    setStatusText("Creating objective...");

    try {
      const objective = await createObjective({
        title,
        desired_outcome: desiredOutcome,
        context: context.trim(),
        constraints: constraints,
      });

      setStatusText("Generating proposed plan from Chief of Staff...");
      await createPlan(objective.id);

      router.push(`/objectives/${objective.id}/plan`);
    } catch (err) {
      console.warn(
        "API offline or error creating objective/plan, falling back to fixture:",
        err
      );
      setStatusText("Using offline demo mode...");
      setTimeout(() => {
        router.push(`/objectives/${sampleObjectives[0].id}/plan`);
      }, 600);
    }
  };

  return (
    <StateContainer
      emptyTitle="No objective draft active"
      emptyDescription="Create a new objective below to instruct the Chief of Staff agent to generate a structured work plan."
    >
      <div style={{ maxWidth: "800px", margin: "0 auto" }}>
        {error && (
          <div
            style={{
              padding: "0.75rem 1rem",
              backgroundColor: "rgba(239, 68, 68, 0.15)",
              border: "1px solid var(--accent-rose)",
              borderRadius: "var(--radius-sm)",
              marginBottom: "1rem",
              color: "var(--accent-rose)",
              fontSize: "0.9rem",
            }}
          >
            {error}
          </div>
        )}

        <div style={{ marginBottom: "1.5rem" }}>
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
          <h1 style={{ fontSize: "1.75rem" }}>Objective Intake</h1>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.95rem" }}>
            Submit a strategic company objective. The Chief of Staff will turn it
            into 2–5 structured work items with owners and deliverables.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="card">
          <div className="form-group">
            <label className="form-label" htmlFor="title">
              Objective Title *
            </label>
            <input
              id="title"
              type="text"
              className="form-input"
              placeholder="e.g., Create a launch plan for a bookkeeping service"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
            <span
              style={{
                fontSize: "0.75rem",
                color: "var(--text-tertiary)",
                marginTop: "0.25rem",
                display: "block",
              }}
            >
              Clear, actionable title describing the goal.
            </span>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="desired_outcome">
              Desired Outcome *
            </label>
            <textarea
              id="desired_outcome"
              className="form-textarea"
              rows={3}
              placeholder="e.g., A complete go-to-market brief, pricing sheet, and client onboarding checklist for a new bookkeeping service."
              value={desiredOutcome}
              onChange={(e) => setDesiredOutcome(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="context">
              Background Context
            </label>
            <textarea
              id="context"
              className="form-textarea"
              rows={2}
              placeholder="e.g., Targeting small professional services firms with 1-10 employees."
              value={context}
              onChange={(e) => setContext(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Constraints & Boundaries</label>
            <div
              style={{
                display: "flex",
                gap: "0.5rem",
                marginBottom: "0.75rem",
              }}
            >
              <input
                type="text"
                className="form-input"
                placeholder="Add constraint rule..."
                value={constraintInput}
                onChange={(e) => setConstraintInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") {
                    e.preventDefault();
                    handleAddConstraint();
                  }
                }}
              />
              <button
                type="button"
                className="btn btn-secondary"
                onClick={handleAddConstraint}
              >
                + Add
              </button>
            </div>

            <div
              style={{
                display: "flex",
                flexDirection: "column",
                gap: "0.5rem",
              }}
            >
              {constraints.map((c, i) => (
                <div
                  key={i}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                    padding: "0.5rem 0.75rem",
                    backgroundColor: "var(--bg-tertiary)",
                    borderRadius: "var(--radius-sm)",
                    fontSize: "0.85rem",
                  }}
                >
                  <span>• {c}</span>
                  <button
                    type="button"
                    style={{
                      background: "none",
                      border: "none",
                      color: "var(--accent-rose)",
                      cursor: "pointer",
                      fontSize: "0.85rem",
                    }}
                    onClick={() => handleRemoveConstraint(i)}
                  >
                    Remove
                  </button>
                </div>
              ))}
            </div>
          </div>

          <div
            style={{
              borderTop: "1px solid var(--border-color)",
              paddingTop: "1.25rem",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              flexWrap: "wrap",
              gap: "1rem",
            }}
          >
            <span
              style={{ fontSize: "0.8rem", color: "var(--text-tertiary)" }}
            >
              Chief of Staff will assign only seeded specialist agents.
            </span>

            <div style={{ display: "flex", gap: "0.75rem" }}>
              <Link href="/" className="btn btn-secondary">
                Cancel
              </Link>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={submitted}
              >
                {submitted
                  ? statusText || "Generating Plan..."
                  : "Submit Objective to Chief of Staff"}
              </button>
            </div>
          </div>
        </form>
      </div>
    </StateContainer>
  );
}
