import logging
from itertools import chain
from pathlib import PurePosixPath
from typing import List
from typing import Optional
from urllib.parse import urlparse
from urllib.parse import urlunparse

from bs4 import BeautifulSoup
from scrapy.http.response import Response

from ._base import ArticleData
from ._base import CustomSpider


logger = logging.getLogger(__name__)


class {{cookiecutter.spider_name|capitalize}}Spider(CustomSpider):
    name = "{{ cookiecutter.spider_name|lower }}_spider"

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

