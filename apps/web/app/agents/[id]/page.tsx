"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { StateContainer } from "../../../components/StateContainer";
import {
  sampleAgents,
  sampleWorkItems,
  sampleCompany,
} from "../../../lib/fixtures";
import {
  listAgents,
  updateAgent,
  listWorkItems,
  AgentDefinition,
  WorkItem,
} from "../../../lib/api-client";

export default function AgentProfilePage() {
  const params = useParams();
  const agentSlug = params?.id as string;

  const initialAgent =
    sampleAgents.find((a) => a.slug === agentSlug || a.id === agentSlug) ||
    sampleAgents[0];
  const initialWork = sampleWorkItems.filter(
    (item) => item.assigned_agent_id === initialAgent.id
  );

  const [agent, setAgent] = useState<AgentDefinition>(
    initialAgent as unknown as AgentDefinition
  );
  const [recentWork, setRecentWork] = useState<WorkItem[]>(
    initialWork as unknown as WorkItem[]
  );
  const [loading, setLoading] = useState(true);
  const [isOffline, setIsOffline] = useState(false);

  // Edit mode state
  const [isEditing, setIsEditing] = useState(false);
  const [name, setName] = useState(initialAgent.name);
  const [role, setRole] = useState(initialAgent.role);
  const [runtimeModelAlias, setRuntimeModelAlias] = useState(
    initialAgent.runtime_model_alias
  );
  const [promptVersion, setPromptVersion] = useState(initialAgent.prompt_version);
  const [objective, setObjective] = useState(initialAgent.objective);
  const [responsibilities, setResponsibilities] = useState(
    initialAgent.responsibilities.join("\n")
  );
  const [enabled, setEnabled] = useState(initialAgent.enabled);

  const [isSaving, setIsSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    Promise.all([listAgents(), listWorkItems()])
      .then(([agentsData, workData]) => {
        if (!mounted) return;
        const found =
          agentsData.find(
            (a) => a.slug === agentSlug || a.id === agentSlug
          ) || agentsData[0];
        if (found) {
          setAgent(found);
          const assignedWork = workData.filter(
            (item) => item.assigned_agent_id === found.id
          );
          setRecentWork(assignedWork);
          setIsOffline(false);
        }
      })
      .catch((err) => {
        if (!mounted) return;
        console.warn(
          "API offline or error fetching agent profile, falling back to fixture:",
          err
        );
        setIsOffline(true);
      })
      .finally(() => {
        if (mounted) setLoading(false);
      });
    return () => {
      mounted = false;
    };
  }, [agentSlug]);

  const handleStartEdit = () => {
    setName(agent.name);
    setRole(agent.role);
    setRuntimeModelAlias(agent.runtime_model_alias);
    setPromptVersion(agent.prompt_version);
    setObjective(agent.objective);
    setResponsibilities(agent.responsibilities.join("\n"));
    setEnabled(agent.enabled);
    setError(null);
    setIsEditing(true);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(false);
    setError(null);

    if (!name.trim()) {
      setError("Agent Name cannot be empty.");
      return;
    }
    if (!role.trim()) {
      setError("Role cannot be empty.");
      return;
    }
    if (!objective.trim()) {
      setError("Primary Objective cannot be empty.");
      return;
    }

    const respList = responsibilities
      .split("\n")
      .map((r) => r.trim())
      .filter(Boolean);

    if (respList.length > 20) {
      setError("Responsibilities cannot exceed 20 items.");
      return;
    }

    setIsSaving(true);
    try {
      const updated = await updateAgent(agent.id, {
        name: name.trim(),
        role: role.trim(),
        runtime_model_alias: runtimeModelAlias.trim(),
        prompt_version: promptVersion.trim(),
        objective: objective.trim(),
        responsibilities: respList,
        enabled: enabled,
      });
      setAgent(updated);
      setIsOffline(false);
      setIsEditing(false);
      setSaved(true);
      setTimeout(() => setSaved(false), 4000);
    } catch (err: unknown) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to save agent profile.";
      setError(`Validation / Save Error: ${errorMessage}`);
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <StateContainer
      emptyTitle="No recent activity for this agent profile"
      emptyDescription="This specialist agent is ready and enabled, but has not yet been assigned any sequential work items."
    >
      <div style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
        {/* Header bar */}
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
                    agent.enabled ? "badge-approved" : "badge-failed"
                  }`}
                >
                  {agent.enabled ? "Enabled & Ready" : "Disabled"}
                </span>
                <span
                  style={{
                    fontSize: "0.75rem",
                    color: "var(--text-tertiary)",
                  }}
                >
                  Prompt Ver: {agent.prompt_version}
                </span>
                {isOffline && (
                  <span className="badge badge-proposed">
                    ⚡ Offline • Local Fixture Mode
                  </span>
                )}
              </div>
              <h1 style={{ fontSize: "1.75rem" }}>{agent.name}</h1>
              <p
                style={{
                  fontSize: "0.95rem",
                  color: "var(--text-secondary)",
                }}
              >
                Fixed specialist profile for <strong>{sampleCompany.name}</strong>
              </p>
            </div>

            <div style={{ display: "flex", gap: "0.75rem" }}>
              {!isEditing && (
                <button
                  type="button"
                  onClick={handleStartEdit}
                  className="btn btn-secondary"
                >
                  ✎ Edit Profile
                </button>
              )}
              <Link href="/work" className="btn btn-secondary">
                View All Work Items →
              </Link>
            </div>
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
              display: "flex",
              alignItems: "center",
              gap: "0.75rem",
              fontSize: "0.9rem",
            }}
          >
            <span>✓</span>
            <span>
              Agent profile updated successfully! Changes are persisted and reflected across the company environment.
            </span>
          </div>
        )}

        {error && !isEditing && (
          <div
            style={{
              backgroundColor: "rgba(239, 68, 68, 0.15)",
              border: "1px solid rgba(239, 68, 68, 0.3)",
              color: "#fca5a5",
              padding: "1rem",
              borderRadius: "var(--radius-sm)",
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

        {isEditing ? (
          /* Edit Form Card */
          <form onSubmit={handleSave} className="card">
            <h2 style={{ fontSize: "1.35rem", marginBottom: "1rem" }}>
              Edit Specialist Agent Profile
            </h2>

            {error && (
              <div
                style={{
                  backgroundColor: "rgba(239, 68, 68, 0.15)",
                  border: "1px solid rgba(239, 68, 68, 0.3)",
                  color: "#fca5a5",
                  padding: "0.85rem 1rem",
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

            <div className="form-group">
              <label className="form-label" htmlFor="agent_name">
                Agent Name *
              </label>
              <input
                id="agent_name"
                type="text"
                className="form-input"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>

            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))",
                gap: "1rem",
              }}
            >
              <div className="form-group">
                <label className="form-label" htmlFor="agent_role">
                  Role *
                </label>
                <input
                  id="agent_role"
                  type="text"
                  className="form-input"
                  value={role}
                  onChange={(e) => setRole(e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="runtime_model">
                  Runtime Model Alias *
                </label>
                <input
                  id="runtime_model"
                  type="text"
                  className="form-input"
                  value={runtimeModelAlias}
                  onChange={(e) => setRuntimeModelAlias(e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label className="form-label" htmlFor="prompt_version">
                  Prompt Version *
                </label>
                <input
                  id="prompt_version"
                  type="text"
                  className="form-input"
                  value={promptVersion}
                  onChange={(e) => setPromptVersion(e.target.value)}
                  required
                />
              </div>
            </div>

            <div className="form-group" style={{ marginBottom: "1.25rem" }}>
              <label
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "0.65rem",
                  cursor: "pointer",
                  fontSize: "0.95rem",
                  fontWeight: 500,
                  color: "var(--text-primary)",
                }}
              >
                <input
                  type="checkbox"
                  checked={enabled}
                  onChange={(e) => setEnabled(e.target.checked)}
                  style={{ width: "18px", height: "18px", cursor: "pointer" }}
                />
                Agent Enabled & Ready for Work Assignments
              </label>
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="objective">
                Primary Objective *
              </label>
              <textarea
                id="objective"
                className="form-textarea"
                rows={3}
                value={objective}
                onChange={(e) => setObjective(e.target.value)}
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="responsibilities">
                Key Operational Responsibilities (one per line) *
              </label>
              <textarea
                id="responsibilities"
                className="form-textarea"
                rows={4}
                value={responsibilities}
                onChange={(e) => setResponsibilities(e.target.value)}
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
                Enter each responsibility on a new line (maximum 20 items).
              </span>
            </div>

            <div
              style={{
                borderTop: "1px solid var(--border-color)",
                paddingTop: "1.25rem",
                display: "flex",
                justifyContent: "flex-end",
                gap: "0.75rem",
              }}
            >
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => setIsEditing(false)}
                disabled={isSaving}
              >
                Cancel
              </button>
              <button
                type="submit"
                className="btn btn-primary"
                disabled={isSaving}
              >
                {isSaving ? "Saving..." : "Save Agent Profile"}
              </button>
            </div>
          </form>
        ) : (
          <>
            {/* Runtime Model & Metadata cards */}
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
                  Role Template
                </div>
                <div
                  style={{
                    fontSize: "1.2rem",
                    fontWeight: 600,
                    color: "var(--text-primary)",
                  }}
                >
                  {agent.role}
                </div>
                <div
                  style={{
                    fontSize: "0.8rem",
                    color: "var(--text-secondary)",
                    marginTop: "0.2rem",
                  }}
                >
                  One of 3 seeded specialist profiles
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
                  Runtime Model Alias
                </div>
                <div
                  style={{
                    fontSize: "1.2rem",
                    fontWeight: 600,
                    color: "var(--text-accent)",
                  }}
                >
                  {agent.runtime_model_alias}
                </div>
                <div
                  style={{
                    fontSize: "0.8rem",
                    color: "var(--text-secondary)",
                    marginTop: "0.2rem",
                  }}
                >
                  Configured frontier LLM
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
                  Assigned Items
                </div>
                <div
                  style={{
                    fontSize: "1.2rem",
                    fontWeight: 600,
                    color: "var(--accent-purple)",
                  }}
                >
                  {recentWork.length} Work Deliverables
                </div>
                <div
                  style={{
                    fontSize: "0.8rem",
                    color: "var(--text-secondary)",
                    marginTop: "0.2rem",
                  }}
                >
                  Sequential execution items
                </div>
              </div>
            </div>

            {/* Objective & Responsibilities */}
            <div className="card">
              <h3 style={{ fontSize: "1.15rem", marginBottom: "0.5rem" }}>
                Primary Objective
              </h3>
              <p
                style={{
                  fontSize: "1rem",
                  color: "var(--text-primary)",
                  lineHeight: 1.6,
                  marginBottom: "1.5rem",
                  borderLeft: "3px solid var(--accent-primary)",
                  paddingLeft: "1rem",
                }}
              >
                {agent.objective}
              </p>

              <h4
                style={{
                  fontSize: "0.95rem",
                  color: "var(--text-secondary)",
                  marginBottom: "0.75rem",
                }}
              >
                Key Operational Responsibilities
              </h4>

              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
                  gap: "0.75rem",
                }}
              >
                {agent.responsibilities.map((resp, idx) => (
                  <div
                    key={idx}
                    style={{
                      backgroundColor: "var(--bg-tertiary)",
                      border: "1px solid var(--border-color)",
                      borderRadius: "var(--radius-sm)",
                      padding: "0.85rem 1rem",
                      display: "flex",
                      alignItems: "center",
                      gap: "0.75rem",
                      fontSize: "0.9rem",
                    }}
                  >
                    <span style={{ color: "var(--accent-emerald)" }}>✓</span>
                    <span>{resp}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Recent Work History Table */}
            <div className="card">
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "space-between",
                  marginBottom: "1rem",
                }}
              >
                <div>
                  <h3 style={{ fontSize: "1.15rem" }}>Recent Assigned Work</h3>
                  <p
                    style={{
                      fontSize: "0.825rem",
                      color: "var(--text-secondary)",
                    }}
                  >
                    Work items assigned to {agent.name} across company objectives
                  </p>
                </div>
                <Link href="/work" className="btn btn-sm btn-secondary">
                  Open Kanban Board →
                </Link>
              </div>

              {recentWork.length === 0 ? (
                <div
                  style={{
                    padding: "2rem",
                    textAlign: "center",
                    color: "var(--text-tertiary)",
                    border: "1px dashed var(--border-color)",
                    borderRadius: "var(--radius-sm)",
                  }}
                >
                  No work items assigned to this agent yet.
                </div>
              ) : (
                <div style={{ overflowX: "auto" }}>
                  <table
                    style={{
                      width: "100%",
                      borderCollapse: "collapse",
                      textAlign: "left",
                      fontSize: "0.9rem",
                    }}
                  >
                    <thead>
                      <tr
                        style={{
                          borderBottom: "1px solid var(--border-color)",
                          color: "var(--text-tertiary)",
                          fontSize: "0.8rem",
                          textTransform: "uppercase",
                        }}
                      >
                        <th style={{ padding: "0.75rem 0.5rem" }}>Deliverable</th>
                        <th style={{ padding: "0.75rem 0.5rem" }}>Title</th>
                        <th style={{ padding: "0.75rem 0.5rem" }}>Status</th>
                        <th style={{ padding: "0.75rem 0.5rem" }}>Last Updated</th>
                        <th
                          style={{
                            padding: "0.75rem 0.5rem",
                            textAlign: "right",
                          }}
                        >
                          Action
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      {recentWork.map((item) => (
                        <tr
                          key={item.id}
                          style={{
                            borderBottom: "1px solid var(--border-color)",
                          }}
                        >
                          <td
                            style={{
                              padding: "0.85rem 0.5rem",
                              fontFamily: "monospace",
                              color: "var(--text-accent)",
                              textTransform: "uppercase",
                              fontSize: "0.8rem",
                            }}
                          >
                            {item.deliverable_type}
                          </td>
                          <td
                            style={{
                              padding: "0.85rem 0.5rem",
                              fontWeight: 500,
                            }}
                          >
                            {item.title}
                          </td>
                          <td style={{ padding: "0.85rem 0.5rem" }}>
                            <span className={`badge badge-${item.status}`}>
                              {item.status}
                            </span>
                          </td>
                          <td
                            style={{
                              padding: "0.85rem 0.5rem",
                              color: "var(--text-secondary)",
                              fontSize: "0.8rem",
                            }}
                          >
                            {new Date(item.updated_at).toLocaleString()}
                          </td>
                          <td
                            style={{
                              padding: "0.85rem 0.5rem",
                              textAlign: "right",
                            }}
                          >
                            <Link
                              href={`/runs/30000000-0000-4000-8000-000000000001`}
                              className="btn btn-sm btn-secondary"
                            >
                              Inspect Run
                            </Link>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </>
        )}
      </div>
    </StateContainer>
  );
}

