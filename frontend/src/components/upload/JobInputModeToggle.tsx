/**
 * Job Input Mode Toggle Component
 * 
 * Allows users to switch between LinkedIn URL and Manual input modes.
 */

import { Link2, FileText } from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';

export function JobInputModeToggle() {
  const { jobInputMode, setJobInputMode } = useAppStore();

  return (
    <div className="job-mode-toggle" role="radiogroup" aria-label="Job input mode">
      <button
        className={`toggle-btn ${jobInputMode === 'linkedin_url' ? 'active' : ''}`}
        onClick={() => setJobInputMode('linkedin_url')}
        role="radio"
        aria-checked={jobInputMode === 'linkedin_url' ? 'true' : 'false'}
        aria-label="LinkedIn URL mode"
      >
        <Link2 size={18} />
        <span>LinkedIn URL</span>
      </button>

      <button
        className={`toggle-btn ${jobInputMode === 'manual' ? 'active' : ''}`}
        onClick={() => setJobInputMode('manual')}
        role="radio"
        aria-checked={jobInputMode === 'manual' ? 'true' : 'false'}
        aria-label="Manual input mode"
      >
        <FileText size={18} />
        <span>Manual Input</span>
      </button>
    </div>
  );
}
