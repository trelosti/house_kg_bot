# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from pymongo import MongoClient
from itemadapter import ItemAdapter
from decouple import config

class HousescraperPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        ## Strip all whitespaces and '\n' symbol from strings
        field_names = adapter.field_names()
        for field_name in field_names:
            if field_name != 'link' and field_name != 'details':
                value = adapter.get(field_name)
                if value is not True and value is not False:
                    if value[0] is not None:
                        adapter[field_name] = value[0].strip().strip("\n")

        return item

class MongoDBPipeline(object):
    def process_item(self, item, spider):
        uri = config('MONGODB_URI')

        connection = MongoClient(uri)
        db = connection["house_kg"]
        collection = db["house"]

        valid = True
        for data in item:
            if not data:
                valid = False
        if valid:
            link = item.get("link")  # Get the link field from the item
            if link:
                existing_document = collection.find_one({"link": link})
                if existing_document:
                    # Update the existing document
                    collection.update_one({"link": link}, {"$set": dict(item)})
                else:
                    # Insert a new document
                    collection.insert_one(dict(item))
        return item