import json

from itemadapter import ItemAdapter
from scrapy.utils.project import get_project_settings

from ._base import BasePipeline

settings = get_project_settings()


class JsonWriterPipeline(BasePipeline):

    def open_spider(self, spider):
        self.file = open(settings["OUTPUT_FILE"], 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict(), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item
