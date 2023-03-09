from copy import deepcopy
from dataclasses import dataclass
from typing import Optional


@dataclass
class LegitNGArticle:
    docid: str
    url: str
    headline: str
    content: str
    category: Optional[str]

    @property
    def data(self):
        return deepcopy(vars(self))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(headline={self.headline}, url={self.url}, articleid={self.docid})"