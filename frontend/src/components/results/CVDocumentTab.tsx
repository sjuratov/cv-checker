/**
 * CV Document Tab Component
 * Displays CV in rendered Markdown format
 */

import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeSanitize from 'rehype-sanitize';
import { FileText } from 'lucide-react';

interface CVDocumentTabProps {
  cvMarkdown: string;
}

export function CVDocumentTab({ cvMarkdown }: CVDocumentTabProps) {
  if (!cvMarkdown || cvMarkdown.trim().length === 0) {
    return (
      <div className="tab-empty-state">
        <FileText size={48} className="empty-icon" />
        <h3>No CV Available</h3>
        <p>CV content was not provided with this analysis.</p>
      </div>
    );
  }

  return (
    <div className="tab-content-document">
      <div className="document-header">
        <FileText size={20} />
        <h3>Your CV Document</h3>
      </div>
      <div className="markdown-content cv-document">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          rehypePlugins={[rehypeSanitize]}
        >
          {cvMarkdown}
        </ReactMarkdown>
      </div>
    </div>
  );
}
