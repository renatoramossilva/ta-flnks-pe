from fastapi import APIRouter, status, Path
from pydantic import BaseModel, Field
from playwright.async_api import async_playwright, TimeoutError, Page, ElementHandle
from typing import List, Dict, Optional
from fastapi.responses import JSONResponse

router = APIRouter()

HACKER_NEWS_URL = "https://news.ycombinator.com/"

class ScraperResponse(BaseModel):
    """Base class for scraper responses."""
    title: str = Field(..., description="Title of the article")
    url: str = Field(..., description="URL of the article")
    sent_by: Optional[str] = Field(None, description="User who submitted the article")
    published: Optional[str] = Field(None, description="Time since the article was published")

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Example Article Title",
                "url": "https://example.com/article",
                "sent_by": "Author Name",
                "published": "2 hours ago"
            }
        }
    }
class Scraper:
    """Base class for web scraping functionality."""

    def __init__(self, url: str):
        self.url = url

    async def scrape(self, pages: int = 1) -> List[ScraperResponse]:
        """
        Scrape the specified number of pages from the given URL.

        **Parameters:**
        - `pages`: The number of pages to scrape (default is 1).

        **Returns:**
        - A list of ScraperResponse containing the scraped articles.

        **Example Response:**
        ```json
        [
            {
                "title": "Article Title 1",
                "url": "https://example.com/article1",
                "sent_by": "Author 1",
                "published": "2 hours ago"
            },
            ...
        ]
        ```
        """
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            results = []
            current_url = self.url

            for _ in range(pages):
                try:
                    await page.goto(current_url, timeout=60000)
                except TimeoutError as err:
                    print(f"[ERROR] Timeout error: {err}")
                    break
                athing_rows = await page.query_selector_all("tr.athing")
                page_results = [
                    await self.extract_article_data(row, page)
                    for row in athing_rows if await row.get_attribute("id")
                ]
                results.extend([r for r in page_results if r])

                more_link = await page.query_selector("a.morelink")
                if more_link:
                    next_href = await more_link.get_attribute("href")
                    if next_href:
                        current_url = self.url + next_href
                    else:
                        break
                else:
                    break

            await browser.close()
            print(f"[INFO] Scraping completed. Total articles scraped: {len(results)}")
            print(f"[DEBUG] Articles found on the current page: {len(athing_rows)}")
            print(f"[DEBUG] Cumulative articles scraped so far: {len(results)}")
            print(f"[INFO] Total pages scraped: {pages}")

            return results

    async def extract_article_data(self, row: ElementHandle, page: Page) -> List[Dict]:
        """Extract data from the page. To be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement this method")


class HackerNewsScraper(Scraper):
    """Scraper for Hacker News."""

    async def extract_article_data(self, row: ElementHandle, page: Page) -> ScraperResponse:
        """
        Extract data from a Hacker News article row.

        **Parameters:**
        - `row`: The row element containing the article data.
        - `page`: The Playwright page object.

        **Returns:**
        - A ScraperResponse object containing the article data.

        **Example Response:**
        ```json
        {
            "title": "Article Title",
            "url": "https://example.com/article",
            "sent_by": "Author Name",
            "published": "2 hours ago"
        }
        ```
        """
        article_id = await row.get_attribute("id")
        title_link = await row.query_selector(".titleline a")
        title = await title_link.inner_text() if title_link else None
        url = await title_link.get_attribute("href") if title_link else None

        score_element = await page.query_selector(f"#score_{article_id}")

        if score_element:
            subtext_row = await score_element.evaluate_handle("node => node.parentElement")

            user_link = await subtext_row.query_selector(".hnuser")
            sent_by = await user_link.inner_text() if user_link else None

            age_span = await subtext_row.query_selector(".age")
            published = await age_span.inner_text() if age_span else None
        else:
            sent_by = None
            published = None

        return ScraperResponse(
            title=title,
            url=url,
            sent_by=sent_by,
            published=published,
        )


@router.get(
    "/",
    summary="Scrape Hacker News",
    description="Scrape Hacker News articles.",
    status_code=status.HTTP_200_OK,
    response_model=List[ScraperResponse],
    tags=["Scraping"]
)
async def scrape() -> ScraperResponse:
    """
    Scrape Hacker News articles.

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
    response_model=List[ScraperResponse],
    tags=["Scraping"]
)
async def scrape_multiple_pages(num_pages: int = Path(... , gt=0, description="Number of pages to scrape")) -> list[ScraperResponse]:
    """"
    Scrape multiple pages of Hacker News articles.
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
