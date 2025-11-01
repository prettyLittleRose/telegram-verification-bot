import asyncio
import threading
import os
import importlib

from framework.logging import logger

from core.app import *
from core.functions import *
from core.states import *
from core.routing import *

from typing import Any, Callable
from telebot.types import (
    User,
    Message,
    ChatJoinRequest
)

for file_name in os.listdir('./cogs/'):
    if file_name.endswith('.py') and file_name != '__init__.py':
        importlib.import_module(f'cogs.{file_name[:-3]}')

@bot.message_handler(func = lambda message: True, content_types = ['text', 'audio', 'video', 'photo', 'voice', 'animation'])
def handle_message(message: Message):
    params = get_params(message.from_user.id)
    state = get_state(message.from_user.id)
    route = get_route(state, message)
    if not route:
        return

    logger.info(f'Message: {str(message.id)}, {str(message.from_user.id)}, {str(state)}, {str(params)} | Route: {str(route)}')
    
    bot.delete_message(message.chat.id, message.id)
    route(message)

@bot.chat_join_request_handler(func = lambda request: True)
def handle_chat_join_request(request: ChatJoinRequest):
    logger.info(f'Chat Join Request: {str(request.from_user.id)}')

    name = request.from_user.full_name
    name_analysis = analyze_text(name)

    settings = database.get_settings()
    allow_fonts = settings['allow_fonts']

    if name_analysis['percent_allowed'] < 50 and not allow_fonts:
        return bot.send_message(request.from_user.id, '🚫 Your join request has been left for manual approval because your name contains too many non-english characters.')
    
    
    bot.send_message(request.from_user.id, f'''👤 <b>Verification Required:</b>

• Please direct message <a href = "https://t.me/{client_username}">this account</a> to be verified automatically. This is essential for gathering more information about your account.'''
    )

async def start_telethon():
    global client_username

    await client.start()
    client_username = (await client.get_me()).username
    await client.run_until_disconnected()

if __name__ == '__main__':
    telethon_thread = threading.Thread(target = lambda: asyncio.run(start_telethon()), daemon = True)
    telethon_thread.start()

    bot.infinity_polling()
