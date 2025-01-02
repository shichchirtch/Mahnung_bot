from aiogram.types import User
from aiogram_dialog import DialogManager
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Row
from aiogram_dialog.widgets.kbd import Button, Start, Cancel, Next
from lexicon import *
from aiogram_dialog.widgets.input import  MessageInput
from aiogram.types import ContentType, Message, CallbackQuery
from input_handlers import message_not_foto_handler
from aiogram_dialog.api.entities.modes import ShowMode
from week_handlers import WEEK_MAHNUNG
from days_handlers import DAY_MAHNUNG
from regular_callback import (go_to_31, button_day_clicked, pre_napominalka, approve_choise,
                              button_hour_clicked, button_minut_clicked, reset_funk_not_for_uniqe,
                              on_photo_sent_for_month, button_zapusk_clicked_for_month)
from postgres_functions import return_lan
from bot_instans import dp, bot_storage_key, MONAT_MAHNUNG
from interval_dialog import INTERVAL




async def get_monat_mahnungen_first_window(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    lan = await return_lan(event_from_user.id)
    getter_data = {'choose_type': choose_type[lan], 'month':month[lan], 'week':week[lan], 'day':day[lan]}
    return getter_data

async def get_30_days(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    lan = await return_lan(event_from_user.id)
    getter_data = {'text_for_day_choose': text_for_monat_choose[lan], 'approve_choise':approve_choise_lexicon[lan]}
    return getter_data

async def getter_for_capture_monat(dialog_manager: DialogManager, event_from_user: User,**kwargs):
    lan = await return_lan(event_from_user.id)
    return {'enter_capture':enter_capture[lan]}

async def choosing_data_for_monat_getter(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    lan = await return_lan(event_from_user.id)
    getter_data = {'text_for_2_wind': choose_hours[lan]}
    return getter_data

async def form_mahnung_for_monat_getter(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    lan = await return_lan(event_from_user.id)
    getter_data = {'text_for_3_wind': choose_minuts[lan]}
    return getter_data

async def get_titel_for_monat(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    lan = await return_lan(event_from_user.id)
    getter_data = {'data_mahnung': set_titel[lan]}
    return getter_data

async def get_enter_capture_monat(dialog_manager: DialogManager, event_from_user: User,**kwargs):
    lan = await return_lan(event_from_user.id)
    return {'data_capture':not_text_capture_send[lan]}

async def zapusk_napom(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    lan = await return_lan(event_from_user.id)
    getter_data = {'text_for_napominalka': zapusk_button[lan], 'remind_me':'▶️'}
    return getter_data

async def mahnung_for_monat_accepted(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    lan = await return_lan(event_from_user.id)
    getter_data = {'accepted': accepted_uniq[lan], 'return_to_basic':return_to_basic[lan]}
    return getter_data

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
                    'selector': 'M', 'real_time': real_time, 'capture':'', 'job_id': real_time_key}
    bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
    b_u_dict = bot_dict[user_id]['reg']  # получаю словарь юзера c регулярными напоминаниями
    if real_time_key not in b_u_dict:
        b_u_dict[real_time_key] = pseudo_class  # Записываю в словарь бота ЭК манунг
        await dp.storage.update_data(key=bot_storage_key, data=bot_dict)  # Обновляю словарь бота
        await message.answer(text=gut[lan])
        dialog_manager.show_mode = ShowMode.SEND
        await message.delete()
        await dialog_manager.switch_to(MONAT_MAHNUNG.napominalka_start)
    else:
        await message.answer(error_same_time[lan])
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await dialog_manager.done()


async def set_foto_mahnung_ohne_capture(cb: CallbackQuery, widget: Button, dialog_manager: DialogManager) -> None:
    """Хэндлер формирует словарь с фото без подписи"""
    user_id = str(cb.from_user.id)
    lan = await return_lan(cb.from_user.id)
    dialog_manager.dialog_data['titel'] = ''
    foto_id = dialog_manager.dialog_data['foto_id']
    days = dialog_manager.dialog_data['day']
    chas = dialog_manager.dialog_data['hours']
    minuts = dialog_manager.dialog_data['minuts']

    day_list = days.split(',')
    days_ohne_koma = new_days = ''
    for x in range(1, len(day_list), 2):
        new_days += day_list[x] + ', '
        days_ohne_koma += day_list[x]

    real_time_key = days_ohne_koma + chas + minuts  # 301550 - составная часть ключа id scheduler
    # print('real_time_key = ', real_time_key)
    dialog_manager.dialog_data['job_id'] = real_time_key
    real_time = f'{new_days[:-2]}, {chas}:{minuts}'  # '26, 29, 17:15'

    dialog_manager.dialog_data['real_time'] = real_time

    pseudo_class = {'titel': '', 'foto_id': foto_id, 'za_chas': chas, 'za_sutki': days,
                    'selector': 'M', 'real_time': real_time, 'capture':'','job_id': real_time_key}
    bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
    b_u_dict = bot_dict[user_id]['reg']  # получаю словарь юзера   {'1300': {'titel': 'day tets', 'foto_id': '', 'za_chas': None, 'za_sutki': None, 'selector': 'D', 'real_time': 'Ежеденевно 13 : 00', 'capture': '', 'job_id': '1300'}}
    # print('b_u_dict = ', b_u_dict)
    if real_time_key not in b_u_dict:
        b_u_dict[real_time_key] = pseudo_class  # Записываю в словарь бота ЭК манунг
        await dp.storage.update_data(key=bot_storage_key, data=bot_dict)  # Обновляю словарь бота
        await cb.message.answer(text=gut[lan])
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await cb.message.delete()
        await dialog_manager.switch_to(MONAT_MAHNUNG.napominalka_start)
    else:
        await cb.message.answer(error_same_time[lan])
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await dialog_manager.done()


async def message_capture_handler_monat(message: Message, widget: MessageInput, dialog_manager: DialogManager) -> None:
    """Хэндлер устанавливает capture"""
    user_id = str(message.from_user.id)
    lan = await return_lan(message.from_user.id)
    dialog_manager.dialog_data['titel'] = ''
    foto_id = dialog_manager.dialog_data['foto_id']
    days = dialog_manager.dialog_data['day']
    chas = dialog_manager.dialog_data['hours']
    minuts = dialog_manager.dialog_data['minuts']
    dialog_manager.dialog_data['capture'] = capture = message.text

    day_list = days.split(',')
    days_ohne_koma = new_days = ''
    for x in range(1, len(day_list), 2):
        new_days += day_list[x] + ', '
        days_ohne_koma += day_list[x]

    real_time_key = days_ohne_koma + chas + minuts  # 301550 - составная часть ключа id scheduler
    # print('real_time_key = ', real_time_key)
    dialog_manager.dialog_data['job_id'] = real_time_key
    real_time = f'{new_days[:-2]}, {chas}:{minuts}'  # '26, 29, 17:15'

    dialog_manager.dialog_data['real_time'] = real_time
    pseudo_class = {'titel': '', 'foto_id': foto_id, 'za_chas': chas, 'za_sutki': days,
                    'selector': 'M', 'real_time': real_time, 'capture': capture, 'job_id': real_time_key}
    bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
    b_u_dict = bot_dict[user_id]['reg']  # получаю словарь юзера
    if real_time_key not in b_u_dict:
        b_u_dict[real_time_key] = pseudo_class  # Записываю в словарь бота ЭК манунг
        await dp.storage.update_data(key=bot_storage_key, data=bot_dict)  # Обновляю словарь бота
        await message.answer(text=gut[lan])
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await message.delete()
        await dialog_manager.next()
    else:
        await message.answer(error_same_time[lan])
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await dialog_manager.done()

async def message_not_text_handler_in_capture_monat(message: Message, widget: MessageInput,
        dialog_manager: DialogManager) -> None:
    dialog_manager.show_mode = ShowMode.NO_UPDATE
    lan = await return_lan(message.from_user.id)
    await message.answer(not_text_capture_send[lan])


async def return_to_tage(cb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    del dialog_manager.dialog_data['day']
    dialog_manager.dialog_data['choosing_data'] = ''
    dialog_manager.show_mode = ShowMode.EDIT
    await dialog_manager.back()

async def return_to_hours(cb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    dialog_manager.dialog_data['hours'] = ''
    dialog_manager.show_mode = ShowMode.EDIT
    await dialog_manager.back()


monat_mahnung_dialog = Dialog(
    Window(  # Окно отправляющее клаву из трёх кнопок
        Format('{choose_type}'),
        Button(text=Format('{month}'),
              id='past_button',
              on_click=go_to_31),
        Start(text=Format('{week}'),
              id='zukunft_button',
              state=WEEK_MAHNUNG.choose_weekdays,
              ),
        Start(text=Format('{day}'),
              id='zukunft_day_button',
              state=DAY_MAHNUNG.first,
              ),
        Start(Const('Interval'),
              id='interval_button',
              state=INTERVAL.interval_data_input,
              ),
        Cancel(Const('◀️'),
               id='Cancel_for_regular_block'),
        state=MONAT_MAHNUNG.general,
        getter=get_monat_mahnungen_first_window
    ),

Window(
        Format('{text_for_day_choose}'),
        Row(
            Button(text=Const('1'), id='button_1', on_click=button_day_clicked),
            Button(text=Const('2'), id='button_2', on_click=button_day_clicked),
            Button(text=Const('3'), id='button_3', on_click=button_day_clicked),
            Button(text=Const('4'), id='button_4', on_click=button_day_clicked),
            Button(text=Const('5'), id='button_5', on_click=button_day_clicked),
            Button(text=Const('6'), id='button_6', on_click=button_day_clicked),
            Button(text=Const('7'), id='button_7', on_click=button_day_clicked),),
        Row(
            Button(text=Const('8'), id='button_8', on_click=button_day_clicked),
            Button(text=Const('9'), id='button_9', on_click=button_day_clicked),
            Button(text=Const('10'), id='button_10', on_click=button_day_clicked),
            Button(text=Const('11'), id='button_11', on_click=button_day_clicked),
            Button(text=Const('12'), id='button_12', on_click=button_day_clicked),
            Button(text=Const('13'), id='button_13', on_click=button_day_clicked),
            Button(text=Const('14'), id='button_14', on_click=button_day_clicked),
        ),
        Row(
            Button(text=Const('15'), id='button_15', on_click=button_day_clicked),
            Button(text=Const('16'), id='button_16', on_click=button_day_clicked),
            Button(text=Const('17'), id='button_17', on_click=button_day_clicked),
            Button(text=Const('18'), id='button_18', on_click=button_day_clicked),
            Button(text=Const('19'), id='button_19', on_click=button_day_clicked),
            Button(text=Const('20'), id='button_20', on_click=button_day_clicked),
            Button(text=Const('21'), id='button_21', on_click=button_day_clicked),
        ),
        Row(
            Button(text=Const('22'), id='button_22', on_click=button_day_clicked),
            Button(text=Const('23'), id='button_23', on_click=button_day_clicked),
            Button(text=Const('24'), id='button_24', on_click=button_day_clicked),
            Button(text=Const('25'), id='button_25', on_click=button_day_clicked),
            Button(text=Const('26'), id='button_26', on_click=button_day_clicked),
            Button(text=Const('27'), id='button_27', on_click=button_day_clicked),
            Button(text=Const('28'), id='button_28', on_click=button_day_clicked)
        ),
        Row(
            Button(text=Const('29'), id='button_29', on_click=button_day_clicked),
            Button(text=Const('30'), id='button_30', on_click=button_day_clicked),
            Button(text=Const('31'), id='button_31', on_click=button_day_clicked)
        ),
    Row(
        Cancel(Const('◀️'), id='monat_cancel'),
        Button(text=Format('{approve_choise}'),id='approve_choise_button',on_click=approve_choise)),
        state=MONAT_MAHNUNG.taily,
        getter=get_30_days
    ),

Window(
        Format('{text_for_2_wind}'),
        Row(
            Button(text=Const('00'), id='button_00', on_click=button_hour_clicked),
            Button(text=Const('01'), id='button_1', on_click=button_hour_clicked),
            Button(text=Const('02'), id='button_2', on_click=button_hour_clicked),
            Button(text=Const('03'), id='button_3', on_click=button_hour_clicked),
            Button(text=Const('04'), id='button_4', on_click=button_hour_clicked),
            Button(text=Const('05'), id='button_5', on_click=button_hour_clicked)),
        Row(
            Button(text=Const('06'), id='button_6', on_click=button_hour_clicked),
            Button(text=Const('07'), id='button_7', on_click=button_hour_clicked),
            Button(text=Const('08'), id='button_8', on_click=button_hour_clicked),
            Button(text=Const('09'), id='button_9', on_click=button_hour_clicked),
            Button(text=Const('10'), id='button_10', on_click=button_hour_clicked),
            Button(text=Const('11'), id='button_11', on_click=button_hour_clicked)),
        Row(
            Button(text=Const('12'), id='button_12', on_click=button_hour_clicked),
            Button(text=Const('13'), id='button_13', on_click=button_hour_clicked),
            Button(text=Const('14'), id='button_14', on_click=button_hour_clicked),
            Button(text=Const('15'), id='button_15', on_click=button_hour_clicked),
            Button(text=Const('16'), id='button_16', on_click=button_hour_clicked),
            Button(text=Const('17'), id='button_17', on_click=button_hour_clicked)),
        Row(
            Button(text=Const('18'), id='button_18', on_click=button_hour_clicked),
            Button(text=Const('19'), id='button_19', on_click=button_hour_clicked),
            Button(text=Const('20'), id='button_20', on_click=button_hour_clicked),
            Button(text=Const('21'), id='button_21', on_click=button_hour_clicked),
            Button(text=Const('22'), id='button_22', on_click=button_hour_clicked),
            Button(text=Const('23'), id='button_23', on_click=button_hour_clicked)
        ),
        Button(Const('◀️'),id='back_to_tage',on_click=return_to_tage),
        state=MONAT_MAHNUNG.hour,
        getter=choosing_data_for_monat_getter
    ),

    Window(  # Окно формирует два задания для планировщика
        Format('{text_for_3_wind}'),
        Row(
            Button(text=Const('00'), id='button_00', on_click=button_minut_clicked),
            Button(text=Const('05'), id='button_05', on_click=button_minut_clicked),
            Button(text=Const('10'), id='button_10', on_click=button_minut_clicked),),
        Row(
            Button(text=Const('15'), id='button_15', on_click=button_minut_clicked),
            Button(text=Const('20'), id='button_20', on_click=button_minut_clicked),
            Button(text=Const('25'), id='button_25', on_click=button_minut_clicked), ),
        Row(
            Button(text=Const('30'), id='button_30', on_click=button_minut_clicked),
            Button(text=Const('35'), id='button_35', on_click=button_minut_clicked),
            Button(text=Const('40'), id='button_40', on_click=button_minut_clicked), ),
        Row(
            Button(text=Const('45'), id='button_45', on_click=button_minut_clicked),
            Button(text=Const('50'), id='button_50', on_click=button_minut_clicked),
            Button(text=Const('55'), id='button_55', on_click=button_minut_clicked), ),
        Row(Button(Const('◀️'),
            id='back_to_stunde',
            on_click=return_to_hours),
            Button(text=Const('▶️'), id='zapusk', on_click=button_zapusk_clicked_for_month),
        ),
        state=MONAT_MAHNUNG.minuten,
        getter=form_mahnung_for_monat_getter
    ),

    Window(  # Окно принимающее содержание напоминания и формирующее ЭК Mahnung
        Format(text='{data_mahnung}'),   # отправьте текст
        MessageInput(
            func=message_text_handler_for_month,
            content_types=ContentType.TEXT,
        ),
        MessageInput(
            func=on_photo_sent_for_month,
            content_types=ContentType.PHOTO,
        ),
        MessageInput(
            func=message_not_foto_handler,
            content_types=ContentType.ANY,
        ),
        Cancel(Const('◀️'),
               id='Cancel_for_uniq_day'),
        state=MONAT_MAHNUNG.get_content,
        getter=get_titel_for_monat
    ),

    Window(  # Окно предлагающее ввести капчу
        Format('{enter_capture}'),  # Хотите сделать подпись по фотографией ?
        Cancel(Const('◀️'),
               id='return_to_basic'),
        Row(Next(Const('😃'),
                 id='yes_capture'),
            Button(Const('❌'),
                   id='no_capture',
                   on_click=set_foto_mahnung_ohne_capture)),

        state=MONAT_MAHNUNG.ask_capture,
        getter=getter_for_capture_monat
    ),

    Window(  # Окно принимающее capture
        Format(text='{data_capture}'),  # Отправьте capture
        MessageInput(
            func=message_capture_handler_monat,
            content_types=ContentType.TEXT,
        ),
        MessageInput(
            func=message_not_text_handler_in_capture_monat,
            content_types=ContentType.ANY,
        ),
        Cancel(Const('◀️'),
               id='Cancel_for_uniq_day'),
        state=MONAT_MAHNUNG.accept_capture,
        getter=get_enter_capture_monat
    ),


    Window(  # Окно запускающее шедулер
        Format('{text_for_napominalka}'),  #   ⬇️
        Button(text=Format('{remind_me}'),  #  Запускаем
               id='pre_napominalka_button',
               on_click=pre_napominalka),
        state=MONAT_MAHNUNG.napominalka_start,
        getter=zapusk_napom
    ),

    Window(  # окно возвращаюшее в Корневое окно
        Format(text='{accepted}'),  #  Напоминание принято
        Button(text=Format(text='{return_to_basic}'),
               id='see_stelle_button',
               on_click=reset_funk_not_for_uniqe),
        state=MONAT_MAHNUNG.nach_napom,
        getter=mahnung_for_monat_accepted
    )
)






