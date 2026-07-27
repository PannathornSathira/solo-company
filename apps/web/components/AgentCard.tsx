"use client";

import React from "react";
import Link from "next/link";
import { AgentDefinition } from "../lib/fixtures";

interface AgentCardProps {
  agent: AgentDefinition;
  statusText?: string;
  badgeType?: "running" | "approved" | "done" | "proposed";
}

export function AgentCard({
  agent,
  statusText = "Active",
  badgeType = "running",
}: AgentCardProps) {
  return (
    <Link
      href={`/agents/${agent.slug}`}
      className="card card-interactive"
      style={{
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
      }}
    >
      <div>
        <div className="card-header">
          <span className={`badge badge-${badgeType}`}>{statusText}</span>
          <span style={{ fontSize: "0.75rem", color: "var(--text-tertiary)" }}>
            {agent.runtime_model_alias}
          </span>
        </div>

        <h3
          className="card-title"
          style={{ marginBottom: "0.5rem", fontSize: "1.15rem" }}
        >
          {agent.name}
        </h3>

        <p
          style={{
            fontSize: "0.875rem",
            color: "var(--text-secondary)",
            marginBottom: "1rem",
            lineHeight: 1.5,
          }}
        >
          {agent.objective}
        </p>

        <div style={{ marginBottom: "1rem" }}>
          <div
            style={{
              fontSize: "0.75rem",
              textTransform: "uppercase",
              color: "var(--text-tertiary)",
              fontWeight: 600,
              marginBottom: "0.35rem",
            }}
          >
            Key Responsibilities
          </div>
          <ul
            style={{
              listStyle: "none",
              padding: 0,
              display: "flex",
              flexDirection: "column",
              gap: "0.3rem",
            }}
          >
            {agent.responsibilities.slice(0, 2).map((r, i) => (
              <li
                key={i}
                style={{
                  fontSize: "0.825rem",
                  color: "var(--text-secondary)",
                  display: "flex",
                  alignItems: "center",
                  gap: "0.4rem",
                }}
              >
                <span style={{ color: "var(--accent-primary)" }}>•</span>
                <span>{r}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div
        style={{
          borderTop: "1px solid var(--border-color)",
          paddingTop: "0.85rem",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          fontSize: "0.85rem",
          color: "var(--text-accent)",
          fontWeight: 500,
        }}
      >
        <span>Inspect Agent Profile</span>
        <span>→</span>
      </div>
    </Link>
  );
}
