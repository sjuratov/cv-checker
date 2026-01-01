/**
 * Analysis Trigger Button Component
 * Integrates with backend API via AnalysisService
 */

import { Sparkles, Loader2 } from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';
import { AnalysisService } from '../../services/analysisService';

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

    // Start analysis in store
    startAnalysis();

    try {
      // Call analysis service
      const result = await AnalysisService.analyze({
        cvMarkdown: currentCV.content,
        jobDescription: currentJob.description,
      });

      if (result.success && result.data) {
        // Analysis succeeded
        completeAnalysis(result.data);
      } else {
        // Analysis failed with validation or API error
        failAnalysis(result.error || 'Analysis failed. Please try again.');
      }
    } catch (error) {
      // Unexpected error
      const errorMessage =
        error instanceof Error
          ? error.message
          : 'An unexpected error occurred. Please try again.';
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
            🤖 Our AI agents are analyzing your CV against the job description...
            <br />
            <small>This typically takes 20-40 seconds as multiple AI agents work together.</small>
          </p>
        </div>
      )}

      {analysis.error && (
        <div className="error-message large">
          <strong>⚠️ Analysis Failed</strong>
          <p>{analysis.error}</p>
          <button className="btn btn-secondary" onClick={handleAnalyze} disabled={!canAnalyze}>
            Retry Analysis
          </button>
        </div>
      )}
    </div>
  );
}
