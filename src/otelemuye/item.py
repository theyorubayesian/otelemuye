from copy import deepcopy
from dataclasses import dataclass
from typing import Optional


@dataclass
class Article:
    url: str
    headline: str
    content: str
    category: Optional[str] = None

    @property
    def data(self):
        return deepcopy(vars(self))

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(headline={self.headline}, url={self.url}, category={self.category})"
    