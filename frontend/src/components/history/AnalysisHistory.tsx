/**
 * Analysis History Component
 */

import { useEffect, useState } from 'react';
import { ArrowLeft, FileText, Calendar, TrendingUp, Loader2 } from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';
import { formatDate, getScoreLabel } from '../../utils/scoring';
import { api } from '../../lib/api';
import type { AnalysisHistory } from '../../types/api';

export function AnalysisHistory() {
  const { analysis, setCurrentView, completeAnalysis } = useAppStore();
  const [history, setHistory] = useState<AnalysisHistory[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch history from backend on mount
  useEffect(() => {
    const fetchHistory = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await api.getHistory('anonymous', 20);
        setHistory(response.history);
      } catch (err) {
        console.error('Failed to fetch history:', err);
        setError(err instanceof Error ? err.message : 'Failed to load history');
      } finally {
        setIsLoading(false);
      }
    };

    fetchHistory();
  }, []);

  const handleViewDetails = (historyItem: AnalysisHistory) => {
    completeAnalysis(historyItem.result);
    setCurrentView('results');
  };

  const handleBack = () => {
    setCurrentView(analysis.result ? 'results' : 'upload');
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="history-container">
        <div className="history-header">
          <button className="btn-back" onClick={handleBack}>
            <ArrowLeft size={20} />
            Back
          </button>
          <h1 className="history-title">Analysis History</h1>
        </div>

        <div className="empty-state">
          <Loader2 size={64} className="empty-icon animate-spin" />
          <h2>Loading history...</h2>
          <p>Fetching your analysis history from the database.</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="history-container">
        <div className="history-header">
          <button className="btn-back" onClick={handleBack}>
            <ArrowLeft size={20} />
            Back
          </button>
          <h1 className="history-title">Analysis History</h1>
        </div>

        <div className="empty-state">
          <TrendingUp size={64} className="empty-icon" />
          <h2>Failed to load history</h2>
          <p>{error}</p>
          <button
            className="btn btn-primary"
            onClick={() => window.location.reload()}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Empty state
  if (history.length === 0) {
    return (
      <div className="history-container">
        <div className="history-header">
          <button className="btn-back" onClick={handleBack}>
            <ArrowLeft size={20} />
            Back
          </button>
          <h1 className="history-title">Analysis History</h1>
        </div>

        <div className="empty-state">
          <TrendingUp size={64} className="empty-icon" />
          <h2>No analyses yet!</h2>
          <p>
            Upload a CV and analyze it against a job description to get started.
          </p>
          <button
            className="btn btn-primary"
            onClick={() => setCurrentView('upload')}
          >
            Start New Analysis
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="history-container">
      <div className="history-header">
        <button className="btn-back" onClick={handleBack}>
          <ArrowLeft size={20} />
          Back
        </button>
        <h1 className="history-title">Analysis History</h1>
      </div>

      <div className="history-list">
        {history.map((item) => {
          const label = getScoreLabel(item.score);

          return (
            <div key={item.id} className="history-card">
              <div className="history-card-header">
                <div className="history-meta">
                  <div className="history-date">
                    <Calendar size={16} />
                    {formatDate(item.timestamp)}
                  </div>
                  <div className="history-cv">
                    <FileText size={16} />
                    {item.cvFilename}
                    {item.jobTitle && (
                      <span className="history-job-title"> • {item.jobTitle}</span>
                    )}
                  </div>
                </div>

                <div
                  className={`history-score history-score-${label.toLowerCase()}`}
                >
                  <span className="score-number">{Math.round(item.score)}</span>
                  <span className="score-label-small">{label}</span>
                </div>
              </div>

              <div className="history-card-footer">
                <div className="history-summary">
                  <strong>Strengths:</strong> {item.result.strengths.length} •{' '}
                  <strong>Gaps:</strong> {item.result.gaps.length} •{' '}
                  <strong>Recommendations:</strong> {item.result.recommendations.length}
                </div>

                <button
                  className="btn btn-secondary small"
                  onClick={() => handleViewDetails(item)}
                >
                  View Details →
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
