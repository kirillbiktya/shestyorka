# Шестерка бот

Запуск бота либо с помощью `python -m shestyorka`, либо используя systemd юнит-файл.
Также можно запустить, используя `bash run.sh`

ОБЯЗАТЕЛЬНО! должен быть файл `config.py` с содержанием типа: 
```python
TELEGRAM_TOKEN = "blah-blah-blah"
```

Файл `users.py` должен содержать список типа:
```python
user_list = [
    {'access_level': 0, 'telegram_id': 123456789, 'full_name': 'Иванов И. И.'}, # админ
    {'access_level': 1, 'telegram_id': 1234567893, 'full_name': 'Иванов И. И.'}, # рядовой юзер
    {'access_level': 1, 'telegram_id': 1234567892, 'full_name': 'Иванов И. И.'},
    {'access_level': 1, 'telegram_id': 1234567891, 'full_name': 'Иванов И. И.'},
    {'access_level': 1, 'telegram_id': 1234567890, 'full_name': 'Иванов И. И.'},
    # ....
    ]
```
