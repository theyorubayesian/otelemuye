import pymongo
from pymongo import DESCENDING
from scrapy.utils.project import get_project_settings
from scrapy.exceptions import DropItem

from ._base import BasePipeline

settings = get_project_settings()


class MongoPipeline(BasePipeline):
    def __init__(self) -> None:
        connection = pymongo.MongoClient(
            settings['MONGODB_URI']
        )
        db = connection[settings['MONGODB_DB']]
        self.collection = db['MONGODB_COLLECTION']

        self.collection.create_index(
            [("docid", DESCENDING)], background=True, unique=True, name="DocIdIndex"
        )

    def process_item(self, item, spider):
        valid = True
        
        # TODO: Validate item

        if valid:
            data = item.data
            query = {"docid": item.docid}
            self.collection.update_one(query, {"$set": data}, upsert=True)
