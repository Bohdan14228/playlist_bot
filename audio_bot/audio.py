import telebot
from telebot import types

bot = telebot.TeleBot('5889277887:AAGi5eXKj0ajY02vdkPeYuc-rvQzXyKkGLE')
all_audio = {}
audio_name_id = []
delete_trak_calldata = ''


def mark_up():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    k1 = types.KeyboardButton('Показати плейлист')
    k2 = types.KeyboardButton('Створити плейлист')
    k3 = types.KeyboardButton('Почати прослуховування')
    k4 = types.KeyboardButton('Видалити')
    markup.add(k1, k2, k3, k4)
    return markup


def inline(func):
    markup_inline = types.InlineKeyboardMarkup()
    for name_playlist in all_audio:
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


@bot.message_handler(commands=['help'])
def help(message):
    markup_inline = types.InlineKeyboardMarkup()
    for _ in range(5):
        markup_inline.row(types.InlineKeyboardButton('Героям Слава', callback_data=f"Героям Слава"))
    bot.send_message(message.chat.id, 'Вибери варіант відповіді\n<u><b>Слава Україні!</b></u>',
                     reply_markup=markup_inline, parse_mode="HTML")


@bot.message_handler(content_types=['audio'])
def handle_audio(message):
    global audio_name_id
    global all_audio
    if message.audio.performer is None and message.audio.title is None:
        audio_name_id.append(message.audio.file_name)
    else:
        audio_name_id.append(f"{message.audio.performer} {message.audio.title}")
    audio_name_id.append(message.audio.file_id)
    if all_audio:
        bot.send_message(message.chat.id, f'Виберіть плейлист для добавлення пісні', reply_markup=inline('supplement'))
    else:
        not_playlist(message, 'Ви ще не створили жодного плейлиста\nСтворіть плейлист і відправте трек наново')


@bot.message_handler(content_types=['text'])
def text(message):
    global all_audio
    if message.text == 'Показати плейлист':
        if all_audio:
            for i in all_audio:
                bot.send_message(message.chat.id, i)
        else:
            # bot.send_message(message.chat.id, 'Ви не додали жодної пісні')
            not_playlist(message)

    elif message.text == 'Створити плейлист':
        bot.send_message(message.chat.id, 'Напишіть назву плейлисту')

    elif message.text == 'Видалити' or message.text == 'Ні':
        delete = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        d1 = types.KeyboardButton('Видалити плейлист з усім вмістом')
        d2 = types.KeyboardButton('Видалити конкретний трек')
        d3 = types.KeyboardButton('Назад')
        delete.add(d1, d2, d3)
        bot.send_message(message.chat.id, 'Видалити', reply_markup=delete)

    elif message.text == 'Видалити плейлист з усім вмістом':
        if all_audio:
            bot.send_message(message.chat.id, f'Виберіть плейлист для видалення',
                             reply_markup=inline('delete_playlist'))
        else:
            not_playlist(message)

    elif message.text == 'Видалити конкретний трек':
        if all_audio:
            bot.send_message(message.chat.id, f'Виберіть плейлист для видалення треку',
                             reply_markup=inline('delete_trak'))
        else:
            not_playlist(message)

    # elif message.text == 'Так':
    #     markup_inline = types.InlineKeyboardMarkup()
    #     for name_playlist in all_audio:
    #         markup_inline.row(types.InlineKeyboardButton(name_playlist, callback_data=f"{name_playlist}"))
    #     return markup_inline

    elif message.text == 'Назад':
        bot.send_message(message.chat.id, 'Назад', reply_markup=mark_up())

    elif message.text == 'Почати прослуховування':
        if all_audio:
            bot.send_message(message.chat.id, f'Виберіть плейлист', reply_markup=inline('listen_playlist'))
        else:
            not_playlist(message)

    elif message.text.isalpha():
        if message.text in all_audio:
            bot.send_message(message.chat.id, 'Плейлист з такою назвою вже існує', reply_markup=mark_up())
        else:
            all_audio[message.text] = {}
            bot.send_message(message.chat.id, f'Створено плейлист: {message.text}', reply_markup=mark_up())


@bot.callback_query_handler(func=lambda call: True)
def test_callback(call):
    global audio_name_id
    global all_audio
    global delete_trak_calldata
    if call.message:

        # додавати треки до плейлисту
        if call.data.split()[-1] == 'supplement':
            all_audio[' '.join(call.data.split()[:-1])][audio_name_id[0]] = audio_name_id[1]
            bot.send_message(call.message.chat.id, f"Трек:\n{audio_name_id[0]}\nДодано до:\n"
                                                   f"{' '.join(call.data.split()[:-1])}")
            audio_name_id = []

        # слухати пісні
        elif call.data.split()[-1] == 'listen_playlist':
            calldata = ' '.join(call.data.split()[:-1])
            if all_audio[calldata]:
                for i in all_audio[calldata]:
                    bot.send_audio(call.message.chat.id, all_audio[calldata][i])
            else:
                bot.send_message(call.message.chat.id, 'Цей плейлист не має треків')

        # видалити плейлист
        elif call.data.split()[-1] == 'delete_playlist':
            calldata = ' '.join(call.data.split()[:-1])
            del all_audio[calldata]
            bot.send_message(call.message.chat.id, f'Ви видалили плейлист: {calldata}')

        # вибрати плейлист для видалення треку
        elif call.data.split()[-1] == 'delete_trak':
            calldata = ' '.join(call.data.split()[:-1])
            if all_audio[calldata]:
                markup_inline = types.InlineKeyboardMarkup()
                for name_trak in all_audio[calldata]:
                    markup_inline.row(types.InlineKeyboardButton(name_trak, callback_data=f"{calldata}:{name_trak}"))
                bot.send_message(call.message.chat.id, 'Виберіть трек для видалення',
                                 reply_markup=markup_inline)
            else:
                bot.send_message(call.message.chat.id, f'В плейлисті <b>{calldata}</b> немає треків', parse_mode="HTML")

        # видалити трек в плейлисті
        elif call.data.split(':')[0] in all_audio and call.data.split(':')[1] in all_audio[call.data.split(':')[0]]:
            bot.send_message(call.message.chat.id, f"Ви видалили трек <b>{call.data.split(':')[1]}</b> в плейлисті "
                                                   f"<b>{call.data.split(':')[0]}</b>", parse_mode="HTML")
            del all_audio[call.data.split(':')[0]][call.data.split(':')[1]]


bot.polling(none_stop=True)
