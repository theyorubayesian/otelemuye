import logging

from bs4 import BeautifulSoup

from ._base import ArticleData
from ._base import CustomSitemapSpider

logger = logging.getLogger(__name__)


class AtelewoSpider(CustomSitemapSpider):
    name = "atelewo_spider"

    def _get_article_data(self, soup: BeautifulSoup) -> ArticleData:
        header = soup.find("h1", attrs={"class": "page-title"}).text
        header = header.replace('\n', '')
        header = header.replace('\t', '')

        category_soup = soup.find("div", attrs={"class": "newsmag-post-meta"})
        category_elements = category_soup.find_all(
            "a", attrs={"rel": "category tag"})
        category = self._clean_string(
            ", ".join([elem.text for elem in category_elements]))

        content_soup = soup.find("div", attrs={"class": "entry-content"})
        content_elements = content_soup.find_all("p")
        content = self._clean_string(
            " ".join([elem.text for elem in content_elements]))

        return self.article_data(header, content, category)
