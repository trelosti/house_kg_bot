import subprocess
import constants
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient
from pymongo import MongoClient
from bson.json_util import dumps
from decouple import config
import json
import logging


TOKEN = config('BOT_TOKEN')

bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)

button_1 = KeyboardButton('Однушки')
button_2 = KeyboardButton('Двушки')
button_3 = KeyboardButton('Трешки')
button_4 = KeyboardButton('Сохраненные')

kb_client = ReplyKeyboardMarkup(resize_keyboard=True)

kb_client.add(button_1).add(button_2).add(button_3).add(button_4)

save_kb = InlineKeyboardMarkup(row_width=2)
save_button = InlineKeyboardButton(text='Сохранить', callback_data='save')
save_kb.add(save_button)

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    await message.answer('Выберите количество комнат для квартиры.', reply_markup=kb_client)

@dp.message_handler(text=['Однушки'])
async def one_handler(message : types.Message):
    delete_data()
    subprocess.run(f'scrapy crawl housespider -a start_url={constants.ONE_ROOM_URL}', shell = True)

    json_data = get_data()

    for msg in json_data:
        print(get_photo(msg))
        await message.answer_photo(get_photo(msg), caption=format_json(msg), parse_mode="HTML", reply_markup=save_kb)

@dp.message_handler(text=['Двушки'])
async def two_handler(message : types.Message):
    delete_data()

    subprocess.run(f'scrapy crawl housespider -a start_url={constants.TWO_ROOM_URL}', shell = True)

    json_data = get_data()

    for msg in json_data:
        print(get_photo(msg))
        await message.answer_photo(get_photo(msg), caption=format_json(msg), parse_mode="HTML", reply_markup=save_kb)

@dp.message_handler(text=['Трешки'])
async def three_handler(message : types.Message):
    delete_data()

    subprocess.run(f'scrapy crawl housespider -a start_url={constants.THREE_ROOM_URL}', shell = True)

    json_data = get_data()

    for msg in json_data:
        print(get_photo(msg))
        await message.answer_photo(get_photo(msg), caption=format_json(msg), parse_mode="HTML", reply_markup=save_kb)

@dp.message_handler(text=['Сохраненные'])
async def saved_handler(message : types.Message):
    json_data = get_saved_data()

    for msg in json_data:
        print(get_photo(msg))
        await message.answer_photo(get_photo(msg), caption=format_json(msg), parse_mode="HTML", reply_markup=save_kb)

@dp.callback_query_handler(text='save')
async def save_call(callback : types.CallbackQuery):
    # chat_id = callback.message.chat.id
    # message_id = callback.message.message_id
    text = callback.message
    # Extract the URL from the caption
    caption = text["caption"]
    url = caption.split("\n")[0]

    uri = config('MONGODB_URI')
    connection = MongoClient(uri)
    db = connection["house_kg"]
    collection = db["house"]

    is_saved = collection.find_one({"link": url})['saved']
    
    if is_saved is False:
        collection.update_one(
            {"link": url},
            {"$set": {
                "saved": True
            }}
        )
        await callback.answer("Сохранено")
    else:
        collection.update_one(
            {"link": url},
            {"$set": {
                "saved": False
            }}
        )
        await callback.answer("Удалено из сохраненных")

def get_data():
    uri = config('MONGODB_URI')

    connection = MongoClient(uri)
    db = connection["house_kg"]
    collection = db["house"]
    cursor = collection.find({}, {'_id': False}).sort([('_id', -1), ('price', 1)]).limit(20)
    json_dumps = dumps(cursor)
    json_data = json.loads(json_dumps)

    return json_data

def get_saved_data():
    uri = config('MONGODB_URI')

    connection = MongoClient(uri)
    db = connection["house_kg"]
    collection = db["house"]
    cursor = collection.find({'saved': True})
    json_dumps = dumps(cursor)
    json_data = json.loads(json_dumps)

    return json_data

def delete_data():
    uri = config('MONGODB_URI')

    connection = MongoClient(uri)
    db = connection["house_kg"]
    collection = db["house"]
    collection.delete_many({"saved": False})

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
    