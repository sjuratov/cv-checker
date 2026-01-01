/**
 * CV Checker Application
 * Main App Component
 */

import { useEffect } from 'react';
import { useAppStore } from './store/useAppStore';
import { UploadView } from './components/views/UploadView';
import { ResultsDisplay } from './components/results/ResultsDisplay';
import { AnalysisHistory } from './components/history/AnalysisHistory';
import './App.css';

function App() {
  const { currentView, analysis, setCurrentView } = useAppStore();

  // Ensure we always have a valid currentView on mount
  useEffect(() => {
    if (!currentView || !['upload', 'results', 'history'].includes(currentView)) {
      setCurrentView('upload');
    }
  }, [currentView, setCurrentView]);

  return (
    <div className="app">
      <div className="app-container">
        {currentView === 'upload' && <UploadView />}
        {currentView === 'results' && analysis.result && (
          <ResultsDisplay result={analysis.result} />
        )}
        {currentView === 'history' && <AnalysisHistory />}
      </div>

      <footer className="app-footer">
        <p>
          CV Checker v1.0 • Powered by Azure OpenAI GPT-4o •{' '}
          <a
            href="https://github.com/microsoft/cv-checker"
            target="_blank"
            rel="noopener noreferrer"
          >
            GitHub
          </a>
        </p>
      </footer>
    </div>
  );
}

export default App;
