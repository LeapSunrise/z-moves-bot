# -*- coding: utf-8 -*-
# !/usr/bin/python3.8.5

from src.schedule_parser.schedule_parser import *
from src.service.buttons import *


def dynamic_menu_links_inline_keyboard_generator(chat_id):
    """
    Generates dynamic main_menu/links inline keyboard.

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
    Generates dynamic main_menu/hotlines inline keyboard.

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
    """
    Generates subjects inline keyboard to add links.
    Button text creates as "(subject name)".
    Callback_data creates as "(first 10 symbols of subject name)".

    :param chat_id:
    :return:
    """
    list_subjects = tuple(Schedule.get_lessons(chat_id))
    keyboard = telebot.types.InlineKeyboardMarkup()
    for item in list_subjects:
        keyboard.add(telebot.types.InlineKeyboardButton(text=item, callback_data=f"link_add_{item[:25]}"))
    keyboard.add(inline_links_first_back_button)

    return keyboard


def generate_inline_subjects_to_add_hotline(chat_id):
    """
    Generates subjects inline keyboard to add hotlines.
    Button text creates as "(subject name)".
    Callback_data creates as "hl_(first 10 symbols of subject name)".

    :param chat_id:
    :return:
    """
    list_subjects = tuple(Schedule.get_lessons(chat_id))
    keyboard = telebot.types.InlineKeyboardMarkup()
    for item in list_subjects:
        keyboard.add(telebot.types.InlineKeyboardButton(text=item, callback_data=f"hotline_add_{item[:25]}"))
    keyboard.add(inline_first_back_button_hotlines)

    return keyboard


def generate_inline_linked_subjects_to_change(chat_id):
    """
    Generates subjects inline keyboard to change links.
    Button text creates as "(subject type) - (subject name)".
    Callback_data creates as "lch_(link addition date)".

    :param chat_id:
    :return:
    """
    keyboard = telebot.types.InlineKeyboardMarkup()
    if db.get_links(chat_id) is not None:
        for item in db.get_links(chat_id):
            keyboard.add(telebot.types.InlineKeyboardButton(text=f"{item[2]} - {item[1]}",
                                                            callback_data=f"link_ch_{item[5]}"))
        keyboard.add(inline_links_first_back_button)
        return keyboard

    else:
        return ''


def generate_inline_hotlined_subjects_to_change(chat_id):
    """
    Generates subjects inline keyboard to change hotlines.
    Button text creates as "(hotline date) - (subject name)".
    Callback_data creates as "hlch_(hotline addition date)".

    :param chat_id:
    :return:
    """
    keyboard = telebot.types.InlineKeyboardMarkup()
    if db.get_hotlines(chat_id) is not None:

        for item in db.get_hotlines(chat_id):
            keyboard.add(telebot.types.InlineKeyboardButton(text=f"{item[3]} - {item[1]}",
                                                            callback_data=f"hotline_ch_{item[4]}"))
        keyboard.add(inline_first_back_button_hotlines)
        return keyboard

    else:
        return ''


def generate_inline_linked_subjects_to_remove(chat_id):
    """
    Generates subjects inline keyboard to remove links.
    Button text creates as "(subject type) - (subject name)".
    Callback_data creates as "lrm_(link addition date)".

    :param chat_id:
    :return:
    """

    keyboard = telebot.types.InlineKeyboardMarkup()
    if db.get_links(chat_id) is not None:
        for item in db.get_links(chat_id):
            keyboard.add(telebot.types.InlineKeyboardButton(text=f"{item[2]} - {item[1]}",
                                                            callback_data=f"link_rm_{item[5]}"))
        keyboard.add(inline_links_first_back_button)
        return keyboard
    else:
        return ''


def generate_inline_hotlined_subjects_to_remove(chat_id):
    """
    Generates subjects inline keyboard to remove hotlines.
    Button text creates as "(hotline date) - (subject name)".
    Callback_data creates as "hlrm_(hotline addition date)".

    :param chat_id:
    :return:
    """

    keyboard = telebot.types.InlineKeyboardMarkup()
    if db.get_hotlines(chat_id) is not None:
        for item in db.get_hotlines(chat_id):
            keyboard.add(telebot.types.InlineKeyboardButton(text=f"{item[3]} - {item[1]}",
                                                            callback_data=f"hotline_rm_{item[4]}"))
        keyboard.add(inline_first_back_button_hotlines)
        return keyboard

    else:
        return ''


def rozklad_api_work_checker():
    """
    Simple rozklad API accessibility checker.

    :return:
    """
    try:
        requests.get('https://api.rozklad.org.ua/', timeout=3)

    except:
        return False
