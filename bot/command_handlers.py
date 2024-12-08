from aiogram import Router
import asyncio
from aiogram.filters import CommandStart, Command
from filters import IS_ADMIN
from dialogs import ZAPUSK
from aiogram.fsm.context import FSMContext
from bot_instans import dp, bot_storage_key
from help_dialog import HELP_DIAL
from admin_dialog import ADMIN
from postgres_functions import check_user_in_table, insert_new_user_in_table
from aiogram_dialog.api.entities.modes import StartMode
from aiogram.types import Message
from aiogram_dialog import DialogManager


ch_router = Router()

@ch_router.message(CommandStart())
async def command_start_process(message:Message, dialog_manager: DialogManager, state:FSMContext):
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    if not await check_user_in_table(user_id):
        print('start if works')
        await insert_new_user_in_table(user_id, user_name)
        await state.set_data({'events':{},'lan':'ru', 'tz':'', 'temp_key':'', 'shalter':True})
        bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
        bot_dict[message.from_user.id] = {}  # Создаю пустой словарь для заметок юзера
        await dp.storage.update_data(key=bot_storage_key, data=bot_dict)  # Обновляю словарь бота
        await message.answer(text=f'👋\n\n<b>Hello, {message.from_user.first_name}!</b>\n'
            'This is a bot scheduler. Tell me when an important event happens'
            " and I'll remind you about it ahead of time!\n\nConvenient, isn't it?")

        await dialog_manager.start(state=ZAPUSK.set_lan, mode=StartMode.RESET_STACK)
    else:
        print('start else works')
        await dialog_manager.start(state=ZAPUSK.add_show, mode=StartMode.RESET_STACK)
        await message.answer(text='Бот перезапущен на сервере')
        await message.delete()


@ch_router.message(Command('basic_menu'))
async def basic_menu_start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=ZAPUSK.add_show, mode=StartMode.RESET_STACK)
    await message.answer('return to basic window')
    await asyncio.sleep(1)
    await message.delete()


@ch_router.message(Command('help'))
async def basic_menu_start(message: Message, dialog_manager: DialogManager):
    await message.answer(text='help works')
    await dialog_manager.start(state=HELP_DIAL.erst)
    await asyncio.sleep(1)
    await message.delete()


@ch_router.message(Command('admin'), IS_ADMIN())
async def basic_menu_start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(ADMIN.first)
    await asyncio.sleep(1)
    await message.delete()


