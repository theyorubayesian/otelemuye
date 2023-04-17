import logging
from itertools import chain
from pathlib import PurePosixPath
from typing import List
from typing import Optional
from urllib.parse import urlparse
from urllib.parse import urlunparse

from bs4 import BeautifulSoup
from scrapy.http.response import Response
{% if cookiecutter.use_selenium == "true" -%}
from scrapy import Request
from scrapy.http.response import Response
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
{%- endif %}

from ._base import ArticleData
from ._base import CustomSpider


logger = logging.getLogger(__name__)


class {{cookiecutter.spider_name|capitalize}}Spider(CustomSpider):
    name = "{{ cookiecutter.spider_name|lower }}_spider"
    {% if cookiecutter.use_selenium == "true" -%}
    sitemap_rules = [("", "_make_selenium_request")]
    {%- endif %}

    def _get_article_data(self, soup: BeautifulSoup) -> ArticleData:
        headline =          # TODO
        category =          # TODO

        content_soup =      # TODO
        content_elements =  # TODO
        content =           # TODO
        
        return self.article_data(headline, content, category)

    def _find_next_page(self, soup: BeautifulSoup, response: Response) -> Optional[str]:
        next_url = # TODO
        
        return next_url

    def _get_article_urls(self, soup: BeautifulSoup) -> List[str]:
        article_urls = [# TODO]
        
        return article_urls

    {% if cookiecutter.use_selenium == "true" -%}
    def _make_selenium_request(self, response: Response) -> Request:
        yield SeleniumRequest(
            url=response.url, 
            callback=self.parse,
            dont_filter=True,
            wait_time=      # TODO
            wait_until=     # TODO
        )
    {%- endif %}


