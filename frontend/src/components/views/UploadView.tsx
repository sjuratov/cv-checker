/**
 * Upload View - Main upload interface
 */

import { CVUpload } from '../upload/CVUpload';
import { JobDescriptionInput } from '../upload/JobDescriptionInput';
import { AnalyzeButton } from '../upload/AnalyzeButton';
import { ConnectionStatus } from '../common/ConnectionStatus';
import { Clock } from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';

export function UploadView() {
  const { history, setCurrentView } = useAppStore();

  return (
    <div className="upload-view">
      <header className="app-header">
        <div className="header-content">
          <h1 className="app-title">CV Checker</h1>
          <p className="app-subtitle">
            AI-powered CV analysis and job matching
          </p>
        </div>
        {history.length > 0 && (
          <button
            className="btn btn-secondary"
            onClick={() => setCurrentView('history')}
          >
            <Clock size={18} />
            History ({history.length})
          </button>
        )}
      </header>

      {/* Backend Connection Status */}
      <ConnectionStatus />

      <div className="upload-grid">
        <div className="upload-column">
          <CVUpload />
        </div>

        <div className="upload-column">
          <JobDescriptionInput />
        </div>
      </div>

      <AnalyzeButton />
    </div>
  );
}
