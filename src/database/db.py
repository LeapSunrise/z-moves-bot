# -*- coding: utf-8 -*-
#!/usr/bin/python3.8.5
from datetime import datetime, timedelta
import src.config.config as config

import psycopg2


__connection = None


def get_connection():
    db = psycopg2.connect(
        dbname=config.DB_NAME,
        user=config.DB_USERNAME,
        password=config.DB_PASSWORD,
        host=config.DB_HOST,
        port=config.DB_PORT
    )
    return db


def init_db():
    conn = get_connection()
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


def add_link(user_id, subject, subject_type, link, password, addition_time):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        'INSERT INTO links (user_id, subject, subject_type, link, password, addition_date) '
        'VALUES (%s, %s, %s, %s, %s, %s)',
        (user_id, subject, subject_type, link, password, addition_time,)
    )
    conn.commit()


def add_hotline(user_id, subject, description, date, addition_date):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        'INSERT INTO hotlines (user_id, subject, description, date, addition_date)'
        'VALUES (%s, %s, %s, %s, %s)',
        (user_id, subject, description, date, addition_date)
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


def get_hotlines(uid):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        'SELECT * FROM hotlines WHERE user_id = %s ORDER BY ("right"(date, 2), "left"(date, 2))', (uid,)
    )
    q = c.fetchall()
    hotline_text = ''
    if len(q) == 0:
        return None
    else:
        print(q)
        return q


def get_hotlines_to_change(user_id, subject, addition_date):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        'SELECT description, date FROM hotlines WHERE user_id = %s AND subject = %s AND addition_date = %s',
        (user_id, subject, addition_date)
    )
    return c.fetchone()


def get_links_to_change(user_id, subject, subject_type, addition_date):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        'SELECT * FROM links WHERE user_id = %s AND subject = %s AND subject_type = %s AND addition_date = %s',
        (user_id, subject, subject_type, addition_date,)
    )

    return c.fetchone()


def change_link(link, password, user_id, subject, subject_type, addition_date):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        'UPDATE links SET link = %s, password = %s WHERE user_id = %s AND subject = %s AND subject_type = %s AND addition_date = %s',
        (link, password, user_id, subject, subject_type, addition_date,)
    )
    conn.commit()


def change_hotline(date, description, user_id, subject, addition_date):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        'UPDATE hotlines SET date = %s, description = %s WHERE user_id = %s AND subject = %s AND addition_date = %s',
        (date, description, user_id, subject, addition_date,)
    )
    conn.commit()


def remove_link(user_id, subject, subject_type, addition_date):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        'DELETE FROM links WHERE user_id = %s AND subject = %s AND subject_type = %s AND addition_date = %s',
        (user_id, subject, subject_type, addition_date,)
    )
    conn.commit()


def remove_hotline(user_id, subject, description, date, addition_date):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        'DELETE FROM hotlines WHERE user_id = %s AND subject = %s AND description = %s AND date = %s AND addition_date = %s',
        (user_id, subject, description, date, addition_date,)
    )
    conn.commit()


def auto_remove_hotline():
    conn = get_connection()
    c = conn.cursor()

    dm = f"'{datetime.strftime(datetime.now() - timedelta(2), '%d.%m')}'"
    print(dm)

    c.execute(
        f'SELECT * FROM hotlines WHERE date <= {dm}'
    )
    q = c.fetchall()

    if len(q) != 0:
        c.execute(
            f'DELETE FROM hotlines WHERE date <= {dm}'
        )
        conn.commit()


def update_blocked_users(user_id, user_name, first_activity, last_activity):
    conn = get_connection()
    c = conn.cursor()
    first_act = get_blocked_user(user_id)[2]
    if first_act is None:

        c.execute(
            'UPDATE blocked_users SET user_name = %s, first_activity = %s, last_activity = %s WHERE user_id = %s',
            (user_name, first_activity, last_activity, user_id,)
        )
        conn.commit()

    else:
        c.execute(
            'UPDATE blocked_users SET user_name = %s, last_activity = %s WHERE user_id = %s',
            (user_name, last_activity, user_id,)
        )
        conn.commit()


def get_blocked_user(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        'SELECT * FROM blocked_users WHERE user_id = %s',
        (user_id,)
    )

    return c.fetchone()
