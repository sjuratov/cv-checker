"""
Unit tests for LinkedIn URL validator.
"""

import pytest

from app.utils.linkedin_validator import is_valid_linkedin_job_url, normalize_linkedin_url


class TestIsValidLinkedInJobURL:
    """Test cases for LinkedIn URL validation."""
    
    def test_valid_url_with_www(self):
        """Test valid LinkedIn URL with www."""
        url = "https://www.linkedin.com/jobs/view/123456789/"
        assert is_valid_linkedin_job_url(url) is True
    
    def test_valid_url_without_www(self):
        """Test valid LinkedIn URL without www."""
        url = "https://linkedin.com/jobs/view/123456789/"
        assert is_valid_linkedin_job_url(url) is True
    
    def test_valid_url_with_query_params(self):
        """Test valid LinkedIn URL with query parameters."""
        url = "https://www.linkedin.com/jobs/view/123456789/?refId=abc123"
        assert is_valid_linkedin_job_url(url) is True
    
    def test_valid_url_collections(self):
        """Test valid LinkedIn collections URL."""
        url = "https://www.linkedin.com/jobs/collections/recommended/123456789/"
        assert is_valid_linkedin_job_url(url) is True
    
    def test_valid_url_without_trailing_slash(self):
        """Test valid LinkedIn URL without trailing slash."""
        url = "https://www.linkedin.com/jobs/view/123456789"
        assert is_valid_linkedin_job_url(url) is True
    
    def test_invalid_url_wrong_domain(self):
        """Test invalid URL with wrong domain."""
        url = "https://google.com/jobs/view/123456789/"
        assert is_valid_linkedin_job_url(url) is False
    
    def test_invalid_url_profile_page(self):
        """Test invalid LinkedIn profile URL."""
        url = "https://www.linkedin.com/in/johndoe/"
        assert is_valid_linkedin_job_url(url) is False
    
    def test_invalid_url_company_page(self):
        """Test invalid LinkedIn company URL."""
        url = "https://www.linkedin.com/company/microsoft/"
        assert is_valid_linkedin_job_url(url) is False
    
    def test_invalid_url_empty_string(self):
        """Test invalid empty string."""
        assert is_valid_linkedin_job_url("") is False
    
    def test_invalid_url_none(self):
        """Test invalid None value."""
        assert is_valid_linkedin_job_url(None) is False
    
    def test_invalid_url_not_string(self):
        """Test invalid non-string value."""
        assert is_valid_linkedin_job_url(123) is False
    
    def test_invalid_url_whitespace(self):
        """Test URL with only whitespace."""
        assert is_valid_linkedin_job_url("   ") is False


class TestNormalizeLinkedInURL:
    """Test cases for LinkedIn URL normalization."""
    
    def test_normalize_url_with_query_params(self):
        """Test normalization removes query parameters."""
        url = "https://www.linkedin.com/jobs/view/123456789/?refId=abc&utm_source=test"
        expected = "https://www.linkedin.com/jobs/view/123456789"
        assert normalize_linkedin_url(url) == expected
    
    def test_normalize_url_with_fragment(self):
        """Test normalization removes fragment identifier."""
        url = "https://www.linkedin.com/jobs/view/123456789/#section"
        expected = "https://www.linkedin.com/jobs/view/123456789"
        assert normalize_linkedin_url(url) == expected
    
    def test_normalize_url_with_trailing_slash(self):
        """Test normalization removes trailing slash."""
        url = "https://www.linkedin.com/jobs/view/123456789/"
        expected = "https://www.linkedin.com/jobs/view/123456789"
        assert normalize_linkedin_url(url) == expected
    
    def test_normalize_url_already_normalized(self):
        """Test normalization of already normalized URL."""
        url = "https://www.linkedin.com/jobs/view/123456789"
        assert normalize_linkedin_url(url) == url
    
    def test_normalize_url_with_whitespace(self):
        """Test normalization trims whitespace."""
        url = "  https://www.linkedin.com/jobs/view/123456789/  "
        expected = "https://www.linkedin.com/jobs/view/123456789"
        assert normalize_linkedin_url(url) == expected
    
    def test_normalize_url_empty_string_raises_error(self):
        """Test normalization raises error for empty string."""
        with pytest.raises(ValueError, match="URL must be a non-empty string"):
            normalize_linkedin_url("")
    
    def test_normalize_url_none_raises_error(self):
        """Test normalization raises error for None."""
        with pytest.raises(ValueError, match="URL must be a non-empty string"):
            normalize_linkedin_url(None)
    
    def test_normalize_url_invalid_format_raises_error(self):
        """Test normalization handles invalid URL format."""
        # This should not raise an error, just return normalized version
        url = "not-a-valid-url"
        result = normalize_linkedin_url(url)
        assert result == "not-a-valid-url"
