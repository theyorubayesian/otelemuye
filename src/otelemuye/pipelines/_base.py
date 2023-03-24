from abc import ABC
from abc import abstractmethod
from pprint import pprint


class BasePipeline(ABC):
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def process_item(self, item, spider):
        pass
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        pass


class StdOutPipeline(BasePipeline):
    def process_item(self, item, spider):
        pprint(repr(item))
        return item
