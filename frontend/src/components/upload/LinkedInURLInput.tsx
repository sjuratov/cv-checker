/**
 * LinkedIn URL Input Component
 * 
 * Allows users to paste a LinkedIn job URL and automatically fetch the job description.
 */

import { useState } from 'react';
import { Link2, Loader, AlertCircle, RefreshCcw, FileText } from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';
import axios from 'axios';

interface FetchError {
  success: false;
  error: string;
  message: string;
  details?: string;
  fallback: string;
}

export function LinkedInURLInput() {
  const { updateJobDescription, setJobInputMode } = useAppStore();
  const [url, setUrl] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<FetchError | null>(null);

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

  const validateURL = (url: string): boolean => {
    const pattern = /^https?:\/\/(www\.)?linkedin\.com\/jobs\/view\/\d+/;
    return pattern.test(url.trim());
  };

  const handleFetch = async () => {
    setError(null);

    const trimmedUrl = url.trim();

    if (!trimmedUrl) {
      setError({
        success: false,
        error: 'empty_url',
        message: 'Please enter a LinkedIn job URL',
        fallback: 'manual_input',
      });
      return;
    }

    if (!validateURL(trimmedUrl)) {
      setError({
        success: false,
        error: 'invalid_url',
        message: 'Invalid LinkedIn URL. Expected format: https://linkedin.com/jobs/view/[ID]',
        fallback: 'manual_input',
      });
      return;
    }

    setIsLoading(true);

    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/v1/jobs`,
        {
          source_type: 'linkedin_url',
          url: trimmedUrl,
        },
        {
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (response.status === 201 && response.data.fetch_status === 'success') {
        // Success - update job description
        updateJobDescription(response.data.content, 'linkedin_url', trimmedUrl);
        setUrl(''); // Clear input after success
        setError(null);
      } else {
        setError({
          success: false,
          error: 'unexpected_response',
          message: 'Unexpected response from server',
          fallback: 'manual_input',
        });
      }
    } catch (err: any) {
      console.error('LinkedIn fetch error:', err);

      if (err.response?.status === 429) {
        setError({
          success: false,
          error: 'rate_limit_exceeded',
          message: 'Too many requests. Please try again later.',
          details: err.response?.data?.detail?.message || 'Rate limit exceeded',
          fallback: 'manual_input',
        });
      } else if (err.response?.data?.detail) {
        // Extract error from API response
        const detail = err.response.data.detail;
        setError({
          success: false,
          error: detail.error || 'unknown',
          message: detail.message || 'Failed to fetch job description',
          details: detail.details,
          fallback: detail.fallback || 'manual_input',
        });
      } else if (err.code === 'ERR_NETWORK') {
        setError({
          success: false,
          error: 'network_error',
          message: 'Network error. Please check your connection and try again.',
          fallback: 'manual_input',
        });
      } else {
        setError({
          success: false,
          error: 'unknown_error',
          message: 'An unexpected error occurred. Please try again.',
          fallback: 'manual_input',
        });
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !isLoading && url.trim()) {
      handleFetch();
    }
  };

  const handleRetry = () => {
    setError(null);
    handleFetch();
  };

  const handleSwitchToManual = () => {
    setError(null);
    setUrl('');
    setJobInputMode('manual');
  };

  return (
    <div className="linkedin-url-input">
      <div className="url-input-wrapper">
        <div className="input-with-icon">
          <Link2 className="input-icon" size={18} />
          <input
            type="text"
            className={`url-input ${error ? 'error' : ''}`}
            placeholder="https://www.linkedin.com/jobs/view/123456789/"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={isLoading}
            aria-label="LinkedIn job URL"
            aria-invalid={error ? "true" : "false"}
          />
        </div>

        <button
          className={`btn-primary ${isLoading ? 'loading' : ''}`}
          onClick={handleFetch}
          disabled={!url.trim() || isLoading}
          aria-label={isLoading ? 'Fetching job description' : 'Fetch job description'}
        >
          {isLoading ? (
            <>
              <Loader className="spin" size={18} />
              <span>Fetching...</span>
            </>
          ) : (
            <span>Fetch Job Description</span>
          )}
        </button>
      </div>

      {error && (
        <div className="error-banner" role="alert">
          <div className="error-content">
            <AlertCircle size={20} className="error-icon" />
            <div>
              <strong>{error.message}</strong>
              {error.details && <p className="error-details">{error.details}</p>}
            </div>
          </div>

          <div className="error-actions">
            <button className="btn-secondary btn-sm" onClick={handleRetry}>
              <RefreshCcw size={16} />
              Try Again
            </button>
            <button className="btn-text btn-sm" onClick={handleSwitchToManual}>
              <FileText size={16} />
              Use Manual Input Instead
            </button>
          </div>
        </div>
      )}

      <div className="url-help-text">
        <p>
          <strong>How to get the LinkedIn URL:</strong>
        </p>
        <ol>
          <li>Open the job posting on LinkedIn</li>
          <li>Copy the URL from your browser's address bar</li>
          <li>Paste it above and click "Fetch Job Description"</li>
        </ol>
      </div>
    </div>
  );
}
