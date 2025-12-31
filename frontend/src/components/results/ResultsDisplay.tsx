/**
 * Complete Analysis Results Display
 */

import { ArrowLeft } from 'lucide-react';
import type { AnalyzeResponse } from '../../types/api';
import { useAppStore } from '../../store/useAppStore';
import { ScoreGauge } from './ScoreGauge';
import { Subscores } from './Subscores';
import { StrengthsGaps } from './StrengthsGaps';
import { Recommendations } from './Recommendations';

interface ResultsDisplayProps {
  result: AnalyzeResponse;
}

export function ResultsDisplay({ result }: ResultsDisplayProps) {
  const { setCurrentView, clearAnalysis } = useAppStore();

  // Calculate subscores
  const skillScore =
    result.skill_matches.length > 0
      ? (result.skill_matches.filter((s) => s.candidate_has).length /
          result.skill_matches.length) *
        100
      : 0;

  const experienceScore =
    typeof result.experience_match.match === 'boolean'
      ? result.experience_match.match
        ? 85
        : 50
      : 75;

  const educationScore =
    typeof result.education_match.match === 'boolean'
      ? result.education_match.match
        ? 90
        : 60
      : 80;

  const handleNewAnalysis = () => {
    clearAnalysis();
    setCurrentView('upload');
  };

  return (
    <div className="results-container">
      <div className="results-header">
        <button className="btn-back" onClick={handleNewAnalysis}>
          <ArrowLeft size={20} />
          New Analysis
        </button>
        <h1 className="results-title">Analysis Results</h1>
      </div>

      <div className="results-content">
        {/* Overall Score */}
        <div className="score-section">
          <ScoreGauge score={result.overall_score} />
          <div className="score-summary">
            <h2>Overall Match Score</h2>
            <p className="summary-text">
              {result.overall_score >= 75
                ? "Your CV is a good match for this role. You have most of the required qualifications."
                : result.overall_score >= 50
                ? "Your CV shows potential for this role, but there are some gaps to address."
                : "Your CV may not be the best fit for this role. Consider the recommendations below to strengthen your application."}
            </p>
          </div>
        </div>

        {/* Subscores */}
        <Subscores
          skillMatches={skillScore}
          experienceMatch={experienceScore}
          educationMatch={educationScore}
        />

        {/* Strengths and Gaps */}
        <StrengthsGaps strengths={result.strengths} gaps={result.gaps} />

        {/* Recommendations */}
        <Recommendations recommendations={result.recommendations} />

        {/* Actions */}
        <div className="results-actions">
          <button className="btn btn-primary" onClick={handleNewAnalysis}>
            Start New Analysis
          </button>
          <button
            className="btn btn-secondary"
            onClick={() => setCurrentView('history')}
          >
            View History
          </button>
        </div>
      </div>
    </div>
  );
}
