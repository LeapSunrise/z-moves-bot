import datetime
import os
import time
import src.config.config as config

import telebot_calendar
from telebot.types import ReplyKeyboardRemove, CallbackQuery
from telebot_calendar import CallbackData

from src.schedule_parser.schedule_parser import *
from src.service import keyboard_generator, stateworker, service
from src.service.buttons import *

bot = telebot.TeleBot(config.BOT_TOKEN)
# db.init_db()
lorem_ipsum = 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'
"""#####################################################################################################################
                                                    START
#####################################################################################################################"""


# @bot.message_handler(func=lambda message: rozklad_api_work_checker() is False)
# def long_request(message):
#
#     bot.send_message(message.chat.id,
#                      f"Йоооой.. Что-то пошло не по плану..\n"
#                      f"Скорее всего API расписания КПИ наився и спыть 🤧\n"
#                      f"Можешь позалипать пока на дино, а я попробую тебя уведомить, как только апишка встанет :(",
#                      reply_markup=telebot.types.ForceReply(),
#                      )
#     bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEB9bhgQ6DCUQz5y_Mh7uwdvVxAWMiosgACEQAD1gWXKgGow7AQ9URiHgQ', reply_markup=telebot.types.ForceReply())
#
#
#
# @bot.message_handler(func=lambda message: rozklad_api_work_checker() is True)
# def good_request(message):
#     bot.send_message(message.chat.id, 'УРРААА, АПИШКА ВСТАЛА ПИЗДЕЦ!',
#                      reply_markup=keyboard_generator.main_menu_keyboard)


@bot.message_handler(func=lambda message: db.get_blocked_user(message.chat.id) is not None and
                                          message.chat.id in db.get_blocked_user(message.chat.id))
def black_list(message):
    user_name = message.from_user.first_name
    if message.from_user.last_name:
        user_name = f"{user_name} {message.from_user.last_name}"
    db.update_blocked_users(message.chat.id,
                            user_name,
                            time.strftime('%d/%m/%y, %X'),
                            time.strftime('%d/%m/%y, %X'))
    bot.send_sticker(message.chat.id,
                     'CAACAgIAAxkBAAEB9bhgQ6DCUQz5y_Mh7uwdvVxAWMiosgACEQAD1gWXKgGow7AQ9URiHgQ')
    bot.send_message(message.chat.id,
                     'Сорян, но ты в ЧС 😢',
                     reply_markup=telebot.types.ReplyKeyboardRemove())


@bot.message_handler(commands=['start', 'START'])
def start_message(message):
    bot.send_message(message.chat.id,
                     f"Привет,  🥴🤙\nZ-Moves на связи 😎\n\n"
                     f"Для работы со мной напиши мне название своей группы.\n\nПример: <b>IO-83</b>",
                     parse_mode='HTML')


    # service.rozklad_api_work_checker()
    # user_name = message.from_user.first_name
    # if message.from_user.last_name:
    #     user_name = f"{user_name} {message.from_user.last_name}"
    #
    # if db.get_user_info(message.chat.id) is None:
    #     bot.send_message(message.chat.id,
    #                      f"Привет, {user_name}! 🥴🤙\nZ-Moves на связи 😎\n\n"
    #                      f"Для работы со мной напиши мне название своей группы.\n\nПример: <b>IO-83</b>",
    #                      parse_mode='HTML')
    #     db.register_user(message.chat.id,
    #                      message.from_user.username,
    #                      stateworker.States.S_REGISTRATION.value,
    #                      time.strftime('%d/%m/%y, %X'),
    #                      time.strftime('%d/%m/%y, %X'))
    #     print(db.get_user_info(message.chat.id))
    #
    # elif db.get_user_info(message.chat.id)[2] is None:
    #     bot.send_message(message.chat.id,
    #                      "Перестань тестировать меня. Введи группу плес")
    #
    #
    # else:
    #     bot.send_message(message.chat.id,
    #                      "Главное меню",
    #                      reply_markup=keyboard_generator.main_menu_keyboard)
    #     db.set_state(message.from_user.username,
    #                  stateworker.States.S_MAIN_MENU.value,
    #                  time.strftime('%d/%m/%y, %X'),
    #                  message.chat.id)


@bot.message_handler(func=lambda message: (db.get_state(message.chat.id).__class__ == tuple and
                                           (db.get_state(message.chat.id)[
                                                0] == stateworker.States.S_REGISTRATION.value or
                                            db.get_state(message.chat.id)[
                                                0] == stateworker.States.S_CHANGE_GROUP.value)))
def group_registration(message):
    if Schedule.is_group_exist(message.text):
        bot.send_message(message.chat.id,
                         f"Есть такая! Ну а теперь приступим 🙂",
                         reply_markup=keyboard_generator.main_menu_keyboard)
        db.register_user_group_name(message.from_user.username,
                                    message.text,
                                    stateworker.States.S_MAIN_MENU.value,
                                    time.strftime('%d/%m/%y, %X'),
                                    message.chat.id)

    elif message.text == cancel_button:
        bot.send_message(message.chat.id,
                         "Настройки",
                         reply_markup=keyboard_generator.settings_menu_keyboard)
        db.set_state(message.from_user.username,
                     stateworker.States.S_SETTINGS_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)

    else:
        bot.send_message(message.chat.id,
                         f"<b>{message.text}</b>? Что-то я о такой группе ещё не слышал 🤥",
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
                         f"Выбери опцию отображения расписания.",
                         reply_markup=keyboard_generator.schedule_menu_keyboard)
        db.set_state(message.from_user.username,
                     stateworker.States.S_SCHEDULE_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)

    elif message.text == settings_button:
        bot.send_message(message.chat.id,
                         f"Что нужно настроить?",
                         reply_markup=keyboard_generator.settings_menu_keyboard)
        db.set_state(message.from_user.username,
                     stateworker.States.S_SETTINGS_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)

    elif message.text == links_button:
        bot.send_message(message.chat.id,
                         f"Здесь ты можешь добавлять ссылки к предметам, изменять и даже их удалять, "
                         f"если они есть.",
                         reply_markup=service.dynamic_menu_links_inline_keyboard_generator(message.chat.id))
        db.set_state(message.from_user.username,
                     stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)

    elif message.text == hotlines_button:
        bot.send_message(message.chat.id,
                         f"Здесь ты можешь добавлять хотлайны (дедлайны - плохо) к предметам",
                         reply_markup=service.dynamic_menu_hotlines_inline_keyboard_generator(message.chat.id))
        db.set_state(message.from_user.username,
                     stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)

    elif message.text == mails_button:
        bot.reply_to(message,
                     service.not_available_reply)
        db.set_state(message.from_user.username,
                     stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)

    elif message.text == info_button:
        info_button_reply = f"Ты залогинен под группой: <b>{db.get_user_info(message.chat.id)[2]}</b>\n\n" \
                            f"Обо мне:\n\n" \
                            f"Я — <b>Z-Moves</b>, единственный наследник ЗМ, истинный владыка семи королевств и ... \n" \
                            f"Впрочем, это уже совсем другая история.\n\n" \
                            f"Я обычный бот, показывающий расписание — скажут хейтеры. Но как бы не так. " \
                            f"Со мной ты можешь:\n\n" \
                            f"1. Прикреплять ссылки 🔗 к парам, которые порой так сложно и долго искать.\n" \
                            f"2. 👺 Хотлайны. Ты всегда сможешь в сию минуту узнать до какого числа нужно сдать вторую " \
                            f"лабу по Взлому Жопы 🧑‍💻\n" \
                            f"3. Такого интерфейса ты ещё не видел 😎\n" \
                            f"4. И это только начало 🤯 Я постепенно развиваюсь и добавляю в себя новые фичи, которые " \
                            f"будут радовать тебя всё больше и больше 🤓\n" \
                            f"5. Хватит читать! Давай бегом ссылки добавлять 🥴\n\n" \
                            f"Да, и чуть не забыл. <a href='https://send.monobank.ua/jar/9RyLwakdWd'>Тут</a> можно " \
                            f"сказать мне спасибо.\n👉👈" \

        bot.send_message(message.chat.id,
                         info_button_reply,
                         reply_markup=keyboard_generator.main_menu_keyboard,
                         parse_mode='HTML',
                         disable_web_page_preview=True)
        db.set_state(message.from_user.username,
                     stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)

    elif message.text == help_button:
        bot.reply_to(message,
                     service.not_available_reply)
        db.set_state(message.from_user.username,
                     stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)


user_links_dict = {}
user_hotlines_dict = {}

"""#####################################################################################################################
                                                    MAIN MENU/LINKS MENU
#####################################################################################################################"""

calendar_1 = CallbackData("calendar_1", "action", "year", "month", "day")
calendar_keyboard = telebot_calendar.create_calendar(name=calendar_1.prefix,
                                                     year=datetime.datetime.now().year,
                                                     month=datetime.datetime.now().month, )


@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_1.prefix) == False)
def links_menu(call):
    inline_subject_keyboard_to_add_link = service.generate_inline_subjects_to_add_link(call.message.chat.id)
    inline_linked_subject_keyboard_to_ch = service.generate_inline_linked_subjects_to_change(call.message.chat.id)
    inline_linked_subject_keyboard_to_rm = service.generate_inline_linked_subjects_to_remove(call.message.chat.id)

    inline_subject_keyboard_to_add_hotline = service.generate_inline_subjects_to_add_hotline(call.message.chat.id)
    inline_hotlined_subject_keyboard_to_ch = service.generate_inline_hotlined_subjects_to_change(call.message.chat.id)
    inline_hotlined_subject_keyboard_to_rm = service.generate_inline_hotlined_subjects_to_remove(call.message.chat.id)

    inline_subject_type_keyboard = telebot.types.InlineKeyboardMarkup()
    inline_subject_type_keyboard.add(inline_lec_button, inline_lab_button, inline_prac_button)
    inline_subject_type_keyboard.add(inline_second_back_button)

    inline_confirm_cancel_keyboard = telebot.types.InlineKeyboardMarkup()
    inline_confirm_cancel_keyboard.add(inline_remove_link_cancel_button, inline_remove_link_confirm_button)

    inline_confirm_cancel_keyboard_hl = telebot.types.InlineKeyboardMarkup()
    inline_confirm_cancel_keyboard_hl.add(inline_remove_hotline_cancel_button, inline_remove_hotline_confirm_button)

    if call.data == 'add_link' or call.data == 'second_back_button':
        bot.edit_message_text(f"Выбери предмет для которого нужно добавить ссылку",
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=inline_subject_keyboard_to_add_link,
                              parse_mode='HTML')

    if call.data == 'add_hotline':
        bot.edit_message_text(f"Выбери предмет для которого нужно добавить хотлайн",
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=inline_subject_keyboard_to_add_hotline,
                              parse_mode='HTML')

    if call.data == 'change_link':
        bot.edit_message_text(f"Выбери предмет для которого нужно изменить ссылку",
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=inline_linked_subject_keyboard_to_ch,
                              parse_mode='HTML')

    if call.data == 'change_hotline':
        bot.edit_message_text(f"Выбери предмет для которого нужно изменить хотлайн",
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=inline_hotlined_subject_keyboard_to_ch,
                              parse_mode='HTML')

    if call.data == 'remove_link':
        bot.edit_message_text(f"Выбери предмет для которого нужно удалить ссылку",
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=inline_linked_subject_keyboard_to_rm,
                              parse_mode='HTML')

    if call.data == 'remove_hotline':
        bot.edit_message_text(f"Выбери хотлайн, который нужно удалить",
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=inline_hotlined_subject_keyboard_to_rm,
                              parse_mode='HTML')

    if call.data == 'first_back_button':
        bot.edit_message_text(f"Здесь ты можешь добавлять ссылки к предметам, изменять и даже их удалять, "
                              f"если они есть.",
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=service.dynamic_menu_links_inline_keyboard_generator(call.message.chat.id),
                              parse_mode='HTML')

    if call.data == 'first_back_button_hl':
        bot.edit_message_text(f"Выбери предмет для которого нужно добавить хотлайн",
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=service.dynamic_menu_hotlines_inline_keyboard_generator(
                                  call.message.chat.id),
                              parse_mode='HTML')

    # jump to ADD_LINK state
    if inline_subject_keyboard_to_add_link != '' and call.data in [button['callback_data'] for buttons in
                                                                   inline_subject_keyboard_to_add_link.to_dict()[
                                                                       'inline_keyboard']
                                                                   for button in buttons]:
        print(inline_subject_keyboard_to_add_link.to_dict()['inline_keyboard'])
        for buttons in inline_subject_keyboard_to_add_link.to_dict()['inline_keyboard'][
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
                                          reply_markup=inline_subject_type_keyboard,
                                          parse_mode='HTML')

    if inline_subject_type_keyboard != '' and call.data in [button['callback_data'] for buttons in
                                                            inline_subject_type_keyboard.to_dict()['inline_keyboard']
                                                            for button in buttons]:
        for button in inline_subject_type_keyboard.to_dict()['inline_keyboard'][
            0]:  # тут [0] чтобы не ловилась бэк-кнопка
            if button['callback_data'] == call.data:
                user_links_dict[call.message.chat.id]['subject_type'] = button['text']
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

    # jump to CHANGE_LINK state

    if inline_linked_subject_keyboard_to_ch != '' and \
            call.data in [button['callback_data'] for buttons in
                          inline_linked_subject_keyboard_to_ch.to_dict()['inline_keyboard'] for button in buttons]:
        for buttons in inline_linked_subject_keyboard_to_ch.to_dict()['inline_keyboard'][
                       :len(inline_linked_subject_keyboard_to_ch.to_dict()[
                                'inline_keyboard']) - 1]:  # тут -1 чтобы не ловилась бэк-кнопка
            for button in buttons:

                if button['callback_data'] == call.data:

                    user_links_dict.update({call.message.chat.id: {  # колдата после _
                        'subject': button['text'][button['text'].find('-') + 2:],  # после -+пробел
                        'subject_type': button['text'][:button['text'].find(' ')],  # до первого пробела
                        'addition_date': button['callback_data'][button['callback_data'].find('_') + 1:]
                        # колдата после _
                    }})

                    user_links_dict[call.message.chat.id]['link'] = db.get_links_to_change(call.message.chat.id,
                                                                                           user_links_dict[
                                                                                               call.message.chat.id][
                                                                                               'subject'],
                                                                                           user_links_dict[
                                                                                               call.message.chat.id][
                                                                                               'subject_type'],
                                                                                           user_links_dict[
                                                                                               call.message.chat.id][
                                                                                               'addition_date'])[3]

                    user_links_dict[call.message.chat.id]['password'] = db.get_links_to_change(call.message.chat.id,
                                                                                               user_links_dict[
                                                                                                   call.message.chat.id][
                                                                                                   'subject'],
                                                                                               user_links_dict[
                                                                                                   call.message.chat.id][
                                                                                                   'subject_type'],
                                                                                               user_links_dict[
                                                                                                   call.message.chat.id][
                                                                                                   'addition_date'])[4]

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

    # remove link
    if inline_linked_subject_keyboard_to_rm != '' and \
            call.data in [button['callback_data'] for buttons in
                          inline_linked_subject_keyboard_to_rm.to_dict()['inline_keyboard'] for button in buttons]:
        for buttons in inline_linked_subject_keyboard_to_rm.to_dict()['inline_keyboard'][
                       :len(inline_linked_subject_keyboard_to_rm.to_dict()[
                                'inline_keyboard']) - 1]:  # тут -1 чтобы не ловилась бэк-кнопка
            for button in buttons:
                if button['callback_data'] == call.data:
                    user_links_dict.update({call.message.chat.id: {
                        'subject': button['text'][int(button['text'].find('-')) + 2:],  # текст кнопки после '- '
                        'subject_type': button['text'][:int(button['text'].find(' '))],  # текст кнопки до ' '
                        'link': '',
                        'password': '',
                        'addition_date': button['callback_data'][button['callback_data'].find('_') + 1:]
                    }})
                    user_links_dict[call.message.chat.id]['link'] = \
                        db.get_links_to_change(call.message.chat.id,
                                               user_links_dict[call.message.chat.id]['subject'],
                                               user_links_dict[call.message.chat.id]['subject_type'],
                                               user_links_dict[call.message.chat.id]['addition_date'])[3]  # 3 - ссылка
                    user_links_dict[call.message.chat.id]['password'] = \
                        db.get_links_to_change(call.message.chat.id,
                                               user_links_dict[call.message.chat.id]['subject'],
                                               user_links_dict[call.message.chat.id]['subject_type'],
                                               user_links_dict[call.message.chat.id]['addition_date'])[4]  # 4 - пароль

                    if user_links_dict[call.message.chat.id]['password'] == '':
                        bot.edit_message_text(f"Ты удаляешь:\n"
                                              f"Предмет: <b>{user_links_dict[call.message.chat.id]['subject']}</b>\n"
                                              f"Тип занятия: <b>{user_links_dict[call.message.chat.id]['subject_type']}</b>\n"
                                              f"Ссылка: <b>{user_links_dict[call.message.chat.id]['link']}</b>\n",
                                              chat_id=call.message.chat.id,
                                              message_id=call.message.message_id,
                                              reply_markup=inline_confirm_cancel_keyboard,
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
                                              reply_markup=inline_confirm_cancel_keyboard,
                                              parse_mode='HTML',
                                              disable_web_page_preview=True)

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
                              reply_markup=inline_linked_subject_keyboard_to_rm,
                              parse_mode='HTML')

    if call.data == 'confirm_remove_hotline':
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)
        db.remove_hotline(call.message.chat.id,
                          user_hotlines_dict[call.message.chat.id]['subject'],
                          user_hotlines_dict[call.message.chat.id]['description'],
                          user_hotlines_dict[call.message.chat.id]['date'],
                          user_hotlines_dict[call.message.chat.id]['addition_date'])

        bot.send_message(call.message.chat.id,
                         f"Хотлайн {user_hotlines_dict[call.message.chat.id]['subject']} успешно удалён")

    if call.data == 'cancel_remove_hotline':
        bot.edit_message_text(f"Выбери хотлайн для удаления",
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=inline_hotlined_subject_keyboard_to_rm,
                              parse_mode='HTML')

    if inline_subject_keyboard_to_add_hotline != '' and \
            call.data in [button['callback_data'] for buttons in
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

    if inline_hotlined_subject_keyboard_to_ch != '' and \
            call.data in [button['callback_data'] for buttons in
                          inline_hotlined_subject_keyboard_to_ch.to_dict()['inline_keyboard'] for button in buttons]:

        for buttons in inline_hotlined_subject_keyboard_to_ch.to_dict()['inline_keyboard'][
                       :len(inline_hotlined_subject_keyboard_to_ch.to_dict()['inline_keyboard']) - 1]:
            for button in buttons:
                if button['callback_data'] == call.data:
                    user_hotlines_dict.update({call.message.chat.id: {
                        'subject': button['text'][button['text'].find('-') + 2:],
                        'description': '',
                        'date': '',
                        'addition_date': button['callback_data'][button['callback_data'].find('_') + 1:]
                    }})

                    user_hotlines_dict[call.message.chat.id]['description'] = \
                        db.get_hotlines_to_change(call.message.chat.id,
                                                  user_hotlines_dict[call.message.chat.id]['subject'],
                                                  user_hotlines_dict[call.message.chat.id]['addition_date'])[0]
                    user_hotlines_dict[call.message.chat.id]['date'] = db.get_hotlines_to_change(call.message.chat.id,
                                                                                                 user_hotlines_dict[
                                                                                                     call.message.chat.id][
                                                                                                     'subject'],
                                                                                                 user_hotlines_dict[
                                                                                                     call.message.chat.id][
                                                                                                     'addition_date'])[
                        1]
                    bot.edit_message_text(f"Выбери новую дату для хотлайна",
                                          chat_id=call.message.chat.id,
                                          message_id=call.message.message_id,
                                          reply_markup=calendar_keyboard,
                                          parse_mode='HTML',
                                          disable_web_page_preview=True)

    if inline_hotlined_subject_keyboard_to_rm != '' and call.data in [button['callback_data'] for buttons in
                                                                      inline_hotlined_subject_keyboard_to_rm.to_dict()[
                                                                          'inline_keyboard'][:len(
                                                                          inline_hotlined_subject_keyboard_to_rm.to_dict()[
                                                                              'inline_keyboard']) - 1] for button in
                                                                      buttons]:
        for buttons in inline_hotlined_subject_keyboard_to_rm.to_dict()['inline_keyboard'][
                       :len(inline_hotlined_subject_keyboard_to_rm.to_dict()['inline_keyboard']) - 1]:
            for button in buttons:
                if button['callback_data'] == call.data:
                    user_hotlines_dict.update({call.message.chat.id: {
                        'subject': button['text'][button['text'].find('-') + 2:],
                        'description': '',
                        'date': '',
                        'addition_date': button['callback_data'][button['callback_data'].find('_') + 1:]
                    }})

                    user_hotlines_dict[call.message.chat.id]['description'] = \
                        db.get_hotlines_to_change(call.message.chat.id,
                                                  user_hotlines_dict[call.message.chat.id]['subject'],
                                                  user_hotlines_dict[call.message.chat.id]['addition_date'])[0]

                    user_hotlines_dict[call.message.chat.id]['date'] = \
                        db.get_hotlines_to_change(call.message.chat.id,
                                                  user_hotlines_dict[call.message.chat.id]['subject'],
                                                  user_hotlines_dict[call.message.chat.id]['addition_date'])[1]

                    bot.edit_message_text(f"Ты удаляешь хотлайн:\n\n"
                                          f"{lorem_ipsum}",
                                          chat_id=call.message.chat.id,
                                          message_id=call.message.message_id,
                                          reply_markup=inline_confirm_cancel_keyboard_hl,
                                          parse_mode='HTML',
                                          disable_web_page_preview=True)


@bot.callback_query_handler(func=lambda call: call.data.startswith(calendar_1.prefix))
def input_hotline_date(call: CallbackQuery):
    name, action, year, month, day = call.data.split(calendar_1.sep)
    date = telebot_calendar.calendar_query_handler(bot=bot,
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
                         reply_markup=ReplyKeyboardRemove())

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

    if message.text == confirm_button:
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
                                                    MAIN MENU/HOTLINES MENU
#####################################################################################################################"""

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
                     stateworker.States.S_SCHEDULE_WEEK_VIEW.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)

    elif message.text == week2_button:
        bot.send_message(message.chat.id,
                         f"А теперь день",
                         reply_markup=keyboard_generator.week2_day_choose_keyboard)
        db.set_state(message.from_user.username,
                     stateworker.States.S_SCHEDULE_WEEK_VIEW.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)


@bot.message_handler(func=lambda message: db.get_state(message.chat.id).__class__ == tuple and
                                          db.get_state(message.chat.id)[
                                              0] == stateworker.States.S_SCHEDULE_WEEK_VIEW.value)
def week_view(message):
    for i in range(0, 5):
        if message.text == week1_day_buttons[i]:
            bot.send_message(message.chat.id,
                             Schedule.show_schedule(message.chat.id, 1, i + 1, week_days[i + 1]),
                             parse_mode="HTML",
                             reply_markup=keyboard_generator.week1_day_choose_keyboard,
                             disable_web_page_preview=True)
            db.set_state(message.from_user.username,
                         stateworker.States.S_SCHEDULE_WEEK_VIEW.value,
                         time.strftime('%d/%m/%y, %X'),
                         message.chat.id)

        elif message.text == week2_day_buttons[i]:
            bot.send_message(message.chat.id,
                             Schedule.show_schedule(message.chat.id, 2, i + 1, week_days[i + 1]),
                             parse_mode="HTML",
                             reply_markup=keyboard_generator.week2_day_choose_keyboard,
                             disable_web_page_preview=True)
            db.set_state(message.from_user.username,
                         stateworker.States.S_SCHEDULE_WEEK_VIEW.value,
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
                     service.not_available_reply)
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
                         f"Настройки",
                         reply_markup=keyboard_generator.settings_menu_keyboard)
        db.set_state(message.from_user.username,
                     stateworker.States.S_SETTINGS_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)


bot.polling()
