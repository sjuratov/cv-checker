/**
 * Analysis Service
 * Coordinates CV analysis workflow with validation, API calls, and state management
 */

import { api } from '../lib/api';
import type { AnalyzeRequest, AnalyzeResponse } from '../types/api';
import { validateCVContent, validateJobDescription, sanitizeText } from '../utils/validation';

// ============================================================================
// Types
// ============================================================================

export interface AnalysisInput {
  cvMarkdown: string;
  cvFilename?: string;
  jobDescription: string;
  sourceType?: 'manual' | 'linkedin_url';
  sourceUrl?: string | null;
}

export interface ValidationResult {
  valid: boolean;
  errors: string[];
}

export interface AnalysisResult {
  success: boolean;
  data?: AnalyzeResponse;
  error?: string;
}

// ============================================================================
// Validation Functions
// ============================================================================

/**
 * Validate analysis inputs before submitting to API
 */
export function validateAnalysisInput(input: AnalysisInput): ValidationResult {
  const errors: string[] = [];

  // Validate CV
  const cvValidation = validateCVContent(input.cvMarkdown);
  if (!cvValidation.valid) {
    errors.push(`CV: ${cvValidation.error}`);
  }

  // Validate Job Description
  const jobValidation = validateJobDescription(input.jobDescription);
  if (!jobValidation.valid) {
    errors.push(`Job: ${jobValidation.error}`);
  }

  return {
    valid: errors.length === 0,
    errors,
  };
}

/**
 * Sanitize analysis inputs
 */
export function sanitizeAnalysisInput(input: AnalysisInput): AnalysisInput {
  return {
    cvMarkdown: sanitizeText(input.cvMarkdown),
    jobDescription: sanitizeText(input.jobDescription),
  };
}

// ============================================================================
// Analysis Service
// ============================================================================

export class AnalysisService {
  /**
   * Perform CV analysis with validation and error handling
   */
  static async analyze(input: AnalysisInput): Promise<AnalysisResult> {
    try {
      // Step 1: Sanitize inputs
      const sanitized = sanitizeAnalysisInput(input);

      // Step 2: Validate inputs
      const validation = validateAnalysisInput(sanitized);
      if (!validation.valid) {
        return {
          success: false,
          error: validation.errors.join('\n'),
        };
      }

      // Step 3: Prepare API request
      const request: AnalyzeRequest = {
        cv_markdown: sanitized.cvMarkdown,
        cv_filename: input.cvFilename || 'resume.pdf',
        job_description: sanitized.jobDescription,
        source_type: input.sourceType || 'manual',
        source_url: input.sourceUrl || null,
      };

      // Step 4: Call API
      console.log('[AnalysisService] Starting analysis...', {
        cvLength: request.cv_markdown.length,
        jobLength: request.job_description.length,
        timestamp: new Date().toISOString(),
      });

      const startTime = performance.now();
      const result = await api.analyze(request);
      const duration = ((performance.now() - startTime) / 1000).toFixed(2);

      console.log('[AnalysisService] Analysis completed', {
        duration: `${duration}s`,
        score: result.overall_score,
        analysisId: result.analysis_id,
      });

      // Step 5: Return success result
      return {
        success: true,
        data: result,
      };
    } catch (error) {
      // Handle errors
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      
      console.error('[AnalysisService] Analysis failed', {
        error: errorMessage,
        timestamp: new Date().toISOString(),
      });

      return {
        success: false,
        error: errorMessage,
      };
    }
  }

  /**
   * Perform CV analysis with real-time progress updates
   */
  static async analyzeWithProgress(
    input: AnalysisInput,
    onProgress: (step: number, totalSteps: number, message: string) => void
  ): Promise<AnalysisResult> {
    try {
      // Step 1: Sanitize inputs
      const sanitized = sanitizeAnalysisInput(input);

      // Step 2: Validate inputs
      const validation = validateAnalysisInput(sanitized);
      if (!validation.valid) {
        return {
          success: false,
          error: validation.errors.join('\n'),
        };
      }

      // Step 3: Prepare API request
      const request: AnalyzeRequest = {
        cv_markdown: sanitized.cvMarkdown,
        cv_filename: input.cvFilename || 'resume.pdf',
        job_description: sanitized.jobDescription,
        source_type: input.sourceType || 'manual',
        source_url: input.sourceUrl || null,
      };

      // Step 4: Call streaming API
      console.log('[AnalysisService] Starting streaming analysis...', {
        cvLength: request.cv_markdown.length,
        jobLength: request.job_description.length,
        timestamp: new Date().toISOString(),
      });

      const startTime = performance.now();
      const result = await api.analyzeWithProgress(request, onProgress);
      const duration = ((performance.now() - startTime) / 1000).toFixed(2);

      console.log('[AnalysisService] Streaming analysis completed', {
        duration: `${duration}s`,
        score: result.overall_score,
        analysisId: result.analysis_id,
      });

      // Step 5: Return success result
      return {
        success: true,
        data: result,
      };
    } catch (error) {
      // Handle errors
      const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
      
      console.error('[AnalysisService] Streaming analysis failed', {
        error: errorMessage,
        timestamp: new Date().toISOString(),
      });

      return {
        success: false,
        error: errorMessage,
      };
    }
  }

  /**
   * Test backend connectivity
   */
  static async testConnection(): Promise<boolean> {
    try {
      const health = await api.healthCheck();
      console.log('[AnalysisService] Health check passed', health);
      return health.status === 'healthy';
    } catch (error) {
      console.error('[AnalysisService] Health check failed', error);
      return false;
    }
  }

  /**
   * Get API base URL for debugging
   */
  static getAPIBaseURL(): string {
    return api.getBaseURL();
  }
}
