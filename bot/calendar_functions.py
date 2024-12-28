from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.api.entities.modes import ShowMode
from datetime import date
from scheduler_functions import scheduler_job, scheduler_za_sutki_job
import datetime
from postgres_functions import insert_timezone, return_lan, return_tz
from lexicon import *
from bot_instans import tz_dict, real_min_dict


async def set_user_tz(callback: CallbackQuery, widget: Button,
                      dialog_manager: DialogManager):
    # print('set_user_tz works')
    # print('callbac_data = ', callback.data)
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
    # print('\n\nday_data = ', datetime.datetime.fromtimestamp(day_data))  #  day_data =  2024-12-16 00:00:00
    in_stamp = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)  # day_data =  2024-12-16 00:00:00
    # print('NOW = ', in_stamp)
    current_day = int(in_stamp.timestamp())
    # print('cur day = ', current_day)

    if current_day <= day_data:
        manager.dialog_data['choosing_data'] = True
        manager.dialog_data['day'] = day_data
        temp_ditc = manager.dialog_data
        # print('\n\nmanager.dialog_data = ', temp_ditc)
        await manager.next()
        manager.show_mode = ShowMode.SEND
    else:
        manager.dialog_data['choosing_data'] = False
        await callback.message.answer(text=car_time[lan])
        manager.show_mode = ShowMode.DELETE_AND_SEND
        await manager.done()


async def button_uhr_clicked(callback: CallbackQuery, widget: Button,
                             manager: DialogManager):
    uhr_dict = {'ubutton_00': '0', 'ubutton_1': '3600', 'ubutton_2': '7200', 'ubutton_3': '10800',
                'ubutton_4': '14400', 'ubutton_5': '18000', 'ubutton_6': '21600', 'ubutton_7': '25200',
                'ubutton_8': '28800', 'ubutton_9': '32400', 'ubutton_10': '36000', 'ubutton_11': '39600',
                'ubutton_12': '43200', 'ubutton_13': '46800', 'ubutton_14': '50400', 'ubutton_15': '54000',
                'ubutton_16': '57600', 'ubutton_17': '61200', 'ubutton_18': '64800', 'ubutton_19': '68400',
                'ubutton_20': '72000', 'ubutton_21': '75600', 'ubutton_22': '79200', 'ubutton_23': '82800',
                }
    otvet_chas_dict_uniq = {'ubutton_00': '00', 'ubutton_1': '01', 'ubutton_2': '02', 'ubutton_3': '03',
                       'ubutton_4': '04', 'ubutton_5': '05', 'ubutton_6': '06', 'ubutton_7': '07',
                       'ubutton_8': '08', 'ubutton_9': '09', 'ubutton_10': '10', 'ubutton_11': '11',
                       'ubutton_12': '12', 'ubutton_13': '13', 'ubutton_14': '14', 'ubutton_15': '15',
                       'ubutton_16': '16', 'ubutton_17': '17', 'ubutton_18': '18', 'ubutton_19': '19',
                       'ubutton_20': '20', 'ubutton_21': '21', 'ubutton_22': '22', 'ubutton_23': '23'}
    in_stamp = datetime.datetime.now().replace(minute=0, second=0, microsecond=0)
    current_hour = int(in_stamp.timestamp())
    # print('cur houres = ', current_hour)
    # print('\n\nim choosing hours dict = ', manager.dialog_data)
    temp_day = manager.dialog_data['day']
    # print('temp day = ', temp_day, type(temp_day))
    additional_hours = int(uhr_dict[callback.data])
    lan = await return_lan(callback.from_user.id)
    tz = await return_tz(callback.from_user.id)
    # print('tz = ', tz_dict[tz])
    await callback.message.answer(f"{chas_selekted[lan]}: <b>{otvet_chas_dict_uniq[callback.data]}</b>")
    day_plus_hours = temp_day + additional_hours - tz_dict[tz]
    # print('day_plus = ', f'{day_plus_hours - current_hour}')
    if day_plus_hours >= current_hour:
        manager.dialog_data['choosing_data'] = True  # ставлю индикатор на True для геттера
        manager.dialog_data['hours'] = int(uhr_dict[callback.data])
        manager.dialog_data['minuts'] = 0
        # print("manager.dialog_data['hours'] = ", manager.dialog_data['hours'])
        # await callback.message.answer(uhr_dict[callback.data])
        await manager.next()
        manager.show_mode = ShowMode.EDIT
    else:
        manager.dialog_data['choosing_data'] = False
        await callback.message.answer(text=car_time[lan])
        manager.show_mode = ShowMode.SEND
        await manager.done()


async def button_min_clicked(callback: CallbackQuery, widget: Button,
                             dialog_manager: DialogManager):
    min_dict = {'button_00': '0', 'button_05': '300', 'button_10': '600', 'button_15': '900',
                'button_20': '1200', 'button_25': '1500', 'button_30': '1800', 'button_35': '2100',
                'button_40': '2400', 'button_45': '2700', 'button_50': '3000', 'button_55': '3300',
                }
    dialog_manager.dialog_data['minuts'] = int(min_dict[callback.data])
    # print("dialog_manager.dialog_data['minuts'] = ", dialog_manager.dialog_data['minuts'])
    lan = await return_lan(callback.from_user.id)
    await callback.message.answer(f"{real_min_selekted[lan]}: <b>{real_min_dict[callback.data]}</b>\n\n{knopka_nazata[lan]}")



async def button_zapusk_clicked(callback: CallbackQuery, widget: Button,
                                dialog_manager: DialogManager):
    '''Формирует время'''

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
    # null_day = str(dialog_manager.dialog_data['day'])  # Для кастомного календаря
    # dialog_manager.dialog_data['time_code'] = null_day
    current_minut = int(in_stamp.timestamp())  # 1732800900
    razniza_vo_vremeni = tz_dict_int[user_tz] * 3600
    # print('temp_dict = ',dialog_manager.dialog_data)
    real_event_time = dialog_manager.dialog_data['day'] + \
                      dialog_manager.dialog_data['hours'] + \
                      dialog_manager.dialog_data['minuts']

    lan = await return_lan(user_id)
    if real_event_time >= current_minut + razniza_vo_vremeni:  #  !!! razniza_vo_vremeni - это по сути и есть таймзона передаваемая в шедулер
        dialog_manager.dialog_data['choosing_data'] = True

        form_vremya = datetime.datetime.fromtimestamp(real_event_time)
        formatted_date = form_vremya.strftime("%d.%m.%Y  %H:%M")  # 2024-11-21 15:55:00 <class 'str'>
        # print('\n\nSOBITIE = ', formatted_date, '\n\n' )  # 20.12.2024  18:30
        await callback.message.answer(f'✅ <b>Event {formatted_date}</b>')
        dialog_manager.dialog_data['real_time'] = formatted_date  # Здесь записывается заголовок напоминания  16.12.2024  15:55

        za_chas = real_event_time - 3600  # Вычитаю час
        za_sutki = real_event_time - 86400  # Вычитаю сутки

        if current_minut + razniza_vo_vremeni + 86400 < real_event_time:
            dialog_manager.dialog_data['za_sutki'] = za_sutki
            dialog_manager.dialog_data['za_chas'] = za_sutki + 82800   # (86400 - 3600)
        else:
            dialog_manager.dialog_data['za_sutki'] = ''  # Если напоминание меньше, чем через сутки - ставлю сутки None
            if real_event_time - (current_minut + razniza_vo_vremeni) <= 3600:
                dialog_manager.dialog_data['za_chas'] = current_minut + razniza_vo_vremeni + 65  # прибавляю 65 секунд, если напоминанеи меньше чем за час
            else:
                dialog_manager.dialog_data['za_chas'] = za_chas

        dialog_manager.show_mode = ShowMode.EDIT
        await dialog_manager.next()
    else:
        dialog_manager.dialog_data['choosing_data'] = False
        await callback.message.answer(text=car_time[lan])
        dialog_manager.show_mode = ShowMode.SEND
        await dialog_manager.done()


async def set_titel_name(callback: CallbackQuery, widget: Button,  # Попробовать виджет NEXT
                         manager: DialogManager):
    await manager.next()


async def pre_scheduler(callback: CallbackQuery, widget: Button,
                        dialog_manager: DialogManager):
    # print('\n\nWe are into pre_scheduler\n\n')
    user_id = callback.from_user.id
    dialog_dict = dialog_manager.dialog_data
    tz = await return_tz(user_id)
    try:
        scheduler_job(user_id, dialog_dict, tz)  # Запуск планировщика
        if dialog_dict['za_sutki']:
            scheduler_za_sutki_job(user_id, dialog_dict, tz)
    except Exception as e: #ConflictingIdError:
        print('\n\n',f'183 {e}')
    await dialog_manager.next()
    dialog_manager.show_mode = ShowMode.SEND
