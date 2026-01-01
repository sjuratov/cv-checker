/**
 * Job Description Tab Component
 * Displays job description in rendered format with source indicator
 */

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeSanitize from 'rehype-sanitize';
import { Briefcase, ExternalLink } from 'lucide-react';

interface JobDescriptionTabProps {
  jobDescription: string;
  sourceType: string;
  sourceUrl?: string | null;
}

export function JobDescriptionTab({
  jobDescription,
  sourceType,
  sourceUrl,
}: JobDescriptionTabProps) {
  if (!jobDescription || jobDescription.trim().length === 0) {
    return (
      <div className="tab-empty-state">
        <Briefcase size={48} className="empty-icon" />
        <h3>No Job Description Available</h3>
        <p>Job description was not provided with this analysis.</p>
      </div>
    );
  }

  return (
    <div className="tab-content-document">
      <div className="document-header">
        <Briefcase size={20} />
        <h3>Job Description</h3>
      </div>

      {/* Source Indicator */}
      <div className="job-source-indicator">
        {sourceType === 'linkedin_url' && sourceUrl ? (
          <a
            href={sourceUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="source-link"
          >
            From LinkedIn <ExternalLink size={14} />
          </a>
        ) : (
          <span className="source-text">Manually entered</span>
        )}
      </div>

      <div className="markdown-content job-description">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          rehypePlugins={[rehypeSanitize]}
        >
          {jobDescription}
        </ReactMarkdown>
      </div>
    </div>
  );
}
