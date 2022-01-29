# -*- coding: utf-8 -*-
# !/usr/bin/python3.8.5
import datetime

from src.database import db

#  registration
start_reply = "Привет, {0}! 🥴🤙\nZ-Moves на связи 😎\n\n"\
              "Для работы со мной напиши мне название своей группы.\n\nПример: <b>IO-83</b>"
repeated_start_reply = "Прекрати меня тестировать на прочность. Введи группу, пожалуйста 😰"
registered_user_start_reply = "Главное меню"

successful_registration = "Есть такая! Ну а теперь приступим 🙂"
unsuccessful_registration = "<b>{0}</b>? Что-то я о такой группе ещё не слышал 🤥"

# schedule
schedule_reply = "Выбери опцию отображения расписания."

# settings
settings_reply = "Что нужно настроить?"

# links
add_link_reply = "Выбери предмет для которого нужно добавить ссылку."
change_link_reply = "Выбери предмет для которого нужно изменить ссылку."
remove_link_reply = "Выбери предмет для которого нужно удалить ссылку."

# hotlines

add_hotline_reply = "Выбери предмет для которого нужно добавить хотлайн."
change_hotline_reply = "Выбери предмет для которого нужно изменить хотлайн."
remove_hotline_reply = "Выбери хотлайн, который нужно удалить."
confirm_remove_hotline_reply = "Хотлайн для «<b>{0}</b>» успешно удалён."

# info
info_button_reply = "Ты залогинен под группой: <b>{0}</b>\n\n" \
                    "Обо мне:\n\n" \
                    "Я — <b>Z-Moves</b>, единственный наследник ЗМ, истинный владыка семи королевств и ... \n" \
                    "Впрочем, это уже совсем другая история.\n\n" \
                    "Я обычный бот, показывающий расписание — скажут хейтеры. Но как бы не так. " \
                    "Со мной ты можешь:\n\n" \
                    "1. Прикреплять ссылки 🔗 к парам, которые порой так сложно и долго искать.\n" \
                    "2. 👺 Хотлайны. Ты всегда сможешь в сию минуту узнать до какого числа нужно сдать вторую " \
                    "лабу по Взлому Жопы 🧑‍💻\n" \
                    "3. Такого интерфейса ты ещё не видел 😎\n" \
                    "4. И это только начало 🤯 Я постепенно развиваюсь и добавляю в себя новые фичи, которые " \
                    "будут радовать тебя всё больше и больше 🤓\n" \
                    "5. Хватит читать! Давай бегом ссылки добавлять 🥴\n\n" \
                    "Да, и чуть не забыл. <a href='https://send.monobank.ua/jar/tkVzvjpUx'>Тут</a> можно " \
                    "сказать мне спасибо.\n👉👈"

# other
not_available_reply = "⛔️В разработке"
api_bad_request_reply = [f"Йоооой.. Что-то пошло не по плану..\n"
                         f"Скорее всего API расписания КПИ наився и спыть 🤧\n" 
                         f"Как только я возобновлю работу, я сразу же уведомлю об этом в"
                         f" <a href='https://t.me/joinchat/bH7h9e6sU81kOTIy'>канале</a>.",
                         'CAACAgIAAxkBAAECFEVgVPzX5INky9p8a_NNA7_hHrZz7QACuwADHEwXNcY4Yk6-qNtrHgQ',
                         'CAACAgIAAxkBAAECFEdgVP0KG63r3tLNf6t9855ccirbcQAC8AAD5UTmIZ8pFoXkR2GTHgQ',
                         'CAACAgIAAxkBAAECFElgVP04fFiugu2fzCqmEBbPgIRKVwACQQAD1gWXKodgfwAB1E-WWh4E',
                         'CAACAgIAAxkBAAECFEtgVP1U5MDF64ZvOCxGkTycv6e93AACUAEAAnSgYT2e8-ipXqrBrh4E',
                         'CAACAgIAAxkBAAECFE1gVP1xGkXEPx5ON1DKMsA1w7PaawACXgEAAntOKhAfEWp8wj0caB4E',
                         'CAACAgIAAxkBAAECFE9gVP2ESOZaINJWfiLwOlOQTNvCBwACtQADs71TMwrV7bObpagqHgQ',
                         'CAACAgIAAxkBAAECFFFgVP2b_O_8tnkXE8tTRH25RKWOugACbwADN4B1OhQiMuVo8Z7NHgQ',
                         'CAACAgIAAxkBAAECFFNgVP2y5YLgQpRRKeX8whsLuEBfmQACkAADN4B1OvLIGEuMGYBoHgQ',
                         'CAACAgIAAxkBAAECFFVgVP3GDec5fAR73MgO0wXNd46ZmQACsgADN4B1Ora8l5Zu5Xk5HgQ',
                         'CAACAgIAAxkBAAECFFdgVP6M7OA6df1Vnly4lsxgfrfvFQAC4AADN4B1OhBADqL0VdLXHgQ',
                         'CAACAgIAAxkBAAECFF5gVP72cnUwUH6ghmImLUGMxkAg9QACjAADSTTlDOXGuFY8iE4zHgQ',
                         'CAACAgIAAxkBAAECFGBgVP8m0E0W3xMbQt3k66ryWR0LTgAC9AQAAhMqCAABn3AJ4huFrlMeBA',
                         'CAACAgIAAxkBAAECFGJgVP88_wSeXpr5TYWmK_v8jb9-6gACHQUAAhMqCAABuqUT6TLPXzgeBA',
                         'CAACAgIAAxkBAAECFGRgVP9J7_8PiHEdwjgUVToMAvxV2wACNgUAAhMqCAABgZhouCSKGT0eBA',
                         'CAACAgIAAxkBAAECFGZgVP9WVvLwnh2sy5RFwqweXRM77gACQwUAAhMqCAABb-q2VMeOINgeBA',
                         'CAACAgIAAxkBAAECFGhgVP9iKXI_KRbpIC8s6yGb0Qfl4gACQgUAAhMqCAABF3d-66yBB2seBA',
                         'CAACAgIAAxkBAAECFHBgVQABcjz2CWOLMbXGgG1MVII8c1EAAi8FAAITKggAAVVdgYyWDCZqHgQ',
                         'CAACAgIAAxkBAAECFH1gVQABwOLGqGvyFaIPrmmLK-5STFoAAhYFAAITKggAASNYFCt32Yz_HgQ']

blocked_user_reply = ['Сорян, но ты в ЧС 😢',
                      'CAACAgIAAxkBAAEB9bhgQ6DCUQz5y_Mh7uwdvVxAWMiosgACEQAD1gWXKgGow7AQ9URiHgQ']

lorem_ipsum = "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et" \
              " dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut" \
              " aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse" \
              " cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa" \
              " qui officia deserunt mollit anim id est laborum."


def hotlines_reply(user_id):
    hotlines_body = ''
    user_group = db.get_user_info(user_id)[2]
    hotlines = db.get_hotlines(user_id)
    print(hotlines)
    if hotlines is not None:
        hotlines_body += f"👺 Хотлайны:\n\n"
        for i in hotlines:
            hotlines_body += f"<i>{i[1]}</i> - {i[2]} - <b>{i[3].strftime('%d.%m')}</b> "
            if (i[3] - datetime.datetime.now().date()).days == 0:
                hotlines_body += '‼'
            elif (i[3] - datetime.datetime.now().date()).days < 0:
                hotlines_body += '❌'
            elif 0 < (i[3] - datetime.datetime.now().date()).days <= 3:
                hotlines_body += '❗'
            hotlines_body += '\n'
    else:
        hotlines_body += 'На текущий момент у тебя нету хотлайнов.'
    return hotlines_body


def links_reply(user_id):
    links_body = ''
    user_group = db.get_user_info(user_id)[2]
    links = db.get_links(user_id)
    if links is not None:
        links_body += f"🔗 Твои ссылки: \n\n"
        for i in links:
            if i[4] == '':
                links_body += f"Предмет: <i>{i[1]}</i> - <b>{i[2]}</b>\n" \
                              f"Ссылка: {i[3]}\n"
            else:
                links_body += f"Предмет: <i>{i[1]}</i> - <b>{i[2]}</b>\n" \
                              f"Ссылка: {i[3]}\n" \
                              f"Код доступа: {i[4]}\n"
            links_body += '\n'
    else:
        links_body = 'На текущий момент у тебя нет ссылок.'
    return links_body
