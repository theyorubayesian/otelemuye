import logging
from abc import ABC
from abc import abstractmethod
from collections import namedtuple
from typing import NamedTuple

import yaml
from bs4 import BeautifulSoup
from scrapy import Request
from scrapy.http.response import Response
from scrapy.spiders import SitemapSpider
from scrapy.spiders.sitemap import iterloc
from scrapy.utils.sitemap import Sitemap
from scrapy.utils.sitemap import sitemap_urls_from_robots

from otelemuye.item import Article

logger = logging.getLogger(__name__)

ArticleData = NamedTuple("article", [("headline", str), ('content', str), ("category", str)])


class CustomSitemapSpider(SitemapSpider):
    """
    Subclass and provide custom_settings as a class attribute
    """
    article_data = namedtuple("article", ["headline", "content", "category"])

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
    
    @abstractmethod
    def _parse_article(self, response: Response) -> Article:
        """
        Use `_get_article_data` to parse a page and return `Article` passed to pipeline
        """
        pass
    