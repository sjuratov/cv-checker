/**
 * Subscores Display Component
 */

import { getScoreLabel } from '../../utils/scoring';

interface SubscoresProps {
  skillMatches: number;
  experienceMatch: number;
  educationMatch: number;
}

export function Subscores({
  skillMatches,
  experienceMatch,
  educationMatch,
}: SubscoresProps) {
  const subscores = [
    { label: 'Skills Match', score: skillMatches, icon: '🎯' },
    { label: 'Experience Match', score: experienceMatch, icon: '💼' },
    { label: 'Education Match', score: educationMatch, icon: '🎓' },
  ];

  return (
    <div className="subscores">
      <h3 className="subsection-title">Score Breakdown</h3>

      <div className="subscores-list">
        {subscores.map((subscore) => {
          const label = getScoreLabel(subscore.score);

          return (
            <div key={subscore.label} className="subscore-item">
              <div className="subscore-header">
                <span className="subscore-icon">{subscore.icon}</span>
                <span className="subscore-label">{subscore.label}</span>
                <span className={`subscore-value subscore-value-${label.toLowerCase()}`}>
                  {Math.round(subscore.score)}
                </span>
              </div>
              <div className="subscore-bar">
                <div
                  className={`subscore-fill subscore-fill-${label.toLowerCase()}`}
                  style={{ ['--score-width' as any]: `${subscore.score}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
