from collections import namedtuple
from itertools import chain

from bs4 import BeautifulSoup
from scrapy.spiders import SitemapSpider
from scrapy import Request
from scrapy.http.response import Response
from selenium.webdriver.support import expected_conditions as EC

from legit.item import LegitNGArticle
from legit.middlewares.http import SeleniumRequest


class LegitNGSpider(SitemapSpider):
    name = "legitng_spider"
    # sitemap_rules = [("", "_make_selenium_request")]
    sitemap_urls = ["https://hausa.legit.ng/legit/sitemap/hausa/news.xml"]
    content_tags = ["p", "strong", "blockquote"]
    article_data = namedtuple("article", ["headline", "content", "article_id"])

    @staticmethod
    def _clean_string(string: str) -> str:
        return " ".join(string.split())

    def _get_article_data(self, soup: BeautifulSoup):
        headline = soup.find("title").text
        article_id="" # TODO

        content_elements = chain(*[soup.find_all(tag) for tag in self.content_tags])
        content = self._clean_string(" ".join([elem.text for elem in content_elements]))
        
        return self.article_data(headline, content, article_id)
    
    def parse(self, response: Response) -> SeleniumRequest:
        self.logger.info("Making selenium request")
        yield SeleniumRequest(
            url=response.url, 
            callback=self._parse_article,
            # wait_until=
        )
    
    def _parse_article(self, response: Response) -> LegitNGArticle:
        self.logger.info("Parsing article")
        soup = BeautifulSoup(response.body)
        article = self._get_article_data(soup)
        item = LegitNGArticle(
            docid=article.article_id, 
            url=response.url, 
            headline=article.headline, 
            content=article.content
        )
        yield item
