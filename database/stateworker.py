from enum import Enum


class States(Enum):
    S_START = "start_message"
    S_REGISTRATION = "registration"
    S_MAIN_MENU = "main_menu"
    S_SCHEDULE_MENU = "schedule_menu"
    S_SCHEDULE_WEEK_VIEW = "week_view"
    S_SETTINGS_MENU = "settings_menu"
    S_CHANGE_GROUP = "change_group"
    S_INPUT_LINK = "input_link"
    S_INPUT_PASSWORD = "input_password"
    S_CHANGE_LINK = "change_link"
    S_CHANGE_PASSWORD = "change_password"

