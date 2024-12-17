import asyncio
from aiogram.types import Message
from aiogram_dialog.widgets.input import ManagedTextInput, MessageInput
from aiogram_dialog import DialogManager, ShowMode
from bot_instans  import dp, bot_storage_key, scheduler
from lexicon import *
from postgres_functions import return_lan

async def message_text_handler(message: Message, widget: MessageInput, dialog_manager: DialogManager) -> None:
    print('message_text_handler works')
    user_id = str(message.from_user.id)
    lan = await return_lan(message.from_user.id)
    dialog_manager.dialog_data['titel'] = message.text
    dialog_manager.dialog_data['foto_id'] = ''
    titel = message.text
    za_chas = dialog_manager.dialog_data['za_chas']
    # print('za chas = ', za_chas)
    str_za_chas = str(za_chas)
    za_sutki = dialog_manager.dialog_data['za_sutki']
    str_za_sutki = str(za_sutki)
    # print('str_za_sutki = ', str_za_sutki)
    real_time = dialog_manager.dialog_data['real_time'] # type srt 2024-11-21 15:55:00
    dialog_manager.dialog_data['selector'] = 'U'

    job_id = str(za_chas)
    dialog_manager.dialog_data['job_id']=job_id
    pseudo_class = {'titel': titel, 'foto_id': '', 'za_chas': str_za_chas, 'za_sutki': str_za_sutki,
                    'selector': 'U', 'real_time': real_time, 'job_id': job_id}
    bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
    b_u_dict = bot_dict[user_id]  # получаю словарь юзера
    if str_za_chas not in b_u_dict:
        bot_dict[user_id][str_za_chas] = pseudo_class
        await dp.storage.update_data(key=bot_storage_key, data=bot_dict)  # Обновляю словарь бота
        await message.answer(text=gut[lan])
        dialog_manager.show_mode = ShowMode.SEND
        await message.delete()
        await dialog_manager.next()
    else:
        await message.answer(error_same_time[lan])
        dialog_manager.show_mode = ShowMode.SEND
        await dialog_manager.done()



async def correct_titel_handler(message: Message, widget: ManagedTextInput,
                               dialog_manager: DialogManager, titel: str) -> None:
    lan = await return_lan(message.from_user.id)
    await message.answer(text=f'{gut[lan]}, <b>{titel.capitalize()}</b>')
    dialog_manager.show_mode = ShowMode.SEND
    await message.delete()
    await dialog_manager.next()


async def error_titel_handler(message: Message,widget: ManagedTextInput,dialog_manager: DialogManager,error: ValueError):
    lan = await return_lan(message.from_user.id)
    await message.answer(text=incorrect_titel[lan])
    await asyncio.sleep(1)


async def on_photo_sent(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    print('on_photo_sent works')
    user_id = str(message.from_user.id)
    lan = await return_lan(message.from_user.id)
    foto_id = message.photo[-1].file_id  # Берем последнее фото (наибольшего размера)
    za_chas = dialog_manager.dialog_data['za_chas']
    str_za_chas = str(za_chas)
    za_sutki = dialog_manager.dialog_data['za_sutki']
    str_za_sutki = str(za_sutki)
    real_time = dialog_manager.dialog_data['real_time']
    dialog_manager.dialog_data['titel']=''
    dialog_manager.dialog_data['foto_id'] = foto_id
    job_id = str_za_chas
    # print('time_data = ', job_id)
    pseudo_class = {'titel': '', 'foto_id': foto_id, 'za_chas': str_za_chas, 'za_sutki': str_za_sutki,
                    'selector': 'U', 'real_time': real_time, 'job_id': job_id}
    bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота

    b_u_dict = bot_dict[user_id]  # получаю словарь юзера
    if str_za_chas not in b_u_dict:
        bot_dict[user_id][str_za_chas] = pseudo_class
        await dp.storage.update_data(key=bot_storage_key, data=bot_dict)  # Обновляю словарь бота
        await message.answer(text=gut[lan])
        dialog_manager.show_mode = ShowMode.SEND
        await message.delete()
        await dialog_manager.next()
    else:
        await message.answer(error_same_time[lan])
        dialog_manager.show_mode = ShowMode.SEND
        await dialog_manager.done()


async def message_not_foto_handler(message: Message, widget: MessageInput,
        dialog_manager: DialogManager) -> None:
    dialog_manager.show_mode = ShowMode.NO_UPDATE
    lan = await return_lan(message.from_user.id)
    await message.answer(data_mahnung[lan])


async def correct_id_handler(message: Message, widget: ManagedTextInput,
        dialog_manager: DialogManager, *args, **kwargs) -> None:
    """Хэндлер удаояет напоминание по введённому id"""
    lan = await return_lan(message.from_user.id)
    user_id = str(message.from_user.id)
    bot_dict = await dp.storage.get_data(key=bot_storage_key)
    us_bot_dict = bot_dict[user_id]
    mahn_id = message.text.strip()
    if mahn_id in us_bot_dict:
        try:
            scheduler_id = str(user_id) + str(mahn_id)
            print('scheduler_id = ', scheduler_id)
            del us_bot_dict[mahn_id]
            await dp.storage.update_data(key=bot_storage_key, data=bot_dict)
            stroka = f'{deleted[lan]}\n\nid = {message.text}'
            scheduler.remove_job(scheduler_id)
            await message.answer(text=stroka)
        except Exception as ex:  # JobLookupError:
            await message.answer(f'{deleted_past[lan]}\n\nid = {message.text}')

    else:
        await message.answer(text=no_id[lan])  # у вас нет напоминания с таким номером
    await asyncio.sleep(1)
    dialog_manager.show_mode = ShowMode.SEND
    await message.delete()
    await dialog_manager.next()


async def error_id_handler(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, error: ValueError):
    lan = await return_lan(message.from_user.id)
    await message.answer(text=incorrect_id[lan])  # Вы введи неверный id попробуйте ещё раз
    await asyncio.sleep(1)


