"use client";

import React from "react";
import { WorkItem, sampleAgents } from "../lib/fixtures";

interface WorkBoardProps {
  items: WorkItem[];
  onSelectWorkItem?: (item: WorkItem) => void;
}

export function WorkBoard({ items, onSelectWorkItem }: WorkBoardProps) {
  const columns: {
    id: "proposed" | "approved" | "running" | "review" | "done" | "failed";
    title: string;
    icon: string;
  }[] = [
    { id: "proposed", title: "Proposed", icon: "📝" },
    { id: "approved", title: "Approved", icon: "✅" },
    { id: "running", title: "Running", icon: "⚡" },
    { id: "review", title: "Review", icon: "👁️" },
    { id: "done", title: "Done", icon: "🎉" },
    { id: "failed", title: "Failed", icon: "⚠️" },
  ];

  const getAgentName = (agentId: string) => {
    const found = sampleAgents.find((a) => a.id === agentId);
    return found ? found.name : "Specialist Agent";
  };

  return (
    <div className="kanban-board">
      {columns.map((col) => {
        const colItems = items.filter((item) => item.status === col.id);
        return (
          <div key={col.id} className="kanban-column">
            <div className="kanban-column-header">
              <span style={{ display: "flex", alignItems: "center", gap: "0.4rem" }}>
                <span>{col.icon}</span>
                <span>{col.title}</span>
              </span>
              <span
                style={{
                  backgroundColor: "var(--bg-primary)",
                  padding: "0.15rem 0.5rem",
                  borderRadius: "var(--radius-full)",
                  fontSize: "0.75rem",
                  color: "var(--text-secondary)",
                }}
              >
                {colItems.length}
              </span>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
              {colItems.length === 0 ? (
                <div
                  style={{
                    padding: "1.5rem 0.5rem",
                    textAlign: "center",
                    color: "var(--text-tertiary)",
                    fontSize: "0.8rem",
                    border: "1px dashed var(--border-color)",
                    borderRadius: "var(--radius-sm)",
                  }}
                >
                  No {col.title.toLowerCase()} items
                </div>
              ) : (
                colItems.map((item) => (
                  <div
                    key={item.id}
                    className="kanban-card"
                    onClick={() => onSelectWorkItem?.(item)}
                  >
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        marginBottom: "0.4rem",
                      }}
                    >
                      <span className={`badge badge-${col.id}`}>#{item.position}</span>
                      <span
                        style={{
                          fontSize: "0.7rem",
                          color: "var(--text-tertiary)",
                          textTransform: "uppercase",
                        }}
                      >
                        {item.deliverable_type}
                      </span>
                    </div>

                    <div className="kanban-card-title">{item.title}</div>

                    <p
                      style={{
                        fontSize: "0.775rem",
                        color: "var(--text-secondary)",
                        marginBottom: "0.75rem",
                        display: "-webkit-box",
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: "vertical",
                        overflow: "hidden",
                      }}
                    >
                      {item.instructions}
                    </p>

                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        justifyContent: "space-between",
                        borderTop: "1px solid var(--border-color)",
                        paddingTop: "0.5rem",
                        fontSize: "0.725rem",
                        color: "var(--text-accent)",
                      }}
                    >
                      <span>👤 {getAgentName(item.assigned_agent_id)}</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
