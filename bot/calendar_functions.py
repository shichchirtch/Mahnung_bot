from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.api.entities.modes import ShowMode
from datetime import date
from scheduler_functions import scheduler_job, scheduler_za_sutki_job
import datetime
from postgres_functions import insert_timezone
from lexicon import *
from bot_instans import dp, bot_storage_key

async def set_user_tz(callback: CallbackQuery, widget: Button,
                        dialog_manager: DialogManager):
    print('set_user_tz works')
    state = dialog_manager.middleware_data["state"]
    tz_dict = {'tz_minus_3':'Europe/London', 'tz_minus_2':'Europe/Berlin', 'tz_minus_1':'Europe/Kiev',
               'tz_gleich':'Europe/Moscow', 'tz_plus_1':'Europe/Berlin',#'Europe/Samara',
               'tz_plus_2':'Asia/Yekaterinburg', 'tz_plus_3':'Europe/Moscow'}#'Asia/Novosibirsk'}

    await state.update_data(tz=tz_dict[callback.data])
    await insert_timezone(callback.from_user.id, tz_dict[callback.data])
    # dialog_manager.dialog_data['tz']=tz_dict[callback.data]  # Зачем передавать таймзону в креткоживущий словарь ?
    await dialog_manager.next()
    dialog_manager.show_mode = ShowMode.SEND


async def on_date_selected(callback: CallbackQuery, widget,
                           manager: DialogManager, selected_date: date):
    state = manager.middleware_data["state"]
    us_dict = await state.get_data()
    lan = us_dict['lan']
    await callback.message.answer(f"{uniqe_date_selekted[lan]}: {selected_date}")
    print('callback.data = ', callback.data)  # 8CvuU6calendar:173274840
    day_data = int(callback.data.split(':')[1])  # 1732057200
    print('day_data = ', day_data)
    in_stamp = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    current_day = int(in_stamp.timestamp())
    print('cur day = ', current_day)

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
    state = manager.middleware_data["state"]
    us_dict = await state.get_data()
    lan = us_dict['lan']
    if (temp_day + additional_hours) >= current_hour:
        manager.dialog_data['choosing_data'] = True # ставлю индикатор на True для геттера
        manager.dialog_data['hours'] = int(uhr_dict[callback.data])
        manager.dialog_data['minuts'] = 0
        # await callback.message.answer(uhr_dict[callback.data])
        await manager.next()
        # manager.show_mode = ShowMode.SEND
    else:
        manager.dialog_data['choosing_data'] = False
        await callback.message.answer(text=car_time[lan])
        # manager.show_mode = ShowMode.DELETE_AND_SEND
        await manager.done()


async def button_min_clicked(callback: CallbackQuery, widget: Button,
                             dialog_manager: DialogManager):
    min_dict = {'button_00': '0', 'button_05': '300', 'button_10': '600', 'button_15': '900',
                'button_20': '1200', 'button_25': '1500', 'button_30': '1800', 'button_35': '2100',
                'button_40': '2400', 'button_45': '2700', 'button_50': '3000', 'button_55': '3300',
                }
    dialog_manager.dialog_data['minuts'] = int(min_dict[callback.data])
    state = dialog_manager.middleware_data["state"]
    us_dict = await state.get_data()
    lan = us_dict['lan']
    # await state.update_data(shalter=True)
    await callback.message.answer(text=knopka_nazata[lan])



async def button_zapusk_clicked(callback: CallbackQuery, widget: Button,
                                dialog_manager: DialogManager):
    '''Запускает напоминание'''
    in_stamp = datetime.datetime.now().replace(second=0, microsecond=0)
    print('in_stamp = ', in_stamp) # 2024-12-05 19:56:00
    current_minut = int(in_stamp.timestamp())
    # print('current_minut = ', current_minut)  # 1732800900
    real_event_time = dialog_manager.dialog_data['day'] + dialog_manager.dialog_data['hours'] + dialog_manager.dialog_data['minuts']
    # # print('real_event_time = ', real_event_time)  # 1732800900
    # zuruck_zu_time = datetime.datetime.fromtimestamp(real_event_time - 7200)
    # # Форматирование времени в формат MM:HH
    # formatted_time = zuruck_zu_time.strftime("%H:%M")
    # print('когда придёт  за час  = ', formatted_time)  # 20:00 Здесь имеется в виду не событие, а время прихода напоминания

    state = dialog_manager.middleware_data["state"]
    us_dict = await state.get_data()
    lan = us_dict['lan']
    if real_event_time >= current_minut:
        dialog_manager.dialog_data['choosing_data'] = True
        # state = dialog_manager.middleware_data["state"]
        # us_dict = await state.get_data()

        form_vremya = datetime.datetime.fromtimestamp(real_event_time)
        formatted_date = form_vremya.strftime("%d.%m.%Y  %H:%M")
        print('form_vremya = ', formatted_date, type(formatted_date))  # 2024-11-21 15:55:00 <class 'str'>
        dialog_manager.dialog_data['real_time'] = formatted_date

        za_chas = real_event_time - 3600 # 7200#3600
        zuruck_zu_time = datetime.datetime.fromtimestamp(za_chas)
        # Форматирование времени в формат MM:HH
        formatted_time = zuruck_zu_time.strftime("%H:%M")
        print('za_chas = ', formatted_time)

        za_sutki = real_event_time - 86400
        print('za sutki = ', za_sutki)
        zuruck_zu_time_za_sutki = datetime.datetime.fromtimestamp(za_sutki)
        # Форматирование времени в формат MM:HH
        formatted_time = zuruck_zu_time_za_sutki.strftime("%d.%m.%Y %H:%M")
        print('za sutki = ', formatted_time)
        if current_minut + 86400 < real_event_time:
            dialog_manager.dialog_data['za_sutki'] = za_sutki
            dialog_manager.dialog_data['za_chas'] = za_sutki + 82800
        else:
            dialog_manager.dialog_data['za_sutki'] = '' # Если напоминание меньше, чем через сутки - ставлю сутки None
            if real_event_time - 3600 <= current_minut:
                print('##Block if works')
                dialog_manager.dialog_data['za_chas'] = current_minut + 10 # 265
                print('current_minut+10 = ', current_minut+10)

            else:
                print('### esle block')
                dialog_manager.dialog_data['za_chas'] = za_chas

        await state.update_data(us_dict)
        dialog_manager.show_mode = ShowMode.SEND
        await dialog_manager.next()
    else:
        dialog_manager.dialog_data['choosing_data'] = False
        await callback.message.answer(text=car_time[lan])
        # dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await dialog_manager.done()


async def set_titel_name (callback: CallbackQuery, widget: Button,  # Попробовать виджет NEXT
                        manager: DialogManager):
    await manager.next()



async def pre_scheduler(callback: CallbackQuery, widget: Button,
                        dialog_manager: DialogManager):
    print('\n\nWe are into pre_scheduler\n\n')
    user_id = callback.from_user.id
    state = dialog_manager.middleware_data["state"]
    us_dict = await state.get_data()
    # await state.update_data(shalter=True)
    # print('us_dict = ', us_dict)
    # temp_key = us_dict['temp_key']
    dialog_dict = dialog_manager.dialog_data
    # print('176 dialog_dict = ', dialog_dict)
    bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
    # sched_dict = bot_dict[str(callback.from_user.id)][temp_key]  # Получаю словарь события
    tz = us_dict['tz']
    # print('sched_dict = ', sched_dict)
    scheduler_job(user_id, dialog_dict, tz)  # Запуск планировщика
    if dialog_dict['za_sutki']:
        print('185 we are za sutki')
        scheduler_za_sutki_job(user_id, dialog_dict, tz)
    await dialog_manager.next()
    dialog_manager.show_mode = ShowMode.SEND








