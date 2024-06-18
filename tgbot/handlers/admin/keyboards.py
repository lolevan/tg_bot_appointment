from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from tgbot.handlers.day.manage_data import START_PROCEDURE_BUTTON, CONFIRM_DECLINE_SCHEDULE, DECLINE_SCHEDULE
from tgbot.handlers.admin.manage_data import (ONE_WAY_BUTTON, MULTIPLE_WAY_BUTTON, SHORT, MEDIUM,
                                              LONG, HAIR_LENGTH_BUTTON, HAIR_DENSITY_BUTTON, THIN, THICK,
                                              CONFIRM_SELECT_HAIR_BUTTON, HAIR_LENGTH)
from tgbot.handlers.admin.static_text import (one_way, multiple_way, short, medium, long, low, high, confirm_select_yes,
                                              confirm_select_no)


def keyboard_confirm_select_hair(select_way: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(confirm_select_yes, callback_data=f'{START_PROCEDURE_BUTTON}{select_way}')],
        [InlineKeyboardButton(confirm_select_no, callback_data=f'{CONFIRM_DECLINE_SCHEDULE}{DECLINE_SCHEDULE}')]
    ]

    return InlineKeyboardMarkup(buttons)


def keyboard_select_density_hair(select_way: str, hair_length: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(low, callback_data=f'{CONFIRM_SELECT_HAIR_BUTTON}{select_way}#{hair_length}#{THIN}')],
        [InlineKeyboardButton(medium, callback_data=f'{CONFIRM_SELECT_HAIR_BUTTON}{select_way}#{hair_length}#{MEDIUM}')],
        [InlineKeyboardButton(high, callback_data=f'{CONFIRM_SELECT_HAIR_BUTTON}{select_way}#{hair_length}#{THICK}')]
    ]

    return InlineKeyboardMarkup(buttons)


def keyboard_select_length_hair(select_way: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(short, callback_data=f'{HAIR_DENSITY_BUTTON}{select_way}#{SHORT}')],
        [InlineKeyboardButton(medium, callback_data=f'{HAIR_DENSITY_BUTTON}{select_way}#{MEDIUM}')],
        [InlineKeyboardButton(long, callback_data=f'{HAIR_DENSITY_BUTTON}{select_way}#{LONG}')]
    ]

    return InlineKeyboardMarkup(buttons)


def keyboard_select_way_appointment() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(one_way, callback_data=f'{HAIR_LENGTH_BUTTON}{ONE_WAY_BUTTON}')],
        [InlineKeyboardButton(multiple_way, callback_data=f'{HAIR_LENGTH_BUTTON}{MULTIPLE_WAY_BUTTON}')]
    ]

    return InlineKeyboardMarkup(buttons)
