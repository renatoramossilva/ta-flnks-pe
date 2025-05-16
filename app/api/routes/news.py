"""Scraper for Hacker News articles."""

from typing import Annotated

from bindl.logger import setup_logger
from fastapi import APIRouter, Path, status
from playwright.async_api import ElementHandle, Page, async_playwright
from pydantic import BaseModel, Field

LOG = setup_logger(__name__)

router = APIRouter()

HACKER_NEWS_URL = "https://news.ycombinator.com/"


class ScraperExceptionError(Exception):
    """Custom exception for scraper errors."""


class ScraperResponse(BaseModel):
    """Base class for scraper responses."""

    title: str = Field(..., description="The title of the article")
    url: str | None = Field(None, description="The URL of the article")
    sent_by: str | None = Field(
        None,
        description="The username of the person who submitted the article",
    )
    published: str | None = Field(
        None,
        description="The relative time since the article was published (e.g., '2 hours ago')",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Example Article Title",
                "url": "https://example.com/article",
                "sent_by": "Author Name",
                "published": "2 hours ago",
            },
        },
    }


class Scraper:
    """Base class for web scraping functionality."""

    def __init__(self, url: str):
        self.url = url

    async def scrape(self, pages: int = 1) -> list[ScraperResponse]:
        """Scrape the specified number of pages from the given URL.

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
        LOG.info("Starting scrape process for %s page(s) at URL: %s", pages, self.url)
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            results = []
            current_url = self.url

            for page_number in range(1, pages + 1):
                LOG.debug("Scraping page %s: %s", page_number, current_url)
                try:
                    await page.goto(current_url, timeout=60000)
                except TimeoutError as err:
                    LOG.error("Timeout error on page %s: %s", page_number, err)
                    break

                athing_rows = await page.query_selector_all("tr.athing")
                LOG.debug(
                    "Found %s article rows on page %s",
                    len(athing_rows),
                    page_number,
                )

                page_results = []
                for row in athing_rows:
                    article_id = await row.get_attribute("id")
                    if article_id:
                        LOG.debug(
                            "Processing article ID: %s on page %s",
                            article_id,
                            page_number,
                        )
                        try:
                            article_data = await self.extract_article_data(row, page)
                            page_results.append(article_data)
                        except Exception as e:  # noqa: BLE001
                            LOG.error("Error scraping article ID %s: %s", article_id, e)

                results.extend(page_results)
                LOG.info(
                    "Page %s scraped. Articles found: %s",
                    page_number,
                    len(page_results),
                )

                more_link = await page.query_selector("a.morelink")
                if more_link:
                    next_href = await more_link.get_attribute("href")
                    if next_href:
                        current_url = self.url + next_href
                    else:
                        LOG.warning(
                            "No 'href' attribute found for 'morelink' on page %s",
                            page_number,
                        )
                        break
                else:
                    LOG.info(
                        "No 'morelink' found. Stopping scrape at page %s",
                        page_number,
                    )
                    break

            await browser.close()
            LOG.info("Scraping completed. Total articles scraped: %s", len(results))
            return results

    async def extract_article_data(
        self,
        row: ElementHandle,
        page: Page,
    ) -> ScraperResponse:
        """Extract data from the page. To be implemented by subclasses."""
        msg = "Subclasses must implement this method"
        raise NotImplementedError(msg)


class HackerNewsScraper(Scraper):
    """Scraper for Hacker News."""

    async def extract_article_data(
        self,
        row: ElementHandle,
        page: Page,
    ) -> ScraperResponse:
        """Extract data from a Hacker News article row.

        **Parameters:**
        - `row`: The row element containing the article data.
        - `page`: The Playwright page object.

        **Returns:**
        - A ScraperResponse object containing the article data.

        **Exception**
            Raise an exception if the article does not have a title

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
        LOG.debug("Extracting data for article ID: %s", article_id)

        title_link = await row.query_selector(".titleline a")
        title = await title_link.inner_text() if title_link else None

        if not title:
            err_msg = "Error: Article title is missing."
            raise ScraperExceptionError(err_msg)

        url = await title_link.get_attribute("href") if title_link else None

        score_element = await page.query_selector(f"#score_{article_id}")

        if score_element:
            parent_handle = await row.get_property("parentElement")
            subtext_row = parent_handle.as_element()

            if subtext_row:
                user_link = await subtext_row.query_selector(".hnuser")
                sent_by = await user_link.inner_text() if user_link else None

                age_span = await subtext_row.query_selector(".age")
                published = await age_span.inner_text() if age_span else None

        else:
            sent_by = None
            published = None
            LOG.warning(
                "No score element found for article ID: %s. sent_by and published fields set to None.",
                article_id,
            )

        response = ScraperResponse(
            title=title,
            url=url,
            sent_by=sent_by,
            published=published,
        )
        LOG.info(
            "Successfully extracted data for article ID: %s: %s \n",
            article_id,
            response.dict(),
        )
        return response


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
