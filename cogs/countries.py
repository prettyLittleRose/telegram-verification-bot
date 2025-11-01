from core.app import *
from core.functions import *

from core.states import *
from core.functions import *

# Functions
def generate_country_blocklist_text(user_id: int, page: int) -> str:
    blocked_countries = database.get_countries()
    total_blocked = len(blocked_countries)
    display_limit = 5

    if total_blocked == 0:
        blocked_text = 'You aren\'t blocking any country at the moment.'
    else:
        shown = [country_list[country['code']][0] for country in blocked_countries[:display_limit]]
        remaining = total_blocked - len(shown)
        blocked_text = ', '.join(shown)
        if remaining > 0:
            blocked_text += ' ' + f'(and {remaining} more)'

    total_pages = (len(country_list) - 1) // 10 + 1

    text = f'''🇺🇸 <b>Country Blocklist & Configuration</b>:

{blocked_text}

• Current Page: <b>{page}/{total_pages}</b>
• Current Block Count: <b>{total_blocked}</b>

Please select a country to block or unblock by pressing a button below. Alternatively, you can toggle a country's status by typing it's abbreviation in the chat.'''
    
    return text

def construct_country_page(user_id: int, page: int):
    blocked_countries = database.get_countries()
    blocked_codes = [country['code'] for country in blocked_countries]

    codes = list(country_list.keys())
    total_pages = (len(codes) - 1) // 10 + 1
    start = (page - 1) * 10
    end = start + 10
    page_items = codes[start:end]

    markup = InlineKeyboardMarkup(row_width = 5)
    buttons = []

    for code in page_items:
        name, flag = country_list[code]
        is_blocked = code in blocked_codes
        button_text = f'{"✓ " if is_blocked else ""}{flag} {code}'
        buttons.append(InlineKeyboardButton(button_text, callback_data = f'toggle_country_{code}'))

    if buttons:
        markup.add(*buttons)

    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton('‹ Previous', callback_data = 'previous_page_countries'))
    if page < total_pages:
        nav_buttons.append(InlineKeyboardButton('Next ›', callback_data = 'next_page_countries'))

    if nav_buttons:
        markup.add(*nav_buttons)

    return markup

# Message Functions
def handle_country_name(message: Message) -> str:
    params = get_params(message.from_user.id)
    if not is_authorized(message.from_user.id):
        return bot.edit_message_text('🚫 You are not authorized to use this feature.',
            params['message_chat_id'],
            params['message_id']
        )

    markup = construct_markup([
        InlineKeyboardButton('‹ Back', callback_data = 'Home'),
        InlineKeyboardButton('↻ Retry', callback_data = f'Countries')
    ], row_widths = [2])
    
    if len(message.text) != 2:
        set_selection(message)
        return bot.edit_message_text('🚫 The country code you entered is invalid. Please enter a valid 2-letter country code.',
            params['message_chat_id'],
            params['message_id'],
            reply_markup = markup
        )
    
    country_code = message.text.upper()
    if country_code not in country_list.keys():
        set_selection(message)
        return bot.edit_message_text('🚫 The country code you entered is invalid. Please enter a valid 2-letter country code.',
            params['message_chat_id'],
            params['message_id'],
            reply_markup = markup
        )
     
    blocked_countries = database.get_countries()
    blocked_codes = [country['code'] for country in blocked_countries]

    if country_code in blocked_codes:
        database.remove_country(country_code)
    else:
        database.add_country(country_code)

    text = generate_country_blocklist_text(message.from_user.id, params.get('page', 0))
    markup = construct_country_page(message.from_user.id, params.get('page', 0))

    return bot.edit_message_text(text, 
        params['message_chat_id'], 
        params['message_id'], 
        reply_markup = markup
    )

# Message Handlers
@bot.message_handler(commands = ['countries'])
def handle_countries(message: Message):
    if not is_authorized(message.from_user.id):
        return bot.send_message(message.chat.id, '🚫 You are not authorized to use this feature.')

    set_selection(message, UserState.AWAITING_COUNTRIES, {'page': 1})

    text = generate_country_blocklist_text(message.from_user.id, 1)
    markup = construct_country_page(message.from_user.id, 1)

    bot_message = bot.reply_to(message, text, reply_markup = markup)

    set_selection(message, UserState.AWAITING_COUNTRIES, {
        'message_chat_id': message.chat.id,
        'message_id': bot_message.id,
        'page': 1
    })

# Callback Handlers
@bot.callback_query_handler(func = lambda call: call.data.startswith('toggle_country_'))
def handle_toggle_country(call: CallbackQuery):
    if not is_authorized(call.from_user.id):
        return bot.answer_callback_query(call.id, '🚫 You are not authorized to use this feature.')

    try:
        check_instance(call, UserState.AWAITING_COUNTRIES)
    except InvalidStateError:
        return bot.answer_callback_query(call.id, 'State Mismatch')
    except InvalidMessageError:
        return bot.answer_callback_query(call.id, 'Message Mismatch')
    
    user_id = call.from_user.id
    params = get_params(user_id)
    page = params.get('page', 1)
    
    country_code = call.data.split('_')[2]
    blocked_countries = database.get_countries()
    blocked_codes = [country['code'] for country in blocked_countries]
    
    if country_code in blocked_codes:
        database.remove_country(country_code)
    else:
        database.add_country(country_code)
    
    text = generate_country_blocklist_text(user_id, page)
    markup = construct_country_page(user_id, page)
    
    bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=markup)

@bot.callback_query_handler(func = lambda call: call.data.startswith('previous_page_countries') or call.data.startswith('next_page_countries'))
def handle_country_pagination(call: CallbackQuery):
    if not is_authorized(call.from_user.id):
        return bot.answer_callback_query(call.id, '🚫 You are not authorized to use this feature.')

    try:
        check_instance(call, UserState.AWAITING_COUNTRIES)
    except InvalidStateError:
        return bot.answer_callback_query(call.id, 'State Mismatch')
    except InvalidMessageError:
        return bot.answer_callback_query(call.id, 'Message Mismatch')
    
    user_id = call.from_user.id
    params = get_params(user_id)
    page = params.get('page', 1)
    
    total_pages = (len(country_list) - 1) // 10 + 1
    
    if call.data == 'next_page_countries':
        page = min(page + 1, total_pages)
    elif call.data == 'previous_page_countries':
        page = max(page - 1, 1)
    
    set_selection(call, UserState.AWAITING_COUNTRIES, {
        'message_chat_id': params['message_chat_id'],
        'message_id': params['message_id'],
        'page': page
    })
    
    text = generate_country_blocklist_text(user_id, page)
    markup = construct_country_page(user_id, page)
    
    bot.edit_message_text(text, call.message.chat.id, call.message.id, reply_markup=markup)

@bot.callback_query_handler(func = lambda call: call.data == 'Countries')
def handle_countries_callback(call: CallbackQuery):
    if not is_authorized(call.from_user.id):
        return bot.answer_callback_query(call.id, '🚫 You are not authorized to use this feature.')
    
    set_selection(call, UserState.AWAITING_COUNTRIES, {
        'message_chat_id': call.message.chat.id,
        'message_id': call.message.id,
        'page': 1
    })

    text = generate_country_blocklist_text(call.from_user.id, 1)
    markup = construct_country_page(call.from_user.id, 1)

    bot.edit_message_text(text, 
        call.message.chat.id, 
        call.message.id, 
        reply_markup = markup
    )
