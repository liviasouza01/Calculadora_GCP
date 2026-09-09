import type {
  CalculationResult,
  ServiceDefinition,
  ServiceInputs,
} from "../types";
import { PUBLIC_APP_URL } from "../shareUrl";

const BASE_URL = "/api";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(`API error ${response.status}: ${detail}`);
  }
  return response.json() as Promise<T>;
}

export function fetchServices(): Promise<ServiceDefinition[]> {
  return request<ServiceDefinition[]>("/services");
}

export function calculateService(
  serviceId: string,
  inputs: ServiceInputs,
): Promise<CalculationResult> {
  return request<CalculationResult>(`/services/${serviceId}/calculate`, {
    method: "POST",
    body: JSON.stringify(inputs),
  });
}

export interface ProjectItem {
  service_id: string;
  inputs: ServiceInputs;
}

export interface ProjectResult {
  currency: string;
  results: CalculationResult[];
  grand_total: number;
}

export function calculateProject(items: ProjectItem[]): Promise<ProjectResult> {
  return request<ProjectResult>("/calculate/project", {
    method: "POST",
    body: JSON.stringify({ items }),
  });
}

export interface AgentFillResult {
  filled_services: Record<string, ServiceInputs>;
  filled_as_is?: Record<string, ServiceInputs>;
  filled_to_be?: Record<string, ServiceInputs>;
  summary: string;
  architecture_image?: string | null;
}

export async function fillFromBriefing(formData: FormData): Promise<AgentFillResult> {
  const response = await fetch(`${BASE_URL}/agent/fill`, {
    method: "POST",
    body: formData,
  });
  if (!response.ok) {
    const raw = await response.text();
    let message = raw;
    try {
      const parsed = JSON.parse(raw) as { detail?: unknown };
      if (typeof parsed.detail === "string") {
        message = parsed.detail;
      }
    } catch {
      message = raw;
    }
    throw new Error(message);
  }
  return response.json() as Promise<AgentFillResult>;
}

export interface CalculatorShare {
  id: string;
  enabled: Record<string, boolean>;
  presets: Record<string, ServiceInputs>;
}

export async function createShare(payload: {
  enabled: Record<string, boolean>;
  presets: Record<string, ServiceInputs>;
}): Promise<{ id: string; path: string }> {
  const response = await fetch(`${PUBLIC_APP_URL}/api/shares`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || `API error ${response.status}`);
  }
  return response.json() as Promise<{ id: string; path: string }>;
}

export function fetchShare(shareId: string): Promise<CalculatorShare> {
  return request<CalculatorShare>(`/shares/${encodeURIComponent(shareId)}`);
}
