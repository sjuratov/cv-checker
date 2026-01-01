/**
 * Job Description Input Component
 * 
 * Supports both manual text input and LinkedIn URL fetching.
 */

import { Briefcase, X } from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';
import { validateJobDescription } from '../../utils/validation';
import { useState } from 'react';
import { JobInputModeToggle } from './JobInputModeToggle';
import { LinkedInURLInput } from './LinkedInURLInput';

export function JobDescriptionInput() {
  const { currentJob, updateJobDescription, clearJob, jobInputMode } = useAppStore();
  const [error, setError] = useState<string | null>(null);

  const maxLength = 10000;
  const currentLength = currentJob.description.length;

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    updateJobDescription(value, 'manual');

    if (value.length > 0) {
      const validation = validateJobDescription(value);
      if (!validation.valid && value.length >= 50) {
        setError(validation.error!);
      } else {
        setError(null);
      }
    } else {
      setError(null);
    }
  };

  const handleClear = () => {
    clearJob();
    setError(null);
  };

  const getCharacterCountColor = () => {
    if (currentLength === 0) return '';
    if (currentLength < 50) return 'text-red';
    if (currentLength > maxLength * 0.9) return 'text-yellow';
    return 'text-green';
  };

  return (
    <div className="job-input-container">
      <h2 className="section-title">
        <Briefcase className="icon" />
        Job Description
      </h2>

      {/* Mode Toggle */}
      <JobInputModeToggle />

      {/* Conditional Rendering based on input mode */}
      {jobInputMode === 'linkedin_url' ? (
        <LinkedInURLInput />
      ) : (
        <div className="textarea-wrapper">
          <textarea
            className={`job-textarea ${error ? 'error' : ''}`}
            placeholder="Paste the job description here...

Example:
Senior Python Developer needed with 5+ years of experience building scalable REST APIs using FastAPI, deploying to cloud platforms (Azure/AWS), and working with SQL databases."
            value={currentJob.description}
            onChange={handleChange}
            rows={12}
          />

          <div className="textarea-footer">
            <span className={`char-count ${getCharacterCountColor()}`}>
              {currentLength.toLocaleString()} / {maxLength.toLocaleString()}
              {currentLength < 50 && currentLength > 0 && (
                <span className="text-red"> (minimum 50)</span>
              )}
            </span>

            {currentJob.description && (
              <button className="btn-text" onClick={handleClear}>
                <X size={16} />
                Clear
              </button>
            )}
          </div>

          {error && (
            <div className="error-message">
              <span>⚠️ {error}</span>
            </div>
          )}
        </div>
      )}

      {/* Show fetched content preview if from LinkedIn */}
      {currentJob.sourceType === 'linkedin_url' && currentJob.description && (
        <div className="fetched-content-preview">
          <div className="preview-header">
            <strong>✅ Job description fetched from LinkedIn</strong>
            {currentJob.sourceUrl && (
              <a
                href={currentJob.sourceUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="source-link"
              >
                View original
              </a>
            )}
          </div>
          <div className="preview-stats">
            <span>{currentJob.description.length.toLocaleString()} characters</span>
            <button className="btn-text btn-sm" onClick={handleClear}>
              <X size={14} />
              Clear
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
