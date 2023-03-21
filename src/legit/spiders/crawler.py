import logging
from collections import namedtuple
from itertools import chain

from bs4 import BeautifulSoup
from scrapy import Request
from scrapy.http.response import Response
from scrapy.spiders import SitemapSpider
from scrapy.spiders.sitemap import iterloc
from scrapy.utils.sitemap import Sitemap
from scrapy.utils.sitemap import sitemap_urls_from_robots
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from legit.item import LegitNGArticle
from legit.middlewares.http import SeleniumRequest

logger = logging.getLogger(__name__)

class LegitNGSpider(SitemapSpider):
    name = "legitng_spider"
    sitemap_rules = [("", "_make_selenium_request")]
    sitemap_urls = ["https://www.legit.ng/legit/sitemap/www/sitemap.xml"]
    content_tags = ["p", "strong", "blockquote"]
    article_data = namedtuple("article", ["headline", "content", "category"])

    @staticmethod
    def _clean_string(string: str) -> str:
        return " ".join(string.split())
    
    def start_requests(self):
        for url in self.sitemap_urls:
            yield Request(url, self._parse_sitemap, dont_filter=True)

    # Sitemap spider does not resume though JOBDIR is set
    # https://github.com/scrapy/scrapy/issues/4479
    def _parse_sitemap(self, response):
        if response.url.endswith("/robots.txt"):
            for url in sitemap_urls_from_robots(response.text, base_url=response.url):
                yield Request(url, callback=self._parse_sitemap, dont_filter=True)
        else:
            body = self._get_sitemap_body(response)
            if body is None:
                logger.warning(
                    "Ignoring invalid sitemap: %(response)s",
                    {"response": response},
                    extra={"spider": self},
                )
                return

            s = Sitemap(body)
            it = self.sitemap_filter(s)

            if s.type == "sitemapindex":
                for loc in iterloc(it, self.sitemap_alternate_links):
                    if any(x.search(loc) for x in self._follow):
                        yield Request(loc, callback=self._parse_sitemap, dont_filter=True)
            elif s.type == "urlset":
                for loc in iterloc(it, self.sitemap_alternate_links):
                    for r, c in self._cbs:
                        if r.search(loc):
                            yield Request(loc, callback=c)
                            break

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
