from aiogram.types import *
from sql_asyncio import *
from asincio_bot import *


async def main_menu():
    kb1 = ReplyKeyboardMarkup(resize_keyboard=True)
    kb1.add(KeyboardButton('Показати плейлисти'), KeyboardButton('Створити плейлист'))
    kb1.add(KeyboardButton('Почати прослуховування'), KeyboardButton('Видалити'))
    return kb1


async def inline(func, chat_id):
    markup_inline = InlineKeyboardMarkup()
    for name_playlist in await check_playlist(chat_id):
        markup_inline.row(InlineKeyboardButton(name_playlist,
                                               callback_data=f"{func}{name_playlist}"))
    markup_inline.add(InlineKeyboardButton('Відмінити', callback_data=f"cancellation"))
    return markup_inline
# print(asyncio.get_event_loop().run_until_complete(inline('supp', '428392590', 'dfsdfsdf')))


async def yes_or_not(name_playlist):
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton("Так", callback_data=f'yes {name_playlist}')],
        [InlineKeyboardButton('Ні', callback_data='not')]
        ]
        )
    return ikb
