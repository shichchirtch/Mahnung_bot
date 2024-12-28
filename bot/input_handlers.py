import asyncio
from aiogram.types import Message
from aiogram_dialog.widgets.input import ManagedTextInput, MessageInput
from aiogram_dialog import DialogManager, ShowMode
from bot_instans  import dp, bot_storage_key, scheduler, WORK_WITH_SCHED
from lexicon import *
from postgres_functions import return_lan, return_spisok_uniq_events, insert_uniq_events

async def message_text_handler(message: Message, widget: MessageInput, dialog_manager: DialogManager) -> None:
    """Хэндлер устанавливает текстовое напоминание"""
    user_id = str(message.from_user.id)
    lan = await return_lan(message.from_user.id)
    dialog_manager.dialog_data['titel'] = message.text
    dialog_manager.dialog_data['foto_id'] = ''
    dialog_manager.dialog_data['capture'] = ''
    titel = message.text
    za_chas = dialog_manager.dialog_data['za_chas']  # Tут записаны инты
    spisok_uniq_za_chas = await return_spisok_uniq_events(message.from_user.id)
    if str(za_chas) not in spisok_uniq_za_chas:
        str_za_chas = str(za_chas)
        za_sutki = dialog_manager.dialog_data['za_sutki']
        str_za_sutki = str(za_sutki)
        real_time = dialog_manager.dialog_data['real_time']  # type srt 2024-11-21 15:55:00
        job_id = str(za_chas)
        dialog_manager.dialog_data['job_id']=job_id
        pseudo_class = {'titel': titel, 'foto_id': '', 'za_chas': str_za_chas, 'za_sutki': str_za_sutki,
                        'selector': 'U', 'real_time': real_time, 'capture':'', 'job_id': job_id}
        time_code = str(dialog_manager.dialog_data['day'])
        bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
        # b_u_dict = bot_dict[user_id]  # получаю словарь юзера
        # b_u_dict_uniq = b_u_dict['uniq']  # Получаю словарь для уникальных событий
        bot_dict[user_id]['uniq'].setdefault(time_code, []).append(pseudo_class)  # Записываю туда вот такую струкутру '173000000':[]
        # print('36 bot_dict',bot_dict)  # 36 bot_dict
        # {'6685637602': {'uniq': {'1734912000': # День в 00:00 value = [], ключа за час - нет
        # [{'titel': 'test', 'foto_id': '', 'za_chas': '1734875400', #  За час и job_id - совпадают
        # 'za_sutki': '', 'selector': 'U', 'real_time': '22.12.2024  14:50',
        # 'job_id': '1734875400'}]},
        # 'reg': {} # Регулярных событий ещё нет
        #   }
        # }  - Не удалять комменатрий !


        await dp.storage.update_data(key=bot_storage_key, data=bot_dict)  # Обновляю словарь бота

        await insert_uniq_events(message.from_user.id, str_za_chas)  # записываю уникальное событие в списоск

        await message.answer(text=gut[lan])
        dialog_manager.show_mode = ShowMode.SEND
        await message.delete()
        await dialog_manager.switch_to(WORK_WITH_SCHED.vor_mahnung)
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


async def message_not_foto_handler(message: Message, widget: MessageInput,
        dialog_manager: DialogManager) -> None:
    dialog_manager.show_mode = ShowMode.NO_UPDATE
    lan = await return_lan(message.from_user.id)
    await message.answer(data_mahnung[lan])


async def correct_id_handler(message: Message, widget: ManagedTextInput,
        dialog_manager: DialogManager, *args, **kwargs) -> None:
    """Хэндлер удаляет регулярные напоминание по введённому id"""
    lan = await return_lan(message.from_user.id)
    user_id = str(message.from_user.id)
    bot_dict = await dp.storage.get_data(key=bot_storage_key)
    us_bot_dict = bot_dict[user_id]['reg']  #  {'1300': {'titel': 'day tets', 'foto_id': '', 'za_chas': None, 'za_sutki': None, 'selector': 'D', 'real_time': 'Ежеденевно 13 : 00', 'capture': '', 'job_id': '1300'}}
    # print('us_bot_dict = ', us_bot_dict)
    # uniq_dict =  bot_dict[user_id]['uniq']
    # print('uniq_dict = ', uniq_dict)
    mahn_id = message.text
    if mahn_id in us_bot_dict:
        try:
            scheduler_id = str(user_id) + str(mahn_id)
            # print('scheduler_id = ', scheduler_id)
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

# 66856376021735304400
# uniq_dict =  {'1735084800':   # Струкура уникального словаря
#                   [
#                       {'titel': 'test 25 9 10', 'foto_id': '', 'za_chas': '1735114200',
#                     'za_sutki': '1735031400', 'selector': 'U', 'real_time': '25.12.2024  09:10', 'job_id': '1735114200'},
#                    {'titel': 'tesr 25 21 50', 'foto_id': '', 'za_chas': '1735159800', 'za_sutki': '1735077000',
#                     'selector': 'U', 'real_time': '25.12.2024  21:50', 'job_id': '1735159800'}
#                   ]
#               }

