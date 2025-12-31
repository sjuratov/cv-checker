/**
 * Score Display Component with Gauge
 */

import { getScoreLabel, getScoreColor } from '../../utils/scoring';

interface ScoreGaugeProps {
  score: number;
}

export function ScoreGauge({ score }: ScoreGaugeProps) {
  const label = getScoreLabel(score);
  const colors = getScoreColor(score);

  // Calculate arc path for the gauge
  const radius = 80;
  const strokeWidth = 12;
  const circumference = Math.PI * radius;
  const scoreArc = (score / 100) * circumference;

  return (
    <div className="score-gauge">
      <svg width="200" height="120" viewBox="0 0 200 120">
        {/* Background arc */}
        <path
          d="M 20 100 A 80 80 0 0 1 180 100"
          fill="none"
          stroke="#e5e7eb"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />
        {/* Score arc */}
        <path
          d="M 20 100 A 80 80 0 0 1 180 100"
          fill="none"
          stroke={colors.border}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          strokeDasharray={`${scoreArc} ${circumference}`}
        />
        {/* Score text */}
        <text
          x="100"
          y="80"
          textAnchor="middle"
          fontSize="36"
          fontWeight="bold"
          fill={colors.text}
        >
          {Math.round(score)}
        </text>
      </svg>

      <div className={`score-label score-label-${label.toLowerCase()}`}>
        {label}
      </div>
    </div>
  );
}
