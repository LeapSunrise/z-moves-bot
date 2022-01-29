# -*- coding: utf-8 -*-
#!/usr/bin/python3.8.5
import datetime

import requests

import src.database.db as db

free_day = '''
░░▄█████████████████▄
░▐████▀▒▒БОЛДАК▒▒▀████
░███▀▒▒▒РАЗРЕШИЛ▒▒▒▒▀██
░▐██▒▒▒▒▒АДИХНУТЬ▒▒▒▒▒██
░▐█▌▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒███
░░█▒▄▀▀▀▀▀▄▒▒▄▀▀▀▀▀▄▒▐██
░░░▐░░░▄▄░░▌▐░░░▄▄░░▌▐██
░▄▀▌░░░▀▀░░▌▐░░░▀▀░░▌▒▀▒
░▌▒▀▄░░░░▄▀▒▒▀▄░░░▄▀▒▒▄▀
░▀▄▐▒▀▀▀▀▒▒▒▒▒▒▀▀▀▒▒▒▒▒▒
░░░▀▌▒▄██▄▄▄▄████▄▒▒▒▒█▀
░░░░▄██████████████▒▒▐▌
░░░▀███▀▀████▀█████▀▒▌
░░░░░▌▒▒▒▄▒▒▒▄▒▒▒▒▒▒▐
░░░░░▌▒▒▒▒▀▀▀▒▒▒▒▒▒▒▐
'''

session_url = 'http://rozklad.kpi.ua/Schedules/ViewSessionSchedule.aspx?g='

week_days = {
    1: 'понедельник',
    2: 'вторник',
    3: 'среду',
    4: 'четверг',
    5: 'пятницу'
}

lesson_numbers = {
    '08:30': '1️⃣',
    '10:25': '2️⃣',
    '12:20': '3️⃣',
    '14:15': '4️⃣',
    '16:10': '5️⃣'
}

subject_enumeration = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']


def get_current_week():
    try:
        api_request = requests.get('http://api.rozklad.org.ua/v2/weeks', timeout=3).json()['data']
        if datetime.date.today().weekday() + 1 == 7:
            return api_request + 1

        else:
            return api_request

    except requests.exceptions.ConnectionError:
        return 'prosto privet. prosto kak dela...'


def show_day(user_id: int, wd: str, day: int):
    if day > 5:
        s = wd + ' пар нету. Отдыхаем'
    else:
        weekday = week_days[day]
        cur_week = get_current_week()
        s = Schedule.show_schedule(user_id, cur_week, day, weekday)

    return s


class Subject:
    lesson_title: str
    lesson_type: str
    teacher_name: str

    def __init__(self, lesson_title, lesson_type, teacher_name):
        self.lesson_title = lesson_title
        self.lesson_type = lesson_type
        self.teacher_name = teacher_name

    def __str__(self):
        return self.lesson_title + '[' + self.lesson_type + "] - " + self.teacher_name + '\n'


# def show_exams(sch: str):
#     return '''Запланированные мувы на экзамены:
# ———————————————
# {schedule}
# ———————————————
# '''.format(schedule=sch)


class Schedule:
    url_for_students_pattern = 'http://api.rozklad.org.ua/v2/groups/{0}/lessons'

    @staticmethod
    def is_group_exist(group: str):
        try:
            url = Schedule.url_for_students_pattern
            return requests.get(url.format(group), timeout=3).ok
        except requests.exceptions.ConnectionError:
            return 'lox'

    @staticmethod
    def show_schedule(user_id, week, day, weekday):
        try:
            user_group = db.get_user_info(user_id)[2]
            url = Schedule.url_for_students_pattern
            r = requests.get(url.format(user_group), timeout=3)
            data = r.json()['data']

            schedule_title = 'Запланированные мувы на ' + weekday + ':'
            schedule_body = ''
            hotlines_body = ''
            sep = '_' * 35

            subject_links = db.get_links(user_id)

            for lesson in data:
                if lesson['lesson_week'] == str(week) and lesson['day_number'] == str(day):
                    lesson_start = lesson["time_start"][:5]
                    lesson_name = lesson["lesson_name"]
                    lesson_type = lesson["lesson_type"]
                    schedule_body += f"\n{str(lesson_numbers.get(lesson_start))} {lesson_start} - <i>{lesson_name}</i>" \
                                     f"\n<b>{lesson_type}</b> - {lesson['teacher_name']}\n"

                    if subject_links is not None:
                        for s in subject_links:
                            if s[1] == lesson_name and s[2] == lesson_type:
                                subject_link = f"Ссылка на конференцию: {s[3]}\n"
                                if s[4] != '' and not None:
                                    subject_link += f"Код доступа: <code>{s[4]}</code>\n"

                                schedule_body += subject_link

            hotlines = db.get_hotlines(user_id, user_group)
            print(hotlines)
            if hotlines != 'lox1':
                hotlines_body += f"{sep}\n\n👺 Хотлайны:\n\n"
                for i in hotlines:
                    hotlines_body += f"<i>{i[1]}</i> - {i[2]} - <b>{i[3].strftime('%d.%m')}</b> "
                    if (i[3] - datetime.datetime.now().date()).days == 0:
                        hotlines_body += '‼'
                    elif (i[3] - datetime.datetime.now().date()).days < 0:
                        hotlines_body += '❌'
                    elif 0 < (i[3] - datetime.datetime.now().date()).days <= 3:
                        hotlines_body += '❗'
                    hotlines_body += '\n'

            if schedule_body == '':
                schedule_body = free_day

            return f"{schedule_title}\n{sep}\n{schedule_body}{hotlines_body}{sep}"

        except requests.exceptions.ConnectionError:
            return 'lox2'

    @staticmethod
    def get_list_of_subjects(user_id, week, day):
        try:
            subjects = []
            user = db.get_user_info(user_id)[2]
            url = Schedule.url_for_students_pattern
            r = requests.get(url.format(user[0]), timeout=3)
            data = r.json()['data']

            for lesson in data:
                if lesson['lesson_week'] == str(week) and lesson['day_number'] == str(day):
                    subject = Subject(lesson["lesson_name"], lesson["lesson_type"], lesson["teacher_name"])
                    subjects.append(subject)

            return subjects
        except requests.exceptions.ConnectionError:
            return 'lox3'

    @staticmethod
    def get_lessons(user_id):
        try:
            reply = []
            user = db.get_user_info(user_id)[2]  # uid, uname, gname, state, factivity, lactivity
            url = Schedule.url_for_students_pattern
            r = requests.get(url.format(user), timeout=3)
            data = r.json()['data']

            for lesson in data:
                reply.append(lesson["lesson_name"])

            return set(reply)
        except requests.exceptions.ConnectionError:
            return '.'

    # @staticmethod
    # def get_session_for_schedule(user_id):
    #     try:
    #         user = db.get_user_info(user_id)[2]
    #         url = 'http://api.rozklad.org.ua/v2/groups/{0}'
    #         r = requests.get(url.format(user[0]), timeout=3)
    #         data = r.json()['data']
    #
    #         group_token = data["group_url"][data["group_url"].index("g="):]
    #         full_url = 'http://rozklad.kpi.ua/Schedules/ViewSessionSchedule.aspx?' + group_token
    #
    #         req = requests.get(full_url, timeout=3)
    #
    #         soup = BeautifulSoup(req.content, 'html.parser')
    #
    #         trs = []
    #         rows = soup.find_all('tr')
    #         schedule = ''
    #         for row in rows:
    #             trs.append(row.find_all('td'))
    #
    #         i = 0
    #         for td in trs:
    #             if td[1].getText():
    #                 schedule += '\n⚠️<b>' + td[0].getText() + '</b>\n' + subject_enumeration[i] + ' '
    #                 for link in td[1].find_all('a', href=True):
    #                     schedule += '\n' + link.getText()
    #                 schedule += ' : ' + td[1].getText()[-5:] + '\n'
    #                 i += 1
    #
    #         return show_exams(schedule)
    #     except requests.exceptions.ConnectionError:
    #         return 'lox6'
