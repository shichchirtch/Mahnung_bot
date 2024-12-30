from aiogram import Router
import asyncio
from aiogram.filters import CommandStart, Command
from filters import IS_ADMIN, USER_BAZA_FILTER, USER_BAZA_TWO_FILTER
from dialogs import ZAPUSK
from aiogram.fsm.context import FSMContext
from bot_instans import dp, bot_storage_key, scheduler
from help_dialog import HELP_DIAL
from admin_dialog import ADMIN
from postgres_functions import check_user_in_table, insert_new_user_in_table
from aiogram_dialog.api.entities.modes import StartMode, ShowMode
from aiogram.types import Message, CallbackQuery
from aiogram_dialog import DialogManager
from postgres_functions import return_lan, insert_last_null, insert_lan, insert_timezone
from lexicon import *

ch_router = Router()


@ch_router.message(CommandStart())
async def command_start_process(message:Message, dialog_manager: DialogManager, state:FSMContext):
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    if not await check_user_in_table(user_id):
        print(f'\n\nBOT START {message.from_user.first_name}, {message.from_user.id}\n\n')
        await insert_new_user_in_table(user_id, user_name)
        bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
        bot_dict[message.from_user.id] = {'uniq':{}, 'reg':{}}  # Создаю пустой словарь для заметок юзера
        await dp.storage.update_data(key=bot_storage_key, data=bot_dict)  # Обновляю словарь бота
        await message.answer(text=f'👋\n\n<b>Hello, {message.from_user.first_name}!</b>\n'
            'This is a bot scheduler. Tell me when an important event happens'
            " and I'll remind you about it ahead of time!\n\nConvenient, isn't it?")

        await dialog_manager.start(state=ZAPUSK.set_lan, mode=StartMode.RESET_STACK)
    else:
        print('start else works')
        await insert_new_user_in_table(user_id, user_name)
        lan = await return_lan(message.from_user.id)
        if not lan:
            await insert_lan(message.from_user.id, 'ru')
            await insert_timezone(message.from_user.id, 'Europe/Moscow')
        await dialog_manager.start(state=ZAPUSK.add_show, mode=StartMode.RESET_STACK)
        await message.answer(text='Bot was restated on server')
        await message.delete()


@ch_router.message(Command('basic_menu'))
async def basic_menu_start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=ZAPUSK.add_show, mode=StartMode.RESET_STACK)
    await message.answer('<i>return to basic window</i>')
    print('Command("basic_menu") dialog_manager.dialog_data = ', dialog_manager.dialog_data)
    dialog_manager.dialog_data.clear()
    await insert_last_null(message.from_user.id)  # Обнуляю строку на всякий случай
    await asyncio.sleep(1)
    await message.delete()


@ch_router.message(Command('help'))
async def basic_menu_help(message: Message, dialog_manager: DialogManager):
    # await message.answer(text='help works')
    await dialog_manager.start(state=HELP_DIAL.erst)
    await asyncio.sleep(1)
    await message.delete()


@ch_router.message(Command('admin'), IS_ADMIN())
async def admin_enter(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(ADMIN.first)
    await asyncio.sleep(1)
    await message.delete()



@ch_router.callback_query(USER_BAZA_FILTER())   # delete
async def delete_last_mahnung(cb:CallbackQuery, dialog_manager: DialogManager, state:FSMContext, *args, **kwargs):
    """Хэндлер удаояет напоминание по кнопке"""
    # print('cb data = ', cb.data)
    lan = await return_lan(cb.from_user.id)
    user_id = str(cb.from_user.id)
    await insert_last_null(cb.from_user.id)  # Вот здесь меняется индикатор last
    bot_dict = await dp.storage.get_data(key=bot_storage_key)
    us_bot_dict = bot_dict[user_id]['reg']
    mahn_id = str(cb.data)
    us_unuq_dict =  bot_dict[user_id]['uniq']
    if mahn_id in us_bot_dict:
        # print('\n\ninto reg')
        try:
            scheduler_id = str(user_id) + mahn_id
            # print('scheduler_id = ', scheduler_id)
            del us_bot_dict[mahn_id]
            await dp.storage.update_data(key=bot_storage_key, data=bot_dict)
            stroka = f'{deleted[lan]}\n\nid = {mahn_id}'
            scheduler.remove_job(scheduler_id)
            try:
                # print('DELETE MESSAGE\n\n')
                await cb.message.delete()  # Убираем клавиатуру
            except Exception:
                print("Клавиатура уже была удалена")
            await cb.message.answer(text=stroka)
        except Exception as ex:  # JobLookupError:
            await cb.message.answer(f'{deleted_past[lan]}\n\nid = {mahn_id}')
            try:
                # print('DELETE MESSAGE\n\n')
                await cb.message.delete()  # Убираем клавиатуру
            except Exception:
                print("Клавиатура уже была удалена")

    elif mahn_id in us_unuq_dict:
        # print('uniq teil\n\n')
        del us_unuq_dict[mahn_id]
        await dp.storage.update_data(key=bot_storage_key, data=bot_dict)
        stroka = f'{deleted[lan]}\n\nid = {mahn_id}'
        try:
            # print('DELETE MESSAGE\n\n')
            await cb.message.delete()  # Убираем клавиатуру
        except Exception:
            print("Клавиатура уже была удалена")
        await cb.message.answer(text=stroka)

    else:
        await cb.message.answer(text=no_id[lan])  # у вас нет напоминания с таким номером
    await asyncio.sleep(1)

    # await message.delete()
    await dialog_manager.start(state=ZAPUSK.add_show, mode=StartMode.RESET_STACK)
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    await asyncio.sleep(1)




@ch_router.callback_query(USER_BAZA_TWO_FILTER())
async def perxvat4ick_mahnung(cb:CallbackQuery, dialog_manager: DialogManager, state:FSMContext, *args, **kwargs):
    """Хэндлер удаояет напоминание по кнопке"""
    print('Perexvat4ic   cb data = ', cb.data)
    await cb.message.answer(text="➡️ /basic_menu")#no_id[lan])  #


