from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.api.entities.modes import ShowMode, StartMode
from bot_instans import ZAPUSK
from lexicon import *
from scheduler_functions import napominalka_sync_for_month
from aiogram_dialog.widgets.input import MessageInput
from postgres_functions import return_lan, return_tz

async def go_to_regular(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    # print('go_to_regular works')
    dialog_manager.show_mode = ShowMode.SEND
    await dialog_manager.next()


async def go_to_31(callback: CallbackQuery, widget: Button, dialog_manager: DialogManager, *args, **kwargs):
    dialog_manager.dialog_data['capture'] = ''
    dialog_manager.dialog_data['choosing_data'] = ''   # Устанавливаю ключ на случай ошибки
    dialog_manager.show_mode = ShowMode.SEND
    await dialog_manager.next()

async def button_day_clicked(callback: CallbackQuery, widget: Button,
                             dialog_manager: DialogManager):
    lan = await return_lan(callback.from_user.id)
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
            await callback.message.answer(f'{day_dict[callback.data]} {already_in_plan[lan]}')
            t = 1
        else:
            day_group = temp_data + ',' + day_dict[callback.data]
            dialog_manager.dialog_data['day'] = day_group
            t = ''
    else:
        # print('here day net')
        dialog_manager.dialog_data['day'] = day_dict[callback.data]
        # print('dialog_manager.dialog_data = ', dialog_manager.dialog_data)
        t = ''
        dialog_manager.dialog_data['choosing_data'] = 1

    if callback.data != 'button_31':
        temp_sending_data = day_dict[callback.data]
        sending_data = temp_sending_data.split(',')[-1]
    else:
        sending_data = 'last day of month or 31'
    if not t:
        await callback.message.answer(f'{sobytie_sluchitsa[lan]} <b>{sending_data}</b>')


async def approve_choise(callback: CallbackQuery, widget: Button,
                        dialog_manager: DialogManager):
    lan = await return_lan(callback.from_user.id)
    if dialog_manager.dialog_data['choosing_data']:
        dialog_manager.show_mode = ShowMode.EDIT
        await dialog_manager.next()
    else:
        await callback.message.answer(Choose_Day[lan])


async def button_hour_clicked(callback: CallbackQuery, widget: Button,
                             manager: DialogManager):
    # print('button_hour_clicked works')
    uhr_dict = {'button_00': '00', 'button_1': '01', 'button_2': '02', 'button_3': '03',
                'button_4': '04', 'button_5': '05', 'button_6': '06', 'button_7': '07',
                'button_8': '08', 'button_9': '09', 'button_10': '10', 'button_11': '11',
                'button_12': '12', 'button_13': '13', 'button_14': '14', 'button_15': '15',
                'button_16': '16', 'button_17': '17', 'button_18': '18', 'button_19': '19',
                'button_20': '20', 'button_21': '21', 'button_22': '22', 'button_23': '23',
                }
    manager.dialog_data['hours'] = uhr_dict[callback.data]
    manager.dialog_data['minuts'] = '00'
    lan = await return_lan(callback.from_user.id)
    strocka = f'{chas_selekted[lan]}  <b>{uhr_dict[callback.data]}</b>'
    await callback.message.answer(text=strocka)
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
    strocka = f'{real_min_selekted[lan]}  <b>{min_dict[callback.data]}</b>\n\n{knopka_nazata[lan]}'
    await callback.message.answer(text=strocka)

async def button_zapusk_clicked_for_month(callback: CallbackQuery, widget: Button,
                                dialog_manager: DialogManager):
    dialog_manager.show_mode = ShowMode.SEND
    await dialog_manager.next()

async def on_photo_sent_for_month(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    # Получаем ID фото
    foto_id = message.photo[-1].file_id  # Берем последнее фото (наибольшего размера)
    dialog_manager.dialog_data['titel'] = ''
    dialog_manager.dialog_data['foto_id'] = foto_id
    dialog_manager.show_mode = ShowMode.SEND
    await dialog_manager.next()

async def reset_funk_not_for_uniqe(callback: CallbackQuery, widget:Button,
                     dialog_manager: DialogManager, *args, **kwargs):
    # print('dialog_manager.dialog_data = ', dialog_manager.dialog_data)
    dialog_manager.dialog_data.clear()  # Очищаю словарь
    # print('dialog_manager.dialog_data = ', dialog_manager.dialog_data)
    await dialog_manager.start(state=ZAPUSK.add_show, mode=StartMode.RESET_STACK)


async def pre_napominalka(callback: CallbackQuery, widget: Button,
                        dialog_manager: DialogManager):
    # print('\n\nWe are into napominalka\n\n')
    us_tz = await return_tz(callback.from_user.id)
    dialog_manager.dialog_data['tz'] = us_tz  # Переливаю значение ТZ в диалоговый словарь
    dialog_dict = dialog_manager.dialog_data
    user_id = callback.from_user.id
    napominalka_sync_for_month(user_id, dialog_dict) # Запуск планировщика
    await dialog_manager.next()
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND













