from aiogram import Bot, Dispatcher, executor, types
from keyboard import *
from sql_asyncio import *

API_TOKEN = '6124666764:AAEsHWHqaUfFKmokV9BhELYx6Q5rEpy_Rco'

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
audio_name_id = []


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    if message.from_user.last_name is None:
        name = f"{message.from_user.first_name}"
    else:
        name = f"{message.from_user.first_name} {message.from_user.last_name}"
    mess = f'Привіт, {name}'
    await message.answer(text=mess, reply_markup=await main_menu())
    await add_user(message.from_user.id)
    await message.delete()


@dp.message_handler(content_types=['audio'])
async def audio_handler(message: types.Message):
    global audio_name_id
    if message.audio.performer is None and message.audio.title is None:
        audio_name_id.append(message.audio.file_name.replace("'", ''))
    else:
        audio_name_id.append(f"{message.audio.performer} {message.audio.title}".replace("'", ''))
    audio_name_id.append(message.audio.file_id)
    audio_name_id.append(message.chat.id)
    if await check_playlist(message.chat.id):
        await message.delete()
        await message.answer(f'Виберіть плейлист для добавлення пісні: <b>{audio_name_id[0]}</b>',
                             parse_mode='HTML',
                             reply_markup=await inline('supplement', message.chat.id))
    else:
        await message.answer('Ви ще не створили жодного плейлиста\nСтворіть плейлист і відправте трек наново')


@dp.message_handler()
async def mess(message: types.Message):
    if message.text == 'Створити плейлист':
        await message.answer('Напишіть назву плейлисту')
    else:
        await message.answer(f'Створити плейлист з назвою:\n <b>{message.text}</b>',
                             parse_mode='HTML',
                             reply_markup=await yes_or_not(message.text))


@dp.callback_query_handler()
async def ikb_close(callback: types.CallbackQuery):
    global audio_name_id
    if callback.data.startswith('supplement'):
        name_playlist = callback.data.replace('supplement', '')
        # await callback.message.answer(name_playlist)
        await add_track(name_playlist, audio_name_id[0], audio_name_id[1], audio_name_id[2])
        await callback.message.edit_text(f'Додано <b>{audio_name_id[0]}</b>\nдо <b>{name_playlist}</b>',
                                         parse_mode='HTML')
        audio_name_id = []
    elif callback.data == 'close':
        await callback.message.delete()
    elif callback.data == 'cancellation':
        await callback.message.delete()
        audio_name_id = []
    elif callback.data.startswith('yes'):
        name_playlist = callback.data.replace('yes', '')
        await add_playlist(callback.message.chat.id, name_playlist)
        await callback.answer(f'Створено {name_playlist}')
        await callback.message.delete()

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)