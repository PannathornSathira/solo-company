"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useDemoState, DemoState } from "../lib/StateContext";
import { sampleCompany, sampleObjectives, sampleRuns } from "../lib/fixtures";

export function Navigation({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { demoState, setDemoState } = useDemoState();

  const navItems = [
    { href: "/", label: "Dashboard", icon: "📊" },
    { href: "/objectives/new", label: "New Objective", icon: "🎯" },
    { href: "/work", label: "Work Board", icon: "📋" },
    { href: "/settings/company", label: "Company Setup", icon: "⚙️" },
  ];

  const quickLinks = [
    {
      href: `/objectives/${sampleObjectives[0].id}/plan`,
      label: "Plan Review (Launch)",
    },
    { href: `/runs/${sampleRuns[0].id}`, label: "Run Inspector (Active)" },
    { href: `/agents/chief-of-staff`, label: "Agent: Chief of Staff" },
  ];

  const states: { id: DemoState; label: string }[] = [
    { id: "completed", label: "Completed" },
    { id: "loading", label: "Loading" },
    { id: "empty", label: "Empty" },
    { id: "error", label: "Error" },
  ];

  return (
    <div className="app-shell">
      {/* Sidebar Navigation */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="brand-logo">S</div>
          <div>
            <div className="brand-title">{sampleCompany.name}</div>
            <div style={{ fontSize: "0.75rem", color: "var(--text-tertiary)" }}>
              Phase 1 Console
            </div>
          </div>
        </div>

        <nav className="sidebar-nav">
          <div
            style={{
              fontSize: "0.75rem",
              textTransform: "uppercase",
              color: "var(--text-tertiary)",
              fontWeight: 600,
              padding: "0.5rem 0.9rem",
            }}
          >
            Core Routes
          </div>
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`nav-link ${isActive ? "active" : ""}`}
              >
                <span>{item.icon}</span>
                <span>{item.label}</span>
              </Link>
            );
          })}

          <div
            style={{
              fontSize: "0.75rem",
              textTransform: "uppercase",
              color: "var(--text-tertiary)",
              fontWeight: 600,
              padding: "1rem 0.9rem 0.3rem",
            }}
          >
            Demo Inspection
          </div>
          {quickLinks.map((ql) => {
            const isActive = pathname === ql.href;
            return (
              <Link
                key={ql.href}
                href={ql.href}
                className={`nav-link ${isActive ? "active" : ""}`}
                style={{ fontSize: "0.85rem" }}
              >
                <span>🔍</span>
                <span>{ql.label}</span>
              </Link>
            );
          })}
        </nav>

        <div className="sidebar-footer">
          <div style={{ fontSize: "0.75rem", color: "var(--text-secondary)" }}>
            Runtime Model:
          </div>
          <div
            style={{
              fontSize: "0.85rem",
              fontWeight: 600,
              color: "var(--text-accent)",
            }}
          >
            gemini-3.1-pro
          </div>
          <div
            style={{
              fontSize: "0.7rem",
              color: "var(--text-tertiary)",
              marginTop: "0.2rem",
            }}
          >
            Module: P1-M02 (Gemini)
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="main-content">
        <header className="topheader">
          <div className="topheader-left">
            <h2 style={{ fontSize: "1.15rem", fontWeight: 600 }}>
              {pathname === "/"
                ? "Company Dashboard"
                : pathname.includes("/objectives/new")
                ? "Objective Intake"
                : pathname.includes("/plan")
                ? "Plan Review"
                : pathname.includes("/work")
                ? "Work Board"
                : pathname.includes("/runs")
                ? "Run Inspection"
                : pathname.includes("/agents")
                ? "Agent Profile"
                : pathname.includes("/settings")
                ? "Company Setup"
                : "Solo Company Console"}
            </h2>
          </div>

          <div className="topheader-right">
            <div
              style={{
                fontSize: "0.75rem",
                color: "var(--text-secondary)",
                marginRight: "0.25rem",
              }}
            >
              Demo State:
            </div>
            <div className="state-switcher">
              {states.map((s) => (
                <button
                  key={s.id}
                  onClick={() => setDemoState(s.id)}
                  className={`state-tab ${demoState === s.id ? "active" : ""}`}
                  title={`Toggle ${s.label} demo state`}
                >
                  {s.label}
                </button>
              ))}
            </div>
          </div>
        </header>

        <div className="page-body">{children}</div>
      </main>
    </div>
  );
}
