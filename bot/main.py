import asyncio
from command_handlers import ch_router
from bot_instans import bot, bot_storage_key, dp
from aiogram_dialog import setup_dialogs
from dialogs import uniqe_dialog, zapusk_dialog
from start_menu import set_main_menu
from days_handlers import day_mahnung_dialog
from monat_handlers import monat_mahnung_dialog
from week_handlers import week_mahnung_dialog
from show_handlers import show_mahnung_dialog
from admin_dialog import admin_dialog
from bot_instans import scheduler
from help_dialog import dialog_help, reset_tz_dialog, review_dialog, scolco_dialog
from postgres_table import init_models


async def main():
    await init_models()

    dp.startup.register(set_main_menu)
    await dp.storage.set_data(key=bot_storage_key, data={})
    scheduler.start()
    dp.include_router(ch_router)
    dp.include_router(zapusk_dialog)
    dp.include_router(uniqe_dialog)
    dp.include_router(show_mahnung_dialog)
    dp.include_router(monat_mahnung_dialog)
    dp.include_router(week_mahnung_dialog)
    dp.include_router(day_mahnung_dialog)
    dp.include_router(dialog_help)
    dp.include_router(admin_dialog)
    dp.include_router(reset_tz_dialog)
    dp.include_router(review_dialog)
    dp.include_router(scolco_dialog)

    # Пропускаем накопившиеся апдейты и запускаем polling
    await bot.delete_webhook(drop_pending_updates=True)
    setup_dialogs(dp)
    await dp.start_polling(bot)

asyncio.run(main())