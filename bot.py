import datetime
import os
import time
import keyboard_generator
from buttons import *
from database import stateworker
from schedule_parser.schedule_parser import *

bot = telebot.TeleBot(os.environ['BOT_TOKEN'])
db.init_db()
not_available_reply = '⛔ В разработке'

"""#####################################################################################################################
                                                    START
#####################################################################################################################"""


@bot.message_handler(commands=['start', 'START'])
def start_message(message):
    user_last_name = ''
    if message.from_user.last_name:
        user_last_name = ' ' + message.from_user.last_name

    if db.get_user_info(message.chat.id) is None:
        bot.send_message(message.chat.id,
                         f"Привет, {message.from_user.first_name}{user_last_name}! 🥴🤙\nZ-Moves на связи 😎\n\n"
                         f"Для работы со мной напиши мне название своей группы.\n\nПример: <b><i>IO-83</i></b>",
                         parse_mode='HTML')
        db.register_user(message.chat.id, message.from_user.username, stateworker.States.S_REGISTRATION.value,
                         time.strftime('%d/%m/%y, %X'), time.strftime('%d/%m/%y, %X'))

    elif db.get_user_info(message.chat.id)[2] is None:
        bot.send_message(message.chat.id, 'Перестань тестировать меня. Введи группу плес', reply_markup=None)

    else:
        bot.send_message(message.chat.id, 'Главное меню', reply_markup=keyboard_generator.main_menu_keyboard)
        db.set_state(message.from_user.username, stateworker.States.S_MAIN_MENU.value, time.strftime('%d/%m/%y, %X'),
                     message.chat.id)


@bot.message_handler(func=lambda message: (db.get_state(message.chat.id).__class__ == tuple and
                                           db.get_state(message.chat.id)[
                                               0] == stateworker.States.S_REGISTRATION.value) or (
                                                  db.get_state(message.chat.id).__class__ == tuple and
                                                  db.get_state(message.chat.id)[
                                                      0] == stateworker.States.S_CHANGE_GROUP.value))
def group_registration(message):
    if Schedule.is_group_exist(message.text):
        bot.send_message(message.chat.id, 'Есть такая! Ну а теперь приступим 🙂',
                         reply_markup=keyboard_generator.main_menu_keyboard)
        db.register_user_group_name(message.from_user.username, message.text, stateworker.States.S_MAIN_MENU.value,
                                    time.strftime('%d/%m/%y, %X'), message.chat.id)

    elif message.text == cancel_button:
        bot.send_message(message.chat.id, 'Настройки', reply_markup=keyboard_generator.settings_menu_keyboard)
        db.set_state(message.from_user.username, stateworker.States.S_SETTINGS_MENU.value,
                     time.strftime('%d/%m/%y, %X'),
                     message.chat.id)

    else:
        bot.send_message(message.chat.id, '<b>{}</b>? Что-то я о такой группе ещё не слышал 🤥'
                                          'Попробуй ещё.'.format(message.text), parse_mode='HTML')
        db.set_state(message.from_user.username, stateworker.States.S_REGISTRATION.value, time.strftime('%d/%m/%y, %X'),
                     message.chat.id)


"""#####################################################################################################################
                                                    MAIN MENU
#####################################################################################################################"""


@bot.message_handler(
    func=lambda message: db.get_state(message.chat.id).__class__ == tuple and db.get_state(message.chat.id)[
        0] == stateworker.States.S_MAIN_MENU.value)
def main_menu(message):
    if message.text == schedule_button:
        bot.send_message(message.chat.id, 'Выбери опцию отображения расписания.',
                         reply_markup=keyboard_generator.schedule_menu_keyboard)
        db.set_state(message.from_user.username, stateworker.States.S_SCHEDULE_MENU.value,
                     time.strftime('%d/%m/%y, %X'), message.chat.id)

    elif message.text == settings_button:
        bot.send_message(message.chat.id, 'Что нужно настроить?',
                         reply_markup=keyboard_generator.settings_menu_keyboard)
        db.set_state(message.from_user.username, stateworker.States.S_SETTINGS_MENU.value,
                     time.strftime('%d/%m/%y, %X'), message.chat.id)

    elif message.text == links_button:
        bot.send_message(message.chat.id, 'Тыкай',
                         reply_markup=keyboard_generator.dynamic_inline_link_menu(message.chat.id))
        db.set_state(message.from_user.username, stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'), message.chat.id)

    elif message.text == hotlines_button:
        bot.reply_to(message, not_available_reply)
        db.set_state(message.from_user.username, stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'), message.chat.id)

    elif message.text == mails_button:
        bot.reply_to(message, not_available_reply)
        db.set_state(message.from_user.username, stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'), message.chat.id)

    elif message.text == info_button:
        bot.reply_to(message, not_available_reply)
        db.set_state(message.from_user.username, stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'), message.chat.id)

    elif message.text == help_button:
        bot.reply_to(message, not_available_reply)
        db.set_state(message.from_user.username, stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'), message.chat.id)


add_link_dict = {}


@bot.callback_query_handler(
    func=lambda call: db.get_state(call.message.chat.id).__class__ == tuple and db.get_state(call.message.chat.id)[
        0] == stateworker.States.S_MAIN_MENU.value)
def links_menu(call):
    subject_keyboard = keyboard_generator.generate_inline_subjects(call.message.chat.id)
    linked_subject_keyboard = keyboard_generator.generate_inline_linked_subjects(call.message.chat.id)
    linked_subject_keyboard_to_rm = keyboard_generator.generate_inline_linked_subjects_to_remove(call.message.chat.id)
    inline_subject_type_keyboard = telebot.types.InlineKeyboardMarkup()
    inline_subject_type_keyboard.add(inline_lec_button, inline_lab_button, inline_prac_button)
    inline_subject_type_keyboard.add(inline_second_back_button)

    if call.data == 'add_link':
        add_link_dict.update({call.message.chat.id: {'lesson': '', 'type': '', 'link': '', 'password': ''}})
        bot.edit_message_text(text='Выбери предмет',
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=subject_keyboard,
                              parse_mode='HTML')

    elif call.data == 'change_link':
        add_link_dict.update({call.message.chat.id: {'lesson': '', 'type': '', 'link': '', 'password': ''}})
        bot.edit_message_text(text='Выбери предмет',
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=linked_subject_keyboard,
                              parse_mode='HTML')

    elif call.data == 'remove_link':
        add_link_dict.update({call.message.chat.id: {'lesson': '', 'type': '', 'link': '', 'password': ''}})
        bot.edit_message_text(text='Выбери предмет',
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=linked_subject_keyboard_to_rm,
                              parse_mode='HTML')

    elif call.data == 'first_back_button':
        bot.edit_message_text(text='214',
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=keyboard_generator.dynamic_inline_link_menu(call.message.chat.id),
                              parse_mode='HTML')

    elif call.data == 'second_back_button':
        bot.edit_message_text(text='Выбери предмет',
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=subject_keyboard,
                              parse_mode='HTML')


    elif call.data in [button['callback_data'] for buttons in subject_keyboard.to_dict()['inline_keyboard'] for button
                       in buttons]:
        for buttons in subject_keyboard.to_dict()['inline_keyboard'][
                       :len(subject_keyboard.to_dict()['inline_keyboard']) - 1]:  # тут -1 чтобы не ловилась бэк-кнопка
            for button in buttons:
                if button['callback_data'] == call.data:
                    add_link_dict[call.message.chat.id]['lesson'] = button['text']
                    bot.edit_message_text(text=f"Предмет: <i>{add_link_dict[call.message.chat.id]['lesson']}</i>\n\n"
                                               f"Выбери тип занятия 🙃",
                                          chat_id=call.message.chat.id,
                                          message_id=call.message.message_id,
                                          reply_markup=inline_subject_type_keyboard,
                                          parse_mode='HTML')

    elif call.data in [button['callback_data'] for buttons in inline_subject_type_keyboard.to_dict()['inline_keyboard']
                       for button in buttons]:
        for button in inline_subject_type_keyboard.to_dict()['inline_keyboard'][0]:
            if button['callback_data'] == call.data:
                add_link_dict[call.message.chat.id]['type'] = button['text']
                bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                keyboard = telebot.types.ReplyKeyboardMarkup(True, True)
                keyboard.add(cancel_button)
                bot.send_message(call.message.chat.id,
                                 f"Предмет: <i>{add_link_dict[call.message.chat.id]['lesson']}</i>\n"
                                 f"Тип занятия: <i>{add_link_dict[call.message.chat.id]['type']}</i>"
                                 f"\n\nТеперь попрошу скинуть мне ссылочку 🤓",
                                 reply_markup=keyboard,
                                 parse_mode='HTML')
                db.set_state(call.message.from_user.username, stateworker.States.S_INPUT_LINK.value,
                             time.strftime('%d/%m/%y, %X'), call.message.chat.id)

    elif call.data in [button['callback_data'] for buttons in linked_subject_keyboard.to_dict()['inline_keyboard'] for
                       button in buttons]:
        for buttons in linked_subject_keyboard.to_dict()['inline_keyboard'][
                       :len(linked_subject_keyboard.to_dict()[
                                'inline_keyboard']) - 1]:  # тут -1 чтобы не ловилась бэк-кнопка
            for button in buttons:
                if button['callback_data'] == call.data:
                    add_link_dict.update({call.message.chat.id: {
                        'lesson': button['text'][int(button['text'].find('-')) + 2:],
                        'type': button['callback_data'][:int(button['callback_data'].find('_'))], 'link': '',
                        'password': ''}})
                    add_link_dict[call.message.chat.id]['link'] = \
                    db.get_links_to_change(call.message.chat.id, add_link_dict[call.message.chat.id]['lesson'],
                                           add_link_dict[call.message.chat.id]['type'])[3]
                    add_link_dict[call.message.chat.id]['password'] = \
                    db.get_links_to_change(call.message.chat.id, add_link_dict[call.message.chat.id]['lesson'],
                                           add_link_dict[call.message.chat.id]['type'])[4]
                    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                    if add_link_dict[call.message.chat.id]['password'] == '':
                        bot.send_message(call.message.chat.id,
                                         f"Предмет: <i>{add_link_dict[call.message.chat.id]['lesson']}</i>\n"
                                         f"Тип занятия: <i>{add_link_dict[call.message.chat.id]['type']}</i>\n"
                                         f"Ссылка: <i>{add_link_dict[call.message.chat.id]['link']}</i>\n",
                                         reply_markup=keyboard_generator.generate_default_keyboard_row(
                                             (add_password_button, confirm_button),
                                             (cancel_button,)),
                                         parse_mode='HTML')
                    else:
                        bot.send_message(call.message.chat.id,
                                         f"Предмет: <i>{add_link_dict[call.message.chat.id]['lesson']}</i>\n"
                                         f"Тип занятия: <i>{add_link_dict[call.message.chat.id]['type']}</i>\n"
                                         f"Ссылка: <i>{add_link_dict[call.message.chat.id]['link']}</i>\n"
                                         f"Пароль: <i>{add_link_dict[call.message.chat.id]['password']}</i>\n",
                                         reply_markup=keyboard_generator.generate_default_keyboard_row(
                                             (change_password_button, confirm_button),
                                             (cancel_button,)),
                                         parse_mode='HTML')
                    db.set_state(call.message.from_user.username, stateworker.States.S_CHANGE_LINK.value,
                                 time.strftime('%d/%m/%y, %X'), call.message.chat.id)


    elif call.data in [button['callback_data'] for buttons in linked_subject_keyboard_to_rm.to_dict()['inline_keyboard']
                       for button in buttons]:
        for buttons in linked_subject_keyboard_to_rm.to_dict()['inline_keyboard'][
                       :len(linked_subject_keyboard_to_rm.to_dict()[
                                'inline_keyboard']) - 1]:  # тут -1 чтобы не ловилась бэк-кнопка
            print(buttons)
            print(linked_subject_keyboard_to_rm.to_dict())
            for button in buttons:
                print(button)
                if button['callback_data'] == call.data:
                    add_link_dict.update({call.message.chat.id: {
                        'lesson': button['text'][int(button['text'].find('-')) + 2:],
                        'type': button['callback_data'][3:int(button['callback_data'].rfind('_'))], 'link': '',
                        'password': ''}})
                    add_link_dict[call.message.chat.id]['link'] = \
                        db.get_links_to_change(call.message.chat.id, add_link_dict[call.message.chat.id]['lesson'],
                                               add_link_dict[call.message.chat.id]['type'])[3]
                    add_link_dict[call.message.chat.id]['password'] = \
                        db.get_links_to_change(call.message.chat.id, add_link_dict[call.message.chat.id]['lesson'],
                                               add_link_dict[call.message.chat.id]['type'])[4]

                    print(add_link_dict)
                    if add_link_dict[call.message.chat.id]['password'] == '':
                        bot.edit_message_text(call.message.chat.id,
                                              f"Вы действительно хотите удалить это дерьмо?:\n"
                                              f"Предмет: <i>{add_link_dict[call.message.chat.id]['lesson']}</i>\n"
                                              f"Тип занятия: <i>{add_link_dict[call.message.chat.id]['type']}</i>\n"
                                              f"Ссылка: <i>{add_link_dict[call.message.chat.id]['link']}</i>\n",
                                              reply_markup=keyboard_generator.generate_inline_keyboard(
                                                  inline_remove_link_cancel_button))


"""#####################################################################################################################
                                                    ADD LINK
#####################################################################################################################"""


@bot.message_handler(
    func=lambda message: db.get_state(message.chat.id).__class__ == tuple and db.get_state(message.chat.id)[
        0] == stateworker.States.S_INPUT_LINK.value)
def input_link(message):
    if message.text == cancel_button:
        bot.send_message(message.chat.id, 'Главное меню', reply_markup=keyboard_generator.main_menu_keyboard)
        db.set_state(message.from_user.username, stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'), message.chat.id)

    elif message.text == confirm_button:

        bot.send_message(message.chat.id, 'ГЦ. Ті справівсі', reply_markup=keyboard_generator.main_menu_keyboard)
        db.set_state(message.from_user.username, stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'), message.chat.id)
        db.add_link(message.chat.id, add_link_dict[message.chat.id]['lesson'], add_link_dict[message.chat.id]['type'],
                    add_link_dict[message.chat.id]['link'], add_link_dict[message.chat.id]['password'])
        add_link_dict.pop(message.chat.id)


    elif message.text == add_password_button or message.text == change_password_button:
        if add_link_dict[message.chat.id]['password'] == '':
            bot.send_message(message.chat.id, f"Предмет: <i>{add_link_dict[message.chat.id]['lesson']}</i>\n"
                                              f"Тип занятия: <i>{add_link_dict[message.chat.id]['type']}</i>\n"
                                              f"Ссылка: <i>{add_link_dict[message.chat.id]['link']}</i>\n"
                                              f"Пароль: \n"
                                              f"Добавляй пассворд",
                             reply_markup=keyboard_generator.generate_default_keyboard_row(
                                 (change_link_button, confirm_button),
                                 (cancel_button,)),
                             parse_mode='HTML')

        elif add_link_dict[message.chat.id]['password'] != '':
            bot.send_message(message.chat.id, f"Предмет: {add_link_dict[message.chat.id]['lesson']}\n"
                                              f"Тип занятия: {add_link_dict[message.chat.id]['type']}\n"
                                              f"Ссылка: {add_link_dict[message.chat.id]['link']}\n"
                                              f"Пароль: {add_link_dict[message.chat.id]['password']}\n\n"
                                              f"Добавляй пассворд",
                             reply_markup=keyboard_generator.generate_default_keyboard_row(
                                 (change_link, confirm_button),
                                 (cancel_button,)),
                             parse_mode='HTML')

        db.set_state(message.from_user.username, stateworker.States.S_INPUT_PASSWORD.value,
                     time.strftime('%d/%m/%y, %X'), message.chat.id)

    elif message.text == message.text:
        if add_link_dict[message.chat.id]['password'] == '':
            add_link_dict[message.chat.id]['link'] = message.text
            bot.send_message(message.chat.id, f"Предмет: {add_link_dict[message.chat.id]['lesson']}\n"
                                              f"Тип занятия: {add_link_dict[message.chat.id]['type']}\n"
                                              f"Ссылка: {add_link_dict[message.chat.id]['link']}\n\n"
                                              f"Тык добавить пас или готово",
                             reply_markup=keyboard_generator.generate_default_keyboard_row(
                                 (add_password_button, confirm_button),
                                 (cancel_button,)))
        elif add_link_dict[message.chat.id]['password'] != '':
            add_link_dict[message.chat.id]['link'] = message.text
            bot.send_message(message.chat.id, f"Предмет: {add_link_dict[message.chat.id]['lesson']}\n"
                                              f"Тип занятия: {add_link_dict[message.chat.id]['type']}\n"
                                              f"Ссылка: {add_link_dict[message.chat.id]['link']}\n"
                                              f"Пароль: {add_link_dict[message.chat.id]['password']}\n\n"
                                              f"Добавляй пассворд",
                             reply_markup=keyboard_generator.generate_default_keyboard_row(
                                 (add_password_button, confirm_button),
                                 (cancel_button,)))


@bot.message_handler(
    func=lambda message: db.get_state(message.chat.id).__class__ == tuple and db.get_state(message.chat.id)[
        0] == stateworker.States.S_INPUT_PASSWORD.value)
def input_password(message):
    if message.text == cancel_button:
        bot.send_message(message.chat.id, 'Главное меню', reply_markup=keyboard_generator.main_menu_keyboard)
        db.set_state(message.from_user.username, stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'), message.chat.id)

    elif message.text == confirm_button:
        bot.send_message(message.chat.id, 'ГЦ. Ті справівсі', reply_markup=keyboard_generator.main_menu_keyboard)
        db.set_state(message.from_user.username, stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'), message.chat.id)
        db.add_link(message.chat.id, add_link_dict[message.chat.id]['lesson'], add_link_dict[message.chat.id]['type'],
                    add_link_dict[message.chat.id]['link'], add_link_dict[message.chat.id]['password'])
        add_link_dict.pop(message.chat.id)

    elif message.text == change_link_button:
        if add_link_dict[message.chat.id]['password'] == '':
            bot.send_message(message.chat.id, f"Предмет: {add_link_dict[message.chat.id]['lesson']}\n"
                                              f"Тип занятия: {add_link_dict[message.chat.id]['type']}\n"
                                              f"Ссылка: {add_link_dict[message.chat.id]['link']}\n\n"
                                              f"Тык добавить пас, готово или отмена",
                             reply_markup=keyboard_generator.generate_default_keyboard_row(
                                 (add_password_button, confirm_button),
                                 (cancel_button,)))

        elif add_link_dict[message.chat.id]['password'] != '':
            bot.send_message(message.chat.id, f"Предмет: {add_link_dict[message.chat.id]['lesson']}\n"
                                              f"Тип занятия: {add_link_dict[message.chat.id]['type']}\n"
                                              f"Ссылка: {add_link_dict[message.chat.id]['link']}\n"
                                              f"Пароль: {add_link_dict[message.chat.id]['password']}\n\n"
                                              f"ТЫК изменить пас, готово или отмена",
                             reply_markup=keyboard_generator.generate_default_keyboard_row(
                                 (change_password_button, confirm_button),
                                 (cancel_button,)))
        db.set_state(message.from_user.username, stateworker.States.S_INPUT_LINK.value,
                     time.strftime('%d/%m/%y, %X'), message.chat.id)

    elif message.text == message.text:
        add_link_dict[message.chat.id]['password'] = message.text
        bot.send_message(message.chat.id, f"Предмет: {add_link_dict[message.chat.id]['lesson']}\n"
                                          f"Тип занятия: {add_link_dict[message.chat.id]['type']}\n"
                                          f"Ссылка: {add_link_dict[message.chat.id]['link']}\n"
                                          f"Пароль: {add_link_dict[message.chat.id]['password']}\n\n"
                                          f"Тык изменить или готово")


"""#####################################################################################################################
                                                    CHANGE LINK
#####################################################################################################################"""


@bot.message_handler(
    func=lambda message: db.get_state(message.chat.id).__class__ == tuple and db.get_state(message.chat.id)[
        0] == stateworker.States.S_CHANGE_LINK.value)
def change_link(message):
    if message.text == cancel_button:
        bot.send_message(message.chat.id, 'Главное меню', reply_markup=keyboard_generator.main_menu_keyboard)
        db.set_state(message.from_user.username, stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'), message.chat.id)

    elif message.text == confirm_button:
        bot.send_message(message.chat.id, 'ГЦ. Ті справівсі', reply_markup=keyboard_generator.main_menu_keyboard)
        db.change_link(add_link_dict[message.chat.id]['link'], add_link_dict[message.chat.id]['password'],
                       message.chat.id, add_link_dict[message.chat.id]['lesson'],
                       add_link_dict[message.chat.id]['type'])
        db.set_state(message.from_user.username, stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'), message.chat.id)

    elif message.text == add_password_button or message.text == change_password_button:
        if add_link_dict[message.chat.id]['password'] == '':
            bot.send_message(message.chat.id, f"Предмет: <i>{add_link_dict[message.chat.id]['lesson']}</i>\n"
                                              f"Тип занятия: <i>{add_link_dict[message.chat.id]['type']}</i>\n"
                                              f"Ссылка: <i>{add_link_dict[message.chat.id]['link']}</i>\n"
                                              f"Пароль: \n\n"
                                              f"Добавляй пассворд",
                             reply_markup=keyboard_generator.generate_default_keyboard_row(
                                 (change_link_button, confirm_button),
                                 (cancel_button,)),
                             parse_mode='HTML')

        elif add_link_dict[message.chat.id]['password'] != '':
            bot.send_message(message.chat.id, f"Предмет: {add_link_dict[message.chat.id]['lesson']}\n"
                                              f"Тип занятия: {add_link_dict[message.chat.id]['type']}\n"
                                              f"Ссылка: {add_link_dict[message.chat.id]['link']}\n"
                                              f"Пароль: {add_link_dict[message.chat.id]['password']}\n\n"
                                              f"Добавляй пассворд",
                             reply_markup=keyboard_generator.generate_default_keyboard_row(
                                 (change_link_button, confirm_button),
                                 (cancel_button,)),
                             parse_mode='HTML')
        db.set_state(message.from_user.username, stateworker.States.S_CHANGE_PASSWORD.value,
                     time.strftime('%d/%m/%y, %X'), message.chat.id)

    elif message.text == message.text:
        if add_link_dict[message.chat.id]['password'] == '':
            add_link_dict[message.chat.id]['link'] = message.text
            bot.send_message(message.chat.id, f"Предмет: {add_link_dict[message.chat.id]['lesson']}\n"
                                              f"Тип занятия: {add_link_dict[message.chat.id]['type']}\n"
                                              f"Ссылка: {add_link_dict[message.chat.id]['link']}\n\n"
                                              f"Тык добавить пас или готово",
                             reply_markup=keyboard_generator.generate_default_keyboard_row(
                                 (add_password_button, confirm_button),
                                 (cancel_button,)))
        elif add_link_dict[message.chat.id]['password'] != '':
            add_link_dict[message.chat.id]['link'] = message.text
            bot.send_message(message.chat.id, f"Предмет: {add_link_dict[message.chat.id]['lesson']}\n"
                                              f"Тип занятия: {add_link_dict[message.chat.id]['type']}\n"
                                              f"Ссылка: {add_link_dict[message.chat.id]['link']}\n"
                                              f"Пароль: {add_link_dict[message.chat.id]['password']}\n\n"
                                              f"Добавляй пассворд",
                             reply_markup=keyboard_generator.generate_default_keyboard_row(
                                 (change_password_button, confirm_button),
                                 (cancel_button,)))


@bot.message_handler(
    func=lambda message: db.get_state(message.chat.id).__class__ == tuple and db.get_state(message.chat.id)[
        0] == stateworker.States.S_CHANGE_PASSWORD.value)
def change_password(message):
    if message.text == cancel_button:
        bot.send_message(message.chat.id, 'Главное меню', reply_markup=keyboard_generator.main_menu_keyboard)
        db.set_state(message.from_user.username, stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'), message.chat.id)

    elif message.text == confirm_button:
        bot.send_message(message.chat.id, 'ГЦ. Ті справівсі', reply_markup=keyboard_generator.main_menu_keyboard)
        db.change_link(add_link_dict[message.chat.id]['link'], add_link_dict[message.chat.id]['password'],
                       message.chat.id, add_link_dict[message.chat.id]['lesson'],
                       add_link_dict[message.chat.id]['type'])
        db.set_state(message.from_user.username, stateworker.States.S_MAIN_MENU.value,
                     time.strftime('%d/%m/%y, %X'), message.chat.id)

    elif message.text == change_link_button:
        if add_link_dict[message.chat.id]['password'] == '':
            bot.send_message(message.chat.id, f"Предмет: {add_link_dict[message.chat.id]['lesson']}\n"
                                              f"Тип занятия: {add_link_dict[message.chat.id]['type']}\n"
                                              f"Ссылка: {add_link_dict[message.chat.id]['link']}\n\n"
                                              f"Тык добавить пас, готово или отмена",
                             reply_markup=keyboard_generator.generate_default_keyboard_row(
                                 (add_password_button, confirm_button),
                                 (cancel_button,)))

        elif add_link_dict[message.chat.id]['password'] != '':
            bot.send_message(message.chat.id, f"Предмет: {add_link_dict[message.chat.id]['lesson']}\n"
                                              f"Тип занятия: {add_link_dict[message.chat.id]['type']}\n"
                                              f"Ссылка: {add_link_dict[message.chat.id]['link']}\n"
                                              f"Пароль: {add_link_dict[message.chat.id]['password']}\n\n"
                                              f"ТЫК изменить пас, готово или отмена",
                             reply_markup=keyboard_generator.generate_default_keyboard_row(
                                 (change_password_button, confirm_button),
                                 (cancel_button,)))
        db.set_state(message.from_user.username, stateworker.States.S_CHANGE_LINK.value,
                     time.strftime('%d/%m/%y, %X'), message.chat.id)

    elif message.text == message.text:
        if add_link_dict[message.chat.id]['password'] == '':
            add_link_dict[message.chat.id]['password'] = message.text
            bot.send_message(message.chat.id, f"Предмет: {add_link_dict[message.chat.id]['lesson']}\n"
                                              f"Тип занятия: {add_link_dict[message.chat.id]['type']}\n"
                                              f"Ссылка: {add_link_dict[message.chat.id]['link']}\n\n"
                                              f"Тык добавить пас или готово",
                             reply_markup=keyboard_generator.generate_default_keyboard_row(
                                 (change_link_button, confirm_button),
                                 (cancel_button,)))
        elif add_link_dict[message.chat.id]['password'] != '':
            add_link_dict[message.chat.id]['password'] = message.text
            bot.send_message(message.chat.id, f"Предмет: {add_link_dict[message.chat.id]['lesson']}\n"
                                              f"Тип занятия: {add_link_dict[message.chat.id]['type']}\n"
                                              f"Ссылка: {add_link_dict[message.chat.id]['link']}\n"
                                              f"Пароль: {add_link_dict[message.chat.id]['password']}\n\n"
                                              f"Добавляй пассворд",
                             reply_markup=keyboard_generator.generate_default_keyboard_row(
                                 (change_link_button, confirm_button),
                                 (cancel_button,)))


"""#####################################################################################################################
                                                    REMOVE LINK
#####################################################################################################################"""


@bot.callback_query_handler(
    func=lambda call: db.get_state(call.message.chat.id).__class__ == tuple and db.get_state(call.message.chat.id)[
        0] == stateworker.States.S_MAIN_MENU.value)
def remove_link(call):
    pass

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
        bot.reply_to(message, not_available_reply)
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
