import logging

from bs4 import BeautifulSoup

from ._base import ArticleData
from ._base import CustomSitemapSpider

logger = logging.getLogger(__name__)


class PremiumTimesSpider(CustomSitemapSpider):
    name = "premiumtimes_spider"
    
    def _get_article_data(self, soup: BeautifulSoup) -> ArticleData:
        headline = soup.find("h1", attrs={"class": "jeg_post_title"}).text
        category = soup.find('a', attrs={"rel": "category tag"}).text

        content_soup = soup.find("div", attrs={"class": "content-inner jeg_link_underline"})
        content_elements = content_soup.find_all("p")
        content = self._clean_string(" ".join([elem.text for elem in content_elements]))
        
        return self.article_data(headline, content, category)
