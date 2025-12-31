/**
 * Analysis History Component
 */

import { ArrowLeft, FileText, Calendar, TrendingUp } from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';
import { formatDate, getScoreLabel } from '../../utils/scoring';

export function AnalysisHistory() {
  const { history, analysis, setCurrentView, completeAnalysis } = useAppStore();

  const handleViewDetails = (historyItem: typeof history[0]) => {
    completeAnalysis(historyItem.result);
    setCurrentView('results');
  };

  const handleBack = () => {
    setCurrentView(analysis.result ? 'results' : 'upload');
  };

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
