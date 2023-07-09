import telebot
from telebot import types
from audio_bot.sql import *

bot = telebot.TeleBot('6124666764:AAEsHWHqaUfFKmokV9BhELYx6Q5rEpy_Rco')
audio_name_id = []


def mark_up():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    k1 = types.KeyboardButton('Показати плейлисти')
    k2 = types.KeyboardButton('Створити плейлист')
    k3 = types.KeyboardButton('Почати прослуховування')
    k4 = types.KeyboardButton('Видалити')
    markup.add(k1, k2, k3, k4)
    return markup


def inline(func, chat_id):
    markup_inline = types.InlineKeyboardMarkup()
    for name_playlist in check_playlist(chat_id):
        markup_inline.row(types.InlineKeyboardButton(name_playlist, callback_data=f"{name_playlist} {func}"))
    return markup_inline


def not_playlist(message, texts='Ви ще не створили жодного плейлисту'):
    bot.send_message(message.chat.id, texts, reply_markup=mark_up())


@bot.message_handler(commands=['start'])
def start(message):
    if message.from_user.last_name is None:
        name = f"{message.from_user.first_name}"
    else:
        name = f"{message.from_user.first_name} {message.from_user.last_name}"
    mess = f'Привіт, {name}'
    bot.send_message(message.chat.id, mess, reply_markup=mark_up())
    connect_db(message.chat.id)


@bot.message_handler(commands=['help'])
def help(message):
    markup_inline = types.InlineKeyboardMarkup()
    for _ in range(5):
        markup_inline.row(types.InlineKeyboardButton('Героям Слава', callback_data=f"Героям Слава"))
    bot.send_message(message.chat.id, '<u><b>Слава Україні!</b></u>\nВибери варіант відповіді',
                     reply_markup=markup_inline, parse_mode="HTML")


@bot.message_handler(content_types=['audio'])
def handle_audio(message):
    global audio_name_id
    if message.audio.performer is None and message.audio.title is None:
        audio_name_id.append(message.audio.file_name.replace("'", ''))
    else:
        audio_name_id.append(f"{message.audio.performer} {message.audio.title}".replace("'", ''))
    audio_name_id.append(message.audio.file_id)

    # print(audio_name_id)
    if check_playlist(message.chat.id):
        bot.send_message(message.chat.id, f'Виберіть плейлист для добавлення пісні',
                         reply_markup=inline('supplement', message.chat.id))
    else:
        not_playlist(message, 'Ви ще не створили жодного плейлиста\nСтворіть плейлист і відправте трек наново')


@bot.message_handler(content_types=['text'])
def text(message):

    if message.text == 'Створити плейлист':
        bot.send_message(message.chat.id, 'Напишіть назву плейлисту')

    elif message.text == 'Видалити' or message.text == 'Ні':
        delete = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        d1 = types.KeyboardButton('Видалити плейлист з усім вмістом')
        d2 = types.KeyboardButton('Видалити конкретний трек')
        d3 = types.KeyboardButton('Назад')
        delete.add(d1, d2, d3)
        bot.send_message(message.chat.id, 'Видалити', reply_markup=delete)

    elif message.text == 'sos':
        markup_inline = types.InlineKeyboardMarkup()
        a = [1, 2, 3, 4]
        for name_playlist in a:
            markup_inline.row(types.InlineKeyboardButton(name_playlist, callback_data=f"{a}"))
        bot.send_message(message.chat.id, f'Виберіть плейлист для видалення треку',
                         reply_markup=markup_inline)

    elif message.text == 'Видалити плейлист з усім вмістом':
        if check_playlist(message.chat.id):
            bot.send_message(message.chat.id, f'Виберіть плейлист для видалення',
                             reply_markup=inline('delete_playlist', message.chat.id))
        else:
            not_playlist(message)

    elif message.text == 'Видалити конкретний трек':
        if check_playlist(message.chat.id):
            bot.send_message(message.chat.id, f'Виберіть плейлист для видалення треку',
                             reply_markup=inline('delete_trak', message.chat.id))

    elif message.text == 'Показати плейлисти':
        if check_playlist(message.chat.id):
            for i in check_playlist(message.chat.id):
                bot.send_message(message.chat.id, i)
        else:
            not_playlist(message)

    elif message.text == 'Назад':
        bot.send_message(message.chat.id, 'Назад', reply_markup=mark_up())

    elif message.text == 'Почати прослуховування':
        if check_playlist(message.chat.id):
            bot.send_message(message.chat.id, f'Виберіть плейлист',
                             reply_markup=inline('listen_playlist', message.chat.id))
        else:
            not_playlist(message)

    elif ''.join(message.text.split()):
        bot.send_message(message.chat.id, create_playlist(message.chat.id, ' '.join(message.text.split())),
                         reply_markup=mark_up())


@bot.callback_query_handler(func=lambda call: True)
def test_callback(call):
    global audio_name_id
    if call.message:
        if call.data == 'Героям Слава':
            bot.send_message(call.message.chat.id, '<b>Правильна відповідь</b>', parse_mode="HTML")

        # додавати треки до плейлисту
        elif call.data.split()[-1] == 'supplement':
            name_playlist = ' '.join(call.data.split()[:-1])
            name_trak = audio_name_id[0]
            id_trak = audio_name_id[1]
            supplement_trak(call.message.chat.id, name_playlist, name_trak, id_trak)
            bot.send_message(call.message.chat.id, f"Трек:\n{audio_name_id[0]}\nДодано до:\n"
                                                   f"{name_playlist}")
            audio_name_id = []

        # слухати пісні
        elif call.data.split()[-1] == 'listen_playlist':
            name_playlist = ' '.join(call.data.split()[:-1])
            if listen_playlist(call.message.chat.id, name_playlist):
                for i in listen_playlist(call.message.chat.id, name_playlist):
                    bot.send_audio(call.message.chat.id, i)
            else:
                bot.send_message(call.message.chat.id, 'Цей плейлист не має треків')

        # видалити плейлист
        elif call.data.split()[-1] == 'delete_playlist':
            name_playlist = ' '.join(call.data.split()[:-1])
            bot.send_message(call.message.chat.id, delete_playlist(call.message.chat.id, name_playlist),
                             parse_mode="HTML")

        # вибрати плейлист для видалення треку
        elif call.data.split()[-1] == 'delete_trak':
            name_playlist = ' '.join(call.data.split()[:-1])
            if trak_in_playlist(call.message.chat.id, name_playlist):
                markup_inline = types.InlineKeyboardMarkup()
                for name_trak in trak_in_playlist(call.message.chat.id, name_playlist):
                    markup_inline.row(types.InlineKeyboardButton(name_trak['name_trak'],
                                                                 callback_data=f"{name_playlist}:"
                                                                               f"{name_trak['id']}"))
                bot.send_message(call.message.chat.id, 'Виберіть трек для видалення',
                                 reply_markup=markup_inline)
            else:
                bot.send_message(call.message.chat.id, f'В плейлисті <b>{name_playlist}</b> немає треків',
                                 parse_mode="HTML")

        # видалити трек в плейлисті
        elif call.data.split(':')[-1].isdigit():
            bot.send_message(call.message.chat.id,
                             f"Ви видалили трек <b>{delete(call.data.split(':')[-1])}</b> в плейлисті "
                             f"<b>{call.data.split(':')[0]}</b>", parse_mode="HTML")


bot.polling(none_stop=True)