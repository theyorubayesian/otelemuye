import logging

from bs4 import BeautifulSoup
from scrapy.http.response import Response

from ._base import ArticleData
from ._base import CustomSitemapSpider
from otelemuye.item import Article

logger = logging.getLogger(__name__)


class PremiumTimesSpider(CustomSitemapSpider):
    name = "premiumtimes_spider"
    
    @staticmethod
    def _clean_string(string: str) -> str:
        return " ".join(string.split())
    
    def _get_article_data(self, soup: BeautifulSoup) -> ArticleData:
        headline = soup.find("h1", attrs={"class": "jeg_post_title"}).text
        category = soup.find('a', attrs={"rel": "category tag"}).text

        content_soup = soup.find("div", attrs={"class": "content-inner jeg_link_underline"})
        content_elements = content_soup.find_all("p")
        content = self._clean_string(" ".join([elem.text for elem in content_elements]))
        
        return self.article_data(headline, content, category)
    
    def parse(self, response: Response, **kwargs) -> Article:
        soup = BeautifulSoup(response.body, features="lxml")
        article = self._get_article_data(soup)
        item = Article(
            url=response.url, 
            headline=article.headline, 
            content=article.content,
            category=article.category
        )
        yield item
