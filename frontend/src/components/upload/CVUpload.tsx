/**
 * CV Upload Component
 */

import { Upload, FileText, X, Check } from 'lucide-react';
import { useState, useRef } from 'react';
import { useAppStore } from '../../store/useAppStore';
import { validateCVFile, validateCVContent, sanitizeText } from '../../utils/validation';

export function CVUpload() {
  const { currentCV, uploadCV, clearCV } = useAppStore();
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isReading, setIsReading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = async (file: File) => {
    setError(null);
    setIsReading(true);

    // Validate file
    const fileValidation = validateCVFile(file);
    if (!fileValidation.valid) {
      setError(fileValidation.error!);
      setIsReading(false);
      return;
    }

    try {
      // Read file content
      const content = await readFileAsText(file);
      const sanitized = sanitizeText(content);

      // Validate content
      const contentValidation = validateCVContent(sanitized);
      if (!contentValidation.valid) {
        setError(contentValidation.error!);
        setIsReading(false);
        return;
      }

      // Upload to store
      uploadCV(file.name, sanitized);
      setIsReading(false);
    } catch (err) {
      setError('Failed to read file. Please try a different file.');
      setIsReading(false);
    }
  };

  const readFileAsText = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target?.result as string);
      reader.onerror = reject;
      reader.readAsText(file, 'UTF-8');
    });
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleButtonClick = () => {
    fileInputRef.current?.click();
  };

  const handleClear = () => {
    clearCV();
    setError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="cv-upload-container">
      <h2 className="section-title">
        <FileText className="icon" />
        Upload Your CV
      </h2>

      {!currentCV.filename ? (
        <div
          className={`drop-zone ${dragActive ? 'active' : ''} ${error ? 'error' : ''}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".md"
            onChange={handleChange}
            className="visually-hidden"
            aria-label="Upload CV file in Markdown format"
          />

          <Upload className="upload-icon" size={48} />

          <p className="drop-text">
            {isReading
              ? 'Reading file...'
              : dragActive
              ? 'Drop your CV here'
              : 'Drag & drop your CV here'}
          </p>

          <p className="or-text">or</p>

          <button
            className="btn btn-primary"
            onClick={handleButtonClick}
            disabled={isReading}
          >
            Choose File
          </button>

          <p className="file-info">Accepted: Markdown (.md) • Max size: 2MB</p>

          {error && (
            <div className="error-message">
              <span>⚠️ {error}</span>
            </div>
          )}
        </div>
      ) : (
        <div className="file-success">
          <div className="success-icon">
            <Check size={24} />
          </div>
          <div className="file-details">
            <p className="filename">
              <FileText size={18} />
              {currentCV.filename}
            </p>
            <p className="file-meta">
              Uploaded {new Date(currentCV.uploadedAt!).toLocaleDateString()}
            </p>
          </div>
          <button className="btn-icon" onClick={handleClear} title="Remove CV">
            <X size={20} />
          </button>
        </div>
      )}
    </div>
  );
}
