/**
 * Subscores Display Component
 */

import { getScoreColor } from '../../utils/scoring';

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
          const colors = getScoreColor(subscore.score);

          return (
            <div key={subscore.label} className="subscore-item">
              <div className="subscore-header">
                <span className="subscore-icon">{subscore.icon}</span>
                <span className="subscore-label">{subscore.label}</span>
                <span className="subscore-value" style={{ color: colors.text }}>
                  {Math.round(subscore.score)}
                </span>
              </div>
              <div className="subscore-bar">
                <div
                  className="subscore-fill"
                  style={{
                    width: `${subscore.score}%`,
                    backgroundColor: colors.border,
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
