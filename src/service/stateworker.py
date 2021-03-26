# -*- coding: utf-8 -*-
#!/usr/bin/python3.8.5
from enum import Enum


class States(Enum):
    S_START = "start_message"
    S_REGISTRATION = "registration"
    S_MAIN_MENU = "main_menu"

    S_SCHEDULE_MENU = "schedule_menu"
    S_SCHEDULE_WEEK_VIEW_1 = "week_view_1"
    S_SCHEDULE_WEEK_VIEW_2 = "week_view_2"

    S_SETTINGS_MENU = "settings_menu"
    S_CHANGE_GROUP = "change_group"
    S_TOKEN_INPUT_MENU = "token_input"

    S_INPUT_LINK = "input_link"
    S_INPUT_PASSWORD = "input_password"
    S_CHANGE_LINK = "change_link"
    S_CHANGE_PASSWORD = "change_password"

    S_INPUT_HOTLINE = "input_hotline"
    S_CHANGE_HOTLINE = "change_hotline"
