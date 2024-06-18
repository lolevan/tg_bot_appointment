from typing import List

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from tgbot.handlers.day.manage_data import PROCEDURE_BUTTON, DATE_BUTTON, CONFIRM_SCHEDULE, DECLINE_SCHEDULE, CONFIRM_DECLINE_SCHEDULE, CHOICE_BUTTON, TIME_SLOT, START_PROCEDURE_BUTTON
from tgbot.handlers.day.static_text import confirm_schedule, decline_schedule

from schedules.models import WorkDay, Procedure


def keyboard_get_procedures(procedures: List[Procedure], select_way: str = '#') -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(procedure.name_rus, callback_data=f'{PROCEDURE_BUTTON}{select_way}{procedure.get_underline_name()}')] for procedure in procedures
    ]

    return InlineKeyboardMarkup(buttons)


def keyboard_get_days(days: WorkDay, procedure_name: str, select_way: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(day.date.strftime('%d.%m.%Y'), callback_data=f'{DATE_BUTTON}{select_way}{day.date}#{procedure_name}')] for day in days
     ]

    buttons.append([InlineKeyboardButton('⬅ Назад', callback_data=f'{START_PROCEDURE_BUTTON}{select_way}')])

    return InlineKeyboardMarkup(buttons)


def keyboard_view_schedule(date: str, procedure_name: str, time_slot: dict, select_way: str) -> InlineKeyboardMarkup:
    print(f'{CHOICE_BUTTON}{select_way}{date}#{procedure_name}#'
          f'{TIME_SLOT}{time_slot["start_time"]}#{time_slot["end_time"]}#'
          f'{str(time_slot["delete_current_appointment"])}')

    buttons = [
        [InlineKeyboardButton(
            f'{date} --- {time_slot["start_time"]} - {time_slot["end_time"]}',
            callback_data=f'{CHOICE_BUTTON}{select_way}{date}#{procedure_name}#'
                          f'{TIME_SLOT}{time_slot["start_time"]}#{time_slot["end_time"]}#'
                          f'{str(time_slot["delete_current_appointment"])}'
        )],
        [InlineKeyboardButton('⬅ Назад', callback_data=f'{PROCEDURE_BUTTON}{select_way}{procedure_name}')]
    ]

    return InlineKeyboardMarkup(buttons)


def keyboard_confirm_schedule(date: str, procedure_name: str, start_time: str,
                              delete_current_appointment: str, select_way: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(
            confirm_schedule,
            callback_data=f'{CONFIRM_DECLINE_SCHEDULE}{CONFIRM_SCHEDULE}{select_way}{date}#{procedure_name}#'
                          f'{start_time}#'
                          f'{delete_current_appointment}'
        )],
        [InlineKeyboardButton(decline_schedule, callback_data=f'{CONFIRM_DECLINE_SCHEDULE}{DECLINE_SCHEDULE}{select_way}')]
    ]

    return InlineKeyboardMarkup(buttons)
