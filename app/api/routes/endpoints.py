"""Hacker News Scraper API Endpoints."""

from typing import Annotated

from fastapi import APIRouter, Path, status

from app.api.routes.news import HackerNewsScraper, ScraperResponse

router = APIRouter()

HACKER_NEWS_URL = "https://news.ycombinator.com/"


@router.get(
    "/",
    summary="Scrape Hacker News",
    description="Scrape Hacker News articles.",
    status_code=status.HTTP_200_OK,
    tags=["Scraping"],
)
async def scrape() -> list[ScraperResponse]:
    """Scrape Hacker News articles.

    **Returns:**
    - A list of dictionaries containing the scraped articles.
    e.g.
        - `/` will scrape the first page of Hacker News articles.
    """
    scraper = HackerNewsScraper(HACKER_NEWS_URL)
    return await scraper.scrape()


@router.get(
    "/{num_pages}",
    summary="Scrape multiple pages of Hacker News",
    description="Scrape multiple pages of Hacker News articles. The number of pages to scrape is specified in the URL.",
    status_code=status.HTTP_200_OK,
    tags=["Scraping"],
)
async def scrape_multiple_pages(
    num_pages: Annotated[int, Path(..., gt=0, description="Number of pages to scrape")],
) -> list[ScraperResponse]:
    """Scrape multiple pages of Hacker News articles.

    The number of pages to scrape is specified in the URL.

    **Parameters:**
    - `num_pages`: The number of pages to scrape.

    **Returns:**
    - A list of ScraperResponse containing the scraped articles.
    e.g.
        - `/scrape/1` will scrape 1 page of Hacker News articles.
        - `/scrape/2` will scrape 2 pages of Hacker News articles.
    """
    scraper = HackerNewsScraper(HACKER_NEWS_URL)
    return await scraper.scrape(pages=num_pages)
