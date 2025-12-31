/**
 * Input validation utilities
 */

export interface FileValidationResult {
  valid: boolean;
  error?: string;
}

export interface TextValidationResult {
  valid: boolean;
  error?: string;
}

/**
 * Validate CV file upload
 */
export function validateCVFile(file: File): FileValidationResult {
  // Check file extension
  if (!file.name.toLowerCase().endsWith('.md')) {
    return {
      valid: false,
      error: 'Invalid file format. Please upload a Markdown (.md) file.',
    };
  }

  // Check file size (2MB max)
  const maxSize = 2 * 1024 * 1024; // 2MB in bytes
  if (file.size > maxSize) {
    const sizeMB = (file.size / (1024 * 1024)).toFixed(2);
    return {
      valid: false,
      error: `File too large. Maximum size is 2MB. Your file is ${sizeMB}MB.`,
    };
  }

  return { valid: true };
}

/**
 * Validate CV content
 */
export function validateCVContent(content: string): TextValidationResult {
  const trimmed = content.trim();

  if (trimmed.length === 0) {
    return {
      valid: false,
      error: 'CV content cannot be empty.',
    };
  }

  if (trimmed.length < 100) {
    return {
      valid: false,
      error: 'CV content is too short. Please provide at least 100 characters.',
    };
  }

  if (trimmed.length > 50000) {
    return {
      valid: false,
      error: 'CV content is too long. Maximum length is 50,000 characters.',
    };
  }

  return { valid: true };
}

/**
 * Validate job description
 */
export function validateJobDescription(description: string): TextValidationResult {
  const trimmed = description.trim();

  if (trimmed.length === 0) {
    return {
      valid: false,
      error: 'Job description cannot be empty.',
    };
  }

  if (trimmed.length < 50) {
    return {
      valid: false,
      error: 'Job description is too short. Please provide at least 50 characters.',
    };
  }

  if (trimmed.length > 10000) {
    return {
      valid: false,
      error: 'Job description is too long. Maximum length is 10,000 characters.',
    };
  }

  return { valid: true };
}

/**
 * Sanitize text content
 */
export function sanitizeText(text: string): string {
  // Trim whitespace
  let sanitized = text.trim();

  // Normalize line endings
  sanitized = sanitized.replace(/\r\n/g, '\n');

  // Remove null bytes
  sanitized = sanitized.replace(/\0/g, '');

  // Remove excessive newlines (more than 2 consecutive)
  sanitized = sanitized.replace(/\n{3,}/g, '\n\n');

  return sanitized;
}
