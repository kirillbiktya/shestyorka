from telebot import TeleBot
from users import user_list
from time import sleep

from flask import Flask, request, abort
from telebot.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton, Update

import config
from shestyorka.assignment import Assignment

street_categories = [
    {'telegram_chat_name': '00', 'name': 'Улицы категории 00', 'telegram_keyboard_data': 'oo'},
    {'telegram_chat_name': 'А', 'name': 'Улицы категории А', 'telegram_keyboard_data': 'a'},
    {'telegram_chat_name': 'Б', 'name': 'Улицы категории Б', 'telegram_keyboard_data': 'b'},
    {'telegram_chat_name': 'В', 'name': 'Улицы категории В', 'telegram_keyboard_data': 'c'},
    {'telegram_chat_name': 'АХП', 'name': 'АХП', 'telegram_keyboard_data': 'akhp'},
    {'telegram_chat_name': 'Спец.АХП', 'name': 'АХП Спец. маршрут', 'telegram_keyboard_data': 'spec_akhp'},
    {'telegram_chat_name': 'Часы', 'name': 'Часы', 'telegram_keyboard_data': 'clock'},
    {'telegram_chat_name': 'Спец.Часы', 'name': 'Спец. маршрут Часы', 'telegram_keyboard_data': 'spec_clock'},
    {'telegram_chat_name': 'МУ', 'name': 'Моя улица', 'telegram_keyboard_data': 'my'},
    {'telegram_chat_name': 'УНО центра', 'name': 'УНО Центра', 'telegram_keyboard_data': 'uno_center'},
    {'telegram_chat_name': 'Иллюминация', 'name': 'Иллюминация', 'telegram_keyboard_data': 'illum'},
    {'telegram_chat_name': 'Спец1', 'name': 'Спец. маршрут 1', 'telegram_keyboard_data': 'spec1'},
    {'telegram_chat_name': 'Спец2', 'name': 'Спец. маршрут 2', 'telegram_keyboard_data': 'spec2'},
    {'telegram_chat_name': 'ЛО', 'name': 'Ландшафтное освещение', 'telegram_keyboard_data': 'lo'},
    {'telegram_chat_name': 'Спец.ЛО', 'name': 'Спец. маршрут ЛО', 'telegram_keyboard_data': 'spec_lo'},
    {'telegram_chat_name': 'АХП Развязки', 'name': 'АХП Развязки МКАД', 'telegram_keyboard_data': 'ahp_mkad'}
]
districts = [
    'САО', 'СВАО', 'ВАО', 'ЮВАО', 'ЮАО', 'ЮЗАО', 'ЗАО', 'СЗАО', 'ЦАО', 'ТиНАО'
]

bot = TeleBot(config.API_TOKEN)


def check_user():
    def _wrapper(func):
        def __wrapper(*args, **kwargs):
            user_id = args[0].chat.id

            if len(list(filter(lambda x: x['telegram_id'] == user_id, user_list))) == 0:
                bot.send_message(user_id, 'Не зарегистрирован.')
                return

            return func(*args, **kwargs)

        return __wrapper

    return _wrapper


app = Flask('shestyorka_webhook')

selected_entries = {}  # {#user_id#: [{'name': #name#, 'district': #district#}]}


def prepare_list(user_id: int):
    selected_entries.update({user_id: []})


def construct_inline_keyboard_with_categories():
    kb = InlineKeyboardMarkup()
    kb.row_width = 3
    row = []
    counter = 0
    for category in street_categories:
        row.append(
            InlineKeyboardButton(
                text=category['telegram_chat_name'], callback_data='cat_kb.' + category['telegram_keyboard_data']
            )
        )
        counter += 1
        if counter == 3:
            counter = 0
            kb.add(*row)
            row = []

    kb.add(*row)

    kb.add(InlineKeyboardButton(text='Отмена', callback_data='cat_kb.cancel'))

    return kb


def construct_inline_keyboard_with_districts(selected_category):
    kb = InlineKeyboardMarkup()
    kb.row_width = 3
    row = []
    counter = 0
    for district in districts:
        row.append(
            InlineKeyboardButton(
                text=district, callback_data='district.' + selected_category + '.' + district
            )
        )
        counter += 1
        if counter == 3:
            counter = 0
            kb.add(*row)
            row = []

    kb.add(*row)

    kb.add(InlineKeyboardButton(text='Отмена', callback_data='district.cancel'))

    return kb


@bot.callback_query_handler(func=lambda call: call.data.startswith('cat_kb'))
def cat_kb_callback(call: CallbackQuery):
    if call.data == 'cat_kb.cancel':
        assignment_start(call.from_user.id, call.message.id)
        return

    selected_category = call.data.split('.')[1]

    markup = construct_inline_keyboard_with_districts(selected_category)
    bot.edit_message_text(
        text='Теперь выбери округ для этой категории:',
        chat_id=call.from_user.id,
        message_id=call.message.id,
        reply_markup=markup
    )
    return


@bot.callback_query_handler(func=lambda call: call.data.startswith('district'))
def district_callback(call: CallbackQuery):
    try:
        if call.data == 'district.cancel':
            assignment_start(call.from_user.id, call.message.id)
            return

        selected_category = call.data.split('.')[1]
        selected_district = call.data.split('.')[2]

        category_name = list(
            filter(
                lambda x: x['telegram_keyboard_data'] == selected_category, street_categories
            )
        )[0]['name']

        selected_entries[call.from_user.id].append({'name': category_name, 'district': selected_district})

        assignment_start(call.from_user.id, call.message.id)
        return
    except KeyError:
        prepare_list(call.from_user.id)
        assignment_start(call.from_user.id, call.message.id)
        bot.answer_callback_query(call.id, text='Ошибка, начинаем заново...')
        return


def assignment_start(user_id, message_id):
    user_selected = selected_entries[user_id]
    text = 'Ты выбрал:\n\n'
    if len(user_selected) > 0:
        for entry in user_selected:
            text += entry['name'] + ', ' + entry['district'] + '\n'
    else:
        text += 'Да нихуя ты пока не выбрал :)'

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text='Добавить категорию', callback_data='assignment.add_category'))
    if len(user_selected) > 0:
        markup.add(InlineKeyboardButton(text='Очистить выбор', callback_data='assignment.remove_all'))
        markup.add(InlineKeyboardButton(text='Я кончил, дай наряд', callback_data='assignment.create'))

    bot.edit_message_text(text=text, chat_id=user_id, message_id=message_id, reply_markup=markup)
    return


def assignment_remove_all(user_id, message_id):
    selected_entries[user_id] = []

    bot.edit_message_text(text='Список очищен', chat_id=user_id, message_id=message_id, reply_markup=None)
    sleep(0.5)
    assignment_start(user_id, message_id)


def assignment_add_category(user_id, message_id):
    markup = construct_inline_keyboard_with_categories()
    bot.edit_message_text(text='Выбери категорию:', chat_id=user_id, message_id=message_id, reply_markup=markup)
    return


def assignment_create(user_id, message_id):
    user_name = list(filter(lambda x: x['telegram_id'] == user_id, user_list))[0]['full_name']
    a = Assignment(user_name, selected_entries[user_id])
    result = a.create()

    filename = 'Наряд-задание ' + result[1] + ' ' + user_name + '.xlsx'

    result[0].save(filename)

    if result[2]:
        bot.edit_message_text(
            text='Ты выбрал больше семи значений, я записал только семь, остальное пиши сам, заебал',
            chat_id=user_id,
            message_id=message_id,
            reply_markup=None
        )
    else:
        bot.edit_message_text(
            text='Твой наряд-задание ⬇️',
            chat_id=user_id,
            message_id=message_id,
            reply_markup=None
        )
    # caption = 'Нажми на текст внизу, что бы скопировать:\n<pre>' + '.'.join(filename.split('.')[:-1]) + '</pre>'
    bot.send_document(
        chat_id=user_id,
        document=open(filename, 'rb'),
        # caption=caption,
        visible_file_name=filename,
        disable_content_type_detection=True,
        parse_mode='html'
    )
    return


@bot.callback_query_handler(func=lambda call: call.data.startswith('assignment'))
def assignment_callback(call: CallbackQuery):
    try:
        if call.data == 'assignment.start':
            assignment_start(call.from_user.id, call.message.id)
            bot.answer_callback_query(call.id)
            return
        elif call.data == 'assignment.add_category':
            assignment_add_category(call.from_user.id, call.message.id)
            bot.answer_callback_query(call.id)
            return
        elif call.data == 'assignment.remove_all':
            assignment_remove_all(call.from_user.id, call.message.id)
            bot.answer_callback_query(call.id)
            return
        elif call.data == 'assignment.create':
            assignment_create(call.from_user.id, call.message.id)
            bot.answer_callback_query(call.id, text='Работаю на этим...')
            return
    except KeyError:
        prepare_list(call.from_user.id)
        assignment_start(call.from_user.id, call.message.id)
        bot.answer_callback_query(call.id, text='Снова Гречка дотыкался по кнопкам, начинаем заново...')
        return


@bot.message_handler(commands=['start'])
@check_user()
def start(message: Message):
    bot.send_message(
        message.from_user.id,
        'Ну привет. Что бы получить наряд - жми /give_me_naryad. Больше ничего я пока не умею.'
    )
    return


@bot.message_handler(commands=['give_me_naryad'])
@check_user()
def give_me_NARYAD(message: Message):
    prepare_list(message.from_user.id)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('ХОЧУ, ДАЙ', callback_data='assignment.start'))
    bot.send_message(message.from_user.id, 'Хочешь наряд?', reply_markup=markup)
    return


@app.route('/', methods=['GET', 'HEAD'])
def index():
    return ''


@app.route(config.WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        abort(403)
