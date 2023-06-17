from aiogram import Bot, Dispatcher, executor, types
from pymongo import MongoClient
from pymongo import MongoClient
from bson.json_util import dumps
from scrapy.crawler import CrawlerProcess
from housescraper.spiders.housespider import HousespiderSpider
from pathlib import Path
import subprocess


TOKEN = ""

bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    uri = ""

    connection = MongoClient(uri)
    db = connection["house_kg"]
    collection = db["house"]
    cursor = collection.find({})
    json_data = dumps(cursor)

    # if len(json_data) > 4096:
    #     for x in range(0, len(json_data), 4096):
    #         await message.reply(json_data[x:x+4096])
    # else:
    #     await message.reply(json_data)
    await message.reply("hi")

@dp.message_handler(commands=['update'])
async def update_handler(message: types.Message):
    subprocess.run('scrapy crawl housespider', shell = True)

if __name__ == '__main__':
    executor.start_polling(dp)
    


