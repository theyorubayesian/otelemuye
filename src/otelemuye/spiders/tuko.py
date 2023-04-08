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


class TukoSpider(CustomSpider):
    name = "tuko_spider"
    content_tags = ["p", "strong"]
    
    def _get_article_data(self, soup: BeautifulSoup) -> ArticleData:
        headline = soup.find("h1", attrs={"class": "c-main-headline"}).text
        category = None

        content_soup = soup.find("div", attrs={"class": "post__content"})
        content_elements = chain(*[content_soup.find_all(tag) for tag in self.content_tags])
        content = self._clean_string(" ".join([elem.text for elem in content_elements]))
        
        return self.article_data(headline, content, category)

    def _find_next_page(self, soup: BeautifulSoup, response: Response) -> Optional[str]:
        # https://stackoverflow.com/a/60398600
        # urlparse – Split URL into component pieces: http://pymotw.com/2/urlparse/
        first_article = soup.find("article", attrs={"class": "c-article-card-horizontal l-article-loadable-list"})
        
        if first_article:
            curr_url = urlparse(response.url)
            try:
                base, category, idx = PurePosixPath(curr_url.path).parts
                idx = int(idx) + 1 
            except ValueError:
                base, category = PurePosixPath(curr_url.path).parts
                idx = 2
            
            next_url = urlunparse(
                (
                    curr_url.scheme, 
                    curr_url.hostname, 
                    PurePosixPath(base, category, str(idx)).as_posix(), 
                    None, None, None
                ))
            return next_url

    def _get_article_urls(self, soup: BeautifulSoup) -> List[str]:
        all_urls = [urlparse(a.get("href")) for a in soup.find_all("a")]
        article_urls = [
            x.geturl() 
            for x in all_urls 
            if x.hostname == "kiswahili.tuko.co.ke"
            and len(x.path.split("-")) > 3
        ]
        return article_urls
