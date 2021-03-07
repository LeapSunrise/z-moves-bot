import telebot
from datetime import datetime
from schedule_parser.schedule_parser import *
from service.buttons import *

not_available_reply = '⛔ В разработке'


def dynamic_menu_links_inline_keyboard_generator(chat_id):
    """
    Генерирует main_menu/links клавиатуру.
    :param chat_id:
    :return:
    """
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(inline_add_link_button)
    if db.get_links(chat_id) is not None:
        keyboard.add(inline_change_link_button)
        keyboard.add(inline_remove_link_button)
    return keyboard


def dynamic_menu_hotlines_inline_keyboard_generator(chat_id):
    """

    :param chat_id:
    :return:
    """
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(inline_add_hotline_button)
    if db.get_hotlines(chat_id) is not None:
        keyboard.add(inline_change_hotline_button)
        keyboard.add(inline_remove_hotline_button)
    return keyboard


def generate_inline_subjects_to_add_link(chat_id):
    list_subjects = tuple(Schedule.get_lessons(chat_id))
    keyboard = telebot.types.InlineKeyboardMarkup()
    for item in list_subjects:
        keyboard.add(telebot.types.InlineKeyboardButton(text=item, callback_data=item[:10]))
    keyboard.add(inline_first_back_button)

    return keyboard


def generate_inline_subjects_to_add_hotline(chat_id):
    list_subjects = tuple(Schedule.get_lessons(chat_id))
    keyboard = telebot.types.InlineKeyboardMarkup()
    for item in list_subjects:
        keyboard.add(telebot.types.InlineKeyboardButton(text=item, callback_data=f"hl_{item[:10]}"))
    keyboard.add(inline_first_back_button_hotlines)

    return keyboard


def generate_inline_linked_subjects_to_change(chat_id):
    keyboard = telebot.types.InlineKeyboardMarkup()
    if db.get_links(chat_id) is not None:
        for item in db.get_links(chat_id):

            keyboard.add(telebot.types.InlineKeyboardButton(text=f"{item[2]} - {item[1]}",
                                                            callback_data=f"lch_{item[5]}"))
        keyboard.add(inline_first_back_button)
        return keyboard

    else:
        return ''


def generate_inline_hotlined_subjects_to_change(chat_id):
    keyboard = telebot.types.InlineKeyboardMarkup()

    if db.get_hotlines(chat_id) is not None:

        for item in db.get_hotlines(chat_id):

            keyboard.add(telebot.types.InlineKeyboardButton(text=f"{item[3]} - {item[1]}",
                                                            callback_data=f"hlch_{item[4]}"))
        keyboard.add(inline_first_back_button_hotlines)
        return keyboard

    else:
        return ''


def generate_inline_linked_subjects_to_remove(chat_id):
    keyboard = telebot.types.InlineKeyboardMarkup()
    if db.get_links(chat_id) is not None:
        for item in db.get_links(chat_id):
            keyboard.add(telebot.types.InlineKeyboardButton(text=f"{item[2]} - {item[1]}",
                                                            callback_data=f"rm_{item[5]}"))
        keyboard.add(inline_first_back_button)
        return keyboard
    else:
        return ''


def generate_inline_hotlined_subjects_to_remove(chat_id):
    keyboard = telebot.types.InlineKeyboardMarkup()
    if db.get_hotlines(chat_id) is not None:
        print(db.get_hotlines(chat_id))
        for item in db.get_hotlines(chat_id):
            keyboard.add(telebot.types.InlineKeyboardButton(text=f"{item[3]} - {item[1]}",
                                                            callback_data=f"hlrm_{item[4]}"))
        keyboard.add(inline_first_back_button_hotlines)
        return keyboard

    else:
        return ''
