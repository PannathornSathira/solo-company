"use client";

import React from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { StateContainer } from "../../../components/StateContainer";
import {
  sampleAgents,
  sampleWorkItems,
  sampleCompany,
} from "../../../lib/fixtures";

export default function AgentProfilePage() {
  const params = useParams();
  const agentSlug = params?.id as string;

  const agent =
    sampleAgents.find(
      (a) => a.slug === agentSlug || a.id === agentSlug
    ) || sampleAgents[0];

  const recentWork = sampleWorkItems.filter(
    (item) => item.assigned_agent_id === agent.id
  );

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
              <Link href="/work" className="btn btn-secondary">
                View All Work Items →
              </Link>
            </div>
          </div>
        </div>

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
                      style={{ padding: "0.75rem 0.5rem", textAlign: "right" }}
                    >
                      Action
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {recentWork.map((item) => (
                    <tr
                      key={item.id}
                      style={{ borderBottom: "1px solid var(--border-color)" }}
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
                      <td style={{ padding: "0.85rem 0.5rem", fontWeight: 500 }}>
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
      </div>
    </StateContainer>
  );
}
