/**
 * API response types — mirrors backend Pydantic schemas.
 *
 * When orval codegen runs (`pnpm codegen` with backend up),
 * these will be auto-generated. Until then, manually maintained.
 */

// --- Workspace & Project ---

export interface Workspace {
  id: string;
  name: string;
  created_at: string;
  updated_at: string;
}

export interface Project {
  id: string;
  name: string;
  workspace_id: string;
  created_at: string;
  updated_at: string;
}

// --- Governance ---

export interface GovernancePolicy {
  id: string;
  project_id: string;
  framework: string;
  policy_id: string;
  name: string;
  description: string;
  category: string;
  subcategory: string;
  severity: string;
  rules: Record<string, unknown>;
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface GovernanceCheckResult {
  overall_score: number;
  results: PolicyResult[];
}

export interface PolicyResult {
  policy_id: string;
  framework: string;
  category: string;
  score: number;
  status: "pass" | "warn" | "fail";
}

export interface ActivateRequest {
  framework_id: string;
}

// --- Evaluation ---

export interface EvalSuggestion {
  policy_db_id: string;
  policy_id: string;
  framework: string;
  criterion_id: string;
  description: string;
  metric: string;
  threshold: string;
}

// --- Analytics ---

export interface NorthStarResponse {
  governance_wired_projects: number;
}

export interface ScoreResponse {
  project_id: string;
  score: number;
}

export interface CoverageResponse {
  project_id: string;
  coverage: Record<string, number>;
}

export interface SnapshotResponse {
  project_id: string;
  score: number;
  policies_active: number;
  frameworks_active: number;
  snapshot_date: string;
}

// --- Export ---

export interface ExportGenerateResponse {
  status: string;
  artifacts: string[];
}

// --- Agent ---

export interface AgentRunRequest {
  workspace_id: string;
  project_id: string;
  prompt: string;
}

// --- Topology ---

export interface TopologyEvaluateResponse {
  pipeline_score: number;
  delegation_depth: number;
  has_circular_delegation: boolean;
  agent_count: number;
  bottleneck_count: number;
  bottlenecks: {
    agent_id: string;
    score: number;
    recommendation: string;
  }[];
}
