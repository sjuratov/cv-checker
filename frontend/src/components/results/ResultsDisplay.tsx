/**
 * Complete Analysis Results Display with Tabbed Interface
 */

import { ArrowLeft } from 'lucide-react';
import type { AnalyzeResponse } from '../../types/api';
import { useAppStore } from '../../store/useAppStore';
import { TabNavigation } from './TabNavigation';
import { CVDocumentTab } from './CVDocumentTab';
import { JobDescriptionTab } from './JobDescriptionTab';
import { AnalysisResultsTab } from './AnalysisResultsTab';

interface ResultsDisplayProps {
  result: AnalyzeResponse;
}

export function ResultsDisplay({ result }: ResultsDisplayProps) {
  const { setCurrentView, clearAnalysis, activeTab, setActiveTab } = useAppStore();

  const tabs = [
    { id: 'cv-document', label: 'CV Document' },
    { id: 'job-description', label: 'Job Description' },
    { id: 'analysis-results', label: 'Analysis Results' },
  ];

  const handleNewAnalysis = () => {
    clearAnalysis();
    setCurrentView('upload');
    // Reset to analysis results tab for next time
    setActiveTab('analysis-results');
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

      {/* Tab Navigation */}
      <TabNavigation
        tabs={tabs}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />

      {/* Tab Content */}
      <div className="tab-panels">
        {/* CV Document Tab */}
        <div
          role="tabpanel"
          id="tabpanel-cv-document"
          aria-labelledby="tab-cv-document"
          hidden={activeTab !== 'cv-document'}
          className="tab-panel"
        >
          {activeTab === 'cv-document' && (
            <CVDocumentTab cvMarkdown={result.cv_markdown} />
          )}
        </div>

        {/* Job Description Tab */}
        <div
          role="tabpanel"
          id="tabpanel-job-description"
          aria-labelledby="tab-job-description"
          hidden={activeTab !== 'job-description'}
          className="tab-panel"
        >
          {activeTab === 'job-description' && (
            <JobDescriptionTab
              jobDescription={result.job_description}
              sourceType={result.source_type}
              sourceUrl={result.source_url}
            />
          )}
        </div>

        {/* Analysis Results Tab */}
        <div
          role="tabpanel"
          id="tabpanel-analysis-results"
          aria-labelledby="tab-analysis-results"
          hidden={activeTab !== 'analysis-results'}
          className="tab-panel"
        >
          {activeTab === 'analysis-results' && (
            <AnalysisResultsTab result={result} />
          )}
        </div>
      </div>

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
  );
}
