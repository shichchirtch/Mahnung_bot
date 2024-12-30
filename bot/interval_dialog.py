import asyncio
import datetime
import random
from datetime import date
from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import DialogManager
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Row
from aiogram_dialog.widgets.kbd import Button, Cancel, Next, Calendar
from aiogram_dialog.api.entities.modes import ShowMode, StartMode
from bot_instans import dp, bot_storage_key, real_min_dict, ZAPUSK
from lexicon import *
from aiogram_dialog.widgets.input import  MessageInput
from scheduler_functions import interval_sched
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ContentType
from input_handlers import message_not_foto_handler
from postgres_functions import return_tz, return_lan

class INTERVAL(StatesGroup):
    interval_data_input = State()
    enter_start_day = State()
    choose_hour = State()
    choose_minuts = State()
    run_day_scheduler = State()
    ask_capture = State()
    accept_capture = State()
    day_sent_mahnung_data = State()
    day_return_to_basic = State()

async def getter_for_capture_day(dialog_manager: DialogManager, event_from_user: User,**kwargs):
    lan = await return_lan(event_from_user.id)
    return {'enter_capture':enter_capture[lan]}

async def get_enter_capture_day(dialog_manager: DialogManager, event_from_user: User,**kwargs):
    lan = await return_lan(event_from_user.id)
    return {'data_capture':not_text_capture_send[lan]}

async  def get_interval_input_data(dialog_manager: DialogManager, event_from_user: User,**kwargs):
    lan = await return_lan(event_from_user.id)
    return {'interval_data': enter_enterval[lan]}

async def accept_foto_for_day(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    foto_id = message.photo[-1].file_id
    dialog_manager.dialog_data['titel'] = ''
    dialog_manager.dialog_data['foto_id'] = foto_id
    dialog_manager.dialog_data['capture'] = ''
    dialog_manager.show_mode = ShowMode.SEND
    await dialog_manager.next()


async def interval_input(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    lan = await return_lan(message.from_user.id)

    input_data = message.text
    if input_data.isdigit() and 1 < int(input_data) < 366:
        dialog_manager.dialog_data['interval'] = message.text
        dialog_manager.show_mode = ShowMode.SEND
        await asyncio.sleep(0.4)
        await message.answer(interval_set[lan])  # 'Отлино ! Интервал установлен !'
        await dialog_manager.next()
    else:
        await asyncio.sleep(1)
        await message.answer(error_interval[lan])
        dialog_manager.show_mode = ShowMode.NO_UPDATE

async def button_hour_for_interval_clicked(callback: CallbackQuery, widget: Button,
                             dialog_manager: DialogManager, *args, **kwargs):
    uhr_dict = {'button_00': '00', 'button_1': '01', 'button_2': '02', 'button_3': '03',
                'button_4': '04', 'button_5': '05', 'button_6': '06', 'button_7': '07',
                'button_8': '08', 'button_9': '09', 'button_10': '10', 'button_11': '11',
                'button_12': '12', 'button_13': '13', 'button_14': '14', 'button_15': '15',
                'button_16': '16', 'button_17': '17', 'button_18': '18', 'button_19': '19',
                'button_20': '20', 'button_21': '21', 'button_22': '22', 'button_23': '23',
                }
    lan = await return_lan(callback.from_user.id)
    await callback.message.answer(f'{chas_selekted[lan]} <b>{uhr_dict[callback.data]}</b>')
    dialog_manager.dialog_data['hours'] = int(uhr_dict[callback.data]) * 3600
    dialog_manager.dialog_data['minuts'] = 0
    dialog_manager.dialog_data['capture'] = ''
    await dialog_manager.next()


async def days_choosing_hour_getter( dialog_manager: DialogManager, event_from_user: User, *args, **kwargs):
    lan = await return_lan(event_from_user.id)
    text_for_day_1_window = choose_hours
    getter_data = {'go_to_minuts_in_days': go_to_minuts_in_days[lan], 'select_hour': text_for_day_1_window[lan]}
    return getter_data


async def day_get_minuts( dialog_manager: DialogManager, event_from_user: User, *args, **kwargs):
    lan = await return_lan(event_from_user.id)
    text_for_days_2_window = vibor_minut
    getter_data = {'text_for_2_day_wind': text_for_days_2_window[lan]}
    return getter_data

async def day_button_minut_clicked(callback: CallbackQuery, widget: Button,
                                    dialog_manager: DialogManager, *args, **kwargs):
        min_dict = {'button_00': 0, 'button_05': 300, 'button_10': 600, 'button_15': 900,
                    'button_20': 1200, 'button_25': 1500, 'button_30': 1800, 'button_35': 2100,
                    'button_40': 2400, 'button_45': 2700, 'button_50': 3000, 'button_55': 3300
                    }
        dialog_manager.dialog_data['minuts'] = min_dict[callback.data]
        lan = await return_lan(callback.from_user.id)
        strocka = f'{real_min_selekted[lan]}  <b>{real_min_dict[callback.data]}</b>\n\n{knopka_nazata[lan]}'
        await callback.message.answer(text=strocka)


async def button_zapusk_clicked_for_interval(callback: CallbackQuery, widget: Button,
                                    dialog_manager: DialogManager, *args, **kwargs):
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
    current_minut = int(in_stamp.timestamp())  # 1732800900
    razniza_vo_vremeni = tz_dict_int[user_tz] * 3600
    random_add_sec = random.randint(1, 20)
    real_event_time = dialog_manager.dialog_data['day'] + \
                      dialog_manager.dialog_data['hours'] + \
                      dialog_manager.dialog_data['minuts'] + random_add_sec

    lan = await return_lan(user_id)
    if real_event_time >= current_minut + razniza_vo_vremeni:
        dialog_manager.dialog_data['job_id'] = real_event_time
        form_vremya = datetime.datetime.fromtimestamp(real_event_time)  # 2024-12-29 12:00:00  <class 'datetime.datetime'>>
        dialog_manager.dialog_data['start_time'] = str(form_vremya)
        formatted_date = form_vremya.strftime("%d.%m.%Y  %H:%M")  # 2024-11-21 15:55:00 <class 'str'>
        print('\n\nSOBITIE = ', formatted_date, '\n\n')  # 20.12.2024  18:30
        await callback.message.answer(f'✅ Event <b>{formatted_date}</b>')
        dialog_manager.dialog_data['zagolovok'] = formatted_date  # Здесь записывается заголовок напоминания  16.12.2024  15:55
        dialog_manager.show_mode = ShowMode.SEND
        await dialog_manager.next()
    else:
        await callback.message.answer(text=car_time[lan])
        dialog_manager.show_mode = ShowMode.SEND
        await dialog_manager.done()

async def message_text_handler_for_interval(message: Message, widget: MessageInput,
                                        dialog_manager: DialogManager, *args, **kwargs) -> None:
    user_id = str(message.from_user.id)
    lan = await return_lan(message.from_user.id)
    dialog_manager.dialog_data['titel'] = message.text
    titel = message.text
    job_id = dialog_manager.dialog_data['job_id']
    real_time = dialog_manager.dialog_data['zagolovok']  # 20.12.2024  18:30
    my_interval = dialog_manager.dialog_data['interval']
    pseudo_class = {'titel': titel, 'foto_id': '',  'my_interval':my_interval,
                    'selector': 'I', 'real_time': real_time, 'capture':'','job_id': job_id}
    bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
    b_u_dict = bot_dict[user_id]['reg']  # получаю словарь юзера
    if job_id not in b_u_dict:  # Если такого времени еще не забухено
        b_u_dict[job_id] = pseudo_class  # Записываю в словарь бота ЭК манунг
        await dp.storage.update_data(key=bot_storage_key, data=bot_dict)  # Обновляю словарь бота
        await message.answer(text=gut[lan])
        dialog_manager.show_mode = ShowMode.SEND
        await message.delete()
        await dialog_manager.switch_to(INTERVAL.run_day_scheduler)
    else:
        await message.answer(error_same_time[lan])
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await dialog_manager.done()


async def form_mahnung_ohne_capture_interval(cb: CallbackQuery, widget:
                                Button, dialog_manager: DialogManager, *args, **kwargs):
    user_id = str(cb.from_user.id)
    lan = await return_lan(cb.from_user.id)
    job_id = dialog_manager.dialog_data['job_id']
    foto_id = dialog_manager.dialog_data['foto_id']
    real_time = dialog_manager.dialog_data['zagolovok']  # 20.12.2024  18:30
    my_interval = dialog_manager.dialog_data['interval']
    pseudo_class = {'titel': '', 'foto_id': foto_id,  'my_interval':my_interval,
                    'selector': 'I', 'real_time': real_time, 'capture': '', 'job_id': job_id}
    bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
    b_u_dict = bot_dict[user_id]['reg']  # получаю словарь юзера
    if job_id not in b_u_dict:  # Если такого времени еще не забухено
        b_u_dict[job_id] = pseudo_class  # Записываю в словарь бота ЭК манунг
        await dp.storage.update_data(key=bot_storage_key, data=bot_dict)  # Обновляю словарь бота
        await cb.message.answer(text=gut[lan])
        dialog_manager.show_mode = ShowMode.SEND
        await cb.message.delete()
        await dialog_manager.switch_to(INTERVAL.run_day_scheduler)
    else:
        await cb.message.answer(error_same_time[lan])
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await dialog_manager.done()


async def set_capture_interval(message: Message, widget:
                                MessageInput, dialog_manager: DialogManager, *args, **kwargs):
    user_id = str(message.from_user.id)
    lan = await return_lan(message.from_user.id)
    dialog_manager.dialog_data['capture'] = message.text
    foto_id = dialog_manager.dialog_data['foto_id']
    job_id = dialog_manager.dialog_data['job_id']
    real_time = dialog_manager.dialog_data['zagolovok']  # 20.12.2024  18:30
    my_interval = dialog_manager.dialog_data['interval']
    pseudo_class = {'titel': '', 'foto_id': foto_id, 'my_interval':my_interval,
                    'selector': 'I', 'real_time': real_time, 'capture': message.text, 'job_id': job_id}
    bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
    b_u_dict = bot_dict[user_id]['reg']  # получаю словарь юзера
    if job_id not in b_u_dict:  # Если такого времени еще не забухено
        b_u_dict[job_id] = pseudo_class  # Записываю в словарь бота ЭК манунг
        await dp.storage.update_data(key=bot_storage_key, data=bot_dict)  # Обновляю словарь бота
        await message.answer(text=gut[lan])
        dialog_manager.show_mode = ShowMode.SEND
        await message.delete()
        await dialog_manager.switch_to(INTERVAL.run_day_scheduler)
    else:
        await message.answer(error_same_time[lan])
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await dialog_manager.done()


async def day_get_for_input_data(dialog_manager: DialogManager,
                                  event_from_user: User, *args, **kwargs):
    lan  = await return_lan(event_from_user.id)
    getter_data = {'day_data_mahnung': set_titel[lan]}
    return getter_data

async def pre_interval_sched(callback: CallbackQuery, widget: Button,
                        dialog_manager: DialogManager):
    tz = await return_tz(callback.from_user.id)
    dialog_dict = dialog_manager.dialog_data
    user_id = callback.from_user.id
    interval_sched(user_id, dialog_dict, tz) # Запуск планировщика
    await dialog_manager.next()
    dialog_manager.show_mode = ShowMode.SEND

async def day_get_runner(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    lan = await return_lan(event_from_user.id)
    getter_data = {'text_for_day_sched': text_for_day[lan], 'day_remind_me':'▶️'}
    return getter_data


async def day_reset_funk_not_for_interval(callback: CallbackQuery, widget:Button,
                     dialog_manager: DialogManager, *args, **kwargs):
    print('reset funk day not_for_uniqe works')
    dialog_manager.dialog_data.clear() # Очищаю словарь
    await dialog_manager.start(state=ZAPUSK.add_show, mode=StartMode.RESET_STACK)

async def day_return_getter(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    lan = await return_lan(event_from_user.id)
    getter_data = {'day_accepted': accepted_uniq[lan], 'day_return_to_basic':return_to_basic[lan]}
    return getter_data

async def message_not_text_handler_in_capture_day(message: Message, widget: MessageInput,
        dialog_manager: DialogManager) -> None:
    dialog_manager.show_mode = ShowMode.NO_UPDATE
    lan = await return_lan(message.from_user.id)
    await message.answer(not_text_capture_send[lan])

async def interval_error_handler(message: Message, widget: MessageInput,
        dialog_manager: DialogManager) -> None:
    dialog_manager.show_mode = ShowMode.NO_UPDATE
    lan = await return_lan(message.from_user.id)
    await message.answer(enter_enterval[lan])

async def on_date_for_interval_selected(callback: CallbackQuery, widget,
                           manager: DialogManager, selected_date: date):
    lan = await return_lan(callback.from_user.id)
    await callback.message.answer(f"{uniqe_date_selekted[lan]}: {selected_date}")
    # print('callback.data = ', callback.data)  # 8CvuU6calendar:173274840
    day_data = int(callback.data.split(':')[1])  # 1732057200
    # print('\n\nday_data = ', datetime.datetime.fromtimestamp(day_data))  #  day_data =  2024-12-16 00:00:00
    in_stamp = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)  # day_data =  2024-12-16 00:00:00
    # print('NOW = ', in_stamp)  🧐 Тут возможно вылезет ошибка, потому что нет таймзоны
    current_day = int(in_stamp.timestamp())

    if current_day <= day_data:
        manager.dialog_data['day'] = int(day_data)
        await manager.next()
        manager.show_mode = ShowMode.SEND
    else:
        await callback.message.answer(text=car_time[lan])
        manager.show_mode = ShowMode.DELETE_AND_SEND
        await manager.done()

async def  select_day_for_interval_start(dialog_manager: DialogManager, event_from_user: User,**kwargs):
    lan = await return_lan(event_from_user.id)
    return {'select_data':selected_data[lan]}


async def return_to_calender(cb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data['hours'] = ''
    dialog_manager.show_mode = ShowMode.EDIT
    await dialog_manager.back()

async def return_to_set_hours(cb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data['minuts'] = ''
    dialog_manager.show_mode = ShowMode.EDIT
    await dialog_manager.back()


###############################################################################################################



interval_mahnung_dialog = Dialog(
    Window(  # Окно принимаюшее дни от 2 до 365
        Format(text='{interval_data}'),  # Введите количество дней (от 2 до 365), через которое будет повторяться событие
        MessageInput(
            func=interval_input,
            content_types=ContentType.TEXT
        ),
        MessageInput(
            func=interval_error_handler,
            content_types=ContentType.ANY
        ),
        Cancel(Const('◀️'),
               id='Cancel_interval'),
        state=INTERVAL.interval_data_input,
        getter=get_interval_input_data
    ),

    Window( # В этом окне юзер выбирает день начала события
        Format('{select_data}'),
        Calendar(id='calendar',
                 on_click=on_date_for_interval_selected),
        Cancel(Const('◀️'),
            id='cancel_interval'),
        state=INTERVAL.enter_start_day,
        getter=select_day_for_interval_start
    ),

    Window(  # Окно отправляющее клаву из часов
        Format('{select_hour}'),
        Row(
            Button(text=Const('00'), id='button_00', on_click=button_hour_for_interval_clicked),
            Button(text=Const('01'), id='button_1', on_click=button_hour_for_interval_clicked),
            Button(text=Const('02'), id='button_2', on_click=button_hour_for_interval_clicked),
            Button(text=Const('03'), id='button_3', on_click=button_hour_for_interval_clicked),
            Button(text=Const('04'), id='button_4', on_click=button_hour_for_interval_clicked),
            Button(text=Const('05'), id='button_5', on_click=button_hour_for_interval_clicked)),
        Row(
            Button(text=Const('06'), id='button_6', on_click=button_hour_for_interval_clicked),
            Button(text=Const('07'), id='button_7', on_click=button_hour_for_interval_clicked),
            Button(text=Const('08'), id='button_8', on_click=button_hour_for_interval_clicked),
            Button(text=Const('09'), id='button_9', on_click=button_hour_for_interval_clicked),
            Button(text=Const('10'), id='button_10', on_click=button_hour_for_interval_clicked),
            Button(text=Const('11'), id='button_11', on_click=button_hour_for_interval_clicked)),
        Row(
            Button(text=Const('12'), id='button_12', on_click=button_hour_for_interval_clicked),
            Button(text=Const('13'), id='button_13', on_click=button_hour_for_interval_clicked),
            Button(text=Const('14'), id='button_14', on_click=button_hour_for_interval_clicked),
            Button(text=Const('15'), id='button_15', on_click=button_hour_for_interval_clicked),
            Button(text=Const('16'), id='button_16', on_click=button_hour_for_interval_clicked),
            Button(text=Const('17'), id='button_17', on_click=button_hour_for_interval_clicked)),
        Row(
            Button(text=Const('18'), id='button_18', on_click=button_hour_for_interval_clicked),
            Button(text=Const('19'), id='button_19', on_click=button_hour_for_interval_clicked),
            Button(text=Const('20'), id='button_20', on_click=button_hour_for_interval_clicked),
            Button(text=Const('21'), id='button_21', on_click=button_hour_for_interval_clicked),
            Button(text=Const('22'), id='button_22', on_click=button_hour_for_interval_clicked),
            Button(text=Const('23'), id='button_23', on_click=button_hour_for_interval_clicked)
            ),
            Button(Const('◀️'),id='day_cancel',on_click=return_to_calender),
        state=INTERVAL.choose_hour,
        getter=days_choosing_hour_getter),

    Window(  # Окно формирует задание для планировщика
        Format('{text_for_2_day_wind}'),
        Row(
            Button(text=Const('00'), id='button_00', on_click=day_button_minut_clicked),
            Button(text=Const('05'), id='button_05', on_click=day_button_minut_clicked),
            Button(text=Const('10'), id='button_10', on_click=day_button_minut_clicked),),
        Row(
            Button(text=Const('15'), id='button_15', on_click=day_button_minut_clicked),
            Button(text=Const('20'), id='button_20', on_click=day_button_minut_clicked),
            Button(text=Const('25'), id='button_25', on_click=day_button_minut_clicked), ),
        Row(
            Button(text=Const('30'), id='button_30', on_click=day_button_minut_clicked),
            Button(text=Const('35'), id='button_35', on_click=day_button_minut_clicked),
            Button(text=Const('40'), id='button_40', on_click=day_button_minut_clicked), ),
        Row(
            Button(text=Const('45'), id='button_45', on_click=day_button_minut_clicked),
            Button(text=Const('50'), id='button_50', on_click=day_button_minut_clicked),
            Button(text=Const('55'), id='button_55', on_click=day_button_minut_clicked), ),
        Row(Button(text=Const('◀️'), id='minuts_back', on_click=return_to_set_hours),
            Button(text=Const('▶️'), id='day_zapusk', on_click=button_zapusk_clicked_for_interval),
        ),
        state=INTERVAL.choose_minuts,
        getter=day_get_minuts
    ),

    Window(  # Окно принимающее содержание напоминания и формирующее ЭК Mahnung
        Format(text='{day_data_mahnung}'),
        MessageInput(
            func=message_text_handler_for_interval,
            content_types=ContentType.TEXT,
        ),
        MessageInput(
            func=accept_foto_for_day,
            content_types=ContentType.PHOTO,
        ),
        MessageInput(
            func=message_not_foto_handler,
            content_types=ContentType.ANY,
        ),
        Cancel(Const('◀️'),
               id='Cancel_for_uniq_day'),
        state=INTERVAL.day_sent_mahnung_data,
        getter=day_get_for_input_data # Из input_getter
    ),

    Window(  # Окно предлагающее ввести капчу
        Format('{enter_capture}'),  # Хотите сделать подпись по фотографией ?
        Cancel(Const('◀️'),
               id='return_to_basic'),
        Row(Next(Const('😃'),
                 id='yes_capture'),
            Button(Const('❌'),
                   id='no_capture',
                   on_click=form_mahnung_ohne_capture_interval)),

        state=INTERVAL.ask_capture,
        getter=getter_for_capture_day
    ),

    Window(  # Окно принимающее capture
        Format(text='{data_capture}'),  # Отправьте capture
        MessageInput(
            func=set_capture_interval,
            content_types=ContentType.TEXT,
        ),
        MessageInput(
            func=message_not_text_handler_in_capture_day,
            content_types=ContentType.ANY,
        ),
        Cancel(Const('◀️'),
               id='Cancel_for_interval'),
        state=INTERVAL.accept_capture,
        getter=get_enter_capture_day
    ),

    Window(  # Окно запускающее шедулер
        Format('{text_for_day_sched}'),
        Button(text=Format('{day_remind_me}'),
               id='pre_day_sched_button',
               on_click=pre_interval_sched),
        state=INTERVAL.run_day_scheduler,
        getter=day_get_runner
    ),

    Window(  # окно возвращаюшее в Корневое окно
        Format(text='{day_accepted}'),
        Button(text=Format(text='{day_return_to_basic}'),
               id='day_see_stelle_button',
               on_click=day_reset_funk_not_for_interval),
        state=INTERVAL.day_return_to_basic,
        getter=day_return_getter
    )
)