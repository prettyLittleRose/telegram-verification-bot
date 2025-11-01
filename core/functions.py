import string
import unicodedata

from .app import *
from .exceptions import *
from .states import *

from telebot.types import (
    User, Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
)

from telethon import TelegramClient
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.functions.channels import GetFullChannelRequest
from telethon.tl.functions.messages import GetPeerSettingsRequest
from telethon.tl.types import (
    User as TelethonUser,
    UserFull as TelethonUserFull,
    InputChannel as TelethonInputChannel,
    PeerUser as TelethonPeerUser,
)

from typing import (
    Union, Optional, Dict, Any, List, Tuple
)

# Essential Functions
def is_authorized(user_id: int) -> bool:
    return user_id in authorized_users

def pass_message_check(message: Message) -> bool:
    return message.chat.id == message.from_user.id

def pass_callback_check(callback: CallbackQuery) -> bool:
    return callback.message.chat.id == callback.from_user.id

def construct_markup(buttons: List[InlineKeyboardButton], row_widths: List[int] = [1]) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    position = 0

    for row_width in row_widths:
        if not position < len(buttons):
            continue

        markup.add(*buttons[position:position + row_width])
        position += row_width

    return markup

def analyze_text(text: str) -> Dict[str, Any]:
    allowed = set(string.ascii_letters + string.digits + string.punctuation)
    
    total = len(text)
    allowed_count = sum(character in allowed for character in text)
    
    non_english_chars = [character for character in text if not character.isascii()]
    has_non_english_chars = len(non_english_chars) > 0
    
    scripts = set()
    for character in non_english_chars:
        try:
            name = unicodedata.name(character)
            script = name.split()[0]
            scripts.add(script)
        except ValueError:
            pass
    
    return {
        'allowed_count': allowed_count,
        'total_characters': total,
        'percent_allowed': round(allowed_count / total * 100, 2) if total > 0 else 0,
        'contains_non_english': has_non_english_chars,
        'non_english_chars': ''.join(non_english_chars),
        'detected_scripts': list(scripts)
    }

def parse_info_telebot(user: User) -> Dict[str, Any]:
    return {
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'language_code': user.language_code,
        'is_bot': user.is_bot,
        'is_premium': user.is_premium,
        'is_verified': user.is_verified
    }

def parse_info_telethon(full: TelethonUserFull) -> Dict[str, Any]:
    full_user = full.full_user
    user = full.users[0]
    user_channel = full.chats[0] if full.chats else None

    struct = {
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_premium': getattr(user, 'premium', None),
        'bio': getattr(full_user, 'about', None),
        'stars': getattr(full_user.stars_rating, 'stars', None) if getattr(full_user, 'stars_rating', None) else None,
        'stars_level': getattr(full_user.stars_rating, 'level', None) if getattr(full_user, 'stars_rating', None) else None,
        'gifts_count': getattr(full_user, 'stargifts_count', None),
        'personal_channel': None
    }

    if user_channel:
        struct['personal_channel'] = {
            'id': user_channel.id,
            'username': user_channel.username,
            'title': user_channel.title,
            'participants_count': getattr(user_channel, 'participants_count', None),
            'access_hash': getattr(user_channel, 'access_hash', None)
        }

    return struct

async def get_user_info(client: TelegramClient, user: Union[TelethonPeerUser, TelethonUser, TelethonUserFull, str, int]) -> Optional[Dict[str, Any]]:
    if isinstance(user, (TelethonUser, TelethonPeerUser, str, int)):
        try:
            if isinstance(user, (TelethonUser, TelethonPeerUser)):
                user_id = getattr(user, 'id', getattr(user, 'user_id', user))
            else:
                user_id = user

            sender = await client.get_entity(user_id)
            full_user = await client(GetFullUserRequest(sender))
        except Exception as E:
            raise UserNotFoundError(f'User {user_id} Not Found: {E}')
    
        try:
            settings = await client(GetPeerSettingsRequest(full_user.full_user.id))
        except Exception as E:
            raise UserNotFoundError(f'User {full_user.full_user.id} Settings Not Found: {E}')

    struct = parse_info_telethon(full_user)
    struct.update({
        'phone_country': getattr(settings, 'phone_country', None),
        'created_at': getattr(settings, 'registration_month', None),
        'photo_change_date': getattr(settings, 'photo_change_date', None)
    })

    if struct.get('personal_channel'):
        try:
            channel = await client(GetFullChannelRequest(TelethonInputChannel(struct['personal_channel']['id'], struct['personal_channel']['access_hash'])))
        except Exception as E:
            raise UserNotFoundError(f'User {struct["personal_channel"]["id"]} Channel Not Found: {E}')
        struct['personal_channel'].update({
            'bio': getattr(channel.full_chat, 'about', None),
        })

    return struct

# Variables
country_list = {
    'AF': ('Afghanistan', '🇦🇫'),
    'AL': ('Albania', '🇦🇱'),
    'DZ': ('Algeria', '🇩🇿'),
    'AD': ('Andorra', '🇦🇩'),
    'AO': ('Angola', '🇦🇴'),
    'AG': ('Antigua and Barbuda', '🇦🇬'),
    'AR': ('Argentina', '🇦🇷'),
    'AM': ('Armenia', '🇦🇲'),
    'AU': ('Australia', '🇦🇺'),
    'AT': ('Austria', '🇦🇹'),
    'AZ': ('Azerbaijan', '🇦🇿'),
    'BS': ('Bahamas', '🇧🇸'),
    'BH': ('Bahrain', '🇧🇭'),
    'BD': ('Bangladesh', '🇧🇩'),
    'BB': ('Barbados', '🇧🇧'),
    'BY': ('Belarus', '🇧🇾'),
    'BE': ('Belgium', '🇧🇪'),
    'BZ': ('Belize', '🇧🇿'),
    'BJ': ('Benin', '🇧🇯'),
    'BT': ('Bhutan', '🇧🇹'),
    'BO': ('Bolivia', '🇧🇴'),
    'BA': ('Bosnia and Herzegovina', '🇧🇦'),
    'BW': ('Botswana', '🇧🇼'),
    'BR': ('Brazil', '🇧🇷'),
    'BN': ('Brunei', '🇧🇳'),
    'BG': ('Bulgaria', '🇧🇬'),
    'BF': ('Burkina Faso', '🇧🇫'),
    'BI': ('Burundi', '🇧🇮'),
    'CV': ('Cape Verde', '🇨🇻'),
    'KH': ('Cambodia', '🇰🇭'),
    'CM': ('Cameroon', '🇨🇲'),
    'CA': ('Canada', '🇨🇦'),
    'CF': ('Central African Republic', '🇨🇫'),
    'TD': ('Chad', '🇹🇩'),
    'CL': ('Chile', '🇨🇱'),
    'CN': ('China', '🇨🇳'),
    'CO': ('Colombia', '🇨🇴'),
    'KM': ('Comoros', '🇰🇲'),
    'CD': ('Congo (DRC)', '🇨🇩'),
    'CG': ('Congo (Republic)', '🇨🇬'),
    'CR': ('Costa Rica', '🇨🇷'),
    'CI': ('Côte d’Ivoire', '🇨🇮'),
    'HR': ('Croatia', '🇭🇷'),
    'CU': ('Cuba', '🇨🇺'),
    'CY': ('Cyprus', '🇨🇾'),
    'CZ': ('Czech Republic', '🇨🇿'),
    'DK': ('Denmark', '🇩🇰'),
    'DJ': ('Djibouti', '🇩🇯'),
    'DM': ('Dominica', '🇩🇲'),
    'DO': ('Dominican Republic', '🇩🇴'),
    'EC': ('Ecuador', '🇪🇨'),
    'EG': ('Egypt', '🇪🇬'),
    'SV': ('El Salvador', '🇸🇻'),
    'GQ': ('Equatorial Guinea', '🇬🇶'),
    'ER': ('Eritrea', '🇪🇷'),
    'EE': ('Estonia', '🇪🇪'),
    'SZ': ('Eswatini', '🇸🇿'),
    'ET': ('Ethiopia', '🇪🇹'),
    'FJ': ('Fiji', '🇫🇯'),
    'FI': ('Finland', '🇫🇮'),
    'FR': ('France', '🇫🇷'),
    'GA': ('Gabon', '🇬🇦'),
    'GM': ('Gambia', '🇬🇲'),
    'GE': ('Georgia', '🇬🇪'),
    'DE': ('Germany', '🇩🇪'),
    'GH': ('Ghana', '🇬🇭'),
    'GR': ('Greece', '🇬🇷'),
    'GD': ('Grenada', '🇬🇩'),
    'GT': ('Guatemala', '🇬🇹'),
    'GN': ('Guinea', '🇬🇳'),
    'GW': ('Guinea-Bissau', '🇬🇼'),
    'GY': ('Guyana', '🇬🇾'),
    'HT': ('Haiti', '🇭🇹'),
    'HN': ('Honduras', '🇭🇳'),
    'HU': ('Hungary', '🇭🇺'),
    'IS': ('Iceland', '🇮🇸'),
    'IN': ('India', '🇮🇳'),
    'ID': ('Indonesia', '🇮🇩'),
    'IR': ('Iran', '🇮🇷'),
    'IQ': ('Iraq', '🇮🇶'),
    'IE': ('Ireland', '🇮🇪'),
    'IL': ('Israel', '🇮🇱'),
    'IT': ('Italy', '🇮🇹'),
    'JM': ('Jamaica', '🇯🇲'),
    'JP': ('Japan', '🇯🇵'),
    'JO': ('Jordan', '🇯🇴'),
    'KZ': ('Kazakhstan', '🇰🇿'),
    'KE': ('Kenya', '🇰🇪'),
    'KI': ('Kiribati', '🇰🇮'),
    'KP': ('North Korea', '🇰🇵'),
    'KR': ('South Korea', '🇰🇷'),
    'KW': ('Kuwait', '🇰🇼'),
    'KG': ('Kyrgyzstan', '🇰🇬'),
    'LA': ('Laos', '🇱🇦'),
    'LV': ('Latvia', '🇱🇻'),
    'LB': ('Lebanon', '🇱🇧'),
    'LS': ('Lesotho', '🇱🇸'),
    'LR': ('Liberia', '🇱🇷'),
    'LY': ('Libya', '🇱🇾'),
    'LI': ('Liechtenstein', '🇱🇮'),
    'LT': ('Lithuania', '🇱🇹'),
    'LU': ('Luxembourg', '🇱🇺'),
    'MG': ('Madagascar', '🇲🇬'),
    'MW': ('Malawi', '🇲🇼'),
    'MY': ('Malaysia', '🇲🇾'),
    'MV': ('Maldives', '🇲🇻'),
    'ML': ('Mali', '🇲🇱'),
    'MT': ('Malta', '🇲🇹'),
    'MH': ('Marshall Islands', '🇲🇭'),
    'MR': ('Mauritania', '🇲🇷'),
    'MU': ('Mauritius', '🇲🇺'),
    'MX': ('Mexico', '🇲🇽'),
    'FM': ('Micronesia', '🇫🇲'),
    'MD': ('Moldova', '🇲🇩'),
    'MC': ('Monaco', '🇲🇨'),
    'MN': ('Mongolia', '🇲🇳'),
    'ME': ('Montenegro', '🇲🇪'),
    'MA': ('Morocco', '🇲🇦'),
    'MZ': ('Mozambique', '🇲🇿'),
    'MM': ('Myanmar', '🇲🇲'),
    'NA': ('Namibia', '🇳🇦'),
    'NR': ('Nauru', '🇳🇷'),
    'NP': ('Nepal', '🇳🇵'),
    'NL': ('Netherlands', '🇳🇱'),
    'NZ': ('New Zealand', '🇳🇿'),
    'NI': ('Nicaragua', '🇳🇮'),
    'NE': ('Niger', '🇳🇪'),
    'NG': ('Nigeria', '🇳🇬'),
    'MK': ('North Macedonia', '🇲🇰'),
    'NO': ('Norway', '🇳🇴'),
    'OM': ('Oman', '🇴🇲'),
    'PK': ('Pakistan', '🇵🇰'),
    'PW': ('Palau', '🇵🇼'),
    'PA': ('Panama', '🇵🇦'),
    'PG': ('Papua New Guinea', '🇵🇬'),
    'PY': ('Paraguay', '🇵🇾'),
    'PE': ('Peru', '🇵🇪'),
    'PH': ('Philippines', '🇵🇭'),
    'PL': ('Poland', '🇵🇱'),
    'PT': ('Portugal', '🇵🇹'),
    'QA': ('Qatar', '🇶🇦'),
    'RO': ('Romania', '🇷🇴'),
    'RU': ('Russia', '🇷🇺'),
    'RW': ('Rwanda', '🇷🇼'),
    'KN': ('Saint Kitts and Nevis', '🇰🇳'),
    'LC': ('Saint Lucia', '🇱🇨'),
    'VC': ('Saint Vincent and the Grenadines', '🇻🇨'),
    'WS': ('Samoa', '🇼🇸'),
    'SM': ('San Marino', '🇸🇲'),
    'ST': ('São Tomé and Príncipe', '🇸🇹'),
    'SA': ('Saudi Arabia', '🇸🇦'),
    'SN': ('Senegal', '🇸🇳'),
    'RS': ('Serbia', '🇷🇸'),
    'SC': ('Seychelles', '🇸🇨'),
    'SL': ('Sierra Leone', '🇸🇱'),
    'SG': ('Singapore', '🇸🇬'),
    'SK': ('Slovakia', '🇸🇰'),
    'SI': ('Slovenia', '🇸🇮'),
    'SB': ('Solomon Islands', '🇸🇧'),
    'SO': ('Somalia', '🇸🇴'),
    'ZA': ('South Africa', '🇿🇦'),
    'SS': ('South Sudan', '🇸🇸'),
    'ES': ('Spain', '🇪🇸'),
    'LK': ('Sri Lanka', '🇱🇰'),
    'SD': ('Sudan', '🇸🇩'),
    'SR': ('Suriname', '🇸🇷'),
    'SE': ('Sweden', '🇸🇪'),
    'CH': ('Switzerland', '🇨🇭'),
    'SY': ('Syria', '🇸🇾'),
    'TW': ('Taiwan', '🇹🇼'),
    'TJ': ('Tajikistan', '🇹🇯'),
    'TZ': ('Tanzania', '🇹🇿'),
    'TH': ('Thailand', '🇹🇭'),
    'TL': ('Timor-Leste', '🇹🇱'),
    'TG': ('Togo', '🇹🇬'),
    'TO': ('Tonga', '🇹🇴'),
    'TT': ('Trinidad and Tobago', '🇹🇹'),
    'TN': ('Tunisia', '🇹🇳'),
    'TR': ('Türkiye', '🇹🇷'),
    'TM': ('Turkmenistan', '🇹🇲'),
    'TV': ('Tuvalu', '🇹🇻'),
    'UG': ('Uganda', '🇺🇬'),
    'UA': ('Ukraine', '🇺🇦'),
    'AE': ('United Arab Emirates', '🇦🇪'),
    'GB': ('United Kingdom', '🇬🇧'),
    'US': ('United States', '🇺🇸'),
    'UY': ('Uruguay', '🇺🇾'),
    'UZ': ('Uzbekistan', '🇺🇿'),
    'VU': ('Vanuatu', '🇻🇺'),
    'VA': ('Vatican City', '🇻🇦'),
    'VE': ('Venezuela', '🇻🇪'),
    'VN': ('Vietnam', '🇻🇳'),
    'YE': ('Yemen', '🇾🇪'),
    'ZM': ('Zambia', '🇿🇲'),
    'ZW': ('Zimbabwe', '🇿🇼'),
    'PS': ('Palestine', '🇵🇸'),
    'PR': ('Puerto Rico', '🇵🇷'),
    'RE': ('Réunion', '🇷🇪'),
    'YT': ('Mayotte', '🇾🇹'),
    'SH': ('Saint Helena', '🇸🇭'),
    'EH': ('Western Sahara', '🇪🇭')
}

# Small Functions
def get_country_name(code: str) -> str:
    return country_list.get(code, (None, None))[0]

def get_country_flag(code: str) -> str:
    return country_list.get(code, (None, None))[1]

def get_country_by_emoji(emoji: str) -> str:
    return next((code for code, (name, flag) in country_list.items() if flag == emoji), None)

def get_country_by_name(name: str) -> str:
    return next((code for code, (country_name, flag) in country_list.items() if country_name == name), None)

# Pagination Functions
def construct_country_page(user_id: int) -> Tuple[str, InlineKeyboardMarkup]:
    params = get_params(user_id, UserState.AWAITING_COUNTRIES)
    page = params.get('page', 1)

    codes = list(country_list.keys())
    total_pages = (len(codes) - 1) // 10 + 1
    start = (page - 1) * 10
    end = start + 10
    page_items = codes[start:end]

    markup = InlineKeyboardMarkup(row_width = 5)
    buttons = []
    if page > 1:
        buttons.append(InlineKeyboardButton('‹ Previous', callback_data = 'previous_page_countries'))
    if page < total_pages:
        buttons.append(InlineKeyboardButton('Next ›', callback_data = 'next_page_countries'))

    markup.add(*buttons)
    return markup
