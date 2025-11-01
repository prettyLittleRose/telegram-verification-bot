import asyncio

from telethon import events
from core.app import *
from core.functions import *

# Event Handlers
@client.on(events.NewMessage(func = lambda event: event.is_private))
async def handle_new_message(event):
    if event.message.sender_id == (await client.get_me()).id:
        return

    terms = database.get_terms()
    countries = database.get_countries()
    settings = database.get_settings()
    user = database.get_user(event.message.sender_id)
    if user:
        logger.error(f'User Already Exists: {str(event.message.sender_id)}')
        return
    
    sender = await event.get_sender()
    user_info = await get_user_info(client, sender)
    if not user_info:
        logger.error(f'User Info Not Found: {str(sender)}')
        return

    database.add_user(
        user_info['id'], 
        user_info['first_name'], 
        user_info['last_name'], 
        user_info['username'], 
        user_info['is_premium'], 
        user_info['stars'], 
        user_info['stars_level'], 
        user_info['gifts_count'], 
        user_info['phone_country'], 
        user_info['bio']
    )

    if settings['should_check_bio'] and user_info['bio'] and any(term.lower() in user_info['bio'].lower() for term in terms):
        try:
            bot.decline_chat_join_request(bot_settings['chat_id'], event.message.from_id.user_id)
        except Exception as E:
            logger.error(f'Decline Error (should_check_bio): {str(E)}')

        return await client.send_message(event.message.from_id.user_id, '🚫 Your join request has been blocked because your bio contains terms that are not allowed.')
    
    if settings['should_check_channel'] and user_info['personal_channel'] and not user_info['personal_channel']['bio']:
        try:
            bot.decline_chat_join_request(bot_settings['chat_id'], event.message.from_id.user_id)
        except Exception as E:
            logger.error(f'Decline Error (should_check_channel): {str(E)}')

        return await client.send_message(event.message.from_id.user_id, '🚫 Your join request has been blocked because your channel\'s bio contains terms that are not allowed.')
    
    if user_info['phone_country'] and user_info['phone_country'] in [country['code'] for country in countries]:
        try:
            bot.decline_chat_join_request(bot_settings['chat_id'], event.message.from_id.user_id)
        except Exception as E:
            logger.error(f'Decline Error (phone_country): {str(E)}')

        return await client.send_message(event.message.from_id.user_id, '🚫 Your join request has been blocked because your phone country is not allowed.')
    
    if not settings['allow_no_premium'] and not user_info['is_premium']:
        try:
            bot.decline_chat_join_request(bot_settings['chat_id'], event.message.from_id.user_id)
        except Exception as E:
            logger.error(f'Decline Error (allow_no_premium): {str(E)}')

        return await client.send_message(event.message.from_id.user_id, '🚫 Your join request has been blocked because you are not a premium user.')
    
    try:
        bot.approve_chat_join_request(bot_settings['chat_id'], event.message.from_id.user_id)
        logger.info(f'Approval Successful: {str(event.message.from_id.user_id)}')
        
        await client.send_message(event.message.from_id.user_id, '''
    🤝 **Verification Successful:**

    You have successfully been verified and can now access the group.''')
    except Exception as E:
        logger.error(f'Approval Error: {str(E)}')
