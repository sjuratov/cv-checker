"""
LinkedIn job scraping service using Playwright.

Extracts job description text from LinkedIn job posting URLs using headless browser automation.
"""

import asyncio
import logging
from typing import Optional

from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)


class LinkedInScraperError(Exception):
    """Base exception for LinkedIn scraping errors."""
    pass


class PageLoadTimeout(LinkedInScraperError):
    """Page failed to load within timeout."""
    pass


class ContentNotFound(LinkedInScraperError):
    """Job description content not found on page."""
    pass


class AntiBotDetected(LinkedInScraperError):
    """LinkedIn anti-bot challenge detected."""
    pass


class LinkedInScraperService:
    """
    Service for scraping LinkedIn job postings using Playwright.
    
    Uses headless Chromium browser to navigate to LinkedIn job pages,
    extract job description text, and handle various error scenarios.
    """
    
    def __init__(self, timeout: int = 15000):
        """
        Initialize LinkedIn scraper service.
        
        Args:
            timeout: Maximum time to wait for page load and selectors (milliseconds)
        """
        self.browser: Optional[Browser] = None
        self._playwright = None
        self._playwright_context_manager = None
        self.timeout = timeout
        self.max_retries = 2
        
    async def initialize(self):
        """
        Initialize Playwright and launch browser instance.
        
        Creates a headless Chromium browser with anti-detection configurations.
        """
        if self.browser:
            return
        
        logger.info("Initializing Playwright browser")
        try:
            # Store the context manager to prevent it from being garbage collected
            self._playwright_context_manager = async_playwright()
            self._playwright = await self._playwright_context_manager.__aenter__()
            
            self.browser = await self._playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-blink-features=AutomationControlled',
                ]
            )
            logger.info("Playwright browser initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Playwright browser: {e}")
            raise LinkedInScraperError(f"Browser initialization failed: {e}")
    
    async def scrape_job_description(self, url: str) -> str:
        """
        Extract job description text from LinkedIn URL.
        
        Navigates to the LinkedIn job posting, waits for content to load,
        and extracts the job description text using multiple fallback selectors.
        
        Args:
            url: LinkedIn job posting URL
            
        Returns:
            Raw job description text
            
        Raises:
            PageLoadTimeout: If page fails to load within timeout
            ContentNotFound: If job description content not found on page
            AntiBotDetected: If LinkedIn anti-bot challenge detected
            LinkedInScraperError: For other scraping failures
        """
        # Initialize or verify browser is ready
        if not self.browser or not self.browser.is_connected():
            logger.warning("Browser not connected, reinitializing...")
            await self.initialize()
        
        page: Optional[Page] = None
        context = None
        
        try:
            # Create a new browser context for isolation
            context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            page = await context.new_page()
            
            # Navigate to job posting
            logger.info(f"Navigating to LinkedIn job: {url}")
            try:
                await page.goto(url, timeout=self.timeout, wait_until='domcontentloaded')
            except PlaywrightTimeoutError:
                raise PageLoadTimeout(f"Page load timeout after {self.timeout}ms")
            
            # Check for anti-bot detection
            if await self._is_anti_bot_page(page):
                raise AntiBotDetected("LinkedIn anti-bot challenge detected")
            
            # Wait for and extract job description using multiple selectors
            content = await self._extract_job_description(page)
            
            if not content or len(content.strip()) == 0:
                raise ContentNotFound("Job description content is empty")
            
            logger.info(f"Successfully scraped job description ({len(content)} chars) from {url}")
            return content.strip()
            
        except (PageLoadTimeout, ContentNotFound, AntiBotDetected):
            raise
        except Exception as e:
            logger.error(f"Unexpected error scraping LinkedIn: {e}")
            raise LinkedInScraperError(f"Failed to scrape LinkedIn job: {e}")
        
        finally:
            # Clean up page and context
            if page and not page.is_closed():
                await page.close()
            if context:
                await context.close()
    
    async def _extract_job_description(self, page: Page) -> str:
        """
        Extract job description text using multiple fallback selectors.
        
        Tries different CSS selectors in order, using the first one that returns content.
        
        Args:
            page: Playwright page object
            
        Returns:
            Extracted job description text
            
        Raises:
            ContentNotFound: If no selector returns valid content
        """
        # Multiple selectors to handle different LinkedIn page layouts
        selectors = [
            '.description__text',
            '.show-more-less-html__markup',
            '.jobs-description__content',
            '[class*="description"]',
            '.jobs-box__html-content',
        ]
        
        content = None
        for selector in selectors:
            try:
                # Wait for selector with shorter timeout (5 seconds per selector)
                await page.wait_for_selector(selector, timeout=5000, state='visible')
                
                # Extract text content
                content = await page.evaluate(f'''() => {{
                    const element = document.querySelector("{selector}");
                    return element ? element.innerText : null;
                }}''')
                
                # Use this content if it's substantial (>100 chars)
                if content and len(content.strip()) > 100:
                    logger.info(f"Successfully extracted content using selector: {selector}")
                    break
            except PlaywrightTimeoutError:
                logger.debug(f"Selector not found: {selector}")
                continue
            except Exception as e:
                logger.warning(f"Error with selector {selector}: {e}")
                continue
        
        if not content:
            raise ContentNotFound("Job description not found using any known selector")
        
        return content
    
    async def _is_anti_bot_page(self, page: Page) -> bool:
        """
        Check if page contains anti-bot challenge (CAPTCHA, verification).
        
        Args:
            page: Playwright page object
            
        Returns:
            True if anti-bot challenge detected, False otherwise
        """
        # Check for CAPTCHA or challenge indicators
        captcha_selectors = [
            'iframe[src*="captcha"]',
            '[id*="captcha"]',
            '[class*="captcha"]',
            'text="Verify you are human"',
            'text="Security Verification"',
        ]
        
        for selector in captcha_selectors:
            try:
                element = await page.query_selector(selector)
                if element:
                    logger.warning(f"Anti-bot challenge detected using selector: {selector}")
                    return True
            except Exception:
                pass
        
        return False
    
    async def close(self):
        """Close browser and Playwright instances."""
        if self.browser:
            await self.browser.close()
            logger.info("Browser closed")
            self.browser = None
            
        if self._playwright_context_manager:
            await self._playwright_context_manager.__aexit__(None, None, None)
            logger.info("Playwright stopped")
            self._playwright = None
            self._playwright_context_manager = None
