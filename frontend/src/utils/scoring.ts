/**
 * Scoring and formatting utilities
 */

export type ScoreLevel = 'poor' | 'fair' | 'good' | 'excellent';

export interface ScoreColor {
  bg: string;
  text: string;
  border: string;
}

/**
 * Get score level based on numeric score
 */
export function getScoreLevel(score: number): ScoreLevel {
  if (score < 50) return 'poor';
  if (score < 75) return 'fair';
  if (score < 90) return 'good';
  return 'excellent';
}

/**
 * Get score label
 */
export function getScoreLabel(score: number): string {
  const level = getScoreLevel(score);
  switch (level) {
    case 'poor':
      return 'Poor Match';
    case 'fair':
      return 'Fair Match';
    case 'good':
      return 'Good Match';
    case 'excellent':
      return 'Excellent Match';
  }
}

/**
 * Get color scheme for score
 */
export function getScoreColor(score: number): ScoreColor {
  const level = getScoreLevel(score);
  switch (level) {
    case 'poor':
      return {
        bg: '#fee2e2',
        text: '#991b1b',
        border: '#fca5a5',
      };
    case 'fair':
      return {
        bg: '#fef3c7',
        text: '#92400e',
        border: '#fcd34d',
      };
    case 'good':
      return {
        bg: '#d1fae5',
        text: '#065f46',
        border: '#6ee7b7',
      };
    case 'excellent':
      return {
        bg: '#dbeafe',
        text: '#1e40af',
        border: '#93c5fd',
      };
  }
}

/**
 * Format date for display
 */
export function formatDate(isoString: string): string {
  const date = new Date(isoString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Format file size
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}
