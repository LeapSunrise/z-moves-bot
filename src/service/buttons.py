# -*- coding: utf-8 -*-
#!/usr/bin/python3.8.5
from datetime import date

import telebot

from src.schedule_parser.schedule_parser import get_current_week

current_week = get_current_week()
current_day = date.today().weekday()

# main_menu
schedule_button = '📆 Расписание'
settings_button = '⚙ Настройки'
links_button = '🔗 Ссылки'
hotlines_button = '👺 Хотлайны'
mails_button = '❓❓❓'
info_button = 'ℹ️Инфо'
help_button = '❓ Помощь'

# main_menu/links
inline_add_link_button = telebot.types.InlineKeyboardButton(text='Добавить ссылку',
                                                            callback_data='add_link')
inline_change_link_button = telebot.types.InlineKeyboardButton(text='Изменить ссылку',
                                                               callback_data='change_link')
inline_remove_link_button = telebot.types.InlineKeyboardButton(text='Удалить ссылку',
                                                               callback_data='remove_link')
inline_remove_link_confirm_button = telebot.types.InlineKeyboardButton(text='Подтвердить',
                                                                       callback_data='confirm_remove_link')
inline_remove_link_cancel_button = telebot.types.InlineKeyboardButton(text='Отмена',
                                                                      callback_data='cancel_remove_link')

inline_lec_button = telebot.types.InlineKeyboardButton(text='Лек',
                                                       callback_data='lec')
inline_prac_button = telebot.types.InlineKeyboardButton(text='Прак',
                                                        callback_data='prac')
inline_lab_button = telebot.types.InlineKeyboardButton(text='Лаб',
                                                       callback_data='lab')

inline_links_first_back_button = telebot.types.InlineKeyboardButton(text='Назад',
                                                                    callback_data='links_first_back_button')
inline_links_second_back_button = telebot.types.InlineKeyboardButton(text='Назад',
                                                                     callback_data='links_second_back_button')

# links
add_password_button = 'Добавить пароль'
change_password_button = 'Изменить пароль'
change_link_button = 'Изменить ссылку'

# main_menu/hotlines
inline_add_hotline_button = telebot.types.InlineKeyboardButton(text='Добавить хотлайн',
                                                               callback_data='add_hotline')
inline_change_hotline_button = telebot.types.InlineKeyboardButton(text='Изменить хотлайн',
                                                                  callback_data='change_hotline')
inline_remove_hotline_button = telebot.types.InlineKeyboardButton(text='Удалить хотлайн',
                                                                  callback_data='remove_hotline')

inline_remove_hotline_confirm_button = telebot.types.InlineKeyboardButton(text='Подтвердить',
                                                                          callback_data='confirm_remove_hotline')
inline_remove_hotline_cancel_button = telebot.types.InlineKeyboardButton(text='Отмена',
                                                                         callback_data='cancel_remove_hotline')

inline_first_back_button_hotlines = telebot.types.InlineKeyboardButton(text='Назад',
                                                                       callback_data='hotlines_first_back_button')


# schedule_menu
today_day_button = "📝 Расписание на сегодня"
tomorrow_day_button = "📝 Расписание на завтра"
week1_button = '1️⃣ Неделя ✅' if current_week == 1 else '1️⃣ Неделя'
week2_button = '2️⃣ Неделя ✅' if current_week == 2 else '2️⃣ Неделя'

week1_day_buttons = [
    '🤯 Пн' + (' ✅' if current_day == 0 and current_week == 1 else ''),
    '😫 Вт' + (' ✅' if current_day == 1 and current_week == 1 else ''),
    '😞 Ср' + (' ✅' if current_day == 2 and current_week == 1 else ''),
    '😏 Чт' + (' ✅' if current_day == 3 and current_week == 1 else ''),
    '🤤 Пт' + (' ✅' if current_day == 4 and current_week == 1 else ''),
]

week2_day_buttons = [
    '🤯 Пн' + (' ✅' if current_day == 0 and current_week == 2 else ''),
    '😫 Вт' + (' ✅' if current_day == 1 and current_week == 2 else ''),
    '😞 Ср' + (' ✅' if current_day == 2 and current_week == 2 else ''),
    '😏 Чт' + (' ✅' if current_day == 3 and current_week == 2 else ''),
    '🤤 Пт' + (' ✅' if current_day == 4 and current_week == 2 else ''),
]

# settings_menu
notifications_button = '📢 Уведомления'
change_group_button = '‍🎓 Изменить группу'
import_button = '♿️Импорт/Экспорт'
import_inline_input_token = telebot.types.InlineKeyboardButton(text='Ввести токен', callback_data='token_input')

# global buttons
back_button = '⬅️Назад'
confirm_button = '✅ Готово'
cancel_button = '❌ Отмена'

# API bad request
dead_api = 'Проверка на жизнь API'
