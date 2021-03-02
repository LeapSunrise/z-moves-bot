import os

import psycopg2

__connection = None


def get_connection():
    global db
    db = psycopg2.connect(
        dbname=os.environ['DB_NAME'],
        user=os.environ['DB_USERNAME'],
        password=os.environ['DB_PASSWORD'],
        host=os.environ['DB_HOST'],
        port=os.environ['DB_PORT']
    )
    return db


def init_db(force: bool = True):
    conn = get_connection()
    c = conn.cursor()

    if force:
        c.execute('DROP TABLE IF EXISTS users CASCADE')
        c.execute('DROP TABLE IF EXISTS hotline')
        c.execute('DROP TABLE IF EXISTS links')
        c.execute('DROP TABLE IF EXISTS mails')
        c.execute('DROP TABLE IF EXISTS notifications')

    c.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id             int  primary key,
                    user_name           text,
                    group_name          text,
                    state               text,
                    registration_date   text,
                    last_activity       text 
                )
            ''')

    c.execute('''
            CREATE TABLE IF NOT EXISTS hotline (
                user_id     int,
                subject     text not null,
                task        text not null,
                deadline    text not null,
                link        text,

                foreign key(user_id) references users(user_id)
            )
        ''')

    c.execute('''
                CREATE TABLE IF NOT EXISTS links (
                    user_id      int,
                    subject      text not null,
                    subject_type text not null,
                    link         text not null,
                    password     text,
                    description  text,

                    foreign key(user_id) references users(user_id)
                )
            ''')

    c.execute('''
                CREATE TABLE IF NOT EXISTS mails (
                    user_id     int,
                    link        text not null,
                    description text not null,

                    foreign key(user_id) references users(user_id)
                )
        ''')

    c.execute('''
                    CREATE TABLE IF NOT EXISTS notifications (
                        user_id     int,
                        cron_date        text not null,

                        foreign key(user_id) references users(user_id)
                    )
            ''')

    conn.commit()


def set_state(user_id, user_name, state, last_activity):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        'UPDATE users SET user_name = %s, state = %s, last_activity = %s WHERE user_id = %s',
        (user_id, user_name, state, last_activity,)
    )
    conn.commit()


def get_state(uid: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        'SELECT state FROM users WHERE user_id = %s',
        (uid,)
    )
    return c.fetchone()


def register_user(user_id, user_name: str, state: str, registration_date: str, last_activity: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        'INSERT INTO users (user_id, user_name, state, last_activity, registration_date) VALUES (%s, %s, %s, %s, %s)',
        (user_id, user_name, state, last_activity, registration_date,)
    )
    conn.commit()


def register_user_group_name(user_id, user_name, group_name, state, last_activity):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        'UPDATE users SET user_name = %s, group_name = %s, state = %s, last_activity = %s WHERE user_id = %s',
        (user_id, user_name, group_name, state, last_activity,)
    )
    conn.commit()


def get_user_info(uid):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        'SELECT * FROM users WHERE user_id = %s', (uid,)
    )

    return c.fetchone()


def add_link(user_id: int, subject, subject_type, link, password='', description=''):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        'INSERT INTO links (user_id, subject, subject_type, link, password, description) '
        'VALUES (%s, %s, %s, %s, %s, %s)',
        (user_id, subject, subject_type, link, password, description,)
    )
    conn.commit()


def get_links(uid):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        'SELECT * FROM links WHERE user_id = %s', (uid,)
    )
    q = c.fetchall()
    if len(q) == 0:
        return None
    else:
        return q


def get_links_to_change(user_id, subject, subject_type):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        'SELECT * FROM links WHERE user_id = %s AND subject = %s AND subject_type = %s', (user_id, subject, subject_type,)
    )

    return c.fetchone()


def change_link(link, password, user_id, subject, subject_type):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        'UPDATE links SET link = %s, password = %s WHERE user_id = %s AND subject = %s AND subject_type = %s',
        (link, password, user_id, subject, subject_type,)
    )
    conn.commit()
