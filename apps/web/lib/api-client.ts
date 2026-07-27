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
