from typing import List

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from tgbot.handlers.auth_user.manage_data import SEND_PHOTO_BUTTON
from tgbot.handlers.auth_user.static_text import start_send_photo

from schedules.models import WorkDay


def keyboard_send_photo_auth() -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton(start_send_photo, callback_data=SEND_PHOTO_BUTTON)]]

    return InlineKeyboardMarkup(keyboard)
