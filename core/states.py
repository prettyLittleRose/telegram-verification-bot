from .app import *

from enum import Enum
from typing import Optional, Union, Dict, Any
from telebot.types import Message, CallbackQuery

class UserState(str, Enum):
    IDLE = 'IDLE'
    AWAITING_SETTINGS = 'AWAITING_SETTINGS'
    AWAITING_COUNTRIES = 'AWAITING_COUNTRIES'
    AWAITING_TERMS = 'AWAITING_TERMS'
    AWAITING_DIRECT_MESSAGE = 'AWAITING_DIRECT_MESSAGE'
    
class InvalidStateError(Exception):
    pass

class InvalidMessageError(Exception):
    pass

def get_selection(message_or_callback: Union[Message, CallbackQuery], state: 'UserState' = UserState.IDLE, params: Optional[Dict[str, Any]] = {}) -> dict:
    return user_selections.setdefault(
        message_or_callback.from_user.id,
        {
            'user': message_or_callback.from_user,
            'message_or_callback': message_or_callback,
            'state': state,
            'params': params
        }
    )

def set_selection(message_or_callback: Union[Message, CallbackQuery], state: 'UserState' = UserState.IDLE, params: Optional[Dict[str, Any]] = None):
    selection = get_selection(message_or_callback)

    if state is not None:
        selection['state'] = state
    if params is not None:
        selection['params'] = params

    selection['user'] = message_or_callback.from_user
    selection['message_or_callback'] = message_or_callback

def get_state(user_id: int) -> UserState:
    return user_selections.get(user_id, {}).get('state', UserState.IDLE)

def get_params(user_id: int) -> dict:
    return user_selections.get(user_id, {}).get('params', {})

def check_instance(message_or_callback: Union[Message, CallbackQuery], expecting_state: 'UserState' = UserState.IDLE) -> bool:
    params = get_params(message_or_callback.from_user.id)
    state = get_state(message_or_callback.from_user.id)

    if (
        not params.get('message_chat_id') or 
        not params.get('message_id')
    ):
        raise InvalidMessageError("Expected 'message_chat_id' OR 'message_id'")
    
    if state != expecting_state:
        raise InvalidStateError(f"Expected {expecting_state}, Got: {state}")

    chat_id = (message_or_callback.message.chat.id if isinstance(message_or_callback, CallbackQuery) else message_or_callback.chat.id)
    if params['message_chat_id'] != chat_id:
        raise InvalidMessageError(
            f"Expected Chat '{params['message_chat_id']}', Got: '{chat_id}'"
        )

    if isinstance(message_or_callback, CallbackQuery):
        bot_msg_id = message_or_callback.message.id
        if params['message_id'] != bot_msg_id:
            raise InvalidMessageError(
                f"Expected Message '{params['message_id']}', Got: '{bot_msg_id}'"
            )
        
    return True
