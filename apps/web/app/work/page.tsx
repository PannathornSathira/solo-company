"use client";

import React, { useState } from "react";
import Link from "next/link";
import { StateContainer } from "../../components/StateContainer";
import { WorkBoard } from "../../components/WorkBoard";
import { sampleWorkItems, WorkItem, sampleAgents } from "../../lib/fixtures";

export default function WorkBoardPage() {
  const [selectedItem, setSelectedItem] = useState<WorkItem | null>(null);
  const [filterAgent, setFilterAgent] = useState<string>("all");

  const filteredItems = sampleWorkItems.filter((item) => {
    if (filterAgent === "all") return true;
    return item.assigned_agent_id === filterAgent;
  });

  const getAgentName = (agentId: string) => {
    const found = sampleAgents.find((a) => a.id === agentId);
    return found ? found.name : "Specialist Agent";
  };

  return (
    <StateContainer
      emptyTitle="Work Board is currently empty"
      emptyDescription="Submit an objective and approve a plan to populate the Kanban columns with sequential specialist work items."
    >
      <div style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
        {/* Header bar */}
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
            <h1 style={{ fontSize: "1.75rem" }}>Company Work Board</h1>
            <p style={{ color: "var(--text-secondary)", fontSize: "0.95rem" }}>
              Sequential specialist work items across 6 durable lifecycle states.
            </p>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <span
                style={{
                  fontSize: "0.85rem",
                  color: "var(--text-secondary)",
                }}
              >
                Filter by Owner:
              </span>
              <select
                className="form-select"
                style={{ width: "220px", padding: "0.45rem 0.75rem" }}
                value={filterAgent}
                onChange={(e) => setFilterAgent(e.target.value)}
              >
                <option value="all">All Specialists ({sampleWorkItems.length})</option>
                {sampleAgents.map((a) => (
                  <option key={a.id} value={a.id}>
                    {a.name}
                  </option>
                ))}
              </select>
            </div>

            <Link href="/objectives/new" className="btn btn-primary">
              + New Objective
            </Link>
          </div>
        </div>

        {/* 6-Column Kanban Board */}
        <WorkBoard items={filteredItems} onSelectWorkItem={setSelectedItem} />

        {/* Selected Work Item Detail Modal */}
        {selectedItem && (
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
            onClick={() => setSelectedItem(null)}
          >
            <div
              className="card"
              style={{ maxWidth: "650px", width: "100%" }}
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
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "0.5rem",
                  }}
                >
                  <span className={`badge badge-${selectedItem.status}`}>
                    {selectedItem.status}
                  </span>
                  <span
                    style={{
                      fontSize: "0.8rem",
                      color: "var(--text-tertiary)",
                    }}
                  >
                    Step #{selectedItem.position}
                  </span>
                </div>
                <button
                  className="btn btn-sm btn-secondary"
                  onClick={() => setSelectedItem(null)}
                >
                  ✕ Close
                </button>
              </div>

              <h3 style={{ fontSize: "1.3rem", marginBottom: "0.5rem" }}>
                {selectedItem.title}
              </h3>

              <div
                style={{
                  marginBottom: "1.25rem",
                  fontSize: "0.95rem",
                  color: "var(--text-secondary)",
                  lineHeight: 1.6,
                }}
              >
                {selectedItem.instructions}
              </div>

              <div
                style={{
                  display: "grid",
                  gridTemplateColumns: "1fr 1fr",
                  gap: "1rem",
                  backgroundColor: "var(--bg-tertiary)",
                  padding: "1rem",
                  borderRadius: "var(--radius-sm)",
                  marginBottom: "1.5rem",
                  fontSize: "0.85rem",
                }}
              >
                <div>
                  <div
                    style={{
                      color: "var(--text-tertiary)",
                      marginBottom: "0.2rem",
                    }}
                  >
                    Assigned Owner
                  </div>
                  <div style={{ fontWeight: 600, color: "var(--text-primary)" }}>
                    {getAgentName(selectedItem.assigned_agent_id)}
                  </div>
                </div>

                <div>
                  <div
                    style={{
                      color: "var(--text-tertiary)",
                      marginBottom: "0.2rem",
                    }}
                  >
                    Deliverable Type
                  </div>
                  <div
                    style={{
                      fontWeight: 600,
                      color: "var(--text-accent)",
                      textTransform: "uppercase",
                    }}
                  >
                    {selectedItem.deliverable_type}
                  </div>
                </div>
              </div>

              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <span
                  style={{
                    fontSize: "0.75rem",
                    color: "var(--text-tertiary)",
                  }}
                >
                  ID: {selectedItem.id}
                </span>

                <Link
                  href={`/runs/30000000-0000-4000-8000-000000000001`}
                  className="btn btn-secondary btn-sm"
                >
                  Inspect Active Run Timeline →
                </Link>
              </div>
            </div>
          </div>
        )}
      </div>
    </StateContainer>
  );
}
