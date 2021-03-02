from buttons import *
from schedule_parser.schedule_parser import *


def generate_default_keyboard(*button_text_tuple):
    """
    Функция генерирует клавиатуру с обычными кнопками в столбец.
    Максимальное количество кнопок в столбце — 300
    Пример:
    reply_markup=keyboard.generate_default_keyboard('value1', 'value2', ..., 'value300')
    :param button_text_tuple: список с текстом кнопок
    :return:
    """

    keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)

    for button_text in button_text_tuple:
        keyboard.add(button_text)

    return keyboard


def generate_default_keyboard_row(*button_text_tuple):
    """
    Функция генерирует клавиатуру с обычными кнопками в ряд.
    Максимальное количество кнопок в ряд — 12.
    Пример для одного ряда:
    reply_markup=keyboard.generate_default_keyboard_row('value1', ..., 'value12')
    Пример для нескольких рядов:
    reply_markup=keyboard.generate_default_keyboard_row(('value1, ..., 'value12'), ('value1', ..., 'value12'), ...)
    :param button_text_tuple: список с текстом кнопок
    :return:
    """

    keyboard = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=False, resize_keyboard=True)

    for item in button_text_tuple:

        if item.__class__ == str:  # если функция принимает один ряд кнопок
            keyboard.row(*button_text_tuple)
            break

        else:  # если функция принимает несколько рядов кнопок
            keyboard.row(*item)

    return keyboard


def generate_inline_keyboard(*args):
    keyboard = telebot.types.InlineKeyboardMarkup()

    for item in args:
        print(item)
        keyboard.add(telebot.types.InlineKeyboardButton(text=item[0], callback_data=item[1]))
    print(keyboard.to_dict())
    return keyboard


def dynamic_inline_link_menu(chat_id):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(inline_add_link_button)
    if db.get_links(chat_id) is not None:
        keyboard.add(inline_change_link_button)
        keyboard.add(inline_remove_link_button)
    return keyboard




def generate_inline_subjects(chat_id):
    """
    Генерирует инлайн список предметов группы.
    :param chat_id:
    :return:
    """
    list_subjects = tuple(Schedule.get_lessons(chat_id))
    keyboard = telebot.types.InlineKeyboardMarkup()
    for item in list_subjects:
        keyboard.add(telebot.types.InlineKeyboardButton(text=item, callback_data=item[:10]))
    keyboard.add(inline_first_back_button)

    return keyboard


def generate_inline_linked_subjects(chat_id):
    keyboard = telebot.types.InlineKeyboardMarkup()
    if db.get_links(chat_id) is not None:
        for item in db.get_links(chat_id):
            keyboard.add((telebot.types.InlineKeyboardButton(text=f"{item[2]} - {item[1]}",
                                                             callback_data=f"{item[2]}_{item[1][:10]}")))
        keyboard.add(inline_first_back_button)
        return keyboard
    else:
        return ''


def generate_inline_linked_subjects_to_remove(chat_id):
    keyboard = telebot.types.InlineKeyboardMarkup()
    if db.get_links(chat_id) is not None:
        for item in db.get_links(chat_id):
            keyboard.add((telebot.types.InlineKeyboardButton(text=f"{item[2]} - {item[1]}",
                                                             callback_data=f"rm_{item[2]}_{item[1][:10]}")))
        keyboard.add(inline_first_back_button)
        return keyboard
    else:
        return ''


main_menu_keyboard = generate_default_keyboard_row((schedule_button, settings_button),
                                                   (links_button, hotlines_button, mails_button),
                                                   (info_button, help_button))

schedule_menu_keyboard = generate_default_keyboard_row((today_day_button, tomorrow_day_button),
                                                       (week1_button, week2_button),
                                                       (back_button,))

week1_day_choose_keyboard = generate_default_keyboard_row(
    (week1_day_buttons[0], week1_day_buttons[1], week1_day_buttons[2]),
    (week1_day_buttons[3], week1_day_buttons[4]),
    (back_button,))

week2_day_choose_keyboard = generate_default_keyboard_row(
    (week2_day_buttons[0], week2_day_buttons[1], week2_day_buttons[2]),
    (week2_day_buttons[3], week2_day_buttons[4]),
    (back_button,))

settings_menu_keyboard = generate_default_keyboard_row((notifications_button, change_group_button),
                                                       (back_button,))









