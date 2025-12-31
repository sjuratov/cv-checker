/**
 * Analysis Trigger Button Component
 */

import { Sparkles, Loader2 } from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';
import { api } from '../../lib/api';
import { validateCVContent, validateJobDescription } from '../../utils/validation';

export function AnalyzeButton() {
  const {
    currentCV,
    currentJob,
    analysis,
    startAnalysis,
    completeAnalysis,
    failAnalysis,
  } = useAppStore();

  const canAnalyze =
    currentCV.content &&
    currentJob.description.length >= 50 &&
    !analysis.isLoading;

  const handleAnalyze = async () => {
    if (!currentCV.content || !currentJob.description) return;

    // Final validation
    const cvValidation = validateCVContent(currentCV.content);
    const jobValidation = validateJobDescription(currentJob.description);

    if (!cvValidation.valid) {
      failAnalysis(cvValidation.error!);
      return;
    }

    if (!jobValidation.valid) {
      failAnalysis(jobValidation.error!);
      return;
    }

    // Start analysis
    startAnalysis();

    try {
      const result = await api.analyze({
        cv_markdown: currentCV.content,
        job_description: currentJob.description,
      });

      completeAnalysis(result);
    } catch (error) {
      const errorMessage =
        error instanceof Error ? error.message : 'Analysis failed. Please try again.';
      failAnalysis(errorMessage);
    }
  };

  return (
    <div className="analyze-button-container">
      <button
        className="btn btn-analyze"
        onClick={handleAnalyze}
        disabled={!canAnalyze}
      >
        {analysis.isLoading ? (
          <>
            <Loader2 className="icon spin" />
            Analyzing...
          </>
        ) : (
          <>
            <Sparkles className="icon" />
            Analyze Match
          </>
        )}
      </button>

      <div className="prerequisites">
        <div className={`prerequisite ${currentCV.content ? 'complete' : ''}`}>
          {currentCV.content ? '✓' : '○'} CV uploaded
        </div>
        <div
          className={`prerequisite ${
            currentJob.description.length >= 50 ? 'complete' : ''
          }`}
        >
          {currentJob.description.length >= 50 ? '✓' : '○'} Job description provided
        </div>
      </div>

      {analysis.isLoading && (
        <div className="loading-status">
          <p className="loading-text">
            Our AI is comparing your CV against the job description.
            <br />
            This usually takes 20-30 seconds.
          </p>
        </div>
      )}

      {analysis.error && (
        <div className="error-message large">
          <strong>⚠️ Analysis Failed</strong>
          <p>{analysis.error}</p>
          <button className="btn btn-secondary" onClick={handleAnalyze}>
            Retry Analysis
          </button>
        </div>
      )}
    </div>
  );
}
