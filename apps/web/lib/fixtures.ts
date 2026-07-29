export interface Company {
  id: string;
  name: string;
  description: string;
  mission: string;
  working_rules: string;
  created_at: string;
  updated_at: string;
}

export interface AgentDefinition {
  id: string;
  company_id: string;
  slug: string;
  name: string;
  role: string;
  objective: string;
  responsibilities: string[];
  runtime_model_alias: string;
  prompt_version: string;
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface Objective {
  id: string;
  company_id: string;
  title: string;
  desired_outcome: string;
  context: string;
  constraints: string[];
  status: "draft" | "active" | "completed" | "failed";
  created_at: string;
  updated_at: string;
}

export interface WorkItem {
  id: string;
  company_id: string;
  objective_id: string;
  parent_id?: string | null;
  assigned_agent_id: string;
  title: string;
  instructions: string;
  deliverable_type: string;
  status: "proposed" | "approved" | "running" | "review" | "done" | "failed";
  position: number;
  created_at: string;
  updated_at: string;
}

export interface AgentRun {
  id: string;
  company_id: string;
  objective_id: string;
  status: "pending" | "running" | "completed" | "failed";
  graph_version: string;
  started_at: string;
  finished_at: string | null;
  error_code: string | null;
  created_at: string;
  updated_at: string;
}

export interface RunEvent {
  id: string;
  company_id: string;
  run_id: string;
  sequence: number;
  event_type:
    | "run.created"
    | "plan.proposed"
    | "plan.revision_requested"
    | "plan.approved"
    | "work.started"
    | "work.progress"
    | "artifact.created"
    | "work.completed"
    | "work.failed"
    | "brief.created"
    | "run.completed"
    | "run.failed";
  summary: string;
  payload_json: Record<string, unknown>;
  created_at: string;
}

export interface Artifact {
  id: string;
  company_id: string;
  run_id: string;
  work_item_id?: string | null;
  artifact_type: string;
  title: string;
  content_markdown: string;
  version: number;
  created_at: string;
  updated_at: string;
}

export const sampleCompany: Company = {
  id: "20000000-0000-4000-8000-000000000001",
  name: "Solo Company",
  description: "Owner console for a single AI-assisted company.",
  mission: "Accelerate autonomous business operations with AI specialists.",
  working_rules:
    "Specialist work is sequential. Every deliverable must be validated before the next item begins.",
  created_at: "2026-07-27T08:00:00Z",
  updated_at: "2026-07-27T08:00:00Z",
};

export const sampleAgents: AgentDefinition[] = [
  {
    id: "a1000000-0000-4000-8000-000000000001",
    company_id: sampleCompany.id,
    slug: "chief-of-staff",
    name: "Chief of Staff / Business Strategist",
    role: "Chief of Staff",
    objective: "Coordinate specialist agents and synthesize executive briefs.",
    responsibilities: [
      "Objective intake and validation",
      "Structured plan generation with owners and deliverables",
      "Executive brief synthesis and follow-up recommendations",
    ],
    runtime_model_alias: "gemini-3.1-pro",
    prompt_version: "v1.0.0",
    enabled: true,
    created_at: "2026-07-27T08:00:00Z",
    updated_at: "2026-07-27T08:00:00Z",
  },
  {
    id: "a2000000-0000-4000-8000-000000000002",
    company_id: sampleCompany.id,
    slug: "marketing-specialist",
    name: "Marketing Specialist",
    role: "Marketing Specialist",
    objective:
      "Create compelling marketing briefs, messaging, and go-to-market assets.",
    responsibilities: [
      "Market research and competitive positioning",
      "Copywriting and messaging framework design",
      "Launch campaign brief creation",
    ],
    runtime_model_alias: "gemini-3.1-pro",
    prompt_version: "v1.0.0",
    enabled: true,
    created_at: "2026-07-27T08:00:00Z",
    updated_at: "2026-07-27T08:00:00Z",
  },
  {
    id: "a3000000-0000-4000-8000-000000000003",
    company_id: sampleCompany.id,
    slug: "operations-manager",
    name: "Operations Manager",
    role: "Operations Manager",
    objective:
      "Design checklists, workflows, and operational procedures for execution.",
    responsibilities: [
      "Workflow and standard operating procedure design",
      "Checklist creation and onboarding documentation",
      "Quality verification and delivery assurance",
    ],
    runtime_model_alias: "gemini-3.1-pro",
    prompt_version: "v1.0.0",
    enabled: true,
    created_at: "2026-07-27T08:00:00Z",
    updated_at: "2026-07-27T08:00:00Z",
  },
];

export const sampleObjectives: Objective[] = [
  {
    id: "o1000000-0000-4000-8000-000000000001",
    company_id: sampleCompany.id,
    title: "Create a launch plan for a bookkeeping service",
    desired_outcome:
      "A complete go-to-market brief, pricing sheet, and client onboarding checklist for a new bookkeeping service.",
    context:
      "Targeting small professional services firms with 1-10 employees.",
    constraints: [
      "Budget must remain under $5,000 for launch tooling",
      "Onboarding time must be under 3 business days per client",
    ],
    status: "active",
    created_at: "2026-07-27T09:00:00Z",
    updated_at: "2026-07-27T09:00:00Z",
  },
  {
    id: "o2000000-0000-4000-8000-000000000002",
    company_id: sampleCompany.id,
    title: "Quarterly customer retention audit",
    desired_outcome:
      "An audit report of Q2 churn factors and 3 prioritized operational fixes.",
    context: "SaaS churn increased by 2.4% in the previous quarter.",
    constraints: ["No headcount additions"],
    status: "completed",
    created_at: "2026-07-15T09:00:00Z",
    updated_at: "2026-07-18T16:00:00Z",
  },
];

export const sampleWorkItems: WorkItem[] = [
  {
    id: "w1000000-0000-4000-8000-000000000001",
    company_id: sampleCompany.id,
    objective_id: sampleObjectives[0].id,
    parent_id: null,
    assigned_agent_id: sampleAgents[1].id, // Marketing Specialist
    title: "Draft bookkeeping launch marketing brief",
    instructions:
      "Research target market messaging and prepare a 2-page marketing brief for professional service firms.",
    deliverable_type: "marketing_brief",
    status: "done",
    position: 1,
    created_at: "2026-07-27T09:10:00Z",
    updated_at: "2026-07-27T09:35:00Z",
  },
  {
    id: "w2000000-0000-4000-8000-000000000002",
    company_id: sampleCompany.id,
    objective_id: sampleObjectives[0].id,
    parent_id: null,
    assigned_agent_id: sampleAgents[2].id, // Operations Manager
    title: "Create client onboarding checklist & SLA",
    instructions:
      "Define standard operating procedure for onboarding new bookkeeping clients within 3 business days.",
    deliverable_type: "operations_checklist",
    status: "running",
    position: 2,
    created_at: "2026-07-27T09:10:00Z",
    updated_at: "2026-07-27T09:40:00Z",
  },
  {
    id: "w3000000-0000-4000-8000-000000000003",
    company_id: sampleCompany.id,
    objective_id: sampleObjectives[0].id,
    parent_id: null,
    assigned_agent_id: sampleAgents[0].id, // Chief of Staff
    title: "Synthesize launch executive brief",
    instructions:
      "Review marketing brief and onboarding checklist; compose executive decision brief with pricing recommendation.",
    deliverable_type: "executive_brief",
    status: "approved",
    position: 3,
    created_at: "2026-07-27T09:10:00Z",
    updated_at: "2026-07-27T09:15:00Z",
  },
  {
    id: "w4000000-0000-4000-8000-000000000004",
    company_id: sampleCompany.id,
    objective_id: sampleObjectives[0].id,
    parent_id: null,
    assigned_agent_id: sampleAgents[1].id,
    title: "Proposed outreach email sequence",
    instructions: "Draft 3 cold outreach templates for prospective accountants.",
    deliverable_type: "email_sequence",
    status: "proposed",
    position: 4,
    created_at: "2026-07-27T09:45:00Z",
    updated_at: "2026-07-27T09:45:00Z",
  },
  {
    id: "w5000000-0000-4000-8000-000000000005",
    company_id: sampleCompany.id,
    objective_id: sampleObjectives[0].id,
    parent_id: null,
    assigned_agent_id: sampleAgents[2].id,
    title: "Review automated payroll integration tool",
    instructions: "Evaluate API reliability for automated payroll imports.",
    deliverable_type: "audit_report",
    status: "review",
    position: 5,
    created_at: "2026-07-27T09:20:00Z",
    updated_at: "2026-07-27T09:50:00Z",
  },
  {
    id: "w6000000-0000-4000-8000-000000000006",
    company_id: sampleCompany.id,
    objective_id: sampleObjectives[0].id,
    parent_id: null,
    assigned_agent_id: sampleAgents[2].id,
    title: "Legacy QuickBooks CSV import validator",
    instructions: "Attempt automatic ingestion of non-standard CSV ledgers.",
    deliverable_type: "script_validation",
    status: "failed",
    position: 6,
    created_at: "2026-07-27T09:15:00Z",
    updated_at: "2026-07-27T09:25:00Z",
  },
];

export const sampleRuns: AgentRun[] = [
  {
    id: "30000000-0000-4000-8000-000000000001",
    company_id: sampleCompany.id,
    objective_id: sampleObjectives[0].id,
    status: "running",
    graph_version: "p1-v1",
    started_at: "2026-07-27T09:15:00Z",
    finished_at: null,
    error_code: null,
    created_at: "2026-07-27T09:15:00Z",
    updated_at: "2026-07-27T09:45:00Z",
  },
  {
    id: "30000000-0000-4000-8000-000000000002",
    company_id: sampleCompany.id,
    objective_id: sampleObjectives[1].id,
    status: "completed",
    graph_version: "p1-v1",
    started_at: "2026-07-15T09:05:00Z",
    finished_at: "2026-07-15T11:45:00Z",
    error_code: null,
    created_at: "2026-07-15T09:05:00Z",
    updated_at: "2026-07-15T11:45:00Z",
  },
  {
    id: "30000000-0000-4000-8000-000000000003",
    company_id: sampleCompany.id,
    objective_id: sampleObjectives[0].id,
    status: "failed",
    graph_version: "p1-v1",
    started_at: "2026-07-26T14:00:00Z",
    finished_at: "2026-07-26T14:12:00Z",
    error_code: "ERR_SPECIALIST_TIMEOUT",
    created_at: "2026-07-26T14:00:00Z",
    updated_at: "2026-07-26T14:12:00Z",
  },
];

export const sampleRunEvents: RunEvent[] = [
  {
    id: "e1000000-0000-4000-8000-000000000001",
    company_id: sampleCompany.id,
    run_id: sampleRuns[0].id,
    sequence: 1,
    event_type: "run.created",
    summary: "Started Phase 1 run for bookkeeping launch objective",
    payload_json: { objective_id: sampleObjectives[0].id },
    created_at: "2026-07-27T09:15:00Z",
  },
  {
    id: "e2000000-0000-4000-8000-000000000002",
    company_id: sampleCompany.id,
    run_id: sampleRuns[0].id,
    sequence: 2,
    event_type: "plan.proposed",
    summary: "Chief of Staff proposed 3 sequential work items",
    payload_json: { work_items_count: 3 },
    created_at: "2026-07-27T09:16:00Z",
  },
  {
    id: "e3000000-0000-4000-8000-000000000003",
    company_id: sampleCompany.id,
    run_id: sampleRuns[0].id,
    sequence: 3,
    event_type: "plan.approved",
    summary: "Owner approved launch plan without revisions",
    payload_json: { approved_by: "owner" },
    created_at: "2026-07-27T09:18:00Z",
  },
  {
    id: "10000000-0000-4000-8000-000000000001",
    company_id: sampleCompany.id,
    run_id: sampleRuns[0].id,
    sequence: 4,
    event_type: "artifact.created",
    summary: "Created marketing brief",
    payload_json: {
      artifact_id: "40000000-0000-4000-8000-000000000001",
      artifact_type: "marketing_brief",
      title: "Bookkeeping service launch brief",
    },
    created_at: "2026-07-27T09:30:00Z",
  },
  {
    id: "e5000000-0000-4000-8000-000000000005",
    company_id: sampleCompany.id,
    run_id: sampleRuns[0].id,
    sequence: 5,
    event_type: "work.started",
    summary: "Operations Manager started client onboarding checklist",
    payload_json: { work_item_id: sampleWorkItems[1].id },
    created_at: "2026-07-27T09:32:00Z",
  },
  {
    id: "e6000000-0000-4000-8000-000000000006",
    company_id: sampleCompany.id,
    run_id: sampleRuns[0].id,
    sequence: 6,
    event_type: "work.progress",
    summary: "Drafted 14-step onboarding checklist and client portal setup",
    payload_json: { completion_percentage: 75 },
    created_at: "2026-07-27T09:40:00Z",
  },
];

export const sampleArtifacts: Artifact[] = [
  {
    id: "40000000-0000-4000-8000-000000000001",
    company_id: sampleCompany.id,
    run_id: sampleRuns[0].id,
    work_item_id: sampleWorkItems[0].id,
    artifact_type: "marketing_brief",
    title: "Bookkeeping service launch brief",
    content_markdown: `# Bookkeeping Service Launch Marketing Brief

## Executive Summary
This document outlines the target market positioning, messaging hierarchy, and launch sequence for Solo Company's new automated bookkeeping service targeting professional service firms (1–10 employees).

### Key Value Proposition
- **3-Day Guaranteed Onboarding**: From ledger connect to first reconciliation.
- **Fixed Monthly Subscription**: Predictable pricing with no hourly surprises.
- **AI-Verified Transaction Categorization**: Over 98% accuracy on recurring vendor expenses.

## Target Audience
1. **Law Firms & Boutique Consultancies**: High transaction volume, need clear trust accounting.
2. **Creative Agencies**: Variable expense tracking and contractor reimbursements.

## Launch Milestones
- **Week 1**: Outreach email campaign to existing network.
- **Week 2**: Launch webinar and automated demo walkthrough.
- **Week 3**: Initial 10 client cohort onboarding.`,
    version: 1,
    created_at: "2026-07-27T09:30:00Z",
    updated_at: "2026-07-27T09:30:00Z",
  },
  {
    id: "40000000-0000-4000-8000-000000000002",
    company_id: sampleCompany.id,
    run_id: sampleRuns[0].id,
    work_item_id: sampleWorkItems[2].id,
    artifact_type: "executive_brief",
    title: "Launch Executive Decision Brief",
    content_markdown: `# Launch Executive Decision Brief: Bookkeeping Service

## Recommendation
Approve the go-to-market launch for the Bookkeeping Service with a standard pricing tier of **$499/month** per client.

### Summary of Specialist Findings
1. **Marketing Specialist**: Identified strong demand among law firms and creative agencies. Client acquisition cost is estimated at $350.
2. **Operations Manager**: Verified 3-day onboarding checklist using automated bank feeds. Maximum capacity without additional headcount is 25 active clients.

### Next Steps for Owner
- Review and approve the draft email sequence in the Work Board.
- Confirm pricing tier of $499/month in company working rules.`,
    version: 1,
    created_at: "2026-07-27T09:45:00Z",
    updated_at: "2026-07-27T09:45:00Z",
  },
];
