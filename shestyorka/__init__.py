from telebot import TeleBot
from config import TELEGRAM_TOKEN
from users import user_list

street_categories = [
{'telegram_chat_name': '00', 'name': 'Улицы категории 00', 'telegram_keyboard_data': 'oo'},
{'telegram_chat_name': 'А', 'name': 'Улицы категории А', 'telegram_keyboard_data': 'a'},
{'telegram_chat_name': 'Б', 'name': 'Улицы категории Б', 'telegram_keyboard_data': 'b'},
{'telegram_chat_name': 'В', 'name': 'Улицы категории В', 'telegram_keyboard_data': 'c'},
{'telegram_chat_name': 'АХП', 'name': 'АХП', 'telegram_keyboard_data': 'akhp'},
{'telegram_chat_name': 'Часы', 'name': 'Часы', 'telegram_keyboard_data': 'clock'},
{'telegram_chat_name': 'Спец.Часы', 'name': 'Спец. маршрут Часы', 'telegram_keyboard_data': 'spec_clock'},
{'telegram_chat_name': 'МУ', 'name': 'Моя улица', 'telegram_keyboard_data': 'my'},
{'telegram_chat_name': 'УНО центра', 'name': 'УНО Центра', 'telegram_keyboard_data': 'uno_center'},
{'telegram_chat_name': 'Иллюминация', 'name': 'Иллюминация', 'telegram_keyboard_data': 'illum'},
{'telegram_chat_name': 'Спец1', 'name': 'Спец. маршрут 1', 'telegram_keyboard_data': 'spec1'},
{'telegram_chat_name': 'Спец.АХП', 'name': 'АХП Спец. маршрут', 'telegram_keyboard_data': 'spec_akhp'},
{'telegram_chat_name': 'ЛО', 'name': 'Ландшафтное освещение', 'telegram_keyboard_data': 'lo'},
{'telegram_chat_name': 'Спец.ЛО', 'name': 'Спец. маршрут ЛО', 'telegram_keyboard_data': 'spec_lo'}
]
districts = [
    'САО', 'СВАО', 'ВАО', 'ЮВАО', 'ЮАО', 'ЮЗАО', 'ЗАО', 'СЗАО', 'ЦАО', 'ТиНАО'
]

bot = TeleBot(TELEGRAM_TOKEN)


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