# -*- coding: utf-8 -*-
# !/usr/bin/python3.8.5

import datetime
import random
import time

from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE

import src.config.config as config
from src.schedule_parser.schedule_parser import *
from src.service import keyboard_generator, stateworker, service
from src.service.buttons import *
from src.service.replies import *
from src.service.service import rozklad_api_work_checker as api_checker

bot = telebot.TeleBot(config.BOT_TOKEN)
calendar = Calendar(RUSSIAN_LANGUAGE)
calendar_1 = CallbackData("calendar_1", "action", "year", "month", "day")
calendar_keyboard = calendar.create_calendar(name=calendar_1.prefix,
                                             year=datetime.datetime.now().year,
                                             month=datetime.datetime.now().month, )

"""#####################################################################################################################
                                                    START
#####################################################################################################################"""


@bot.message_handler(func=lambda message: api_checker() is False)
def bad_request(message):
    bot.send_message(message.chat.id,
                     api_bad_request_reply[0],
                     reply_markup=telebot.types.ReplyKeyboardRemove(),
                     parse_mode='HTML')
    bot.send_sticker(message.chat.id, api_bad_request_reply[random.randint(1, len(api_bad_request_reply) - 1)],
                     reply_markup=None)


@bot.message_handler(func=lambda message: message.chat.id == db.get_blocked_user(message.chat.id)[0])
def black_list(message):
    user_name = message.from_user.first_name

    if message.from_user.last_name:
        user_name = f"{user_name} {message.from_user.last_name}"

    db.update_blocked_users(message.chat.id,
                            user_name,
                            time.strftime('%d/%m/%y, %X'),
                            time.strftime('%d/%m/%y, %X'))
    bot.send_sticker(message.chat.id,
                     blocked_user_reply[1])
    bot.send_message(message.chat.id,
                     blocked_user_reply[0],
                     reply_markup=telebot.types.ReplyKeyboardRemove())


@bot.message_handler(commands=['start', 'START'])
def start_message(message):
    user_name = message.from_user.first_name

    if message.from_user.last_name:
        user_name = f"{user_name} {message.from_user.last_name}"

    if db.get_user_info(message.chat.id) is None:
        bot.send_message(message.chat.id,
                         start_reply.format(user_name),
                         parse_mode='HTML')
        db.register_user(message.chat.id,
                         message.from_user.username,
                         stateworker.States.S_REGISTRATION.value,
                         time.strftime('%d/%m/%y, %X'),
                         time.strftime('%d/%m/%y, %X'))

    elif db.get_user_info(message.chat.id)[2] is None:
        bot.send_message(message.chat.id,
                         repeated_start_reply,
                         reply_markup=None,
                         parse_mode='HTML')
        db.set_state(message.from_user.username,
                     stateworker.States.S_REGISTRATION.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)


    else:
        bot.send_message(message.chat.id,
                         registered_user_start_reply,
                         reply_markup=keyboard_generator.main_menu_keyboard,
                         parse_mode='HTML')
        db.set_state(message.from_user.username,
                     stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)


@bot.message_handler(func=lambda message: (db.get_state(message.chat.id).__class__ == tuple and
                     (db.get_state(message.chat.id)[0] == stateworker.States.S_REGISTRATION.value or
                      db.get_state(message.chat.id)[0] == stateworker.States.S_CHANGE_GROUP.value)) and
                     message.text.startswith("#") is False)
def group_registration(message):
    if Schedule.is_group_exist(message.text):
        bot.send_message(message.chat.id,
                         successful_registration,
                         reply_markup=keyboard_generator.main_menu_keyboard)
        db.register_user_group_name(message.from_user.username,
                                    message.text.lower(),
                                    stateworker.States.S_MAIN_MENU.value,
                                    time.strftime('%d/%m/%y, %X'),
                                    message.chat.id)

    elif message.text == cancel_button:
        bot.send_message(message.chat.id,
                         settings_reply,
                         reply_markup=keyboard_generator.settings_menu_keyboard)
        db.set_state(message.from_user.username,
                     stateworker.States.S_SETTINGS_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)

    else:
        bot.send_message(message.chat.id,
                         unsuccessful_registration.format(message.text),
                         parse_mode='HTML')
        db.set_state(message.from_user.username,
                     stateworker.States.S_REGISTRATION.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)


"""#####################################################################################################################
                                                    MAIN MENU
#####################################################################################################################"""


@bot.message_handler(func=lambda message: db.get_state(message.chat.id).__class__ == tuple and
                     db.get_state(message.chat.id)[0] == stateworker.States.S_MAIN_MENU.value)
def main_menu(message):
    db.auto_remove_hotline()
    if message.text == schedule_button:
        bot.send_message(message.chat.id,
                         schedule_reply,
                         reply_markup=keyboard_generator.schedule_menu_keyboard)
        db.set_state(message.from_user.username,
                     stateworker.States.S_SCHEDULE_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)

    elif message.text == settings_button:
        bot.send_message(message.chat.id,
                         settings_reply,
                         reply_markup=keyboard_generator.settings_menu_keyboard)
        db.set_state(message.from_user.username,
                     stateworker.States.S_SETTINGS_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)

    elif message.text == links_button:
        bot.send_message(message.chat.id,
                         links_reply,
                         reply_markup=service.dynamic_menu_links_inline_keyboard_generator(message.chat.id))
        db.set_state(message.from_user.username,
                     stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)

    elif message.text == hotlines_button:
        bot.send_message(message.chat.id,
                         hotlines_reply,
                         reply_markup=service.dynamic_menu_hotlines_inline_keyboard_generator(message.chat.id))
        db.set_state(message.from_user.username,
                     stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)

    elif message.text == mails_button:
        bot.reply_to(message,
                     not_available_reply)
        db.set_state(message.from_user.username,
                     stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)

    elif message.text == info_button:
        bot.send_message(message.chat.id,
                         info_button_reply.format(db.get_user_info(message.chat.id)[2]),
                         reply_markup=keyboard_generator.main_menu_keyboard,
                         parse_mode='HTML',
                         disable_web_page_preview=True)
        db.set_state(message.from_user.username,
                     stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)

    elif message.text == help_button:
        bot.reply_to(message,
                     not_available_reply)
        db.set_state(message.from_user.username,
                     stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)


user_links_dict = {}  # links manager dictionary
user_hotlines_dict = {}  # hotlines manager dictionary

"""#####################################################################################################################
                                                    MAIN MENU/LINKS MENU
#####################################################################################################################"""


@bot.callback_query_handler(func=lambda call: call.data in ['add_link', 'change_link', 'remove_link',
                                                            'links_first_back_button', 'links_second_back_button'])
def links_menu(call):
    if call.data == 'add_link' or call.data == 'links_second_back_button':
        bot.edit_message_text(add_link_reply,
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=service.generate_inline_subjects_to_add_link(call.message.chat.id),
                              parse_mode='HTML')

    if call.data == 'change_link':
        bot.edit_message_text(change_link_reply,
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=service.generate_inline_linked_subjects_to_change(call.message.chat.id),
                              parse_mode='HTML')

    if call.data == 'remove_link':
        bot.edit_message_text(remove_link_reply,
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=service.generate_inline_linked_subjects_to_remove(call.message.chat.id),
                              parse_mode='HTML')

    if call.data == 'links_first_back_button':
        bot.edit_message_text(links_reply,
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=service.dynamic_menu_links_inline_keyboard_generator(call.message.chat.id),
                              parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: call.data.startswith('link_add_'))
def links_menu_add_link_subject(call):
    inline_subject_keyboard_to_add_link = service.generate_inline_subjects_to_add_link(call.message.chat.id)

    if inline_subject_keyboard_to_add_link != '' and call.data in \
            [button['callback_data'] for buttons in inline_subject_keyboard_to_add_link.to_dict()['inline_keyboard']
             for button in buttons]:
        for buttons in \
                inline_subject_keyboard_to_add_link.to_dict()['inline_keyboard'][
                :len(inline_subject_keyboard_to_add_link.to_dict()[
                         'inline_keyboard']) - 1]:  # тут -1 чтобы не ловилась бэк-кнопка

            for button in buttons:

                if button['callback_data'] == call.data:
                    user_links_dict.update({call.message.chat.id: {
                        'addition_date': '',
                        'subject': button['text'],
                        'subject_type': '',
                        'link': '',
                        'password': '',
                    }})

                    bot.edit_message_text(f"Предмет: <b>{user_links_dict[call.message.chat.id]['subject']}</b>\n\n"
                                          f"Выбери тип занятия 🙃",
                                          chat_id=call.message.chat.id,
                                          message_id=call.message.message_id,
                                          reply_markup=keyboard_generator.inline_subject_type_keyboard,
                                          parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: call.data in ['lec', 'lab', 'prac'])
def links_menu_add_link_subject_type(call):
    type_inverter_dict = {'lec': 'Лек',
                          'lab': 'Лаб',
                          'prac': 'Прак'
                          }
    if call.data == 'lec' or call.data == 'lab' or call.data == 'prac':
        user_links_dict[call.message.chat.id]['subject_type'] = type_inverter_dict[call.data]

        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

        keyboard = keyboard_generator.generate_default_keyboard(cancel_button)

        bot.send_message(call.message.chat.id,
                         f"Предмет: <b>{user_links_dict[call.message.chat.id]['subject']}</b>\n"
                         f"Тип занятия: <b>{user_links_dict[call.message.chat.id]['subject_type']}</b>\n\n"
                         f"Теперь попрошу скинуть мне ссылочку 🤓",
                         reply_markup=keyboard,
                         parse_mode='HTML')
        db.set_state(call.from_user.username,
                     stateworker.States.S_INPUT_LINK.value,
                     time.strftime('%d/%m/%y, %X'),
                     call.message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('link_ch_'))
def links_menu_change_link(call):
    inline_linked_subject_keyboard_to_ch = service.generate_inline_linked_subjects_to_change(call.message.chat.id)

    for buttons in inline_linked_subject_keyboard_to_ch.to_dict()['inline_keyboard'][
                   :len(inline_linked_subject_keyboard_to_ch.to_dict()[
                            'inline_keyboard']) - 1]:  # -1 чтобы не ловилась бэк-кнопка
        for button in buttons:

            if button['callback_data'] == call.data:

                user_links_dict.update({call.message.chat.id: {
                    'subject': button['text'][button['text'].find('-') + 2:],
                    'subject_type': button['text'][:button['text'].find(' ')],
                    'addition_date': button['callback_data'][len('link_ch_'):]
                }})

                linked_subject = db.get_links_to_change(call.message.chat.id,
                                                        user_links_dict[call.message.chat.id]['subject'],
                                                        user_links_dict[call.message.chat.id]['subject_type'],
                                                        user_links_dict[call.message.chat.id]['addition_date'])

                user_links_dict[call.message.chat.id]['link'] = linked_subject[3]
                user_links_dict[call.message.chat.id]['password'] = linked_subject[4]

                bot.delete_message(chat_id=call.message.chat.id,
                                   message_id=call.message.message_id)

                if user_links_dict[call.message.chat.id]['password'] == '':
                    bot.send_message(call.message.chat.id,
                                     f"Предмет: <b>{user_links_dict[call.message.chat.id]['subject']}</b>\n"
                                     f"Тип занятия: <b>{user_links_dict[call.message.chat.id]['subject_type']}</b>\n"
                                     f"Ссылка: <b>{user_links_dict[call.message.chat.id]['link']}</b>\n",
                                     reply_markup=keyboard_generator.generate_default_keyboard_row(
                                         (add_password_button, confirm_button),
                                         (cancel_button,)),
                                     parse_mode='HTML',
                                     disable_web_page_preview=True)

                elif user_links_dict[call.message.chat.id]['password'] != '':
                    bot.send_message(call.message.chat.id,
                                     f"Предмет: <b>{user_links_dict[call.message.chat.id]['subject']}</b>\n"
                                     f"Тип занятия: <b>{user_links_dict[call.message.chat.id]['subject_type']}</b>\n"
                                     f"Ссылка: <b>{user_links_dict[call.message.chat.id]['link']}</b>\n"
                                     f"Пароль: <b>{user_links_dict[call.message.chat.id]['password']}</b>\n",
                                     reply_markup=keyboard_generator.generate_default_keyboard_row(
                                         (change_password_button, confirm_button),
                                         (cancel_button,)),
                                     parse_mode='HTML',
                                     disable_web_page_preview=True)

                db.set_state(call.message.from_user.username,
                             stateworker.States.S_CHANGE_LINK.value,
                             time.strftime('%d/%m/%y, %X'),
                             call.message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('link_rm_'))
def links_menu_remove_link(call):
    inline_linked_subject_keyboard_to_rm = service.generate_inline_linked_subjects_to_remove(call.message.chat.id)

    for buttons in inline_linked_subject_keyboard_to_rm.to_dict()['inline_keyboard'][
                   :len(inline_linked_subject_keyboard_to_rm.to_dict()[
                            'inline_keyboard']) - 1]:  # тут -1 чтобы не ловилась бэк-кнопка
        for button in buttons:
            if button['callback_data'] == call.data:
                user_links_dict.update({call.message.chat.id: {
                    'subject': button['text'][int(button['text'].find('-')) + 2:],  # текст кнопки после '- '
                    'subject_type': button['text'][:int(button['text'].find(' '))],  # текст кнопки до пробела
                    'link': '',
                    'password': '',
                    'addition_date': button['callback_data'][len('link_rm_'):]
                }})

                linked_subject = db.get_links_to_change(call.message.chat.id,
                                                        user_links_dict[call.message.chat.id]['subject'],
                                                        user_links_dict[call.message.chat.id]['subject_type'],
                                                        user_links_dict[call.message.chat.id]['addition_date'])

                user_links_dict[call.message.chat.id]['link'] = linked_subject[3]  # 3 - ссылка
                user_links_dict[call.message.chat.id]['password'] = linked_subject[4]  # 4 - пароль

                if user_links_dict[call.message.chat.id]['password'] == '':
                    bot.edit_message_text(f"Ты удаляешь:\n"
                                          f"Предмет: <b>{user_links_dict[call.message.chat.id]['subject']}</b>\n"
                                          f"Тип занятия: <b>{user_links_dict[call.message.chat.id]['subject_type']}</b>\n"
                                          f"Ссылка: <b>{user_links_dict[call.message.chat.id]['link']}</b>\n",
                                          chat_id=call.message.chat.id,
                                          message_id=call.message.message_id,
                                          reply_markup=keyboard_generator.inline_confirm_cancel_links_keyboard,
                                          parse_mode='HTML',
                                          disable_web_page_preview=True)

                elif user_links_dict[call.message.chat.id]['password'] != '':
                    bot.edit_message_text(f"Ты удаляешь:\n"
                                          f"Предмет: <b>{user_links_dict[call.message.chat.id]['subject']}</b>\n"
                                          f"Тип занятия: <b>{user_links_dict[call.message.chat.id]['subject_type']}</b>\n"
                                          f"Ссылка: <b>{user_links_dict[call.message.chat.id]['link']}</b>\n"
                                          f"Пароль: <b>{user_links_dict[call.message.chat.id]['password']}</b>",
                                          chat_id=call.message.chat.id,
                                          message_id=call.message.message_id,
                                          reply_markup=keyboard_generator.inline_confirm_cancel_links_keyboard,
                                          parse_mode='HTML',
                                          disable_web_page_preview=True)


@bot.callback_query_handler(func=lambda call: call.data in ['confirm_remove_link', 'cancel_remove_link'])
def links_menu_confirm_cancel_remove_link(call):
    if call.data == 'confirm_remove_link':
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)
        db.remove_link(call.message.chat.id,
                       user_links_dict[call.message.chat.id]['subject'],
                       user_links_dict[call.message.chat.id]['subject_type'],
                       user_links_dict[call.message.chat.id]['addition_date'])

        bot.send_message(call.message.chat.id,
                         f"Ссылка <i>'{user_links_dict[call.message.chat.id]['link']}'</i> на предмет "
                         f"'<b>{user_links_dict[call.message.chat.id]['subject_type']}</b> - "
                         f"<b>{user_links_dict[call.message.chat.id]['subject']}</b>' "
                         f"успешно удалена.",
                         reply_markup=keyboard_generator.main_menu_keyboard,
                         parse_mode='HTML',
                         disable_web_page_preview=True)

    if call.data == 'cancel_remove_link':
        bot.edit_message_text(f"Выбери предмет для удаления ссылки",
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=service.generate_inline_linked_subjects_to_remove(call.message.chat.id),
                              parse_mode='HTML')


"""#####################################################################################################################
                                                    MAIN MENU/HOTLINE MENU
#####################################################################################################################"""


@bot.callback_query_handler(func=lambda call: call.data in ['add_hotline', 'change_hotline', 'remove_hotline',
                                                            'hotlines_first_back_button'])
def hotlines_menu(call):
    if call.data == 'add_hotline':
        bot.edit_message_text(add_hotline_reply,
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=service.generate_inline_subjects_to_add_hotline(call.message.chat.id),
                              parse_mode='HTML')

    if call.data == 'change_hotline':
        bot.edit_message_text(change_hotline_reply,
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=service.generate_inline_hotlined_subjects_to_change(call.message.chat.id),
                              parse_mode='HTML')

    if call.data == 'remove_hotline':
        bot.edit_message_text(remove_hotline_reply,
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=service.generate_inline_hotlined_subjects_to_remove(call.message.chat.id),
                              parse_mode='HTML')

    if call.data == 'hotlines_first_back_button':
        bot.edit_message_text(hotlines_reply,
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=service.dynamic_menu_hotlines_inline_keyboard_generator(
                                  call.message.chat.id),
                              parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: call.data.startswith('hotline_add_'))
def hotlines_menu_add_hotline(call):
    inline_subject_keyboard_to_add_hotline = service.generate_inline_subjects_to_add_hotline(call.message.chat.id)

    if inline_subject_keyboard_to_add_hotline != '' and call.data in \
            [button['callback_data'] for buttons in
             inline_subject_keyboard_to_add_hotline.to_dict()['inline_keyboard'] for button in buttons]:
        for buttons in inline_subject_keyboard_to_add_hotline.to_dict()['inline_keyboard'][
                       :len(inline_subject_keyboard_to_add_hotline.to_dict()['inline_keyboard']) - 1]:
            for button in buttons:
                if button['callback_data'] == call.data:
                    user_hotlines_dict.update({call.message.chat.id: {
                        'subject': button['text'],
                        'description': '',
                        'date': '',
                    }})
                    bot.edit_message_text(f"Предмет: <b>{user_hotlines_dict[call.message.chat.id]['subject']}</b>\n\n"
                                          f"Выбери дату для хотлайна",
                                          chat_id=call.message.chat.id,
                                          message_id=call.message.message_id,
                                          reply_markup=calendar_keyboard,
                                          parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: call.data.startswith('hotline_ch_'))
def hotlines_menu_change_hotline(call):
    inline_hotlined_subject_keyboard_to_ch = service.generate_inline_hotlined_subjects_to_change(call.message.chat.id)

    for buttons in inline_hotlined_subject_keyboard_to_ch.to_dict()['inline_keyboard'][
                   :len(inline_hotlined_subject_keyboard_to_ch.to_dict()['inline_keyboard']) - 1]:
        for button in buttons:
            if button['callback_data'] == call.data:
                user_hotlines_dict.update({call.message.chat.id: {
                    'subject': button['text'][button['text'].find('-') + 2:],
                    'description': '',
                    'date': '',
                    'addition_date': button['callback_data'][len('hotline_ch_'):]
                }})

                hotlined_subject = db.get_hotlines_to_change(call.message.chat.id,
                                                             user_hotlines_dict[call.message.chat.id]['subject'],
                                                             user_hotlines_dict[call.message.chat.id]['addition_date'])

                user_hotlines_dict[call.message.chat.id]['description'] = hotlined_subject[0]
                user_hotlines_dict[call.message.chat.id]['date'] = hotlined_subject[1]

                bot.edit_message_text(f"Выбери новую дату для хотлайна",
                                      chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      reply_markup=calendar_keyboard,
                                      parse_mode='HTML',
                                      disable_web_page_preview=True)


@bot.callback_query_handler(func=lambda call: call.data.startswith('hotline_rm_'))
def hotlines_menu_remove_hotline(call):
    inline_hotlined_subject_keyboard_to_rm = service.generate_inline_hotlined_subjects_to_remove(call.message.chat.id)

    for buttons in inline_hotlined_subject_keyboard_to_rm.to_dict()['inline_keyboard'][
                   :len(inline_hotlined_subject_keyboard_to_rm.to_dict()['inline_keyboard']) - 1]:
        for button in buttons:
            if button['callback_data'] == call.data:
                user_hotlines_dict.update({call.message.chat.id: {
                    'subject': button['text'][button['text'].find('-') + 2:],
                    'description': '',
                    'date': '',
                    'addition_date': button['callback_data'][len('hotline_rm_'):]
                }})

                hotlined_subject = db.get_hotlines_to_change(call.message.chat.id,
                                                             user_hotlines_dict[call.message.chat.id]['subject'],
                                                             user_hotlines_dict[call.message.chat.id]['addition_date'])

                user_hotlines_dict[call.message.chat.id]['description'] = hotlined_subject[0]
                user_hotlines_dict[call.message.chat.id]['date'] = hotlined_subject[1]

                bot.edit_message_text(f"Ты удаляешь хотлайн:\n\n"
                                      f"{lorem_ipsum}",
                                      chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      reply_markup=keyboard_generator.inline_confirm_cancel_hotlines_keyboard,
                                      parse_mode='HTML',
                                      disable_web_page_preview=True)


@bot.callback_query_handler(func=lambda call: call.data in ['confirm_remove_hotline', 'cancel_remove_hotline'])
def hotlines_menu_confirm_cancel_remove_hotline(call):
    if call.data == 'confirm_remove_hotline':
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)
        db.remove_hotline(call.message.chat.id,
                          user_hotlines_dict[call.message.chat.id]['subject'],
                          user_hotlines_dict[call.message.chat.id]['description'],
                          user_hotlines_dict[call.message.chat.id]['date'],
                          user_hotlines_dict[call.message.chat.id]['addition_date'])

        bot.send_message(call.message.chat.id,
                         confirm_remove_hotline_reply.format(user_hotlines_dict[call.message.chat.id]['subject']))

    if call.data == 'cancel_remove_hotline':
        bot.edit_message_text(remove_hotline_reply,
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=service.generate_inline_hotlined_subjects_to_remove(call.message.chat.id),
                              parse_mode='HTML')


@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_1.prefix))
def input_hotline_date(call: telebot.types.CallbackQuery):
    name, action, year, month, day = call.data.split(calendar_1.sep)
    date = calendar.calendar_query_handler(bot=bot,
                                           call=call,
                                           name=name,
                                           action=action,
                                           year=year,
                                           month=month,
                                           day=day)

    if action == "DAY":
        user_hotlines_dict[call.message.chat.id]['date'] = date.strftime('%d.%m')
        bot.send_message(chat_id=call.from_user.id,
                         text=f"Предмет: {user_hotlines_dict[call.message.chat.id]['subject']}\n"
                              f"Дата: {date.strftime('%d.%m')}\n\n"
                              f"Теперь добавь описание :)",
                         reply_markup=keyboard_generator.generate_default_keyboard(cancel_button))

        if len(user_hotlines_dict[call.message.chat.id]) == 3:
            db.set_state(call.message.from_user.username,
                         stateworker.States.S_INPUT_HOTLINE.value,
                         time.strftime('%d/%m/%y, %X'),
                         call.message.chat.id)
        else:
            db.set_state(call.message.from_user.username,
                         stateworker.States.S_CHANGE_HOTLINE.value,
                         time.strftime('%d/%m/%y, %X'),
                         call.message.chat.id)

        user_hotlines_dict[call.message.chat.id]['date'] = date.strftime('%d.%m')

    elif action == "CANCEL":
        bot.send_message(chat_id=call.from_user.id,
                         text="Главное меню",
                         reply_markup=keyboard_generator.main_menu_keyboard)


@bot.message_handler(func=lambda message: db.get_state(message.chat.id).__class__ == tuple and
                     db.get_state(message.chat.id)[0] == stateworker.States.S_INPUT_HOTLINE.value)
def input_hotline(message):
    if message.text == cancel_button:
        bot.send_message(message.chat.id,
                         f"Главное меню",
                         reply_markup=keyboard_generator.main_menu_keyboard)
        db.set_state(message.from_user.username,
                     stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)

    elif message.text == confirm_button:
        bot.send_message(message.chat.id,
                         f"Хотлайн для <b>'{user_hotlines_dict[message.chat.id]['subject']}' </b>"
                         f"успешно добавлен.",
                         reply_markup=keyboard_generator.main_menu_keyboard,
                         parse_mode='HTML')
        db.set_state(message.from_user.username,
                     stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)
        user_hotlines_dict[message.chat.id]['addition_date'] = time.strftime('%d/%m/%y, %X')

        db.add_hotline(message.chat.id,
                       user_hotlines_dict[message.chat.id]['subject'],
                       user_hotlines_dict[message.chat.id]['description'],
                       user_hotlines_dict[message.chat.id]['date'],
                       user_hotlines_dict[message.chat.id]['addition_date'])

    else:
        user_hotlines_dict[message.chat.id]['description'] = message.text
        bot.send_message(message.chat.id,
                         f"<b>{user_hotlines_dict[message.chat.id]['subject']}</b> - "
                         f"<b>{user_hotlines_dict[message.chat.id]['description']}</b> - "
                         f"<b>{user_hotlines_dict[message.chat.id]['date']}</b>",
                         reply_markup=keyboard_generator.generate_default_keyboard_row((confirm_button,),
                                                                                       (cancel_button,)),
                         parse_mode='HTML')


@bot.message_handler(func=lambda message: db.get_state(message.chat.id).__class__ == tuple and
                     db.get_state(message.chat.id)[0] == stateworker.States.S_CHANGE_HOTLINE.value)
def change_hotline(message):
    if message.text == cancel_button:
        bot.send_message(message.chat.id,
                         f"Главное меню",
                         reply_markup=keyboard_generator.main_menu_keyboard)
        db.set_state(message.from_user.username,
                     stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)

    elif message.text == confirm_button:
        bot.send_message(message.chat.id,
                         f"Хотлайн для <b>'{user_hotlines_dict[message.chat.id]['subject']}' </b>"
                         f"успешно изменён.",
                         reply_markup=keyboard_generator.main_menu_keyboard,
                         parse_mode='HTML')
        db.set_state(message.from_user.username,
                     stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)

        db.change_hotline(user_hotlines_dict[message.chat.id]['date'],
                          user_hotlines_dict[message.chat.id]['description'],
                          message.chat.id,
                          user_hotlines_dict[message.chat.id]['subject'],
                          user_hotlines_dict[message.chat.id]['addition_date'])

    elif message.text == message.text:
        user_hotlines_dict[message.chat.id]['description'] = message.text
        bot.send_message(message.chat.id,
                         f"<b>{user_hotlines_dict[message.chat.id]['subject']}</b> - "
                         f"<b>{user_hotlines_dict[message.chat.id]['description']}</b> - "
                         f"<b>{user_hotlines_dict[message.chat.id]['date']}</b>",
                         reply_markup=keyboard_generator.generate_default_keyboard_row((confirm_button,),
                                                                                       (cancel_button,)),
                         parse_mode='HTML')


"""#####################################################################################################################
                                                    ADD LINK
#####################################################################################################################"""


@bot.message_handler(func=lambda message: db.get_state(message.chat.id).__class__ == tuple and
                     db.get_state(message.chat.id)[0] == stateworker.States.S_INPUT_LINK.value)
def input_link(message):
    if message.text == cancel_button:
        bot.send_message(message.chat.id,
                         f"Главное меню",
                         reply_markup=keyboard_generator.main_menu_keyboard)
        db.set_state(message.from_user.username,
                     stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)

    elif message.text == confirm_button:
        bot.send_message(message.chat.id,
                         f"Ссылка для <b>'{user_links_dict[message.chat.id]['subject_type']}</b> - "
                         f"<b>{user_links_dict[message.chat.id]['subject']}'</b> успешно добавлена.",
                         reply_markup=keyboard_generator.main_menu_keyboard,
                         parse_mode='HTML',
                         disable_web_page_preview=True)
        user_links_dict[message.chat.id]['addition_time'] = time.strftime('%d/%m/%y %X')
        db.add_link(message.chat.id,
                    user_links_dict[message.chat.id]['subject'],
                    user_links_dict[message.chat.id]['subject_type'],
                    user_links_dict[message.chat.id]['link'],
                    user_links_dict[message.chat.id]['password'],
                    db.get_user_info(message.chat.id)[2],
                    user_links_dict[message.chat.id]['addition_time'])
        db.set_state(message.from_user.username,
                     stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)

    elif message.text == add_password_button or message.text == change_password_button:
        if user_links_dict[message.chat.id]['password'] == '':
            keyboard = keyboard_generator.generate_default_keyboard_row((change_link_button, confirm_button),
                                                                        (cancel_button,))
            bot.send_message(message.chat.id,
                             f"Предмет: <b>{user_links_dict[message.chat.id]['subject']}</b>\n"
                             f"Тип занятия: <b>{user_links_dict[message.chat.id]['subject_type']}</b>\n"
                             f"Ссылка: <b>{user_links_dict[message.chat.id]['link']}</b>\n\n"
                             f"Ты можешь:\n"
                             f"1. Отправить мне <b>пароль</b>\n"
                             f"2. Изменить <b>ссылку</b>, нажав <b>'{change_link_button}'</b>\n"
                             f"3. Нажать <b>'{confirm_button}'</b> (ссылка добавится в расписание) и перейти в главное меню\n"
                             f"4. Нажать <b>'{cancel_button}'</b> (ссылки не добавится в расписание) и перейти в главное меню",
                             reply_markup=keyboard,
                             parse_mode='HTML',
                             disable_web_page_preview=True)

        elif user_links_dict[message.chat.id]['password'] != '':
            keyboard = keyboard_generator.generate_default_keyboard_row((change_link_button, confirm_button),
                                                                        (cancel_button,))
            bot.send_message(message.chat.id,
                             f"Предмет: <b>{user_links_dict[message.chat.id]['subject']}</b>\n"
                             f"Тип занятия: <b>{user_links_dict[message.chat.id]['subject_type']}</b>\n"
                             f"Ссылка: <b>{user_links_dict[message.chat.id]['link']}</b>\n"
                             f"Пароль: <b>{user_links_dict[message.chat.id]['password']}</b>\n\n"
                             f"Ты можешь:\n"
                             f"1. Отправить мне <b>пароль</b> повторно (заменяется предыдущий)\n"
                             f"2. Изменить <b>ссылку</b>, нажав <b>'{change_link_button}'</b>\n"
                             f"3. Нажать <b>'{confirm_button}'</b> (ссылка будет видна в расписании) и перейти в главное меню\n"
                             f"4. Нажать <b>'{cancel_button}'</b> (ссылки не будет видно в расписании) и перейти в главное меню",
                             reply_markup=keyboard,
                             parse_mode='HTML',
                             disable_web_page_preview=True)

        db.set_state(message.from_user.username,
                     stateworker.States.S_INPUT_PASSWORD.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)

    elif message.text == message.text:
        user_links_dict[message.chat.id]['link'] = message.text
        if user_links_dict[message.chat.id]['password'] == '':
            keyboard = keyboard_generator.generate_default_keyboard_row((add_password_button, confirm_button),
                                                                        (cancel_button,))
            bot.send_message(message.chat.id,
                             f"Предмет: <b>{user_links_dict[message.chat.id]['subject']}</b>\n"
                             f"Тип занятия: <b>{user_links_dict[message.chat.id]['subject_type']}</b>\n"
                             f"Ссылка: <b>{user_links_dict[message.chat.id]['link']}</b>\n\n"
                             f"Ты можешь:\n"
                             f"1. Отправить мне <b>ссылку</b> повторно (заменяется предыдущая)\n"
                             f"2. Добавить <b>пароль</b> к ссылке, нажав <b>'{add_password_button}'</b>\n"
                             f"3. Нажать <b>'{confirm_button}'</b> (ссылка будет видна в расписании) и перейти в главное меню\n"
                             f"4. Нажать <b>'{cancel_button}'</b> (ссылки не будет видно в расписании) и перейти в главное меню",
                             reply_markup=keyboard,
                             parse_mode='HTML',
                             disable_web_page_preview=True)

        elif user_links_dict[message.chat.id]['password'] != '':
            keyboard = keyboard_generator.generate_default_keyboard_row((change_password_button, confirm_button),
                                                                        (cancel_button,))
            bot.send_message(message.chat.id,
                             f"Предмет: <b>{user_links_dict[message.chat.id]['subject']}</b>\n"
                             f"Тип занятия: <b>{user_links_dict[message.chat.id]['subject_type']}</b>\n"
                             f"Ссылка: <b>{user_links_dict[message.chat.id]['link']}</b>\n"
                             f"<b>пароль</b>: <b>{user_links_dict[message.chat.id]['password']}</b>\n\n"
                             f"Ты можешь:\n"
                             f"1. Отправить мне <b>ссылку</b> повторно (заменяется предыдущая)\n"
                             f"2. Изменить к ссылке, нажав <b>'{change_password_button}'</b>\n"
                             f"3. Нажать <b>'{confirm_button}'</b> (ссылка будет видна в расписании) и перейти в главное меню\n"
                             f"4. Нажать <b>'{cancel_button}'</b> (ссылки не будет видно в расписании) и перейти в главное меню",
                             reply_markup=keyboard,
                             parse_mode='HTML',
                             disable_web_page_preview=True)


@bot.message_handler(func=lambda message: db.get_state(message.chat.id).__class__ == tuple and
                                          db.get_state(message.chat.id)[0] == stateworker.States.S_INPUT_PASSWORD.value)
def input_password(message):
    if message.text == cancel_button:
        bot.send_message(message.chat.id,
                         f"Главное меню",
                         reply_markup=keyboard_generator.main_menu_keyboard)
        db.set_state(message.from_user.username,
                     stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)

    elif message.text == confirm_button:
        bot.send_message(message.chat.id,
                         f"Ссылка для <b>'{user_links_dict[message.chat.id]['subject_type']}</b> - "
                         f"<b>{user_links_dict[message.chat.id]['subject']}'</b> успешно добавлена.",
                         reply_markup=keyboard_generator.main_menu_keyboard,
                         parse_mode='HTML',
                         disable_web_page_preview=True)
        db.set_state(message.from_user.username,
                     stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)
        user_links_dict[message.chat.id]['addition_time'] = time.strftime('%d/%m/%y %X')
        db.add_link(message.chat.id,
                    user_links_dict[message.chat.id]['subject'],
                    user_links_dict[message.chat.id]['subject_type'],
                    user_links_dict[message.chat.id]['link'],
                    user_links_dict[message.chat.id]['password'],
                    user_links_dict[message.chat.id]['addition_time'])

    elif message.text == change_link_button:
        db.set_state(message.from_user.username,
                     stateworker.States.S_INPUT_LINK.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)

        if user_links_dict[message.chat.id]['password'] == '':
            keyboard = keyboard_generator.generate_default_keyboard_row((add_password_button, confirm_button),
                                                                        (cancel_button,))
            bot.send_message(message.chat.id,
                             f"Предмет: <b>{user_links_dict[message.chat.id]['subject']}</b>\n"
                             f"Тип занятия: <b>{user_links_dict[message.chat.id]['subject_type']}</b>\n"
                             f"Ссылка: <b>{user_links_dict[message.chat.id]['link']}</b>\n\n"
                             f"Ты можешь:\n"
                             f"1. Отправить мне <b>ссылку</b> повторно (заменяется предыдущая)\n"
                             f"2. Добавить <b>пароль</b> к ссылке, нажав <b>'{add_password_button}'</b>\n"
                             f"3. Нажать <b>'{confirm_button}'</b> (ссылка будет видна в расписании) и перейти в главное меню\n"
                             f"4. Нажать <b>'{cancel_button}'</b> (ссылки не будет видно в расписании) и перейти в главное меню",
                             reply_markup=keyboard,
                             parse_mode='HTML',
                             disable_web_page_preview=True)

        elif user_links_dict[message.chat.id]['password'] != '':
            keyboard = keyboard_generator.generate_default_keyboard_row((change_password_button, confirm_button),
                                                                        (cancel_button,))
            bot.send_message(message.chat.id,
                             f"Предмет: <b>{user_links_dict[message.chat.id]['subject']}</b>\n"
                             f"Тип занятия: <b>{user_links_dict[message.chat.id]['subject_type']}</b>\n"
                             f"Ссылка: <b>{user_links_dict[message.chat.id]['link']}</b>\n"
                             f"Пароль: <b>{user_links_dict[message.chat.id]['password']}</b>\n\n"
                             f"Ты можешь:\n"
                             f"1. Отправить мне <b>ссылку</b> повторно (заменяется предыдущая)\n"
                             f"2. Изменить <b>пароль</b> к ссылке, нажав <b>'{change_password_button}'</b>\n"
                             f"3. Нажать <b>'{confirm_button}'</b> (ссылка будет видна в расписании) и перейти в главное меню\n"
                             f"4. Нажать <b>'{cancel_button}'</b> (ссылки не будет видно в расписании) и перейти в главное меню",
                             reply_markup=keyboard,
                             parse_mode='HTML',
                             disable_web_page_preview=True)

    elif message.text == message.text:
        user_links_dict[message.chat.id]['password'] = message.text
        bot.send_message(message.chat.id,
                         f"Предмет: <b>{user_links_dict[message.chat.id]['subject']}</b>\n"
                         f"Тип занятия: <b>{user_links_dict[message.chat.id]['subject_type']}</b>\n"
                         f"Ссылка: <b>{user_links_dict[message.chat.id]['link']}</b>\n"
                         f"Пароль: <b>{user_links_dict[message.chat.id]['password']}</b>\n\n"
                         f"Ты можешь:\n"
                         f"1. Отправить мне <b>пароль</b> повторно (заменяется предыдущий)\n"
                         f"2. Изменить <b>ссылку</b> нажав <b>'{change_link_button}'</b>\n"
                         f"3. Нажать <b>'{confirm_button}'</b> (ссылка будет видна в расписании) и перейти в главное меню\n"
                         f"4. Нажать <b>'{cancel_button}'</b> (ссылки не будет видно в расписании) и перейти в главное меню",
                         parse_mode='HTML',
                         disable_web_page_preview=True)


"""#####################################################################################################################
                                                    CHANGE LINK
#####################################################################################################################"""


@bot.message_handler(func=lambda message: db.get_state(message.chat.id).__class__ == tuple and
                     db.get_state(message.chat.id)[0] == stateworker.States.S_CHANGE_LINK.value)
def change_link(message):
    if message.text == cancel_button:
        bot.send_message(message.chat.id,
                         f"Главное меню",
                         reply_markup=keyboard_generator.main_menu_keyboard)
        db.set_state(message.from_user.username,
                     stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)

    elif message.text == confirm_button:
        bot.send_message(message.chat.id,
                         f"Ссылка для <b>'{user_links_dict[message.chat.id]['subject_type']}</b> - "
                         f"<b>{user_links_dict[message.chat.id]['subject']}'</b> успешно изменена.",
                         reply_markup=keyboard_generator.main_menu_keyboard,
                         parse_mode='HTML',
                         disable_web_page_preview=True)
        db.change_link(user_links_dict[message.chat.id]['link'],  # update
                       user_links_dict[message.chat.id]['password'],
                       message.chat.id,  # where
                       user_links_dict[message.chat.id]['subject'],
                       user_links_dict[message.chat.id]['subject_type'],
                       user_links_dict[message.chat.id]['addition_date'])
        db.set_state(message.from_user.username,
                     stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)

    elif message.text == add_password_button or message.text == change_password_button:
        if user_links_dict[message.chat.id]['password'] == '':
            bot.send_message(message.chat.id,
                             f"Предмет: <b>{user_links_dict[message.chat.id]['subject']}</b>\n"
                             f"Тип занятия: <b>{user_links_dict[message.chat.id]['subject_type']}</b>\n"
                             f"Ссылка: <b>{user_links_dict[message.chat.id]['link']}</b>\n\n"
                             f"Ты можешь:\n"
                             f"1. Отправить мне <b>пароль</b>\n"
                             f"2. Изменить <b>ссылку</b>, нажав <b>'{change_link_button}'</b>\n"
                             f"3. Нажать <b>'{confirm_button}'</b> (ссылка будет видна в расписании) и перейти в главное меню\n"
                             f"4. Нажать <b>'{cancel_button}'</b> (ссылки не будет видно в расписании) и перейти в главное меню",
                             reply_markup=keyboard_generator.generate_default_keyboard_row(
                                 (change_link_button, confirm_button),
                                 (cancel_button,)),
                             parse_mode='HTML',
                             disable_web_page_preview=True)

        elif user_links_dict[message.chat.id]['password'] != '':
            bot.send_message(message.chat.id,
                             f"Предмет: <b>{user_links_dict[message.chat.id]['subject']}</b>\n"
                             f"Тип занятия: <b>{user_links_dict[message.chat.id]['subject_type']}</b>\n"
                             f"Ссылка: <b>{user_links_dict[message.chat.id]['link']}</b>\n"
                             f"Пароль: <b>{user_links_dict[message.chat.id]['password']}</b>\n\n"
                             f"Ты можешь:\n"
                             f"1. Отправить мне <b>пароль</b> повторно (заменяется предыдущий)\n"
                             f"2. Изменить <b>ссылку</b>, нажав <b>'{change_link_button}'</b>\n"
                             f"3. Нажать <b>'{confirm_button}'</b> (ссылка будет видна в расписании) и перейти в главное меню\n"
                             f"4. Нажать <b>'{cancel_button}'</b> (ссылки не будет видно в расписании) и перейти в главное меню",
                             reply_markup=keyboard_generator.generate_default_keyboard_row(
                                 (change_link_button, confirm_button),
                                 (cancel_button,)),
                             parse_mode='HTML',
                             disable_web_page_preview=True)
        db.set_state(message.from_user.username,
                     stateworker.States.S_CHANGE_PASSWORD.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)

    elif message.text == message.text:
        user_links_dict[message.chat.id]['link'] = message.text
        if user_links_dict[message.chat.id]['password'] == '':
            bot.send_message(message.chat.id,
                             f"Предмет: <b>{user_links_dict[message.chat.id]['subject']}</b>\n"
                             f"Тип занятия: <b>{user_links_dict[message.chat.id]['subject_type']}</b>\n"
                             f"Ссылка: <b>{user_links_dict[message.chat.id]['link']}</b>\n\n"
                             f"Ты можешь:\n"
                             f"1. Отправить мне <b>ссылку</b> повторно (заменяется предыдущая)\n"
                             f"2. Добавить <b>пароль</b>, нажав <b>'{add_password_button}'</b>\n"
                             f"3. Нажать <b>'{confirm_button}'</b> (ссылка будет видна в расписании) и перейти в главное меню\n"
                             f"4. Нажать <b>'{cancel_button}'</b> (ссылки не будет видно в расписании) и перейти в главное меню",
                             reply_markup=keyboard_generator.generate_default_keyboard_row(
                                 (add_password_button, confirm_button),
                                 (cancel_button,)),
                             parse_mode='HTML',
                             disable_web_page_preview=True)

        elif user_links_dict[message.chat.id]['password'] != '':
            user_links_dict[message.chat.id]['link'] = message.text
            bot.send_message(message.chat.id,
                             f"Предмет: <b>{user_links_dict[message.chat.id]['subject']}</b>\n"
                             f"Тип занятия: <b>{user_links_dict[message.chat.id]['subject_type']}</b>\n"
                             f"Ссылка: <b>{user_links_dict[message.chat.id]['link']}</b>\n"
                             f"Пароль: <b>{user_links_dict[message.chat.id]['password']}</b>\n\n"
                             f"Ты можешь:\n"
                             f"1. Отправить мне <b>ссылку</b> повторно (заменяется предыдущая)\n"
                             f"2. Изменить <b>пароль</b>, нажав <b>'{change_password_button}'</b>\n"
                             f"3. Нажать <b>'{confirm_button}'</b> (ссылка будет видна в расписании) и перейти в главное меню\n"
                             f"4. Нажать <b>'{cancel_button}'</b> (ссылки не будет видно в расписании) и перейти в главное меню",
                             reply_markup=keyboard_generator.generate_default_keyboard_row(
                                 (change_password_button, confirm_button),
                                 (cancel_button,)),
                             parse_mode='HTML',
                             disable_web_page_preview=True)


@bot.message_handler(func=lambda message: db.get_state(message.chat.id).__class__ == tuple and
                                          db.get_state(message.chat.id)[
                                              0] == stateworker.States.S_CHANGE_PASSWORD.value)
def change_password(message):
    if message.text == cancel_button:
        bot.send_message(message.chat.id,
                         f"Главное меню",
                         reply_markup=keyboard_generator.main_menu_keyboard)
        db.set_state(message.from_user.username,
                     stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)

    elif message.text == confirm_button:
        bot.send_message(message.chat.id,
                         f"Ссылка для <b>'{user_links_dict[message.chat.id]['subject_type']}</b> - "
                         f"<b>{user_links_dict[message.chat.id]['subject']}'</b> успешно изменена.",
                         reply_markup=keyboard_generator.main_menu_keyboard,
                         parse_mode='HTML',
                         disable_web_page_preview=True)
        db.change_link(user_links_dict[message.chat.id]['link'],
                       user_links_dict[message.chat.id]['password'],
                       message.chat.id,
                       user_links_dict[message.chat.id]['subject'],
                       user_links_dict[message.chat.id]['subject_type'],
                       user_links_dict[message.chat.id]['addition_date'])
        db.set_state(message.from_user.username,
                     stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)

    elif message.text == change_link_button:
        if user_links_dict[message.chat.id]['password'] == '':
            bot.send_message(message.chat.id,
                             f"Предмет: <b>{user_links_dict[message.chat.id]['subject']}</b>\n"
                             f"Тип занятия: <b>{user_links_dict[message.chat.id]['subject_type']}</b>\n"
                             f"Ссылка: <b>{user_links_dict[message.chat.id]['link']}</b>\n\n"
                             f"Ты можешь:\n"
                             f"1. Отправить мне <b>ссылку</b> повторно (заменяется предыдущая)\n"
                             f"2. Добавить <b>пароль</b>, нажав <b>'{add_password_button}'</b>\n"
                             f"3. Нажать <b>'{confirm_button}'</b> (ссылка будет видна в расписании) и перейти в главное меню\n"
                             f"4. Нажать <b>'{cancel_button}'</b> (ссылки не будет видно в расписании) и перейти в главное меню",
                             reply_markup=keyboard_generator.generate_default_keyboard_row(
                                 (add_password_button, confirm_button),
                                 (cancel_button,)),
                             parse_mode='HTML',
                             disable_web_page_preview=True)

        elif user_links_dict[message.chat.id]['password'] != '':
            bot.send_message(message.chat.id,
                             f"Предмет: <b>{user_links_dict[message.chat.id]['subject']}</b>\n"
                             f"Тип занятия: <b>{user_links_dict[message.chat.id]['subject_type']}</b>\n"
                             f"Ссылка: <b>{user_links_dict[message.chat.id]['link']}</b>\n"
                             f"Пароль: <b>{user_links_dict[message.chat.id]['password']}</b>\n\n"
                             f"Ты можешь:\n"
                             f"1. Отправить мне <b>ссылку</b> повторно (заменяется предыдущая)\n"
                             f"2. Изменить <b>пароль</b>, нажав <b>'{change_password_button}'</b>\n"
                             f"3. Нажать <b>'{confirm_button}'</b> (ссылка будет видна в расписании) и перейти в главное меню\n"
                             f"4. Нажать <b>'{cancel_button}'</b> (ссылки не будет видно в расписании) и перейти в главное меню",
                             reply_markup=keyboard_generator.generate_default_keyboard_row(
                                 (change_password_button, confirm_button),
                                 (cancel_button,)),
                             parse_mode='HTML',
                             disable_web_page_preview=True)
        db.set_state(message.from_user.username,
                     stateworker.States.S_CHANGE_LINK.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)

    elif message.text == message.text:
        user_links_dict[message.chat.id]['password'] = message.text
        if user_links_dict[message.chat.id]['password'] == '':
            bot.send_message(message.chat.id,
                             f"Предмет: <b>{user_links_dict[message.chat.id]['subject']}</b>\n"
                             f"Тип занятия: <b>{user_links_dict[message.chat.id]['subject_type']}</b>\n"
                             f"Ссылка: <b>{user_links_dict[message.chat.id]['link']}</b>\n\n"
                             f"Ты можешь:\n"
                             f"1. Отправить мне <b>пароль</b>\n"
                             f"2. Изменить <b>ссылку</b>, нажав <b>'{change_link_button}'</b>\n"
                             f"3. Нажать <b>'{confirm_button}'</b> (ссылка будет видна в расписании) и перейти в главное меню\n"
                             f"4. Нажать <b>'{cancel_button}'</b> (ссылки не будет видно в расписании) и перейти в главное меню",
                             reply_markup=keyboard_generator.generate_default_keyboard_row(
                                 (change_link_button, confirm_button),
                                 (cancel_button,)),
                             parse_mode='HTML',
                             disable_web_page_preview=True)

        elif user_links_dict[message.chat.id]['password'] != '':
            user_links_dict[message.chat.id]['password'] = message.text
            bot.send_message(message.chat.id,
                             f"Предмет: <b>{user_links_dict[message.chat.id]['subject']}</b>\n"
                             f"Тип занятия: <b>{user_links_dict[message.chat.id]['subject_type']}</b>\n"
                             f"Ссылка: <b>{user_links_dict[message.chat.id]['link']}</b>\n"
                             f"Пароль: <b>{user_links_dict[message.chat.id]['password']}</b>\n\n"
                             f"Ты можешь:\n"
                             f"1. Отправить мне <b>пароль</b> повторно (заменяется предыдущий)\n"
                             f"2. Изменить <b>ссылку</b>, нажав <b>'{change_link_button}'</b>\n"
                             f"3. Нажать <b>'{confirm_button}'</b> (ссылка будет видна в расписании) и перейти в главное меню\n"
                             f"4. Нажать <b>'{cancel_button}'</b> (ссылки не будет видно в расписании) и перейти в главное меню",
                             reply_markup=keyboard_generator.generate_default_keyboard_row(
                                 (change_link_button, confirm_button),
                                 (cancel_button,)),
                             parse_mode='HTML',
                             disable_web_page_preview=True)


"""#####################################################################################################################
                                                    SCHEDULE MENU
#####################################################################################################################"""


@bot.message_handler(func=lambda message: db.get_state(message.chat.id).__class__ == tuple and
                     db.get_state(message.chat.id)[0] == stateworker.States.S_SCHEDULE_MENU.value)
def schedule_menu(message):
    if message.text == back_button:
        bot.send_message(message.chat.id,
                         f"Возвращаемся...",
                         reply_markup=keyboard_generator.main_menu_keyboard)
        db.set_state(message.from_user.username,
                     stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)

    elif message.text == today_day_button:
        bot.send_message(message.chat.id,
                         show_day(message.chat.id, f"Сегодня", date.today().weekday() + 1),
                         parse_mode="HTML",
                         reply_markup=keyboard_generator.schedule_menu_keyboard,
                         disable_web_page_preview=True)
        db.set_state(message.from_user.username,
                     stateworker.States.S_SCHEDULE_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)

    elif message.text == tomorrow_day_button:
        bot.send_message(message.chat.id,
                         show_day(message.chat.id, "Завтра", (date.today() + datetime.timedelta(days=1)).weekday() + 1),
                         parse_mode="HTML",
                         reply_markup=keyboard_generator.schedule_menu_keyboard,
                         disable_web_page_preview=True)
        db.set_state(message.from_user.username,
                     stateworker.States.S_SCHEDULE_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)

    elif message.text == week1_button:
        bot.send_message(message.chat.id,
                         f"А теперь день",
                         reply_markup=keyboard_generator.week1_day_choose_keyboard)
        db.set_state(message.from_user.username,
                     stateworker.States.S_SCHEDULE_WEEK_VIEW_1.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)

    elif message.text == week2_button:
        bot.send_message(message.chat.id,
                         f"А теперь день",
                         reply_markup=keyboard_generator.week2_day_choose_keyboard)
        db.set_state(message.from_user.username,
                     stateworker.States.S_SCHEDULE_WEEK_VIEW_2.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)


@bot.message_handler(func=lambda message: db.get_state(message.chat.id).__class__ == tuple and
                     db.get_state(message.chat.id)[0] == stateworker.States.S_SCHEDULE_WEEK_VIEW_1.value)
def week_view_1(message):
    for i in range(0, 5):
        if message.text == week1_day_buttons[i]:
            bot.send_message(message.chat.id,
                             Schedule.show_schedule(message.chat.id, 1, i + 1, week_days[i + 1]),
                             parse_mode="HTML",
                             reply_markup=keyboard_generator.week1_day_choose_keyboard,
                             disable_web_page_preview=True)
            db.set_state(message.from_user.username,
                         stateworker.States.S_SCHEDULE_WEEK_VIEW_1.value,
                         time.strftime('%d/%m/%y, %X'),
                         message.chat.id)

    if message.text == back_button:
        bot.send_message(message.chat.id,
                         f"Возвращаемся...",
                         reply_markup=keyboard_generator.schedule_menu_keyboard)
        db.set_state(message.from_user.username,
                     stateworker.States.S_SCHEDULE_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)


@bot.message_handler(func=lambda message: db.get_state(message.chat.id).__class__ == tuple and
                     db.get_state(message.chat.id)[0] == stateworker.States.S_SCHEDULE_WEEK_VIEW_2.value)
def week_view_2(message):
    for i in range(0, 5):
        if message.text == week2_day_buttons[i]:
            bot.send_message(message.chat.id,
                             Schedule.show_schedule(message.chat.id, 2, i + 1, week_days[i + 1]),
                             parse_mode="HTML",
                             reply_markup=keyboard_generator.week2_day_choose_keyboard,
                             disable_web_page_preview=True)
            db.set_state(message.from_user.username,
                         stateworker.States.S_SCHEDULE_WEEK_VIEW_2.value,
                         time.strftime('%d/%m/%y, %X'),
                         message.chat.id)

    if message.text == back_button:
        bot.send_message(message.chat.id,
                         f"Возвращаемся...",
                         reply_markup=keyboard_generator.schedule_menu_keyboard)
        db.set_state(message.from_user.username,
                     stateworker.States.S_SCHEDULE_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)


"""#####################################################################################################################
                                                    SETTINGS MENU
#####################################################################################################################"""


@bot.message_handler(func=lambda message: db.get_state(message.chat.id).__class__ == tuple and
                     db.get_state(message.chat.id)[0] == stateworker.States.S_SETTINGS_MENU.value)
def settings_menu(message):
    if message.text == back_button:
        bot.send_message(message.chat.id,
                         f"Главное меню",
                         reply_markup=keyboard_generator.main_menu_keyboard)
        db.set_state(message.from_user.username,
                     stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)

    if message.text == notifications_button:
        bot.reply_to(message,
                     not_available_reply)
        db.set_state(message.from_user.username,
                     stateworker.States.S_SETTINGS_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)

    if message.text == change_group_button:
        bot.send_message(message.chat.id,
                         f"Введи название группы",
                         reply_markup=keyboard_generator.generate_default_keyboard(cancel_button))
        db.set_state(message.from_user.username,
                     stateworker.States.S_CHANGE_GROUP.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)

    if message.text == cancel_button:
        bot.send_message(message.chat.id,
                         settings_reply,
                         reply_markup=keyboard_generator.settings_menu_keyboard)
        db.set_state(message.from_user.username,
                     stateworker.States.S_SETTINGS_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)


bot.polling()
