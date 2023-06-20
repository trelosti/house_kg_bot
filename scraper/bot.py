import subprocess
import constants
from aiogram import Bot, Dispatcher, executor, types
from pymongo import MongoClient
from pymongo import MongoClient
from bson.json_util import dumps
from decouple import config
import json
import logging


TOKEN = config('BOT_TOKEN')

bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    await message.answer('Выберите количество комнат для квартиры.')

@dp.message_handler(commands=['one'])
async def update_handler(message: types.Message):
    delete_data()
    subprocess.run(f'scrapy crawl housespider -a start_url={constants.ONE_ROOM_URL}', shell = True)

    json_data = get_data()

    for msg in json_data:
        print(get_photo(msg))
        await message.answer_photo(get_photo(msg), caption=format_json(msg), parse_mode="HTML")

@dp.message_handler(commands=['two'])
async def update_handler(message: types.Message):
    delete_data()

    subprocess.run(f'scrapy crawl housespider -a start_url={constants.TWO_ROOM_URL}', shell = True)

    json_data = get_data()

    for msg in json_data:
        print(get_photo(msg))
        await message.answer_photo(get_photo(msg), caption=format_json(msg), parse_mode="HTML")

@dp.message_handler(commands=['three'])
async def update_handler(message: types.Message):
    delete_data()

    subprocess.run(f'scrapy crawl housespider -a start_url={constants.THREE_ROOM_URL}', shell = True)

    json_data = get_data()

    for msg in json_data:
        print(get_photo(msg))
        await message.answer_photo(get_photo(msg), caption=format_json(msg), parse_mode="HTML")

def get_data():
    uri = config('MONGODB_URI')

    connection = MongoClient(uri)
    db = connection["house_kg"]
    collection = db["house"]
    cursor = collection.find({}, {'_id': False}).sort([('price', 1)]).limit(20)
    json_dumps = dumps(cursor)
    json_data = json.loads(json_dumps)

    return json_data

def delete_data():
    uri = config('MONGODB_URI')

    connection = MongoClient(uri)
    db = connection["house_kg"]
    collection = db["house"]
    collection.delete_many({})

def format_json(json_data):
    reply = ''
    reply += f"{json_data['link'][0]}\n"
    reply += f"{json_data['header']}\n"
    reply += f"{json_data['price']}\n"
    reply += f"{json_data['upped']}\n"
    details = json_data['details']
    for item in details:
        for val in item:
            label = val['label']
            info = val['info']
            reply += f"{label}: {info}\n"
            
    return reply

def get_photo(json_data):
    reply = f"{json_data['image']}"

    return reply

if __name__ == '__main__':
    executor.start_polling(dp)
    