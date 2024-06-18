from typing import List, Dict

import telegram
from telegram import Update, ParseMode
from telegram.ext import CallbackContext

from schedules.models import (WorkDay, ProcedureHaircut, ProcedureSimpleColor, ProcedureComplexColor, ProcedureBotox,
                              ProcedureKeratin, ProcedureLaying, ProcedureCurls, ProcedureHairstyle,
                              ProcedureHairExtensionsFull, ProcedureHairExtensionsTemple, ProcedureHighlights,
                              Procedure, ProcedureHairCheck)

from users.models import User

from tgbot.handlers.utils.decorators import verified_only
from tgbot.handlers.day import static_text
from tgbot.handlers.day.keyboards import keyboard_get_days, keyboard_get_procedures, keyboard_confirm_schedule, \
    keyboard_view_schedule
from tgbot.handlers.utils.info import extract_user_data_from_update

import datetime

procedure_classes: Dict[str, Procedure] = {
    'Haircut': ProcedureHaircut(),
    'Simple Color': ProcedureSimpleColor(),
    'Complex Color': ProcedureComplexColor(),
    'Botox': ProcedureBotox(),
    'Keratin': ProcedureKeratin(),
    'Laying': ProcedureLaying(),
    'Curls': ProcedureCurls(),
    'Hairstyle': ProcedureHairstyle(),
    'Hair ext full': ProcedureHairExtensionsFull(),
    'Hair ext temple': ProcedureHairExtensionsTemple(),
    'Highlights': ProcedureHighlights(),
    # 'Hair check': ProcedureHairCheck(),
}


def get_available_days(update: Update, context: CallbackContext) -> None:
    print(update.callback_query.data)
    user_id = extract_user_data_from_update(update)['user_id']
    current_date = datetime.date.today()

    days = WorkDay.objects.filter(is_visible=True, date__gt=current_date)
    text = static_text.start_day

    select_way = update.callback_query.data.split('#')[1] + '#'
    procedure_name = update.callback_query.data.split('#')[2]

    context.bot.edit_message_text(
        text=text,
        chat_id=user_id,
        message_id=update.callback_query.message.message_id,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard_get_days(days, procedure_name, select_way)
    )


@verified_only
def get_start_procedures(update: Update, context: CallbackContext) -> None:
    procedures: List[Procedure] = list(procedure_classes.values())
    text: str = static_text.all_procedures

    update.message.reply_text(
        text=text,
        reply_markup=keyboard_get_procedures(procedures)
    )


def get_procedures(update: Update, context: CallbackContext) -> None:
    user_id = extract_user_data_from_update(update)['user_id']
    procedures: List[Procedure] = list(procedure_classes.values())[:-1]
    text: str = static_text.all_procedures
    select_way: str = update.callback_query.data.split('#')[1] + '#'

    print(f'select_way 1 {select_way}')

    if select_way == 'ONEWAY#' or select_way == 'True#':
        select_way = 'True#'
        procedures = list(procedure_classes.values())
    elif select_way == 'MULTIPLEWAY#' or select_way == 'False#':
        select_way = 'False#'
        procedures = list(procedure_classes.values())

    print(f'select_way 2 {select_way}')

    print(update.callback_query.data)

    context.bot.edit_message_text(
        text=text,
        chat_id=user_id,
        message_id=update.callback_query.message.message_id,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard_get_procedures(procedures, select_way)
    )


def get_procedure_stages(procedure_class: Procedure, user: User) -> dict:
    """
    Вычисляет этапы процедуры на основе данных пользователя и класса процедуры.
    """
    hair_length = str(user.hair_length)
    hair_density = str(user.hair_density)
    return procedure_class.calculate_duration(hair_length, hair_density)


def get_procedure_info(update: Update) -> tuple[str, str, str, Procedure, str, User, dict]:
    user_id = extract_user_data_from_update(update)['user_id']
    select_way = update.callback_query.data.split('#')[1] + '#'

    print(select_way)

    if select_way == 'True#':
        user: User = User.objects.get(user_id=111)
    elif select_way == 'False#':
        user: User = User.objects.get(user_id=222)
    else:
        user: User = User.objects.get(user_id=user_id)

    print(user)

    date: str = update.callback_query.data.split('#')[2]
    procedure_name: str = ' '.join(update.callback_query.data.split('#')[3].split('_'))
    procedure_class: Procedure = procedure_classes[procedure_name]
    procedure_stages: dict = get_procedure_stages(procedure_class, user)
    day: WorkDay = WorkDay.objects.get(date=date)
    time_slot: Dict[str, str | bool] = day.get_available_time_slot(procedure_stages, user)
    return user_id, date, procedure_name, procedure_class, select_way, user, time_slot


def view_schedule(update: Update, context: CallbackContext) -> None:
    print(update.callback_query.data)
    user_id, date, procedure_name, procedure_class, select_way, _, time_slot = get_procedure_info(update)
    if time_slot['cancelled']:
        text = static_text.no_time_procedure.format(
            date=date,
            procedure=procedure_class.name_rus
        )
        context.bot.send_message(chat_id=user_id, text=text)
    else:
        text = static_text.view_schedule
        context.bot.edit_message_text(
            text=text,
            chat_id=user_id,
            message_id=update.callback_query.message.message_id,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard_view_schedule(date, procedure_name, time_slot, select_way)
        )


def confirm_schedule(update: Update, context: CallbackContext) -> None:
    print(update.callback_query.data)
    user_id, date, procedure_name, procedure_class, select_way, *_ = get_procedure_info(update)
    procedure_name_rus = procedure_class.name_rus
    start_time = update.callback_query.data.split('#')[5]
    end_time = update.callback_query.data.split('#')[6]
    delete_current_appointment = update.callback_query.data.split('#')[7]

    print(start_time, end_time, delete_current_appointment)

    text = static_text.confirm_information.format(
        username=update.callback_query.from_user.first_name,
        date=date,
        procedure=procedure_name_rus,
        start_time=start_time,
        end_time=end_time,
    )
    context.bot.edit_message_text(
        text=text,
        chat_id=user_id,
        message_id=update.callback_query.message.message_id,
        parse_mode=ParseMode.HTML,
        reply_markup=keyboard_confirm_schedule(date, procedure_name, start_time, delete_current_appointment, select_way)
    )


def notify_registration(update: Update, context: CallbackContext) -> None:
    print(update.callback_query.data)
    user_id, date, procedure_name, procedure_class, select_way, user, _ = get_procedure_info(update)
    start_time = datetime.datetime.strptime(update.callback_query.data.split('#')[4], '%H:%M').time()
    delete_current_appointment: bool = False if update.callback_query.data.split('#')[5] == 'False' else True
    procedure_stages = get_procedure_stages(procedure_class, user)
    day: WorkDay = WorkDay.objects.get(date=date)

    print('delete_current_appointment:', delete_current_appointment)

    day.make_appointment(user, procedure_stages, delete_current_appointment, start_time, procedure_name)
    text = static_text.notify_registration
    context.bot.edit_message_text(
        text=text,
        chat_id=user_id,
        message_id=update.callback_query.message.message_id,
        parse_mode=ParseMode.HTML,
    )


def notify_decline_schedule(update: Update, context: CallbackContext) -> None:
    print(update.callback_query.data)
    user_id = extract_user_data_from_update(update)['user_id']
    text = static_text.notify_decline_schedule
    context.bot.edit_message_text(
        text=text,
        chat_id=user_id,
        message_id=update.callback_query.message.message_id,
        parse_mode=ParseMode.HTML,
    )
