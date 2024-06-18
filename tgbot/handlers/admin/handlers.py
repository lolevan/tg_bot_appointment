from typing import Dict

from datetime import timedelta

from django.utils.timezone import now
from telegram import ParseMode, Update
from telegram.ext import CallbackContext

from tgbot.handlers.admin import static_text
from tgbot.handlers.admin.utils import _get_csv_from_qs_values
from tgbot.handlers.utils.decorators import admin_only, send_typing_action
from tgbot.handlers.utils.info import extract_user_data_from_update

from .keyboards import (keyboard_select_way_appointment, keyboard_select_density_hair, keyboard_select_length_hair,
                        keyboard_confirm_select_hair)

from users.models import User, HairLengthEnum, HairDensityEnum

from django_enumfield import enum


hair_length_enum: Dict[str, HairLengthEnum] = {
    'SHORT': HairLengthEnum.SHORT,
    'MEDIUM': HairLengthEnum.MEDIUM,
    'LONG': HairLengthEnum.LONG,
}

hair_density_enum: Dict[str, HairDensityEnum] = {
    'THIN': HairDensityEnum.THIN,
    'MEDIUM': HairDensityEnum.MEDIUM,
    'THICK': HairDensityEnum.THICK,
}


@admin_only
def admin(update: Update, context: CallbackContext) -> None:
    """ Show help info about all secret admins commands """
    update.message.reply_text(static_text.secret_admin_commands)


@admin_only
def stats(update: Update, context: CallbackContext) -> None:
    """ Show help info about all secret admins commands """
    text = static_text.users_amount_stat.format(
        user_count=User.objects.count(),  # count may be ineffective if there are a lot of users.
        active_24=User.objects.filter(updated_at__gte=now() - timedelta(hours=24)).count()
    )

    update.message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


@admin_only
@send_typing_action
def export_users(update: Update, context: CallbackContext) -> None:
    # in values argument you can specify which fields should be returned in output csv
    users = User.objects.all().values()
    csv_users = _get_csv_from_qs_values(users)
    update.message.reply_document(csv_users)


def confirm_select_hair(update: Update, context: CallbackContext) -> None:
    user_id: str = extract_user_data_from_update(update)['user_id']

    select_way: str = update.callback_query.data.split('#')[1]
    hair_length: str = update.callback_query.data.split('#')[2]
    hair_density: str = update.callback_query.data.split('#')[3]

    text: str = static_text.confirm_select_hair.format(
        density_hair=hair_density,
        length_hair=hair_length
    )

    print(select_way, hair_length, hair_density)

    if select_way == 'ONEWAY':
        user: User = User.objects.get(user_id=111)
    else:
        user: User = User.objects.get(user_id=222)

    user.hair_length = hair_length_enum[hair_length]
    user.hair_density = hair_density_enum[hair_density]

    user.save()

    print(user.hair_density, user.hair_length)

    context.bot.edit_message_text(
        text=text,
        chat_id=user_id,
        message_id=update.callback_query.message.message_id,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard_confirm_select_hair(select_way)
    )


def select_density_hair(update: Update, context: CallbackContext) -> None:
    user_id: str = extract_user_data_from_update(update)['user_id']
    text: str = static_text.select_density_hair

    select_way: str = update.callback_query.data.split('#')[1]
    hair_length: str = update.callback_query.data.split('#')[2]

    context.bot.edit_message_text(
        text=text,
        chat_id=user_id,
        message_id=update.callback_query.message.message_id,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard_select_density_hair(select_way, hair_length)
    )


def select_length_hair(update: Update, context: CallbackContext) -> None:
    user_id: str = extract_user_data_from_update(update)['user_id']
    text: str = static_text.select_length_hair

    select_way: str = update.callback_query.data.split('#')[1]

    context.bot.edit_message_text(
        text=text,
        chat_id=user_id,
        message_id=update.callback_query.message.message_id,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard_select_length_hair(select_way)
    )


@admin_only
def select_way_appointment(update: Update, context: CallbackContext) -> None:
    text = static_text.select_way_appointment

    update.message.reply_text(
        text=text,
        reply_markup=keyboard_select_way_appointment()
    )
