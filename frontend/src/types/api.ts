/**
 * TypeScript types for CV Checker API
 * Generated from backend OpenAPI schema
 */

export interface AnalyzeRequest {
  cv_markdown: string;
  job_description: string;
}

export interface SkillMatch {
  skill_name: string;
  required: boolean;
  candidate_has: boolean;
  proficiency_level?: string | null;
  years_experience?: number | null;
  match_score: number;
}

export interface AnalyzeResponse {
  analysis_id: string;
  overall_score: number;
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
}

export interface ErrorResponse {
  error: string;
  message: string;
  details?: Record<string, any>;
}

// Frontend-specific types
export interface AnalysisHistory {
  id: string;
  timestamp: string;
  cvFilename: string;
  jobTitle?: string;
  score: number;
  result: AnalyzeResponse;
}
