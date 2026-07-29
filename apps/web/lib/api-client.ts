import { components } from "./api-types";

export type Company = components["schemas"]["Company"];
export type CompanyUpdate = components["schemas"]["CompanyUpdate"];
export type AgentDefinition = components["schemas"]["AgentDefinition"];
export type AgentUpdate = components["schemas"]["AgentUpdate"];
export type Objective = components["schemas"]["Objective"];
export type ObjectiveCreate = components["schemas"]["ObjectiveCreate"];
export type WorkItem = components["schemas"]["WorkItem"];
export type Health = components["schemas"]["Health"];
export type ErrorResponse = components["schemas"]["Error"];
export type Plan = components["schemas"]["Plan"];
export type PlanRevision = components["schemas"]["PlanRevision"];
export type AgentRun = components["schemas"]["AgentRun"];
export type RunEvent = components["schemas"]["RunEvent"];
export type Artifact = components["schemas"]["Artifact"];
export type RunStatus = components["schemas"]["RunStatus"];
export type EventType = components["schemas"]["EventType"];
export type RunErrorCode = components["schemas"]["RunErrorCode"];

const API_BASE_URL = process.env["NEXT_PUBLIC_API_URL"] || "http://localhost:8000";

async function fetchJson<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers || {}),
    },
  });

  if (!response.ok) {
    let errorDetails: ErrorResponse | undefined;
    try {
      errorDetails = (await response.json()) as ErrorResponse;
    } catch {
      // ignore parse failure
    }
    const message = errorDetails?.message || `API error (${response.status})`;
    throw new Error(message);
  }

  return response.json() as Promise<T>;
}

export async function getCompany(): Promise<Company> {
  return fetchJson<Company>("/api/company");
}

export async function updateCompany(
  data: CompanyUpdate
): Promise<Company> {
  return fetchJson<Company>("/api/company", {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function listAgents(): Promise<AgentDefinition[]> {
  return fetchJson<AgentDefinition[]>("/api/agents");
}

export async function getAgent(agentId: string): Promise<AgentDefinition> {
  return fetchJson<AgentDefinition>(`/api/agents/${encodeURIComponent(agentId)}`);
}

export async function updateAgent(
  agentId: string,
  data: AgentUpdate
): Promise<AgentDefinition> {
  return fetchJson<AgentDefinition>(`/api/agents/${encodeURIComponent(agentId)}`, {
    method: "PATCH",
    body: JSON.stringify(data),
  });
}

export async function listObjectives(): Promise<Objective[]> {
  return fetchJson<Objective[]>("/api/objectives");
}

export async function createObjective(
  data: ObjectiveCreate
): Promise<Objective> {
  return fetchJson<Objective>("/api/objectives", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getObjective(
  objectiveId: string
): Promise<Objective> {
  return fetchJson<Objective>(`/api/objectives/${encodeURIComponent(objectiveId)}`);
}

export async function listWorkItems(params?: {
  objective_id?: string;
  status?: string;
}): Promise<WorkItem[]> {
  const searchParams = new URLSearchParams();
  if (params?.objective_id) {
    searchParams.set("objective_id", params.objective_id);
  }
  if (params?.status) {
    searchParams.set("status", params.status);
  }
  const queryString = searchParams.toString();
  const endpoint = `/api/work-items${queryString ? `?${queryString}` : ""}`;
  return fetchJson<WorkItem[]>(endpoint);
}

export async function getHealth(): Promise<Health> {
  return fetchJson<Health>("/api/health");
}

export function generateIdempotencyKey(): string {
  if (typeof crypto !== "undefined" && typeof crypto.randomUUID === "function") {
    return crypto.randomUUID();
  }
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

export async function createPlan(objectiveId: string): Promise<Plan> {
  return fetchJson<Plan>(`/api/objectives/${encodeURIComponent(objectiveId)}/plan`, {
    method: "POST",
  });
}

export async function revisePlan(
  objectiveId: string,
  data: PlanRevision
): Promise<Plan> {
  return fetchJson<Plan>(`/api/objectives/${encodeURIComponent(objectiveId)}/plan/revise`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function approvePlan(
  objectiveId: string,
  idempotencyKey: string
): Promise<AgentRun> {
  return fetchJson<AgentRun>(
    `/api/objectives/${encodeURIComponent(objectiveId)}/plan/approve`,
    {
      method: "POST",
      headers: {
        "Idempotency-Key": idempotencyKey,
      },
    }
  );
}

export async function getRun(runId: string): Promise<AgentRun> {
  return fetchJson<AgentRun>(`/api/runs/${encodeURIComponent(runId)}`);
}

export async function listRunEvents(
  runId: string,
  afterSequence?: number
): Promise<RunEvent[]> {
  const searchParams = new URLSearchParams();
  if (afterSequence !== undefined && afterSequence > 0) {
    searchParams.set("after_sequence", String(afterSequence));
  }
  const queryString = searchParams.toString();
  const endpoint = `/api/runs/${encodeURIComponent(runId)}/events${
    queryString ? `?${queryString}` : ""
  }`;
  return fetchJson<RunEvent[]>(endpoint);
}

export async function listRunArtifacts(runId: string): Promise<Artifact[]> {
  return fetchJson<Artifact[]>(`/api/runs/${encodeURIComponent(runId)}/artifacts`);
}

export async function retryRun(
  runId: string,
  idempotencyKey: string
): Promise<AgentRun> {
  return fetchJson<AgentRun>(`/api/runs/${encodeURIComponent(runId)}/retry`, {
    method: "POST",
    headers: {
      "Idempotency-Key": idempotencyKey,
    },
  });
}

export function getApiBaseUrl(): string {
  return API_BASE_URL;
}

