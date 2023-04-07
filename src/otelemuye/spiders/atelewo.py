import logging
from itertools import chain

from bs4 import BeautifulSoup
from scrapy import Request
from scrapy.http.response import Response
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from ._base import ArticleData, CustomSitemapSpider
from otelemuye.item import Article
from otelemuye.middlewares import SeleniumRequest

logger = logging.getLogger(__name__)


class AtelewoSpider(CustomSitemapSpider):
    name = "atelewo_spider"
    sitemap_rules = [("", "_make_selenium_request")]
    content_tags = ["p", "strong", "blockquote"]

    def _make_selenium_request(self, response: Response) -> Request:
        yield SeleniumRequest(
            url=response.url,
            callback=self.parse,
            dont_filter=True,
            # wait_time=30,
            # wait_until=EC.presence_of_element_located((By.CSS_SELECTOR, "div.post__content"))
        )

    def _get_article_data(self, soup: BeautifulSoup) -> ArticleData:
        header = soup.find("h1", attrs={"class": "page-title"}).text
        header = header.replace('\n', '')
        header = header.replace('\t', '')
        category_sec = soup.find("div", attrs={"class": "newsmag-post-meta"})
        category = category_sec.find(
            "a", attrs={"rel": "category tag"}).text if category_sec else "N/A"
        content_soup = soup.find("div", attrs={"class": "entry-content"})
        content_elements = content_soup.find_all("p")
        content = self._clean_string(
            " ".join([elem.text for elem in content_elements]))

        return self.article_data(header, content, category)
