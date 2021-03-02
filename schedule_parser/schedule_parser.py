import requests
from bs4 import BeautifulSoup

import database.db as db

free = '''
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


def get_links(user_id):
    links = db.get_links_info(user_id)
    links_text = ''
    if len(links) == 0:
        links_text = 'Вы еще не добавили ни одной ссылки.\nДля занесения ссылки перейдите в настройки ⚙'
    else:
        for l in links:
            hl = '1️⃣️  <a href="{link}">{text}</a>\n'
            links_text += hl.format(link=l[0], text=l[1])

    return links_text


def get_current_week():
    week_url = 'http://api.rozklad.org.ua/v2/weeks'
    week = requests.get(week_url).json()['data']
    return week


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


def show_exams(sch: str):
    return '''Запланированные мувы на экзамены: 	
———————————————	
{schedule}	
———————————————	
'''.format(schedule=sch)


class Schedule:
    url_for_students_pattern = 'http://api.rozklad.org.ua/v2/groups/{0}/lessons'

    @staticmethod
    def is_group_exist(group: str):
        url = Schedule.url_for_students_pattern
        return requests.get(url.format(group)).ok

    @staticmethod
    def show_schedule(user_id, week, day, weekday):
        user = db.get_user_info(user_id)[2]
        url = Schedule.url_for_students_pattern
        r = requests.get(url.format(user))
        data = r.json()['data']

        schedule_title = 'Запланированные мувы на ' + weekday + ':'
        schedule_body = ''

        subject_links = db.get_user_info(user_id)[2]
        for lesson in data:
            if lesson['lesson_week'] == str(week) and lesson['day_number'] == str(day):
                lesson_start = lesson["time_start"][:5]
                lesson_name = lesson["lesson_name"]
                lesson_type = lesson["lesson_type"]
                schedule_body += '\n' + str(lesson_numbers.get(lesson_start)) + ' ' + lesson_start + ' — <i>' + \
                                 lesson_name + '</i> <b>\n' + \
                                 lesson_type + "</b> — " + \
                                 lesson["teacher_name"] + '\n'

                for s in subject_links:
                    if s[0] == lesson_name and s[1] == lesson_type:
                        subject_link = '\t<u>Ссылка на конференцию:</u> {0}\n'.format(s[2])
                        if s[3] is not None:
                            subject_link += "\tКод доступа: <code>{0}</code>\n".format(s[3])

                        if s[4] is not None:
                            subject_link += '\tℹ️{0}\n'.format(s[4])

                        schedule_body += subject_link

        if schedule_body == '':
            schedule_body = free

        hl = 'db.get_hotlines_info(user_id)'

        return '''
{title}
———————————————
{schedule}
———————————————
👺 Hotlines: 
{hotlines}
———————————————
            '''.format(title=schedule_title, schedule=schedule_body, hotlines=hl)

    @staticmethod
    def get_list_of_subjects(user_id, week, day):
        subjects = []
        user = db.get_user_info(user_id)[2]
        url = Schedule.url_for_students_pattern
        r = requests.get(url.format(user[0]))
        data = r.json()['data']

        for lesson in data:
            if lesson['lesson_week'] == str(week) and lesson['day_number'] == str(day):
                subject = Subject(lesson["lesson_name"], lesson["lesson_type"], lesson["teacher_name"])
                subjects.append(subject)

        return subjects

    @staticmethod
    def get_lessons(user_id):
        reply = []
        user = db.get_user_info(user_id)[2]
        url = Schedule.url_for_students_pattern
        r = requests.get(url.format(user))
        data = r.json()['data']

        for lesson in data:
            reply.append(lesson["lesson_full_name"])

        return set(reply)

    @staticmethod
    def get_session_for_schedule(user_id):
        user = db.get_user_info(user_id)[2]
        url = 'http://api.rozklad.org.ua/v2/groups/{0}'
        r = requests.get(url.format(user[0]))
        data = r.json()['data']

        group_token = data["group_url"][data["group_url"].index("g="):]
        full_url = 'http://rozklad.kpi.ua/Schedules/ViewSessionSchedule.aspx?' + group_token

        req = requests.get(full_url)

        soup = BeautifulSoup(req.content, 'html.parser')

        trs = []
        rows = soup.find_all('tr')
        schedule = ''
        for row in rows:
            trs.append(row.find_all('td'))

        i = 0
        for td in trs:
            if td[1].getText():
                schedule += '\n⚠️<b>' + td[0].getText() + '</b>\n' + subject_enumeration[i] + ' '
                for link in td[1].find_all('a', href=True):
                    schedule += '\n' + link.getText()
                schedule += ' : ' + td[1].getText()[-5:] + '\n'
                i += 1

        return show_exams(schedule)
