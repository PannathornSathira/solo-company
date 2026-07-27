"use client";

import React, { useState } from "react";
import Link from "next/link";
import { StateContainer } from "../../../components/StateContainer";
import { sampleCompany } from "../../../lib/fixtures";

export default function CompanySetupPage() {
  const [name, setName] = useState(sampleCompany.name);
  const [description, setDescription] = useState(sampleCompany.description);
  const [mission, setMission] = useState(sampleCompany.mission);
  const [workingRules, setWorkingRules] = useState(sampleCompany.working_rules);
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <StateContainer
      emptyTitle="No company profile configured"
      emptyDescription="Enter your company name, mission statement, and operational working rules to initialize the Solo Company environment."
    >
      <div style={{ maxWidth: "800px", margin: "0 auto" }}>
        {/* Header bar */}
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
          <h1 style={{ fontSize: "1.75rem" }}>Company Setup & Rules</h1>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.95rem" }}>
            Configure the seeded company identity, mission statement, and
            operational rules enforced across all specialist agents.
          </p>
        </div>

        {saved && (
          <div
            style={{
              backgroundColor: "rgba(16, 185, 129, 0.15)",
              border: "1px solid rgba(16, 185, 129, 0.3)",
              color: "#6ee7b7",
              padding: "1rem",
              borderRadius: "var(--radius-sm)",
              marginBottom: "1.25rem",
              display: "flex",
              alignItems: "center",
              gap: "0.75rem",
              fontSize: "0.9rem",
            }}
          >
            <span>✓</span>
            <span>
              Company settings saved successfully! Changes are reflected across
              the dashboard and agent working rules.
            </span>
          </div>
        )}

        <form onSubmit={handleSave} className="card">
          <div className="form-group">
            <label className="form-label" htmlFor="name">
              Company Name *
            </label>
            <input
              id="name"
              type="text"
              className="form-input"
              value={name}
              onChange={(e) => setName(e.target.value)}
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
              The primary brand name displayed across the console.
            </span>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="description">
              Company Description *
            </label>
            <input
              id="description"
              type="text"
              className="form-input"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="mission">
              Company Mission Statement *
            </label>
            <textarea
              id="mission"
              className="form-textarea"
              rows={2}
              value={mission}
              onChange={(e) => setMission(e.target.value)}
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
              Strategic north star used by Chief of Staff to evaluate objectives.
            </span>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="working_rules">
              Operational Working Rules *
            </label>
            <textarea
              id="working_rules"
              className="form-textarea"
              rows={4}
              value={workingRules}
              onChange={(e) => setWorkingRules(e.target.value)}
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
              Mandates and constraints respected by all specialist agents during
              sequential execution.
            </span>
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
              Seeded Company ID: {sampleCompany.id}
            </span>

            <div style={{ display: "flex", gap: "0.75rem" }}>
              <Link href="/" className="btn btn-secondary">
                Cancel
              </Link>
              <button type="submit" className="btn btn-primary">
                Save Company Settings
              </button>
            </div>
          </div>
        </form>
      </div>
    </StateContainer>
  );
}
