/**
 * Strengths and Gaps Component
 */

import { TrendingUp, AlertTriangle } from 'lucide-react';

interface StrengthsGapsProps {
  strengths: string[];
  gaps: string[];
}

export function StrengthsGaps({ strengths, gaps }: StrengthsGapsProps) {
  return (
    <div className="strengths-gaps">
      <div className="strengths-section">
        <h3 className="subsection-title success">
          <TrendingUp className="icon" />
          Top Strengths
        </h3>
        <ul className="list">
          {strengths.slice(0, 3).map((strength, index) => (
            <li key={index} className="list-item success">
              <span className="bullet">✓</span>
              {strength}
            </li>
          ))}
        </ul>
      </div>

      <div className="gaps-section">
        <h3 className="subsection-title warning">
          <AlertTriangle className="icon" />
          Areas to Improve
        </h3>
        <ul className="list">
          {gaps.slice(0, 3).map((gap, index) => (
            <li key={index} className="list-item warning">
              <span className="bullet">⚠</span>
              {gap}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
