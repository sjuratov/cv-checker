"""
LinkedIn URL validation utilities.

Provides functions to validate and normalize LinkedIn job posting URLs.
"""

import re
from urllib.parse import urlparse


# LinkedIn job URL patterns
LINKEDIN_JOB_PATTERNS = [
    r"^https?://(?:www\.)?linkedin\.com/jobs/view/\d+/?",
    r"^https?://(?:www\.)?linkedin\.com/jobs/collections/[^/]+/\d+/?",
]


def is_valid_linkedin_job_url(url: str) -> bool:
    """
    Validate LinkedIn job posting URL format.
    
    Accepts URLs matching patterns:
    - https://linkedin.com/jobs/view/123456789/
    - https://www.linkedin.com/jobs/view/123456789/
    - https://linkedin.com/jobs/collections/recommended/123456789/
    
    Args:
        url: URL string to validate
        
    Returns:
        True if URL matches LinkedIn job pattern, False otherwise
    """
    if not url or not isinstance(url, str):
        return False
    
    # Remove whitespace
    url = url.strip()
    
    # Check domain
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    
    if parsed.netloc not in ["linkedin.com", "www.linkedin.com"]:
        return False
    
    # Check path pattern
    return any(re.match(pattern, url) for pattern in LINKEDIN_JOB_PATTERNS)


def normalize_linkedin_url(url: str) -> str:
    """
    Remove query parameters and normalize LinkedIn URL.
    
    Normalizes URL by:
    - Removing query parameters
    - Removing fragment identifiers
    - Ensuring consistent format
    
    Args:
        url: LinkedIn URL to normalize
        
    Returns:
        Normalized URL string
        
    Raises:
        ValueError: If URL is invalid
    """
    if not url or not isinstance(url, str):
        raise ValueError("URL must be a non-empty string")
    
    url = url.strip()
    
    try:
        parsed = urlparse(url)
    except ValueError as e:
        raise ValueError(f"Invalid URL format: {e}")
    
    # Reconstruct URL without query params and fragments
    normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    
    # Remove trailing slash if present
    if normalized.endswith("/"):
        normalized = normalized[:-1]
    
    return normalized
