from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.api.entities.modes import ShowMode, StartMode
from bot_instans import dp, bot_storage_key, ZAPUSK
from lexicon import *
from scheduler_functions import napominalka_sync_for_month
from aiogram_dialog.widgets.input import MessageInput
from postgres_functions import return_lan, return_tz

async def go_to_regular(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    print('go_to_regular works')
    dialog_manager.show_mode = ShowMode.SEND
    await dialog_manager.next()


async def go_to_31(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    lan = await return_lan(callback.from_user.id)
    dialog_manager.dialog_data['lan'] = lan
    dialog_manager.show_mode = ShowMode.SEND
    await dialog_manager.next()

async def button_day_clicked(callback: CallbackQuery, widget: Button,
                             dialog_manager: DialogManager):
    day_dict = {'button_1': 'last,1', 'button_2': '1,2', 'button_3': '2,3',
                'button_4': '3,4', 'button_5': '4,5', 'button_6': '5,6', 'button_7': '6,7',
                'button_8': '7,8', 'button_9': '8,9', 'button_10': '9,10', 'button_11': '10,11',
                'button_12': '11,12', 'button_13': '12,13', 'button_14': '13,14', 'button_15': '14,15',
                'button_16': '15,16', 'button_17': '16,17', 'button_18': '17,18', 'button_19': '18,19',
                'button_20': '19,20', 'button_21': '20,21', 'button_22': '21,22', 'button_23': '22,23',
                'button_24': '23,24', 'button_25': '24,25', 'button_26': '25,26', 'button_27': '26,27',
                'button_28': '27,28', 'button_29': '28,29', 'button_30': '29,30', 'button_31': '30,last',
                }
    if 'day' in dialog_manager.dialog_data:
        temp_data = dialog_manager.dialog_data['day']
        if day_dict[callback.data] in temp_data:
            await callback.message.answer(f'{day_dict[callback.data]} is already in Plan')
            t = 1
        else:
            day_group = temp_data + ',' + day_dict[callback.data]
            dialog_manager.dialog_data['day'] = day_group
            t = ''
    else:
        # print('here day net')
        dialog_manager.dialog_data['day'] = day_dict[callback.data]
        t = ''
        dialog_manager.dialog_data['choosing_data'] = 1
    lan = dialog_manager.dialog_data['lan']
    if callback.data != 'button_31':
        temp_sending_data = day_dict[callback.data]
        sending_data = temp_sending_data.split(',')[-1]
    else:
        sending_data = 'last day of month or 31'
    if not t:
        await callback.message.answer(f'{sobytie_sluchitsa[lan]} {sending_data}')


async def approve_choise(callback: CallbackQuery, widget: Button,
                        dialog_manager: DialogManager):
    if dialog_manager.dialog_data['choosing_data']:
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await dialog_manager.next()
    else:
        await callback.message.answer('Choose Day')


async def button_hour_clicked(callback: CallbackQuery, widget: Button,
                             manager: DialogManager):
    print('button_hour_clicked works')
    uhr_dict = {'button_00': '00', 'button_1': '01', 'button_2': '02', 'button_3': '03',
                'button_4': '04', 'button_5': '05', 'button_6': '06', 'button_7': '07',
                'button_8': '08', 'button_9': '09', 'button_10': '10', 'button_11': '11',
                'button_12': '12', 'button_13': '13', 'button_14': '14', 'button_15': '15',
                'button_16': '16', 'button_17': '17', 'button_18': '18', 'button_19': '19',
                'button_20': '20', 'button_21': '21', 'button_22': '22', 'button_23': '23',
                }
    hour_mahnung = uhr_dict[callback.data]
    manager.dialog_data['hours'] = hour_mahnung
    manager.show_mode = ShowMode.DELETE_AND_SEND
    await manager.next()

async def button_minut_clicked(callback: CallbackQuery, widget: Button,
                             manager: DialogManager):
    print('button_minut_clicked works')
    min_dict = {'button_00': '00', 'button_05': '05', 'button_10': '10', 'button_15': '15',
                'button_20': '20', 'button_25': '25', 'button_30': '30', 'button_35': '35',
                'button_40': '40', 'button_45': '45', 'button_50': '50', 'button_55': '55',
                }
    manager.dialog_data['minuts'] = min_dict[callback.data]
    lan = await return_lan(callback.from_user.id)
    await callback.message.answer(text=knopka_nazata[lan])

async def button_zapusk_clicked_for_month(callback: CallbackQuery, widget: Button,
                                dialog_manager: DialogManager):
    if 'minuts' in dialog_manager.dialog_data:
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await dialog_manager.next()
    else:
        await callback.message.answer('Choose Minuts')
        dialog_manager.show_mode = ShowMode.SEND



async def message_text_handler_for_month(message: Message, widget: MessageInput, dialog_manager: DialogManager) -> None:
    user_id = str(message.from_user.id)
    lan = await return_lan(message.from_user.id)
    dialog_manager.dialog_data['titel'] = message.text
    titel = message.text
    days = dialog_manager.dialog_data['day']
    print('days = ', days)
    chas = dialog_manager.dialog_data['hours']
    minuts = dialog_manager.dialog_data['minuts']
    day_list = days.split(',')
    days_ohne_koma = new_days = ''
    for x in range(1, len(day_list), 2):
        new_days += day_list[x] + ', '
        days_ohne_koma += day_list[x]

    real_time_key = days_ohne_koma + chas + minuts  # 301550 - составная часть ключа id scheduler
    # print('real_time_key = ', real_time_key)
    real_time = f'{new_days[:-2]}, {chas}:{minuts}'  # '26, 29, 17:15'
    dialog_manager.dialog_data['job_id'] = real_time_key  # 301550
    dialog_manager.dialog_data['real_time'] = real_time  # '26, 29, 17:15'

    pseudo_class = {'titel': titel, 'foto_id': '', 'za_chas': chas, 'za_sutki': days,
                    'selector': 'M', 'real_time': real_time, 'job_id': real_time_key}
    bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
    b_u_dict = bot_dict[user_id]
    if real_time_key not in b_u_dict:
        bot_dict[user_id][real_time_key] = pseudo_class  # Записываю в словарь бота псевдоманунг
        await dp.storage.update_data(key=bot_storage_key, data=bot_dict)  # Обновляю словарь бота
        await message.answer(text=gut[lan])
    else:
        await message.answer('error 🤷')
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    await dialog_manager.next()

async def on_photo_sent_for_month(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    # Получаем ID фото
    print('on_photo_sent works')
    user_id = str(message.from_user.id)
    lan = await return_lan(message.from_user.id)
    foto_id = message.photo[-1].file_id  # Берем последнее фото (наибольшего размера)
    dialog_manager.dialog_data['titel'] = ''
    dialog_manager.dialog_data['foto_id'] = foto_id
    days = dialog_manager.dialog_data['day']
    chas = dialog_manager.dialog_data['hours']
    minuts = dialog_manager.dialog_data['minuts']

    day_list = days.split(',')
    days_ohne_koma = new_days = ''
    for x in range(1, len(day_list), 2):
        new_days += day_list[x] + ', '
        days_ohne_koma+=day_list[x]

    real_time_key = days_ohne_koma + chas + minuts  # 301550 - составная часть ключа id scheduler
    # print('real_time_key = ', real_time_key)
    dialog_manager.dialog_data['job_id'] = real_time_key
    real_time = f'{new_days[:-2]}, {chas}:{minuts}'  #'26, 29, 17:15'

    dialog_manager.dialog_data['real_time'] = real_time

    pseudo_class = {'titel': '', 'foto_id': foto_id, 'za_chas': chas, 'za_sutki': days,
                    'selector': 'M', 'real_time': real_time, 'job_id': real_time_key}
    bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
    b_u_dict = bot_dict[user_id]
    if real_time_key not in b_u_dict:
        bot_dict[user_id][real_time_key] = pseudo_class  # Записываю в словарь бота pseudoclass
        await dp.storage.update_data(key=bot_storage_key, data=bot_dict)  # Обновляю словарь бота
        await message.answer(text=gut[lan])
    else:
        await message.answer('error 🤷')
    await message.delete()
    await dialog_manager.next()


async def reset_funk_not_for_uniqe(callback: CallbackQuery, widget:Button,
                     dialog_manager: DialogManager, *args, **kwargs):
    print('reset funk not_for_uniqe works')
    # print('dialog_manager.dialog_data = ', dialog_manager.dialog_data)
    dialog_manager.dialog_data.clear()  # Очищаю словарь
    # print('dialog_manager.dialog_data = ', dialog_manager.dialog_data)
    await dialog_manager.start(state=ZAPUSK.add_show, mode=StartMode.RESET_STACK)


async def pre_napominalka(callback: CallbackQuery, widget: Button,
                        dialog_manager: DialogManager):
    print('\n\nWe are into napominalka\n\n')
    us_tz = await return_tz(callback.from_user.id)
    dialog_manager.dialog_data['tz'] = us_tz  # Переливаю значение ТZ в диалоговый словарь
    dialog_dict = dialog_manager.dialog_data
    user_id = callback.from_user.id
    napominalka_sync_for_month(user_id, dialog_dict) # Запуск планировщика
    await dialog_manager.next()
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND













