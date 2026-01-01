/**
 * TypeScript types for CV Checker API
 * Matches backend OpenAPI schema exactly
 */

// ============================================================================
// Request Types
// ============================================================================

export interface AnalyzeRequest {
  cv_markdown: string;
  job_description: string;
}

// ============================================================================
// Response Types (Backend Contract)
// ============================================================================

export interface SkillMatch {
  skill_name: string;
  required: boolean;
  candidate_has: boolean;
  proficiency_level?: string | null;
  years_experience?: number | null;
  match_score: number; // 0.0 to 1.0
}

export interface AnalyzeResponse {
  analysis_id: string;
  overall_score: number; // 0-100
  skill_matches: SkillMatch[];
  experience_match: Record<string, any>;
  education_match: Record<string, any>;
  strengths: string[];
  gaps: string[];
  recommendations: string[];
}

export interface HealthCheckResponse {
  status: string;
  version: string;
  service: string;
  azure_openai?: string;
  cosmos_db?: string;
}

export interface ErrorResponse {
  error: string;
  message: string;
  details?: Record<string, any>;
}

// ============================================================================
// Frontend-Specific Types
// ============================================================================

export interface AnalysisHistory {
  id: string;
  timestamp: string;
  cvFilename: string;
  jobTitle?: string;
  score: number;
  result: AnalyzeResponse;
}

// ============================================================================
// API Error Types
// ============================================================================

export class APIError extends Error {
  constructor(
    message: string,
    public statusCode?: number,
    public errorType?: string,
    public details?: Record<string, any>
  ) {
    super(message);
    this.name = 'APIError';
  }
}
