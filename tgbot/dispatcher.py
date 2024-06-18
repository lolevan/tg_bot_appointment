"""
    Telegram event handlers
"""
from telegram.ext import (
    Dispatcher, Filters,
    CommandHandler, MessageHandler,
    CallbackQueryHandler,
)

from dtb.settings import DEBUG
from tgbot.handlers.broadcast_message.manage_data import CONFIRM_DECLINE_BROADCAST
from tgbot.handlers.broadcast_message.static_text import broadcast_command
from tgbot.handlers.onboarding.manage_data import SECRET_LEVEL_BUTTON
from tgbot.handlers.day.manage_data import (PROCEDURE_BUTTON, CONFIRM_DECLINE_SCHEDULE, DATE_BUTTON, CHOICE_BUTTON,
                                            START_PROCEDURE_BUTTON, CONFIRM_SCHEDULE, DECLINE_SCHEDULE)
from tgbot.handlers.auth_user.manage_data import SEND_PHOTO_BUTTON
from tgbot.handlers.admin.manage_data import HAIR_LENGTH_BUTTON, HAIR_DENSITY_BUTTON, CONFIRM_SELECT_HAIR_BUTTON

from tgbot.handlers.utils import files, error
from tgbot.handlers.admin import handlers as admin_handlers
from tgbot.handlers.location import handlers as location_handlers
from tgbot.handlers.onboarding import handlers as onboarding_handlers
from tgbot.handlers.broadcast_message import handlers as broadcast_handlers
from tgbot.handlers.day import handlers as day_handlers
from tgbot.handlers.auth_user import handlers as auth_user_handlers
from tgbot.main import bot


def setup_dispatcher(dp):
    """
    Adding handlers for events from Telegram
    """
    # onboarding
    dp.add_handler(CommandHandler("start", onboarding_handlers.command_start))

    # admin commands
    dp.add_handler(CommandHandler("admin", admin_handlers.admin))
    dp.add_handler(CommandHandler("stats", admin_handlers.stats))
    dp.add_handler(CommandHandler('export_users', admin_handlers.export_users))
    dp.add_handler(CommandHandler("appointment_user", admin_handlers.select_way_appointment))
    dp.add_handler(
        CallbackQueryHandler(admin_handlers.select_length_hair, pattern=f"{HAIR_LENGTH_BUTTON}")
    )
    dp.add_handler(
        CallbackQueryHandler(admin_handlers.select_density_hair, pattern=f"{HAIR_DENSITY_BUTTON}")
    )
    dp.add_handler(
        CallbackQueryHandler(admin_handlers.confirm_select_hair, pattern=f"{CONFIRM_SELECT_HAIR_BUTTON}")
    )

    # location
    dp.add_handler(CommandHandler("ask_location", location_handlers.ask_for_location))
    dp.add_handler(MessageHandler(Filters.location, location_handlers.location_handler))

    # secret level
    dp.add_handler(CallbackQueryHandler(onboarding_handlers.secret_level, pattern=f"^{SECRET_LEVEL_BUTTON}"))

    # broadcast message
    dp.add_handler(
        MessageHandler(Filters.regex(rf'^{broadcast_command}(/s)?.*'), broadcast_handlers.broadcast_command_with_message)
    )
    dp.add_handler(
        CallbackQueryHandler(broadcast_handlers.broadcast_decision_handler, pattern=f"^{CONFIRM_DECLINE_BROADCAST}")
    )

    # schedule message
    dp.add_handler(
        CommandHandler("appointment", day_handlers.get_start_procedures)
    )
    dp.add_handler(
        CallbackQueryHandler(day_handlers.get_procedures, pattern=f"{START_PROCEDURE_BUTTON}")
    )
    dp.add_handler(
        CallbackQueryHandler(day_handlers.get_available_days, pattern=f"{PROCEDURE_BUTTON}")
    )
    dp.add_handler(
        CallbackQueryHandler(day_handlers.view_schedule, pattern=f"{DATE_BUTTON}")
    )
    dp.add_handler(
        CallbackQueryHandler(day_handlers.confirm_schedule, pattern=f"{CHOICE_BUTTON}")
    )
    dp.add_handler(
        CallbackQueryHandler(day_handlers.notify_registration, pattern=f"{CONFIRM_DECLINE_SCHEDULE}{CONFIRM_SCHEDULE}")
    )
    dp.add_handler(
        CallbackQueryHandler(day_handlers.notify_decline_schedule, pattern=f"{CONFIRM_DECLINE_SCHEDULE}{DECLINE_SCHEDULE}")
    )

    # NonAuthUser message

    dp.add_handler(
        CommandHandler("authentication", auth_user_handlers.authentication_user)
    )
    dp.add_handler(
        CallbackQueryHandler(auth_user_handlers.get_photo_user, pattern=f"^{SEND_PHOTO_BUTTON}")
    )
    dp.add_handler(
        MessageHandler(Filters.photo, auth_user_handlers.upload_photo_user)
    )



    # files
    dp.add_handler(MessageHandler(
        Filters.animation, files.show_file_id,
    ))

    # handling errors
    dp.add_error_handler(error.send_stacktrace_to_tg_chat)

    # EXAMPLES FOR HANDLERS
    # dp.add_handler(MessageHandler(Filters.text, <function_handler>))
    # dp.add_handler(MessageHandler(
    #     Filters.document, <function_handler>,
    # ))
    # dp.add_handler(CallbackQueryHandler(<function_handler>, pattern="^r\d+_\d+"))
    # dp.add_handler(MessageHandler(
    #     Filters.chat(chat_id=int(TELEGRAM_FILESTORAGE_ID)),
    #     # & Filters.forwarded & (Filters.photo | Filters.video | Filters.animation),
    #     <function_handler>,
    # ))

    return dp


n_workers = 0 if DEBUG else 4
dispatcher = setup_dispatcher(Dispatcher(bot, update_queue=None, workers=n_workers, use_context=True))
