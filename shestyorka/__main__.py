from shestyorka import bot, street_categories, districts, user_list, check_user
from telebot.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from time import sleep
from shestyorka.assignment import Assignment
from datetime import datetime


# регистрация по заявке, вручную
# /give_me_NARYAD -> список выбранных, предложение добавить -> выбор категории -> выбор рэса -> |
#                                     ^                                                         v
#                                     |----------------------------------------------------------

selected_entries = {}  # {#user_id#: [{'name': #name#, 'district': #district#}]}


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

    return kb


@bot.callback_query_handler(func=lambda call: call.data.startswith('cat_kb'))
def cat_kb_callback(call: CallbackQuery):
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
    sleep(2)
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
            text='Да на, заебешь',
            chat_id=user_id,
            message_id=message_id,
            reply_markup=None
        )

    bot.send_document(
        chat_id=user_id,
        document=open(filename, 'rb'),
        caption=filename,
        visible_file_name=filename,
        disable_content_type_detection=True
    )
    return


@bot.callback_query_handler(func=lambda call: call.data.startswith('assignment'))
def assignment_callback(call: CallbackQuery):
    if call.data == 'assignment.start':
        assignment_start(call.from_user.id, call.message.id)
        return
    elif call.data == 'assignment.add_category':
        assignment_add_category(call.from_user.id, call.message.id)
        return
    elif call.data == 'assignment.remove_all':
        assignment_remove_all(call.from_user.id, call.message.id)
        return
    elif call.data == 'assignment.create':
        assignment_create(call.from_user.id, call.message.id)
        return


@check_user()
@bot.message_handler(commands=['start'])
def start(message: Message):
    bot.send_message(
        message.chat.id,
        'Ну привет. Что бы получить наряд - жми /give_me_naryad. Больше ничего я пока не умею.'
    )
    return


@check_user()
@bot.message_handler(commands=['give_me_naryad'])
def give_me_NARYAD(message: Message):
    selected_entries.update({message.chat.id: []})
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('ХОЧУ, ДАЙ', callback_data='assignment.start'))
    bot.send_message(message.chat.id, 'Хочешь наряд?', reply_markup=markup)
    return


if __name__ == "__main__":
    bot.polling()
