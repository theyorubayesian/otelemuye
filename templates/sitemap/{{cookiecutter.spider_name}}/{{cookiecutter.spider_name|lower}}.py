import logging

from bs4 import BeautifulSoup
{% if cookiecutter.use_selenium == "true" -%}
from scrapy import Request
from scrapy.http.response import Response
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
{%- endif %}

from ._base import ArticleData
from ._base import CustomSitemapSpider


logger = logging.getLogger(__name__)


class {{cookiecutter.spider_name|capitalize}}Spider(CustomSitemapSpider):
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
