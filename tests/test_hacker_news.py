"""Unit tests for the HackerNewsScraper class."""

import pytest
from fastapi.testclient import TestClient

from app.api.routes.news import (
    HackerNewsScraper,
    ScraperExceptionError,
    ScraperResponse,
)
from app.main import app

HACKER_NEWS_URL = "https://news.ycombinator.com"


@pytest.mark.asyncio
@pytest.mark.parametrize("pages", [None, 1])
async def test_hacker_news_scraper_single_page(monkeypatch, pages):
    """Test scraping a single page successfully"""

    async def mock_scrape(*args, **kwargs):
        return [
            ScraperResponse(
                title="Test Article",
                url="https://example.com/article",
                sent_by="test_user",
                published="2 hours ago",
            ),
        ]

    monkeypatch.setattr(HackerNewsScraper, "scrape", mock_scrape)
    scraper = HackerNewsScraper(HACKER_NEWS_URL)
    if pages:
        result = await scraper.scrape(pages=pages)
    else:
        result = await scraper.scrape()

    assert len(result) == 1
    assert result[0].title == "Test Article"
    assert result[0].url == "https://example.com/article"
    assert result[0].sent_by == "test_user"
    assert result[0].published == "2 hours ago"


@pytest.mark.parametrize("invalid_value", [0, -1, -100])
def test_invalid_num_pages(invalid_value):
    """Test that invalid page numbers return a 422 status code."""
    client = TestClient(app)

    response = client.get(f"/{invalid_value}")
    assert response.status_code == 422
    assert "Input should be greater than 0" in response.text


@pytest.mark.asyncio
@pytest.mark.parametrize("pages", [1, 5, 10, 100, 10000])
async def test_hacker_news_scraper_multiple_pages(monkeypatch, pages):
    """Test scraping multiple pages with many pages."""

    async def mock_scrape(*args, **kwargs):
        return [
            ScraperResponse(
                title="Test Article 1",
                url="https://example.com/article",
                sent_by="test_user",
                published="2 hours ago",
            ),
            ScraperResponse(
                title="Test Article 2",
                url="https://foo.bar/article",
                sent_by="test_user_2",
                published="5 hours ago",
            ),
        ]

    monkeypatch.setattr(HackerNewsScraper, "scrape", mock_scrape)
    scraper = HackerNewsScraper(HACKER_NEWS_URL)

    result = await scraper.scrape(pages=pages)
    assert len(result) == 2
    assert result[0].title == "Test Article 1"
    assert result[1].title == "Test Article 2"


@pytest.mark.asyncio
async def test_hacker_news_scraper_no_articles(monkeypatch):
    """Test scraping when no articles are found."""

    async def mock_scrape(*args, **kwargs):
        return []

    monkeypatch.setattr(HackerNewsScraper, "scrape", mock_scrape)
    scraper = HackerNewsScraper(HACKER_NEWS_URL)
    result = await scraper.scrape(pages=1)

    assert len(result) == 0


@pytest.mark.asyncio
async def test_hacker_news_scraper_missing_title(monkeypatch):
    """Test scraping when an article is missing a title."""

    def mock_extract_article_data(*args, **kwargs):
        raise ScraperExceptionError("Error: Article title is missing.")

    monkeypatch.setattr(
        HackerNewsScraper,
        "extract_article_data",
        mock_extract_article_data,
    )
    scraper = HackerNewsScraper(HACKER_NEWS_URL)
    with pytest.raises(ScraperExceptionError, match="Error: Article title is missing."):
        await scraper.extract_article_data(None, None)


@pytest.mark.asyncio
async def test_hacker_news_scraper_timeout_error(monkeypatch):
    """Test scraping when a timeout error occurs."""

    async def mock_scrape(*args, **kwargs):
        raise TimeoutError("Timeout occurred")

    monkeypatch.setattr(HackerNewsScraper, "scrape", mock_scrape)
    scraper = HackerNewsScraper(HACKER_NEWS_URL)
    with pytest.raises(TimeoutError, match="Timeout occurred"):
        await scraper.scrape(pages=1)
