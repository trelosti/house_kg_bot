# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pymongo
from pymongo import MongoClient
from itemadapter import ItemAdapter

class HousescraperPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        ## Strip all whitespaces and '\n' symbol from strings
        field_names = adapter.field_names()
        for field_name in field_names:
            if field_name != 'link' and field_name != 'details':
                value = adapter.get(field_name)
                if value[0] is not None:
                    adapter[field_name] = value[0].strip().strip("\n")

        return item

class MongoDBPipeline(object):
    def process_item(self, item, spider):
        uri = ""

        connection = MongoClient(uri)
        db = connection["house_kg"]
        collection = db["house"]

        valid = True
        for data in item:
            if not data:
                valid = False
        if valid:
            collection.insert_one(dict(item))
        return item