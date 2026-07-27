"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { StateContainer } from "../../../components/StateContainer";
import { sampleCompany } from "../../../lib/fixtures";
import { getCompany, updateCompany } from "../../../lib/api-client";

export default function CompanySetupPage() {
  const [name, setName] = useState(sampleCompany.name);
  const [description, setDescription] = useState(sampleCompany.description);
  const [mission, setMission] = useState(sampleCompany.mission);
  const [workingRules, setWorkingRules] = useState(sampleCompany.working_rules);
  const [companyId, setCompanyId] = useState(sampleCompany.id);

  const [loading, setLoading] = useState(true);
  const [isOffline, setIsOffline] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    getCompany()
      .then((data) => {
        if (!mounted) return;
        setName(data.name);
        setDescription(data.description);
        setMission(data.mission);
        setWorkingRules(data.working_rules.join("\n"));
        setCompanyId(data.id);
        setIsOffline(false);
      })
      .catch((err) => {
        if (!mounted) return;
        console.warn("API offline or error fetching company, falling back to fixture:", err);
        setIsOffline(true);
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(false);
    setError(null);

    if (!name.trim()) {
      setError("Company Name cannot be empty.");
      return;
    }
    if (!mission.trim()) {
      setError("Company Mission Statement cannot be empty.");
      return;
    }

    const rulesList = workingRules
      .split("\n")
      .map((r) => r.trim())
      .filter(Boolean);

    if (rulesList.length > 20) {
      setError("Operational working rules cannot exceed 20 items.");
      return;
    }

    setIsSaving(true);
    try {
      const updated = await updateCompany({
        name: name.trim(),
        description: description.trim(),
        mission: mission.trim(),
        working_rules: rulesList,
      });
      setName(updated.name);
      setDescription(updated.description);
      setMission(updated.mission);
      setWorkingRules(updated.working_rules.join("\n"));
      setCompanyId(updated.id);
      setIsOffline(false);
      setSaved(true);
      setTimeout(() => setSaved(false), 4000);
    } catch (err: unknown) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to save company settings.";
      setError(`Validation / Save Error: ${errorMessage}`);
    } finally {
      setIsSaving(false);
    }
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
              <h1 style={{ fontSize: "1.75rem" }}>Company Setup & Rules</h1>
              <p style={{ color: "var(--text-secondary)", fontSize: "0.95rem" }}>
                Configure the seeded company identity, mission statement, and
                operational rules enforced across all specialist agents.
              </p>
            </div>
            {isOffline && (
              <span className="badge badge-proposed">
                ⚡ Offline • Local Fixture Mode
              </span>
            )}
          </div>
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

        {error && (
          <div
            style={{
              backgroundColor: "rgba(239, 68, 68, 0.15)",
              border: "1px solid rgba(239, 68, 68, 0.3)",
              color: "#fca5a5",
              padding: "1rem",
              borderRadius: "var(--radius-sm)",
              marginBottom: "1.25rem",
              display: "flex",
              alignItems: "center",
              gap: "0.75rem",
              fontSize: "0.9rem",
            }}
          >
            <span>✕</span>
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSave} className="card">
          {loading ? (
            <div
              style={{
                padding: "3rem",
                textAlign: "center",
                color: "var(--text-tertiary)",
              }}
            >
              Loading company profile...
            </div>
          ) : (
            <>
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
                  Operational Working Rules (one rule per line) *
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
                  sequential execution (maximum 20 items).
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
                  Seeded Company ID: {companyId}
                </span>

                <div style={{ display: "flex", gap: "0.75rem" }}>
                  <Link href="/" className="btn btn-secondary">
                    Cancel
                  </Link>
                  <button
                    type="submit"
                    className="btn btn-primary"
                    disabled={isSaving}
                  >
                    {isSaving ? "Saving..." : "Save Company Settings"}
                  </button>
                </div>
              </div>
            </>
          )}
        </form>
      </div>
    </StateContainer>
  );
}

