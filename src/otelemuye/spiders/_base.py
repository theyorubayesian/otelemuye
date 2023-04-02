import logging
from abc import ABC
from abc import abstractmethod
from collections import namedtuple
from typing import List
from typing import NamedTuple
from typing import Optional

import yaml
from bs4 import BeautifulSoup
from scrapy import Request
from scrapy import Spider
from scrapy.http.response import Response
from scrapy.spiders import SitemapSpider
from scrapy.spiders.sitemap import iterloc
from scrapy.utils.sitemap import Sitemap
from scrapy.utils.sitemap import sitemap_urls_from_robots

from otelemuye.item import Article

logger = logging.getLogger(__name__)

ArticleData = NamedTuple("article", [("headline", str), ('content', str), ("category", str)])


class BaseSpider:
    article_data = namedtuple("article", ["headline", "content", "category"])

    @staticmethod
    def get_config_from_file(config_file: str) -> dict:
        with open(config_file, "r") as f:
            try:
                config = yaml.safe_load(f)
            except yaml.YAMLError as exc:
                logger.warning(f"Custom settings could not be loaded from {config_file}")
                logger.warning(exc)
                config = {}
        return config

    @classmethod
    def set_spider_attributes(cls, spider_config_file: str) -> None:
        config: dict = cls.get_config_from_file(spider_config_file)
        for key in config:
            setattr(cls, key, config[key])

    @staticmethod
    def _clean_string(string: str) -> str:
        """
        Clean article content
        """
        return " ".join(string.split())

    @abstractmethod
    def _get_article_data(self, soup: BeautifulSoup) -> ArticleData:
        """
        Parse a page's soup and return headline, content and category in namedtuple
        """
        pass
    
    def parse(self, response: Response, **kwargs) -> Article:
        soup = BeautifulSoup(response.body, "lxml")
        article = self._get_article_data(soup)
        item = Article(
            url=response.url, 
            headline=article.headline, 
            content=article.content,
            category=article.category
        )
        yield item


class CustomSitemapSpider(ABC, BaseSpider, SitemapSpider):
    """
    Subclass and provide custom_settings as a class attribute
    """    
    def start_requests(self):
        for url in self.sitemap_urls:
            yield Request(url, self._parse_sitemap, dont_filter=True)

    # Sitemap spider does not resume though JOBDIR is set
    # https://github.com/scrapy/scrapy/issues/4479
    def _parse_sitemap(self, response) -> Request:
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


class CustomSpider(ABC, BaseSpider, Spider):
    def start_requests(self):
        if not self.start_urls and hasattr(self, "start_url"):
            raise AttributeError(
                "Crawling could not start: 'start_urls' not found "
                "or empty (but found 'start_url' attribute instead, "
                "did you miss an 's'?)"
            )
        for url in self.start_urls:
            yield Request(url, dont_filter=True, callback=self._parse_list_page)

    @abstractmethod
    def _find_next_page(self, soup: BeautifulSoup, response: Response) -> Optional[str]:
        """
        Usually by finding the scroll or the navigation bar at bottom
        """
        pass
    
    @abstractmethod
    def _get_article_urls(self, soup: BeautifulSoup) -> List[str]:
        pass

    def _parse_list_page(self, response):
        soup = BeautifulSoup(response.body, "lxml")
        next_page = self._find_next_page(soup, response)

        if next_page:
            yield Request(
                url=next_page,
                callback=self._parse_list_page
            )

        article_urls = self._get_article_urls(soup)
        if article_urls:
            for url in article_urls:
                yield Request(
                    url=url,
                    callback=self.parse
                )
