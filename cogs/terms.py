from core.app import *
from core.functions import *

from core.states import *
from core.functions import *

# Message Functions
def handle_term(message: Message) -> str:
    params = get_params(message.from_user.id)
    if not is_authorized(message.from_user.id):
        return bot.edit_message_text('🚫 You are not authorized to use this feature.',
            params['message_chat_id'],
            params['message_id']
        )

    term = message.text
    if database.does_term_exist(term.lower()):
        database.remove_term(term)
    else:
        database.add_term(term)

    terms = database.get_terms()
    total_terms = len(terms)
    term_text = ', '.join(terms) if terms else 'You aren\'t blocking any terms at the moment.'

    try:
        bot.edit_message_text(f'''
🔍 <b>Term Blocklist & Configuration</b>

• Current Terms: <b>{term_text}</b>
• Current Term Count: <b>{total_terms}</b>

Please enter a term to add/remove from the term blocklist by typing it in the chat.''',
            params['message_chat_id'],
            params['message_id']
        )
    except:
        pass

# Message Handlers
@bot.message_handler(commands = ['terms'])
def handle_terms(message: Message):
    if not is_authorized(message.from_user.id):
        return bot.send_message(message.chat.id, '🚫 You are not authorized to use this feature.')

    set_selection(message, UserState.AWAITING_TERMS)

    terms = database.get_terms()
    total_terms = len(terms)
    term_text = ', '.join(terms) if terms else 'You aren\'t blocking any terms at the moment.'

    bot_message = bot.send_message(message.chat.id, f'''
🔍 <b>Term Blocklist & Configuration</b>

• Current Terms: <b>{term_text}</b>
• Current Term Count: <b>{total_terms}</b>

Please enter a term to add/remove from the term blocklist by typing it in the chat.'''
    )

    set_selection(message, UserState.AWAITING_TERMS, {
        'message_chat_id': bot_message.chat.id,
        'message_id': bot_message.id
    })
