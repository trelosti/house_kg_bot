import subprocess
import constants
from aiogram import Bot, Dispatcher, executor, types
from pymongo import MongoClient
from pymongo import MongoClient
from bson.json_util import dumps
from decouple import config
import json


TOKEN = config('BOT_TOKEN')

bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    uri = config('MONGODB_URI')

    connection = MongoClient(uri)
    db = connection["house_kg"]
    collection = db["house"]
    cursor = collection.find({}, {'_id': False})
    json_dumps = dumps(cursor)
    json_data = json.loads(json_dumps)

    for msg in json_data:
        print(get_photo(msg))
        await message.answer_photo(get_photo(msg), caption=format_json(msg), parse_mode="HTML")
        # print(format_json(msg))

@dp.message_handler(commands=['update'])
async def update_handler(message: types.Message):
    subprocess.run(f'scrapy crawl housespider -a start_url={constants.ONE_ROOM_URL}', shell = True)

def format_json(json_data):
    reply = ''
    reply += f"{json_data['link'][0]}\n"
    reply += f"{json_data['header']}\n"
    reply += f"{json_data['price']}\n"
    reply += f"{json_data['upped']}\n"
    # reply += '<a href="' + f"{json_data['image']}" + '"></a>\n'
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
    