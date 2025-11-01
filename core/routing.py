from typing import Union

from core.states import *
from cogs.countries import handle_country_name
from cogs.terms import handle_term

from telebot.types import (
    User,
    Message,
    CallbackQuery
)

class UserRouting:
    ROUTES = {
        UserState.AWAITING_COUNTRIES: handle_country_name,
        UserState.AWAITING_TERMS: handle_term,
    }

def get_route(state: 'UserState', message_or_callback: Union[Message, CallbackQuery] = None) -> Any:
    if handler := UserRouting.ROUTES.get(state):
        return handler
