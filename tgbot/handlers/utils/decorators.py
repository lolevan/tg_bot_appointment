from functools import wraps
from typing import Callable

from telegram import Update, ChatAction
from telegram.ext import CallbackContext

from users.models import User


def admin_only(func: Callable):
    """
    Admin only decorator
    Used for handlers that only admins have access to
    """

    @wraps(func)
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        user = User.get_user(update, context)

        if not user.is_admin:
            return

        return func(update, context, *args, **kwargs)

    return wrapper


def send_typing_action(func: Callable):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update: Update, context: CallbackContext, *args, **kwargs):
        update.effective_chat.send_chat_action(ChatAction.TYPING)
        return func(update, context, *args, **kwargs)

    return command_func


def verified_only(func: Callable):
    """
    Verified only decorator
    Used for handlers that only verified users have access to
    """

    @wraps(func)
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        user = User.get_user(update, context)

        if not user.is_verified_user:
            return

        return func(update, context, *args, **kwargs)

    return wrapper


def not_verified_only(func: Callable):
    """
    Not verified only decorator
    Used for handlers that only not verified users have access to
    """

    @wraps(func)
    def wrapper(update: Update, context: CallbackContext, *args, **kwargs):
        user = User.get_user(update, context)

        if user.is_verified_user:
            return

        return func(update, context, *args, **kwargs)

    return wrapper
