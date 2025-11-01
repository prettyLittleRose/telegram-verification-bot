from core.app import *
from core.functions import *

from core.states import *
from core.functions import *

# Message Handlers
@bot.message_handler(commands = ['start'])
def handle_start(message: Message):
    if not pass_message_check(message):
        logger.error(f'Message Not Passed Check: {str(message)}')
        return
    
    set_selection(message, UserState.IDLE)
    bot.send_message(message.chat.id, '''
🎯 <b>@EasySecureBot</b>

One of the first bots to integrate directly with Telegram’s User API, providing user verification and enforcing your group’s security policies.

<b>Default:</b>
• /start: Command Information

<b>Settings:</b>
• /settings: Configure Settings
• /terms: Term Blocklist
• /countries: Country Blocklist''')

@bot.message_handler(commands = ['settings'])
def handle_settings(message: Message):
    if not is_authorized(message.from_user.id):
        logger.info(f'Unauthorized Message: {str(message.id)}, {str(message.from_user.id)}')
        return bot.send_message(message.chat.id, '🚫 You are not authorized to use this feature.')

    set_selection(message, UserState.AWAITING_SETTINGS)
    def mark(name: str, value: str) -> str:
        return f'✓ {name}' if value == 'Yes' else f'✗ {name}'

    countries = database.get_countries()
    terms = database.get_terms()

    settings = database.get_settings()
    allow_fonts = 'Yes' if settings['allow_fonts'] else 'No'
    allow_no_premium = 'Yes' if settings['allow_no_premium'] else 'No'
    should_check_channel = 'Yes' if settings['should_check_channel'] else 'No'
    should_check_bio = 'Yes' if settings['should_check_bio'] else 'No'

    markup = construct_markup([
        InlineKeyboardButton(mark('Fonts', allow_fonts), callback_data = 'toggle_allow_fonts'),
        InlineKeyboardButton(mark('Premium', allow_no_premium), callback_data = 'toggle_allow_no_premium'),
        InlineKeyboardButton(mark('Check Bio', should_check_bio), callback_data = 'toggle_should_check_bio'),
        InlineKeyboardButton(mark('Check Channel Bio', should_check_channel), callback_data = 'toggle_should_check_channel'),
        InlineKeyboardButton('‹ Back', callback_data = 'Home'),
    ], row_widths = [2, 1, 1, 1])

    bot.send_message(message.chat.id, '''
🔧 <b>Settings</b>

• Country Blocklist Count: <b>{}</b>
• Term Blocklist Count: <b>{}</b>

• Allow Fonts: <b>{}</b>
• Allow No Premium: <b>{}</b>
• Should Check Channel Bio: <b>{}</b>
• Should Check Bio: <b>{}</b>'''.format(
        len(countries),
        len(terms),
        allow_fonts,
        allow_no_premium,
        should_check_channel,
        should_check_bio
    ), reply_markup = markup)

# Callback Handlers
@bot.callback_query_handler(func = lambda call: call.data.startswith('toggle_') and not call.data.startswith('toggle_country_'))
def handle_toggle(call: CallbackQuery):
    if not is_authorized(call.from_user.id):
        logger.info(f'Unauthorized Callback: {str(call.id)}, {str(call.from_user.id)}')
        return bot.answer_callback_query(call.id, '🚫 You are not authorized to use this feature.')

    def mark(name: str, value: str) -> str:
        return f'✓ {name}' if value == 'Yes' else f'✗ {name}'
    
    key = call.data.split('_', 1)[1]
    settings = database.get_settings()
    new_value = 1 if settings[key] == 0 else 0
    database.edit_setting(key, new_value)

    settings = database.get_settings()
    countries = database.get_countries()
    terms = database.get_terms()

    allow_fonts = 'Yes' if settings['allow_fonts'] else 'No'
    allow_no_premium = 'Yes' if settings['allow_no_premium'] else 'No'
    should_check_channel = 'Yes' if settings['should_check_channel'] else 'No'
    should_check_bio = 'Yes' if settings['should_check_bio'] else 'No'

    markup = construct_markup([
        InlineKeyboardButton(mark('Fonts', allow_fonts), callback_data = 'toggle_allow_fonts'),
        InlineKeyboardButton(mark('Premium', allow_no_premium), callback_data = 'toggle_allow_no_premium'),
        InlineKeyboardButton(mark('Check Bio', should_check_bio), callback_data = 'toggle_should_check_bio'),
        InlineKeyboardButton(mark('Check Channel Bio', should_check_channel), callback_data = 'toggle_should_check_channel'),
        InlineKeyboardButton('‹ Back', callback_data = 'Home'),
    ], row_widths = [2, 1, 1, 1])

    bot.edit_message_text(
        '''
🔧 <b>Settings</b>

• Country Blocklist Count: <b>{}</b>
• Term Blocklist Count: <b>{}</b>

• Allow Fonts: <b>{}</b>
• Allow No Premium: <b>{}</b>
• Should Check Channel Bio: <b>{}</b>
• Should Check Bio: <b>{}</b>'''.format(
            len(countries),
            len(terms),
            allow_fonts,
            allow_no_premium,
            should_check_channel,
            should_check_bio
        ),
        call.message.chat.id,
        call.message.id,
        reply_markup = markup
    )

@bot.callback_query_handler(func = lambda call: call.data == 'Home')
def handle_home(call: CallbackQuery):
    if not pass_callback_check(call):
        return

    set_selection(call, UserState.IDLE)
    bot.edit_message_text('''
🎯 <b>@EasySecureBot</b>

One of the first bots to integrate directly with Telegram's User API, providing user verification and enforcing your group's security policies.

<b>Default:</b>
• /start: Command Information

<b>Settings:</b>
• /settings: Configure Settings
• /terms: Term Blocklist
• /countries: Country Blocklist

<b>Information:</b>
• /statistics: Join Statistics
• /lock: Lock Verification
• /unlock: Unlock Verification''',
        call.message.chat.id,
        call.message.id)

