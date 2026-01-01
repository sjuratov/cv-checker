/**
 * Backend Connection Status Component
 * Tests connectivity to backend API and displays status
 */

import { useEffect, useState } from 'react';
import { CheckCircle, XCircle, Loader2, AlertCircle } from 'lucide-react';
import { AnalysisService } from '../../services/analysisService';

export function ConnectionStatus() {
  const [status, setStatus] = useState<'checking' | 'connected' | 'disconnected' | 'error'>('checking');
  const [message, setMessage] = useState<string>('Checking backend connection...');

  useEffect(() => {
    checkConnection();
  }, []);

  const checkConnection = async () => {
    setStatus('checking');
    setMessage('Connecting to backend API...');

    try {
      const isConnected = await AnalysisService.testConnection();
      
      if (isConnected) {
        setStatus('connected');
        setMessage('Backend connected successfully');
      } else {
        setStatus('error');
        setMessage('Backend is not responding correctly');
      }
    } catch (error) {
      setStatus('disconnected');
      const apiUrl = AnalysisService.getAPIBaseURL();
      setMessage(`Cannot connect to backend at ${apiUrl}`);
    }
  };

  const getIcon = () => {
    switch (status) {
      case 'checking':
        return <Loader2 className="icon spin" size={16} />;
      case 'connected':
        return <CheckCircle className="icon text-green" size={16} />;
      case 'error':
        return <AlertCircle className="icon text-yellow" size={16} />;
      case 'disconnected':
        return <XCircle className="icon text-red" size={16} />;
    }
  };

  const getClassName = () => {
    return `connection-status status-${status}`;
  };

  return (
    <div className={getClassName()}>
      {getIcon()}
      <span className="status-message">{message}</span>
      {status !== 'checking' && status !== 'connected' && (
        <button className="btn-text btn-sm" onClick={checkConnection}>
          Retry
        </button>
      )}
    </div>
  );
}
