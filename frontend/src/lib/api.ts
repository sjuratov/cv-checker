/**
 * API client for CV Checker backend
 * Implements comprehensive error handling, retry logic, and request/response interceptors
 */

import axios from 'axios';
import type { AxiosError, AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import type {
  AnalyzeRequest,
  AnalyzeResponse,
  HealthCheckResponse,
  ErrorResponse,
  APIError,
  HistoryResponse,
} from '../types/api';

// ============================================================================
// Configuration
// ============================================================================

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
const API_TIMEOUT = 90000; // 90 seconds for analysis (agents can take time)
const HEALTH_CHECK_TIMEOUT = 5000; // 5 seconds for health check
const MAX_RETRIES = 2; // Retry failed requests up to 2 times
const RETRY_DELAY = 1000; // 1 second between retries

// ============================================================================
// Helper Functions
// ============================================================================

/**
 * Delay execution for specified milliseconds
 */
const delay = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms));

/**
 * Determine if error is retryable (network errors, 5xx, 429)
 */
function isRetryableError(error: AxiosError): boolean {
  if (!error.response) {
    // Network error - retry
    return true;
  }

  const status = error.response.status;
  // Retry on 5xx server errors and 429 rate limit
  return status >= 500 || status === 429;
}

/**
 * Extract user-friendly error message from API error
 */
function extractErrorMessage(error: AxiosError): string {
  if (error.response) {
    const data = error.response.data as ErrorResponse;
    
    // Handle validation errors (422)
    if (error.response.status === 422) {
      if (data.details) {
        const detailsStr = JSON.stringify(data.details, null, 2);
        return `Validation Error: ${data.message}\n\nDetails:\n${detailsStr}`;
      }
      return `Validation Error: ${data.message || 'Invalid request data'}`;
    }

    // Handle other errors
    return data.message || data.error || `Server error (${error.response.status})`;
  }

  if (error.request) {
    return 'Unable to connect to the server. Please check your internet connection and ensure the backend is running.';
  }

  return `Request failed: ${error.message}`;
}

// ============================================================================
// API Client Class
// ============================================================================

class CVCheckerAPI {
  private client: AxiosInstance;
  private requestCount = 0;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: API_TIMEOUT,
    });

    this.setupInterceptors();
  }

  /**
   * Configure request and response interceptors
   */
  private setupInterceptors(): void {
    // Request interceptor - add request ID and logging
    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        this.requestCount++;
        const requestId = `req-${Date.now()}-${this.requestCount}`;
        
        // Add custom header for tracing
        config.headers = config.headers || {};
        config.headers['X-Request-ID'] = requestId;

        console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`, {
          requestId,
          timestamp: new Date().toISOString(),
        });

        return config;
      },
      (error) => {
        console.error('[API Request Error]', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor - handle errors and logging
    this.client.interceptors.response.use(
      (response) => {
        console.log(`[API Response] ${response.status} ${response.config.url}`, {
          requestId: response.config.headers?.['X-Request-ID'],
          duration: response.headers['x-process-time'] || 'unknown',
        });
        return response;
      },
      async (error: AxiosError) => {
        const requestId = error.config?.headers?.['X-Request-ID'];
        console.error(`[API Error] ${error.config?.url}`, {
          requestId,
          status: error.response?.status,
          message: error.message,
        });

        // Handle retry logic
        const config = error.config as any;
        if (!config || !config.retryCount) {
          config.retryCount = 0;
        }

        if (config.retryCount < MAX_RETRIES && isRetryableError(error)) {
          config.retryCount++;
          console.log(`[API Retry] Attempt ${config.retryCount}/${MAX_RETRIES}`, {
            requestId,
            url: config.url,
          });

          await delay(RETRY_DELAY * config.retryCount);
          return this.client.request(config);
        }

        // Extract and throw user-friendly error
        const message = extractErrorMessage(error);
        throw new Error(message);
      }
    );
  }

  /**
   * Get API base URL for debugging
   */
  getBaseURL(): string {
    return API_BASE_URL;
  }

  /**
   * Health check endpoint
   * @throws Error if health check fails
   */
  async healthCheck(): Promise<HealthCheckResponse> {
    try {
      const response = await this.client.get<HealthCheckResponse>('/api/v1/health', {
        timeout: HEALTH_CHECK_TIMEOUT,
      });
      return response.data;
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Health check failed');
    }
  }

  /**
   * Analyze CV against job description
   * @param request - CV markdown and job description
   * @returns Analysis results with score, matches, recommendations
   * @throws Error on validation failure, server error, or network issue
   */
  async analyze(request: AnalyzeRequest): Promise<AnalyzeResponse> {
    // Validate request before sending
    if (!request.cv_markdown || request.cv_markdown.trim().length === 0) {
      throw new Error('CV content is required');
    }

    if (!request.job_description || request.job_description.trim().length === 0) {
      throw new Error('Job description is required');
    }

    try {
      console.log('[API] Starting CV analysis...', {
        cvLength: request.cv_markdown.length,
        jobLength: request.job_description.length,
      });

      const response = await this.client.post<AnalyzeResponse>(
        '/api/v1/analyze',
        request,
        {
          timeout: API_TIMEOUT,
        }
      );

      console.log('[API] Analysis completed successfully', {
        analysisId: response.data.analysis_id,
        score: response.data.overall_score,
      });

      return response.data;
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Analysis failed unexpectedly');
    }
  }

  /**
   * Test connection to backend
   * @returns true if connection successful
   */
  async testConnection(): Promise<boolean> {
    try {
      await this.healthCheck();
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Get analysis history for a user
   * @param userId - User ID (default: anonymous)
   * @param limit - Maximum number of results (default: 20)
   * @returns History items with CV and Job data
   * @throws Error on server error or network issue
   */
  async getHistory(userId: string = 'anonymous', limit: number = 20): Promise<HistoryResponse> {
    try {
      console.log('[API] Fetching analysis history...', {
        userId,
        limit,
      });

      const response = await this.client.get<HistoryResponse>('/api/v1/history', {
        params: { user_id: userId, limit },
        timeout: HEALTH_CHECK_TIMEOUT,
      });

      console.log('[API] History fetched successfully', {
        count: response.data.count,
      });

      return response.data;
    } catch (error) {
      if (error instanceof Error) {
        throw error;
      }
      throw new Error('Failed to fetch history');
    }
  }
}

// ============================================================================
// Export Singleton Instance
// ============================================================================

export const api = new CVCheckerAPI();
