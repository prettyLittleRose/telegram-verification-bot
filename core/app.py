import json
from telethon import TelegramClient
from telebot import TeleBot

from framework.database import Database
from framework.logging import *

with open('./settings.json', 'r') as f:
    settings = json.load(f)

database = Database('database.db')

user_settings = settings['user']
bot_settings = settings['bot']
authorized_users = settings['authorized_users']

user_selections = {}

bot = TeleBot(bot_settings['token'], parse_mode = 'HTML', disable_web_page_preview = True)

client = TelegramClient('EasySecureClient', user_settings['app_id'], user_settings['app_hash'])
client_username = None
