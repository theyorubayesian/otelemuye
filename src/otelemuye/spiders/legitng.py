import logging
from itertools import chain

from bs4 import BeautifulSoup
from scrapy import Request
from scrapy.http.response import Response
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from ._base import ArticleData
from ._base import CustomSitemapSpider
from otelemuye.middlewares import SeleniumRequest

logger = logging.getLogger(__name__)


class LegitNGSpider(CustomSitemapSpider):
    name = "legitng_spider"
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
        header = soup.find("header", attrs={"class": "post__header"})
        headline = header.find("h1").text
        category = header.find("a", attrs={"c-label-item"}).text

        content_soup=soup.find("div", attrs={"class": "post__content"})
        content_elements = chain(*[content_soup.find_all(tag) for tag in self.content_tags])
        content = self._clean_string(" ".join([elem.text for elem in content_elements]))
        
        return self.article_data(headline, content, category)
