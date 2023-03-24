import json

from itemadapter import ItemAdapter

from ._base import BasePipeline


class JsonWriterPipeline(BasePipeline):

    def open_spider(self, spider):
        self.file = open(spider.settings["OUTPUT_FILE"], 'a')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict(), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item
