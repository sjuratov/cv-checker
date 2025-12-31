/**
 * API client for CV Checker backend
 */

import axios, { AxiosError } from 'axios';
import type { AxiosInstance } from 'axios';
import type { AnalyzeRequest, AnalyzeResponse, HealthCheckResponse } from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

class CVCheckerAPI {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 60000, // 60 seconds for analysis
    });

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response) {
          // Server responded with error status
          const data = error.response.data as any;
          throw new Error(data?.message || data?.error || 'An error occurred');
        } else if (error.request) {
          // Request made but no response
          throw new Error('Unable to connect to server. Please check your internet connection.');
        } else {
          // Error setting up request
          throw new Error('Request failed: ' + error.message);
        }
      }
    );
  }

  /**
   * Health check endpoint
   */
  async healthCheck(): Promise<HealthCheckResponse> {
    const response = await this.client.get<HealthCheckResponse>('/api/v1/health', {
      timeout: 5000,
    });
    return response.data;
  }

  /**
   * Analyze CV against job description
   */
  async analyze(request: AnalyzeRequest): Promise<AnalyzeResponse> {
    const response = await this.client.post<AnalyzeResponse>('/api/v1/analyze', request);
    return response.data;
  }
}

export const api = new CVCheckerAPI();
