from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.api.entities.modes import ShowMode
from datetime import date
from scheduler_functions import scheduler_job, scheduler_za_sutki_job
import datetime
from postgres_functions import insert_timezone, return_lan, return_tz
from lexicon import *
from bot_instans import otvet_chas_dict, real_min_dict


async def set_user_tz(callback: CallbackQuery, widget: Button,
                      dialog_manager: DialogManager):
    print('set_user_tz works')
    print('callbac_data = ', callback.data)
    tz_dict = {'tz_gleich': 'Europe/London',
               'tz_plus_1': 'Europe/Berlin',  # tz_plus_1
               'tz_plus_2': "Europe/Kiev",
               'tz_plus_3': 'Europe/Moscow',
               'tz_plus_4': 'Europe/Samara',
               'tz_plus_5': "Asia/Yekaterinburg",
               'tz_plus_6': 'Asia/Novosibirsk'}
    await insert_timezone(callback.from_user.id, tz_dict[callback.data])
    await dialog_manager.next()
    dialog_manager.show_mode = ShowMode.SEND


async def on_date_selected(callback: CallbackQuery, widget,
                           manager: DialogManager, selected_date: date):
    lan = await return_lan(callback.from_user.id)
    await callback.message.answer(f"{uniqe_date_selekted[lan]}: {selected_date}")
    # print('callback.data = ', callback.data)  # 8CvuU6calendar:173274840
    day_data = int(callback.data.split(':')[1])  # 1732057200
    # print('day_data = ', day_data)
    in_stamp = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    current_day = int(in_stamp.timestamp())
    # print('cur day = ', current_day)

    if current_day <= day_data:
        manager.dialog_data['choosing_data'] = True
        manager.dialog_data['day'] = day_data
        await manager.next()
        manager.show_mode = ShowMode.SEND
    else:
        manager.dialog_data['choosing_data'] = False
        await callback.message.answer(text=car_time[lan])
        manager.show_mode = ShowMode.DELETE_AND_SEND
        await manager.done()


async def button_uhr_clicked(callback: CallbackQuery, widget: Button,
                             manager: DialogManager):
    uhr_dict = {'button_00': '0', 'button_1': '3600', 'button_2': '7200', 'button_3': '10800',
                'button_4': '14400', 'button_5': '18000', 'button_6': '21600', 'button_7': '25200',
                'button_8': '28800', 'button_9': '324000', 'button_10': '36000', 'button_11': '39600',
                'button_12': '43200', 'button_13': '46800', 'button_14': '50400', 'button_15': '54000',
                'button_16': '57600', 'button_17': '61200', 'button_18': '64800', 'button_19': '68400',
                'button_20': '72000', 'button_21': '75600', 'button_22': '79200', 'button_23': '82800',
                }

    in_stamp = datetime.datetime.now().replace(minute=0, second=0, microsecond=0)
    current_hour = int(in_stamp.timestamp())
    # print('cur houres = ', current_hour)
    temp_day = manager.dialog_data['day']
    # print('temp day = ', temp_day, type(temp_day))
    additional_hours = int(uhr_dict[callback.data])
    lan = await return_lan(callback.from_user.id)

    await callback.message.answer(f"{chas_selekted[lan]}: {otvet_chas_dict[callback.data]}")

    if (temp_day + additional_hours) >= current_hour:
        manager.dialog_data['choosing_data'] = True  # ставлю индикатор на True для геттера
        manager.dialog_data['hours'] = int(uhr_dict[callback.data])
        manager.dialog_data['minuts'] = 0
        # await callback.message.answer(uhr_dict[callback.data])
        await manager.next()
        # manager.show_mode = ShowMode.SEND
    else:
        manager.dialog_data['choosing_data'] = False
        await callback.message.answer(text=car_time[lan])
        await manager.done()


async def button_min_clicked(callback: CallbackQuery, widget: Button,
                             dialog_manager: DialogManager):
    min_dict = {'button_00': '0', 'button_05': '300', 'button_10': '600', 'button_15': '900',
                'button_20': '1200', 'button_25': '1500', 'button_30': '1800', 'button_35': '2100',
                'button_40': '2400', 'button_45': '2700', 'button_50': '3000', 'button_55': '3300',
                }
    dialog_manager.dialog_data['minuts'] = int(min_dict[callback.data])
    lan = await return_lan(callback.from_user.id)
    await callback.message.answer(f"{real_min_selekted[lan]}: {real_min_dict[callback.data]}")
    await callback.message.answer(text=knopka_nazata[lan])


async def button_zapusk_clicked(callback: CallbackQuery, widget: Button,
                                dialog_manager: DialogManager):
    '''Запускает напоминание'''
    print('\n\nButton zapusk_clicked work\n\n')

    tz_dict_int = {'Europe/London': 0,
                   'Europe/Berlin': 1,  # tz_plus_1
                   "Europe/Kiev": 2,
                   'Europe/Moscow': 3,
                   'Europe/Samara': 4,
                   "Asia/Yekaterinburg": 5,
                   'Asia/Novosibirsk': 6}

    user_tz = await return_tz(callback.from_user.id)
    user_id = callback.from_user.id
    in_stamp = datetime.datetime.now().replace(second=0, microsecond=0)  # 2024-12-05 19:56:00

    current_minut = int(in_stamp.timestamp())  # 1732800900
    razniza_vo_vremeni = tz_dict_int[user_tz] * 3600

    real_event_time = dialog_manager.dialog_data['day'] + \
                      dialog_manager.dialog_data['hours'] + \
                      dialog_manager.dialog_data['minuts']

    lan = await return_lan(user_id)
    if real_event_time >= current_minut + razniza_vo_vremeni:  #  !!! razniza_vo_vremeni - это по сути и есть таймзона передаваемая в шедулер
        # print('\n\nstr 123')
        dialog_manager.dialog_data['choosing_data'] = True

        form_vremya = datetime.datetime.fromtimestamp(real_event_time)
        formatted_date = form_vremya.strftime("%d.%m.%Y  %H:%M")  # 2024-11-21 15:55:00 <class 'str'>

        dialog_manager.dialog_data['real_time'] = formatted_date

        za_chas = real_event_time - 3600  # Вычитаю час
        zuruck_zu_time = datetime.datetime.fromtimestamp(za_chas)
        # Форматирование времени в формат MM:HH
        formatted_time = zuruck_zu_time.strftime("%H:%M")
        # print('za_chas = ', formatted_time)

        za_sutki = real_event_time - 86400  # Вычитаю сутки
        # print('za sutki = ', za_sutki)
        zuruck_zu_time_za_sutki = datetime.datetime.fromtimestamp(za_sutki)
        # Форматирование времени в формат MM:HH
        formatted_time = zuruck_zu_time_za_sutki.strftime("%d.%m.%Y %H:%M")
        # print('za sutki = ', formatted_time)
        if current_minut + razniza_vo_vremeni + 86400 < real_event_time:
            dialog_manager.dialog_data['za_sutki'] = za_sutki
            dialog_manager.dialog_data['za_chas'] = za_sutki + 82800   # (86400 - 3600)
        else:
            dialog_manager.dialog_data['za_sutki'] = ''  # Если напоминание меньше, чем через сутки - ставлю сутки None
            if real_event_time - (current_minut + razniza_vo_vremeni)<=3600:
                # print('##Block if works')
                dialog_manager.dialog_data['za_chas'] = current_minut + razniza_vo_vremeni + 150  # прибавляю 30 секунд, если напоминанеи меньше чем за час
                # print('current_minut+90 = ', current_minut + 90)

            else:
                # print('### esle block')
                dialog_manager.dialog_data['za_chas'] = za_chas

        dialog_manager.show_mode = ShowMode.SEND
        await dialog_manager.next()
    else:
        dialog_manager.dialog_data['choosing_data'] = False
        await callback.message.answer(text=car_time[lan])
        await dialog_manager.done()


async def set_titel_name(callback: CallbackQuery, widget: Button,  # Попробовать виджет NEXT
                         manager: DialogManager):
    await manager.next()


async def pre_scheduler(callback: CallbackQuery, widget: Button,
                        dialog_manager: DialogManager):
    print('\n\nWe are into pre_scheduler\n\n')
    user_id = callback.from_user.id
    dialog_dict = dialog_manager.dialog_data
    tz = await return_tz(user_id)
    scheduler_job(user_id, dialog_dict, tz)  # Запуск планировщика
    if dialog_dict['za_sutki']:
        scheduler_za_sutki_job(user_id, dialog_dict, tz)
    await dialog_manager.next()
    dialog_manager.show_mode = ShowMode.SEND
