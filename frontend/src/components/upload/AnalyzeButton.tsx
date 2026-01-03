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
    updateProgress,
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
      // Call streaming analysis service
      const result = await AnalysisService.analyzeWithProgress(
        {
          cvMarkdown: currentCV.content,
          cvFilename: currentCV.filename || 'resume.pdf',
          jobDescription: currentJob.description,
          sourceType: currentJob.sourceType,
          sourceUrl: currentJob.sourceUrl,
        },
        (step, totalSteps, message) => {
          // Update progress in store
          updateProgress(step, totalSteps, message);
        }
      );

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
          <div className="progress-container">
            {analysis.progress && (
              <>
                {/* Dynamic width based on progress - inline style required */}
                <div className="progress-bar-wrapper">
                  <div 
                    className="progress-bar-fill"
                    style={{ width: `${(analysis.progress.currentStep / analysis.progress.totalSteps) * 100}%` }}
                  />
                </div>
                <div className="progress-steps">
                  {[1, 2, 3, 4].map((step) => {
                    const stepMessages = [
                      'Parsing job description',
                      'Parsing CV',
                      'Analyzing compatibility',
                      'Generating recommendations',
                    ];
                    
                    const isCompleted = analysis.progress && step < analysis.progress.currentStep;
                    const isCurrent = analysis.progress && step === analysis.progress.currentStep;

                    return (
                      <div
                        key={step}
                        className={`progress-step ${
                          isCompleted ? 'completed' : isCurrent ? 'current' : 'pending'
                        }`}
                      >
                        <span className="step-icon">
                          {isCompleted ? '✓' : isCurrent ? '⏳' : '○'}
                        </span>
                        <span className="step-text">
                          Step {step}/4: {stepMessages[step - 1]}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </>
            )}
            {!analysis.progress && (
              <p className="loading-text">
                🤖 Starting analysis...
              </p>
            )}
          </div>
          <p className="loading-subtext">
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
