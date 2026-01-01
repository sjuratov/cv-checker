"""
Unit tests for LinkedIn scraper service.

Note: These tests use mocked Playwright to avoid actual web requests.
Integration tests with real LinkedIn should be run in staging only.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from app.services.linkedin_scraper import (
    AntiBotDetected,
    ContentNotFound,
    LinkedInScraperError,
    LinkedInScraperService,
    PageLoadTimeout,
)


@pytest.fixture
async def scraper():
    """Create LinkedIn scraper instance."""
    service = LinkedInScraperService(timeout=15000)
    yield service
    await service.close()


@pytest.mark.asyncio
class TestLinkedInScraperService:
    """Test cases for LinkedInScraperService."""
    
    async def test_initialize_browser(self, scraper):
        """Test browser initialization."""
        with patch("app.services.linkedin_scraper.async_playwright") as mock_playwright:
            mock_playwright_instance = AsyncMock()
            mock_playwright.return_value.start = AsyncMock(return_value=mock_playwright_instance)
            
            mock_browser = AsyncMock()
            mock_playwright_instance.chromium.launch = AsyncMock(return_value=mock_browser)
            
            await scraper.initialize()
            
            assert scraper.browser is not None
            mock_playwright_instance.chromium.launch.assert_called_once()
    
    async def test_scrape_job_description_success(self, scraper):
        """Test successful job description scraping."""
        with patch("app.services.linkedin_scraper.async_playwright") as mock_playwright:
            # Setup mocks
            mock_playwright_instance = AsyncMock()
            mock_playwright.return_value.start = AsyncMock(return_value=mock_playwright_instance)
            
            mock_browser = AsyncMock()
            mock_page = AsyncMock()
            mock_browser.new_page = AsyncMock(return_value=mock_page)
            mock_playwright_instance.chromium.launch = AsyncMock(return_value=mock_browser)
            
            # Mock page navigation and content extraction
            mock_page.goto = AsyncMock()
            mock_page.wait_for_selector = AsyncMock()
            mock_page.evaluate = AsyncMock(return_value="This is a sample job description with more than 100 characters to meet the minimum content length requirement.")
            mock_page.query_selector = AsyncMock(return_value=None)  # No CAPTCHA
            mock_page.close = AsyncMock()
            
            scraper.browser = mock_browser
            scraper.playwright = mock_playwright_instance
            
            url = "https://www.linkedin.com/jobs/view/123456789/"
            result = await scraper.scrape_job_description(url)
            
            assert len(result) > 100
            assert "sample job description" in result
            mock_page.goto.assert_called_once()
            mock_page.close.assert_called_once()
    
    async def test_scrape_job_description_page_timeout(self, scraper):
        """Test scraping fails with page load timeout."""
        with patch("app.services.linkedin_scraper.async_playwright") as mock_playwright:
            from playwright.async_api import TimeoutError as PlaywrightTimeoutError
            
            mock_playwright_instance = AsyncMock()
            mock_playwright.return_value.start = AsyncMock(return_value=mock_playwright_instance)
            
            mock_browser = AsyncMock()
            mock_page = AsyncMock()
            mock_browser.new_page = AsyncMock(return_value=mock_page)
            mock_playwright_instance.chromium.launch = AsyncMock(return_value=mock_browser)
            
            # Mock timeout on page.goto
            mock_page.goto = AsyncMock(side_effect=PlaywrightTimeoutError("Timeout"))
            mock_page.close = AsyncMock()
            
            scraper.browser = mock_browser
            scraper.playwright = mock_playwright_instance
            
            url = "https://www.linkedin.com/jobs/view/123456789/"
            
            with pytest.raises(PageLoadTimeout):
                await scraper.scrape_job_description(url)
            
            mock_page.close.assert_called_once()
    
    async def test_scrape_job_description_content_not_found(self, scraper):
        """Test scraping fails when content not found."""
        with patch("app.services.linkedin_scraper.async_playwright") as mock_playwright:
            from playwright.async_api import TimeoutError as PlaywrightTimeoutError
            
            mock_playwright_instance = AsyncMock()
            mock_playwright.return_value.start = AsyncMock(return_value=mock_playwright_instance)
            
            mock_browser = AsyncMock()
            mock_page = AsyncMock()
            mock_browser.new_page = AsyncMock(return_value=mock_page)
            mock_playwright_instance.chromium.launch = AsyncMock(return_value=mock_browser)
            
            mock_page.goto = AsyncMock()
            # All selectors timeout (content not found)
            mock_page.wait_for_selector = AsyncMock(side_effect=PlaywrightTimeoutError("Selector timeout"))
            mock_page.query_selector = AsyncMock(return_value=None)
            mock_page.close = AsyncMock()
            
            scraper.browser = mock_browser
            scraper.playwright = mock_playwright_instance
            
            url = "https://www.linkedin.com/jobs/view/123456789/"
            
            with pytest.raises(ContentNotFound):
                await scraper.scrape_job_description(url)
            
            mock_page.close.assert_called_once()
    
    async def test_scrape_job_description_anti_bot_detected(self, scraper):
        """Test scraping fails when anti-bot challenge detected."""
        with patch("app.services.linkedin_scraper.async_playwright") as mock_playwright:
            mock_playwright_instance = AsyncMock()
            mock_playwright.return_value.start = AsyncMock(return_value=mock_playwright_instance)
            
            mock_browser = AsyncMock()
            mock_page = AsyncMock()
            mock_browser.new_page = AsyncMock(return_value=mock_page)
            mock_playwright_instance.chromium.launch = AsyncMock(return_value=mock_browser)
            
            mock_page.goto = AsyncMock()
            # Mock CAPTCHA element found
            mock_captcha_element = MagicMock()
            mock_page.query_selector = AsyncMock(return_value=mock_captcha_element)
            mock_page.close = AsyncMock()
            
            scraper.browser = mock_browser
            scraper.playwright = mock_playwright_instance
            
            url = "https://www.linkedin.com/jobs/view/123456789/"
            
            with pytest.raises(AntiBotDetected):
                await scraper.scrape_job_description(url)
            
            mock_page.close.assert_called_once()
    
    async def test_is_anti_bot_page_detected(self, scraper):
        """Test anti-bot page detection."""
        mock_page = AsyncMock()
        mock_captcha = MagicMock()
        mock_page.query_selector = AsyncMock(return_value=mock_captcha)
        
        result = await scraper._is_anti_bot_page(mock_page)
        assert result is True
    
    async def test_is_anti_bot_page_not_detected(self, scraper):
        """Test anti-bot page not detected."""
        mock_page = AsyncMock()
        mock_page.query_selector = AsyncMock(return_value=None)
        
        result = await scraper._is_anti_bot_page(mock_page)
        assert result is False
    
    async def test_close_browser(self, scraper):
        """Test browser and playwright cleanup."""
        mock_browser = AsyncMock()
        mock_playwright = AsyncMock()
        
        scraper.browser = mock_browser
        scraper.playwright = mock_playwright
        
        await scraper.close()
        
        mock_browser.close.assert_called_once()
        mock_playwright.stop.assert_called_once()
