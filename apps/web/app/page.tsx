"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import {
  sampleCompany,
  sampleAgents,
  sampleObjectives,
  sampleRuns,
} from "../lib/fixtures";
import {
  getCompany,
  listAgents,
  Company,
  AgentDefinition,
} from "../lib/api-client";
import { AgentCard } from "../components/AgentCard";
import { StateContainer } from "../components/StateContainer";

export default function Home() {
  const [company, setCompany] = useState<Company>(
    sampleCompany as unknown as Company
  );
  const [agents, setAgents] = useState<AgentDefinition[]>(
    sampleAgents as unknown as AgentDefinition[]
  );
  const [isOffline, setIsOffline] = useState(false);

  useEffect(() => {
    let mounted = true;
    Promise.all([getCompany(), listAgents()])
      .then(([companyData, agentsData]) => {
        if (!mounted) return;
        setCompany(companyData);
        setAgents(agentsData);
        setIsOffline(false);
      })
      .catch((err) => {
        if (!mounted) return;
        console.warn(
          "API offline or error fetching dashboard data, falling back to fixtures:",
          err
        );
        setIsOffline(true);
      });
    return () => {
      mounted = false;
    };
  }, []);

  const activeObjective = sampleObjectives.find((o) => o.status === "active");
  const recentRuns = sampleRuns;

  return (
    <StateContainer
      emptyTitle="No company activity yet"
      emptyDescription="Welcome to Solo Company! To get started, configure your company objective or inspect the three specialist agents."
    >
      <div style={{ display: "flex", flexDirection: "column", gap: "2rem" }}>
        {/* Company Mission Header Card */}
        <div
          className="card"
          style={{
            background:
              "linear-gradient(135deg, rgba(31, 41, 55, 0.9), rgba(17, 24, 39, 0.95))",
            border: "1px solid rgba(96, 165, 250, 0.25)",
            boxShadow: "var(--shadow-lg)",
          }}
        >
          <div
            style={{
              display: "flex",
              alignItems: "flex-start",
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
                  gap: "0.5rem",
                  marginBottom: "0.25rem",
                }}
              >
                <div
                  style={{
                    fontSize: "0.75rem",
                    textTransform: "uppercase",
                    color: "var(--text-accent)",
                    fontWeight: 600,
                    letterSpacing: "0.05em",
                  }}
                >
                  Company Mission
                </div>
                {isOffline && (
                  <span className="badge badge-proposed" style={{ fontSize: "0.65rem" }}>
                    ⚡ Offline Mode
                  </span>
                )}
              </div>
              <h1
                style={{
                  fontSize: "1.75rem",
                  fontWeight: 700,
                  marginBottom: "0.5rem",
                }}
              >
                {company.name}
              </h1>
              <p
                style={{
                  fontSize: "1.05rem",
                  color: "var(--text-primary)",
                  maxWidth: "750px",
                  lineHeight: 1.6,
                }}
              >
                “{company.mission}”
              </p>
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
                href="/settings/company"
                className="btn btn-sm btn-secondary"
              >
                ⚙️ Company Setup
              </Link>
              <span
                style={{ fontSize: "0.75rem", color: "var(--text-tertiary)" }}
              >
                1 seeded company • {agents.length} agents
              </span>
            </div>
          </div>

          <div
            style={{
              marginTop: "1.25rem",
              paddingTop: "1rem",
              borderTop: "1px solid var(--border-color)",
              display: "flex",
              alignItems: "center",
              gap: "1.5rem",
              flexWrap: "wrap",
              fontSize: "0.85rem",
              color: "var(--text-secondary)",
            }}
          >
            <div>
              <strong style={{ color: "var(--text-primary)" }}>
                Working Rules:
              </strong>{" "}
              {Array.isArray(company.working_rules)
                ? company.working_rules.join(" • ")
                : company.working_rules}
            </div>
          </div>
        </div>

        {/* Active Objective Banner */}
        {activeObjective && (
          <div
            className="card"
            style={{
              borderLeft: "4px solid var(--accent-primary)",
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
                  gap: "0.5rem",
                  marginBottom: "0.25rem",
                }}
              >
                <span className="badge badge-running">Active Objective</span>
                <span
                  style={{
                    fontSize: "0.75rem",
                    color: "var(--text-tertiary)",
                  }}
                >
                  Planning Phase
                </span>
              </div>
              <h2 style={{ fontSize: "1.25rem", marginBottom: "0.25rem" }}>
                {activeObjective.title}
              </h2>
              <p
                style={{
                  fontSize: "0.9rem",
                  color: "var(--text-secondary)",
                }}
              >
                {activeObjective.desired_outcome}
              </p>
            </div>

            <div style={{ display: "flex", gap: "0.75rem" }}>
              <Link
                href={`/objectives/${activeObjective.id}/plan`}
                className="btn btn-primary btn-sm"
              >
                Review Plan →
              </Link>
            </div>
          </div>
        )}

        {/* Specialist Agent Profiles Grid */}
        <div>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              marginBottom: "1rem",
            }}
          >
            <div>
              <h2 style={{ fontSize: "1.25rem" }}>
                Fixed Specialist Agents
              </h2>
              <p
                style={{
                  fontSize: "0.85rem",
                  color: "var(--text-secondary)",
                }}
              >
                Three seeded agents with distinct responsibilities and runtime
                models
              </p>
            </div>

            <span
              style={{ fontSize: "0.8rem", color: "var(--text-tertiary)" }}
            >
              Sequential specialist execution
            </span>
          </div>

          <div className="grid-cols-3">
            {agents.map((agent) => (
              <AgentCard
                key={agent.id}
                agent={agent as any}
                badgeType={
                  agent.slug === "chief-of-staff"
                    ? "approved"
                    : agent.slug === "marketing-specialist"
                    ? "running"
                    : "proposed"
                }
                statusText={agent.enabled ? "Ready" : "Disabled"}
              />
            ))}
          </div>
        </div>

        {/* Recent Runs Table */}
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
              <h3 style={{ fontSize: "1.15rem" }}>Recent Agent Runs</h3>
              <p
                style={{
                  fontSize: "0.825rem",
                  color: "var(--text-secondary)",
                }}
              >
                Durable execution timeline across objective plans
              </p>
            </div>
            <Link
              href={`/runs/${recentRuns[0]?.id}`}
              className="btn btn-sm btn-secondary"
            >
              View Active Run Timeline →
            </Link>
          </div>

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
                  <th style={{ padding: "0.75rem 0.5rem" }}>Run ID</th>
                  <th style={{ padding: "0.75rem 0.5rem" }}>Objective</th>
                  <th style={{ padding: "0.75rem 0.5rem" }}>Status</th>
                  <th style={{ padding: "0.75rem 0.5rem" }}>Graph Ver.</th>
                  <th style={{ padding: "0.75rem 0.5rem" }}>Started</th>
                  <th style={{ padding: "0.75rem 0.5rem", textAlign: "right" }}>
                    Action
                  </th>
                </tr>
              </thead>
              <tbody>
                {recentRuns.map((run) => {
                  const obj = sampleObjectives.find(
                    (o) => o.id === run.objective_id
                  );
                  return (
                    <tr
                      key={run.id}
                      style={{
                        borderBottom: "1px solid var(--border-color)",
                        transition: "background-color 150ms",
                      }}
                    >
                      <td
                        style={{
                          padding: "0.85rem 0.5rem",
                          fontFamily: "monospace",
                          color: "var(--text-accent)",
                        }}
                      >
                        {run.id.slice(0, 8)}...
                      </td>
                      <td
                        style={{
                          padding: "0.85rem 0.5rem",
                          fontWeight: 500,
                        }}
                      >
                        {obj?.title || "Company Objective"}
                      </td>
                      <td style={{ padding: "0.85rem 0.5rem" }}>
                        <span
                          className={`badge ${
                            run.status === "completed"
                              ? "badge-done"
                              : run.status === "running"
                              ? "badge-running"
                              : "badge-failed"
                          }`}
                        >
                          {run.status}
                        </span>
                      </td>
                      <td
                        style={{
                          padding: "0.85rem 0.5rem",
                          color: "var(--text-tertiary)",
                          fontSize: "0.8rem",
                        }}
                      >
                        {run.graph_version}
                      </td>
                      <td
                        style={{
                          padding: "0.85rem 0.5rem",
                          color: "var(--text-secondary)",
                          fontSize: "0.8rem",
                        }}
                      >
                        {new Date(run.started_at).toLocaleString()}
                      </td>
                      <td
                        style={{
                          padding: "0.85rem 0.5rem",
                          textAlign: "right",
                        }}
                      >
                        <Link
                          href={`/runs/${run.id}`}
                          className="btn btn-sm btn-secondary"
                        >
                          Inspect Run
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </StateContainer>
  );
}
