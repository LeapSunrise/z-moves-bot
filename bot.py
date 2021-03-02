import datetime
import os
import time

from schedule_parser.schedule_parser import *
from service import keyboard_generator, stateworker
from service import service
from service.buttons import *

bot = telebot.TeleBot(os.environ['BOT_TOKEN'])
db.init_db()

"""#####################################################################################################################
                                                    START
#####################################################################################################################"""


@bot.message_handler(commands=['start', 'START'])
def start_message(message):
    user_name = message.from_user.first_name
    if message.from_user.last_name:
        user_name = f"{user_name} {message.from_user.last_name}"

    if db.get_user_info(message.chat.id) is None:
        bot.send_message(message.chat.id,
                         f"Привет, {user_name}! 🥴🤙\nZ-Moves на связи 😎\n\n"
                         f"Для работы со мной напиши мне название своей группы.\n\nПример: <b>IO-83<</b>",
                         parse_mode='HTML')
        db.register_user(message.chat.id,
                         message.from_user.username,
                         stateworker.States.S_REGISTRATION.value,
                         time.strftime('%d/%m/%y, %X'),
                         time.strftime('%d/%m/%y, %X'))

    elif db.get_user_info(message.chat.id)[2] is None:
        bot.send_message(message.chat.id,
                         f"Перестань тестировать меня. Введи группу плес")

    else:
        bot.send_message(message.chat.id,
                         f"Главное меню",
                         reply_markup=keyboard_generator.main_menu_keyboard)
        db.set_state(message.from_user.username,
                     stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)


@bot.message_handler(func=lambda message: (db.get_state(message.chat.id).__class__ == tuple and
                                           db.get_state(message.chat.id)[
                                               0] == stateworker.States.S_REGISTRATION.value) or

                                          (db.get_state(message.chat.id).__class__ == tuple and
                                           db.get_state(message.chat.id)[0] == stateworker.States.S_CHANGE_GROUP.value))
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
                         f"Настройки",
                         reply_markup=keyboard_generator.settings_menu_keyboard)
        db.set_state(message.from_user.username,
                     stateworker.States.S_SETTINGS_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)

    else:
        bot.send_message(message.chat.id, '<b>{}</b>? Что-то я о такой группе ещё не слышал 🤥'
                                          'Попробуй ещё.'.format(message.text), parse_mode='HTML')
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
        bot.reply_to(message,
                     service.not_available_reply)
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
        bot.reply_to(message,
                     service.not_available_reply)
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


@bot.callback_query_handler(func=lambda call: True)
def links_menu(call):
    inline_subject_keyboard = service.generate_inline_subjects(call.message.chat.id)
    inline_linked_subject_keyboard_to_ch = service.generate_inline_linked_subjects_to_change(call.message.chat.id)
    inline_linked_subject_keyboard_to_rm = service.generate_inline_linked_subjects_to_remove(call.message.chat.id)
    inline_subject_type_keyboard = telebot.types.InlineKeyboardMarkup()
    inline_subject_type_keyboard.add(inline_lec_button, inline_lab_button, inline_prac_button)
    inline_subject_type_keyboard.add(inline_second_back_button)
    inline_confirm_cancel_keyboard = telebot.types.InlineKeyboardMarkup()
    inline_confirm_cancel_keyboard.add(inline_remove_link_cancel_button, inline_remove_link_confirm_button)

    if call.data == 'add_link' or call.data == 'second_back_button':
        user_links_dict.update({call.message.chat.id: {
            'subject': '',
            'subject_type': '',
            'link': '',
            'password': ''}})
        bot.edit_message_text(f"Выбери предмет для которого нужно добавить ссылку",
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=inline_subject_keyboard,
                              parse_mode='HTML')

    elif call.data == 'change_link':
        user_links_dict.update({call.message.chat.id: {
            'subject': '',
            'subject_type': '',
            'link': '',
            'password': ''}})
        bot.edit_message_text(f"Выбери предмет для которого нужно изменить ссылку",
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=inline_linked_subject_keyboard_to_ch,
                              parse_mode='HTML')

    elif call.data == 'remove_link':
        user_links_dict.update({call.message.chat.id: {
            'subject': '',
            'subject_type': '',
            'link': '',
            'password': ''}})
        bot.edit_message_text(f"Выбери предмет для которого нужно удалить ссылку",
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=inline_linked_subject_keyboard_to_rm,
                              parse_mode='HTML')

    elif call.data == 'first_back_button':
        bot.edit_message_text(f"Здесь ты можешь добавлять ссылки к предметам, изменять и даже их удалять, "
                              f"если они есть.",
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=service.dynamic_menu_links_inline_keyboard_generator(call.message.chat.id),
                              parse_mode='HTML')

    # jump to ADD_LINK state
    elif call.data in [button['callback_data'] for buttons in inline_subject_keyboard.to_dict()['inline_keyboard']
                       for button in buttons]:
        for buttons in inline_subject_keyboard.to_dict()['inline_keyboard'][
                       :len(inline_subject_keyboard.to_dict()['inline_keyboard']) - 1]:  # тут -1 чтобы не ловилась бэк-кнопка
            for button in buttons:
                if button['callback_data'] == call.data:
                    user_links_dict[call.message.chat.id]['subject'] = button['text']
                    bot.edit_message_text(f"Предмет: <b>{user_links_dict[call.message.chat.id]['subject']}</b>\n\n"
                                          f"Выбери тип занятия 🙃",
                                          chat_id=call.message.chat.id,
                                          message_id=call.message.message_id,
                                          reply_markup=inline_subject_type_keyboard,
                                          parse_mode='HTML')

    elif call.data in [button['callback_data'] for buttons in inline_subject_type_keyboard.to_dict()['inline_keyboard']
                       for button in buttons]:
        for button in inline_subject_type_keyboard.to_dict()['inline_keyboard'][0]:  # тут [0] чтобы не ловилась бэк-кнопка
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
                db.set_state(call.message.from_user.username,
                             stateworker.States.S_INPUT_LINK.value,
                             time.strftime('%d/%m/%y, %X'),
                             call.message.chat.id)

    # jump to CHANGE_LINK state
    elif call.data in [button['callback_data'] for buttons in
                       inline_linked_subject_keyboard_to_ch.to_dict()['inline_keyboard'] for button in buttons]:
        for buttons in inline_linked_subject_keyboard_to_ch.to_dict()['inline_keyboard'][
                       :len(inline_linked_subject_keyboard_to_ch.to_dict()['inline_keyboard']) - 1]:  # тут -1 чтобы не ловилась бэк-кнопка
            for button in buttons:
                if button['callback_data'] == call.data:
                    user_links_dict.update({call.message.chat.id: {
                        'subject': button['text'][int(button['text'].find('-')) + 2:],  # текст кнопки после '- '
                        'subject_type': button['text'][:int(button['text'].find(' '))],  # текст кнопки до ' '
                        'link': '',
                        'password': ''}})
                    user_links_dict[call.message.chat.id]['link'] = \
                        db.get_links_to_change(call.message.chat.id,
                                               user_links_dict[call.message.chat.id]['subject'],
                                               user_links_dict[call.message.chat.id]['subject_type'])[3]  # 3 - ссылка
                    user_links_dict[call.message.chat.id]['password'] = \
                        db.get_links_to_change(call.message.chat.id,
                                               user_links_dict[call.message.chat.id]['subject'],
                                               user_links_dict[call.message.chat.id]['subject_type'])[4]  # 4 - пароль
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
                                         parse_mode='HTML')

                    elif user_links_dict[call.message.chat.id]['password'] != '':
                        bot.send_message(call.message.chat.id,
                                         f"Предмет: <b>{user_links_dict[call.message.chat.id]['subject']}</b>\n"
                                         f"Тип занятия: <b>{user_links_dict[call.message.chat.id]['subject_type']}</b>\n"
                                         f"Ссылка: <b>{user_links_dict[call.message.chat.id]['link']}</b>\n"
                                         f"Пароль: <b>{user_links_dict[call.message.chat.id]['password']}</b>\n",
                                         reply_markup=keyboard_generator.generate_default_keyboard_row(
                                             (change_password_button, confirm_button),
                                             (cancel_button,)),
                                         parse_mode='HTML')

                    db.set_state(call.message.from_user.username,
                                 stateworker.States.S_CHANGE_LINK.value,
                                 time.strftime('%d/%m/%y, %X'),
                                 call.message.chat.id)

    # remove link
    elif call.data in [button['callback_data'] for buttons in
                       inline_linked_subject_keyboard_to_rm.to_dict()['inline_keyboard'] for button in buttons]:
        for buttons in inline_linked_subject_keyboard_to_rm.to_dict()['inline_keyboard'][
                       :len(inline_linked_subject_keyboard_to_rm.to_dict()['inline_keyboard']) - 1]:  # тут -1 чтобы не ловилась бэк-кнопка
            for button in buttons:
                if button['callback_data'] == call.data:
                    user_links_dict.update({call.message.chat.id: {
                        'subject': button['text'][int(button['text'].find('-')) + 2:],  # текст кнопки после '- '
                        'subject_type': button['text'][:int(button['text'].find(' '))],  # текст кнопки до ' '
                        'link': '',
                        'password': ''}})
                    user_links_dict[call.message.chat.id]['link'] = \
                        db.get_links_to_change(call.message.chat.id,
                                               user_links_dict[call.message.chat.id]['subject'],
                                               user_links_dict[call.message.chat.id]['subject_type'])[3]  # 3 - ссылка
                    user_links_dict[call.message.chat.id]['password'] = \
                        db.get_links_to_change(call.message.chat.id,
                                               user_links_dict[call.message.chat.id]['subject'],
                                               user_links_dict[call.message.chat.id]['subject_type'])[4]  # 4 - пароль

                    if user_links_dict[call.message.chat.id]['password'] == '':
                        bot.edit_message_text(f"Ты удаляешь:\n"
                                              f"Предмет: <b>{user_links_dict[call.message.chat.id]['subject']}</b>\n"
                                              f"Тип занятия: <b>{user_links_dict[call.message.chat.id]['subject_type']}</b>\n"
                                              f"Ссылка: <b>{user_links_dict[call.message.chat.id]['link']}</b>\n",
                                              chat_id=call.message.chat.id,
                                              message_id=call.message.message_id,
                                              reply_markup=inline_confirm_cancel_keyboard,
                                              parse_mode='HTML')

                    elif user_links_dict[call.message.chat.id]['password'] != '':
                        bot.edit_message_text(f"Ты удаляешь:\n"
                                              f"Предмет: <b>{user_links_dict[call.message.chat.id]['subject']}</b>\n"
                                              f"Тип занятия: <b>{user_links_dict[call.message.chat.id]['subject_type']}</b>\n"
                                              f"Ссылка: <b>{user_links_dict[call.message.chat.id]['link']}</b>\n"
                                              f"Пароль: <b>{user_links_dict[call.message.chat.id]['password']}</b>",
                                              chat_id=call.message.chat.id,
                                              message_id=call.message.message_id,
                                              reply_markup=inline_confirm_cancel_keyboard,
                                              parse_mode='HTML')

    elif call.data == 'confirm_remove_link':
        bot.delete_message(chat_id=call.message.chat.id,
                           message_id=call.message.message_id)
        db.remove_link(call.message.chat.id, user_links_dict[call.message.chat.id]['subject'],
                       user_links_dict[call.message.chat.id]['subject_type'])
        bot.send_message(call.message.chat.id,
                         f"Ссылка <i>'{user_links_dict[call.message.chat.id]['link']}'</i> на предмет "
                         f"'<b>{user_links_dict[call.message.chat.id]['subject_type']}</b> - "
                         f"<b>{user_links_dict[call.message.chat.id]['subject']}</b>' "
                         f"успешно удалена.",
                         reply_markup=keyboard_generator.main_menu_keyboard,
                         parse_mode='HTML')

    elif call.data == 'cancel_remove_link':
        bot.edit_message_text("Выбери предмет для удаления ссылки",
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=inline_linked_subject_keyboard_to_rm,
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
                         parse_mode='HTML')
        db.add_link(message.chat.id,
                    user_links_dict[message.chat.id]['subject'],
                    user_links_dict[message.chat.id]['subject_type'],
                    user_links_dict[message.chat.id]['link'],
                    user_links_dict[message.chat.id]['password'])
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
                             parse_mode='HTML')

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
                             parse_mode='HTML')

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
                             parse_mode='HTML')

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
                             parse_mode='HTML')


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
                         reply_markup=keyboard_generator.main_menu_keyboard)
        db.set_state(message.from_user.username,
                     stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)
        db.add_link(message.chat.id,
                    user_links_dict[message.chat.id]['subject'],
                    user_links_dict[message.chat.id]['subject_type'],
                    user_links_dict[message.chat.id]['link'],
                    user_links_dict[message.chat.id]['password'])

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
                             parse_mode='HTML')

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
                             parse_mode='HTML')

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
                         parse_mode='HTML')


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
                         parse_mode='HTML')
        db.change_link(user_links_dict[message.chat.id]['link'],
                       user_links_dict[message.chat.id]['password'],
                       message.chat.id,
                       user_links_dict[message.chat.id]['subject'],
                       user_links_dict[message.chat.id]['subject_type'])
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
                             parse_mode='HTML')

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
                             parse_mode='HTML')
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
                             parse_mode='HTML')


@bot.message_handler(func=lambda message: db.get_state(message.chat.id).__class__ == tuple and
                                          db.get_state(message.chat.id)[0] == stateworker.States.S_CHANGE_PASSWORD.value)
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
                         parse_mode='HTML')
        db.change_link(user_links_dict[message.chat.id]['link'],
                       user_links_dict[message.chat.id]['password'],
                       message.chat.id,
                       user_links_dict[message.chat.id]['subject'],
                       user_links_dict[message.chat.id]['subject_type'])
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
                             parse_mode='HTML')

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
                             parse_mode='HTML')
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
                             parse_mode='HTML')

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
                             parse_mode='HTML')


"""#####################################################################################################################
                                                    SCHEDULE MENU
#####################################################################################################################"""


@bot.message_handler(
    func=lambda message: db.get_state(message.chat.id).__class__ == tuple and db.get_state(message.chat.id)[
        0] == stateworker.States.S_SCHEDULE_MENU.value)
def schedule_menu(message):
    if message.text == back_button:
        bot.send_message(message.chat.id, 'Возвращаемся...', reply_markup=keyboard_generator.main_menu_keyboard)
        db.set_state(message.from_user.username, stateworker.States.S_MAIN_MENU.value, time.strftime('%d/%m/%y, %X'),
                     message.chat.id)

    elif message.text == today_day_button:
        s = show_day(message.chat.id, "Сегодня", date.today().weekday() + 1)
        bot.send_message(message.chat.id, s, parse_mode="HTML", reply_markup=keyboard_generator.schedule_menu_keyboard)
        db.set_state(message.from_user.username, stateworker.States.S_SCHEDULE_MENU.value,
                     time.strftime('%d/%m/%y, %X'), message.chat.id)

    elif message.text == tomorrow_day_button:
        tomorrow = (date.today() + datetime.timedelta(days=1)).weekday() + 1
        s = show_day(message.chat.id, "Завтра", tomorrow)
        bot.send_message(message.chat.id, s, parse_mode="HTML", reply_markup=keyboard_generator.schedule_menu_keyboard)
        db.set_state(message.from_user.username, stateworker.States.S_SCHEDULE_MENU.value,
                     time.strftime('%d/%m/%y, %X'), message.chat.id)

    elif message.text == week1_button:
        bot.send_message(message.chat.id, 'А теперь день', reply_markup=keyboard_generator.week1_day_choose_keyboard)
        db.set_state(message.from_user.username, stateworker.States.S_SCHEDULE_WEEK_VIEW.value,
                     time.strftime('%d/%m/%y, %X'), message.chat.id)

    elif message.text == week2_button:
        bot.send_message(message.chat.id, 'А теперь день', reply_markup=keyboard_generator.week2_day_choose_keyboard)
        db.set_state(message.from_user.username, stateworker.States.S_SCHEDULE_WEEK_VIEW.value,
                     time.strftime('%d/%m/%y, %X'), message.chat.id)


@bot.message_handler(
    func=lambda message: db.get_state(message.chat.id).__class__ == tuple and db.get_state(message.chat.id)[
        0] == stateworker.States.S_SCHEDULE_WEEK_VIEW.value)
def week_view(message):
    for i in range(0, 5):
        if message.text == week1_day_buttons[i]:
            bot.send_message(message.chat.id, Schedule.show_schedule(message.chat.id, 1, i + 1, week_days[i + 1]),
                             parse_mode="HTML", reply_markup=keyboard_generator.week1_day_choose_keyboard)
            db.set_state(message.from_user.username, stateworker.States.S_SCHEDULE_WEEK_VIEW.value,
                         time.strftime('%d/%m/%y, %X'), message.chat.id)

        elif message.text == week2_day_buttons[i]:
            bot.send_message(message.chat.id, Schedule.show_schedule(message.chat.id, 2, i + 1, week_days[i + 1]),
                             parse_mode="HTML", reply_markup=keyboard_generator.week2_day_choose_keyboard)
            db.set_state(message.from_user.username, stateworker.States.S_SCHEDULE_WEEK_VIEW.value,
                         time.strftime('%d/%m/%y, %X'), message.chat.id)

    if message.text == back_button:
        bot.send_message(message.chat.id, 'Возвращаемся...', reply_markup=keyboard_generator.schedule_menu_keyboard)
        db.set_state(message.from_user.username, stateworker.States.S_SCHEDULE_MENU.value,
                     time.strftime('%d/%m/%y, %X'), message.chat.id)


"""#####################################################################################################################
                                                    SETTINGS MENU
#####################################################################################################################"""


@bot.message_handler(
    func=lambda message: db.get_state(message.chat.id).__class__ == tuple and db.get_state(message.chat.id)[
        0] == stateworker.States.S_SETTINGS_MENU.value)
def settings_menu(message):
    if message.text == back_button:
        bot.send_message(message.chat.id, 'Главное меню', reply_markup=keyboard_generator.main_menu_keyboard)
        db.set_state(message.from_user.username, stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'), message.chat.id)

    if message.text == notifications_button:
        bot.reply_to(message, service.not_available_reply)
        db.set_state(message.from_user.username, stateworker.States.S_SETTINGS_MENU.value,
                     time.strftime('%d/%m/%y, %X'), message.chat.id)

    if message.text == change_group_button:
        bot.send_message(message.chat.id, 'Введи название группы',
                         reply_markup=keyboard_generator.generate_default_keyboard(cancel_button))
        db.set_state(message.from_user.username, stateworker.States.S_CHANGE_GROUP.value,
                     time.strftime('%d/%m/%y, %X'), message.chat.id)

    if message.text == cancel_button:
        bot.send_message(message.chat.id, 'Настройки', reply_markup=keyboard_generator.settings_menu_keyboard)
        db.set_state(message.from_user.username, stateworker.States.S_SETTINGS_MENU.value,
                     time.strftime('%d/%m/%y, %X'), message.chat.id)


bot.polling()
