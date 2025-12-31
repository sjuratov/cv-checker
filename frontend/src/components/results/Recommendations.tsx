/**
 * Recommendations Display Component
 */

import { useState } from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';

interface RecommendationsProps {
  recommendations: string[];
}

export function Recommendations({ recommendations }: RecommendationsProps) {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  const toggleExpand = (index: number) => {
    setExpandedIndex(expandedIndex === index ? null : index);
  };

  // Infer priority based on position (first 3 = high, next 3 = medium, rest = low)
  const getPriority = (index: number): 'high' | 'medium' | 'low' => {
    if (index < 3) return 'high';
    if (index < 6) return 'medium';
    return 'low';
  };

  return (
    <div className="recommendations">
      <h3 className="subsection-title">
        Recommendations ({recommendations.length})
      </h3>

      <div className="recommendations-list">
        {recommendations.map((recommendation, index) => {
          const priority = getPriority(index);
          const isExpanded = expandedIndex === index;

          return (
            <div key={index} className="recommendation-card">
              <div
                className="recommendation-header"
                onClick={() => toggleExpand(index)}
              >
                <div className="recommendation-title">
                  <span
                    className={`priority-badge ${priority}`}
                  >
                    {priority.toUpperCase()}
                  </span>
                  <span className="recommendation-text">{recommendation}</span>
                </div>
                <button className="expand-button">
                  {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                </button>
              </div>

              {isExpanded && (
                <div className="recommendation-details">
                  <p className="recommendation-full">{recommendation}</p>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
