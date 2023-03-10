from collections import namedtuple
from itertools import chain

from bs4 import BeautifulSoup
from scrapy.spiders import SitemapSpider
from scrapy import Request
from scrapy.http.response import Response
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from legit.item import LegitNGArticle
from legit.middlewares.http import SeleniumRequest


class LegitNGSpider(SitemapSpider):
    name = "legitng_spider"
    sitemap_rules = [("", "_make_selenium_request")]
    sitemap_urls = ["https://hausa.legit.ng/legit/sitemap/www/sitemap.xml"]
    content_tags = ["p", "strong", "blockquote"]
    article_data = namedtuple("article", ["headline", "content", "category"])

    @staticmethod
    def _clean_string(string: str) -> str:
        return " ".join(string.split())

    def _get_article_data(self, soup: BeautifulSoup):
        header = soup.find("header", attrs={"class": "post__header"})
        headline = header.find("h1").text
        category = header.find("a", attrs={"c-label-item"}).text

        content_soup=soup.find("div", attrs={"class": "post__content"})
        content_elements = chain(*[content_soup.find_all(tag) for tag in self.content_tags])
        content = self._clean_string(" ".join([elem.text for elem in content_elements]))
        
        return self.article_data(headline, content, category)
    
    def _make_selenium_request(self, response: Response) -> Request:
        yield SeleniumRequest(
            url=response.url, 
            callback=self._parse_article,
            dont_filter=True,
            # wait_time=30,
            # wait_until=EC.presence_of_element_located((By.CSS_SELECTOR, "div.post__content"))
        )
    
    def _parse_article(self, response: Response) -> LegitNGArticle:
        soup = BeautifulSoup(response.body)
        article = self._get_article_data(soup)
        item = LegitNGArticle(
            url=response.url, 
            headline=article.headline, 
            content=article.content,
            category=article.category
        )
        yield item
