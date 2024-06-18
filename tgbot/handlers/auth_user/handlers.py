import tempfile
from typing import List

import telegram
from telegram import Update, ParseMode
from telegram.ext import CallbackContext

from schedules.models import UserAuthenticationRequest

from users.models import User

from tgbot.handlers.utils.decorators import not_verified_only
from tgbot.handlers.auth_user import static_text
from tgbot.handlers.auth_user.keyboards import keyboard_send_photo_auth
from tgbot.handlers.utils.info import extract_user_data_from_update


def authentication_user(update: Update, context: CallbackContext) -> None:
    user = User.get_user(update, context)
    if not user.is_verified_user:
        # прохождение аунтификации
        update.message.reply_text(
            text=static_text.authentication_required,
            reply_markup=keyboard_send_photo_auth()
        )
    else:
        ...


def get_photo_user(update: Update, context: CallbackContext) -> None:
    user_id = extract_user_data_from_update(update)['user_id']
    text = static_text.waiting_photo

    context.bot.edit_message_text(
        text=text,
        chat_id=user_id,
        message_id=update.callback_query.message.message_id,
        parse_mode=ParseMode.HTML,
    )


@not_verified_only
def upload_photo_user(update: Update, context: CallbackContext) -> None:
    user: User = User.get_user(update, context)

    # Get the highest resolution photo from the message
    photo_id = update.message.photo[-1].file_id
    photo_file = context.bot.get_file(photo_id)

    # Download the photo and save it temporarily
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as temp_photo:
        # Download the photo and save it to the temporary file
        photo_file.download(out=temp_photo)

        # Get or create a UserAuthenticationRequest instance for the user
        user_request, created = UserAuthenticationRequest.objects.get_or_create(user=user)

        # Pass the temporary file path to the add_photo method of the user_request instance
        photo_added: bool = user_request.add_photo(temp_photo.name)

    if photo_added:
        text = static_text.photo_uploaded
    else:
        text = static_text.photo_not_uploaded

    update.message.reply_text(
        text=text,
        reply_markup=telegram.ReplyKeyboardRemove(),
    )
