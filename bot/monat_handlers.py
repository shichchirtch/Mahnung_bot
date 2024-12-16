from aiogram.types import  User
from aiogram_dialog import DialogManager
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Row
from aiogram_dialog.widgets.kbd import Button, Start, Cancel
from lexicon import *
from aiogram_dialog.widgets.input import  MessageInput
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ContentType
from input_handlers import message_not_foto_handler
from week_handlers import WEEK_MAHNUNG
from days_handlers import DAY_MAHNUNG
from regular_callback import (go_to_31, button_day_clicked, pre_napominalka, approve_choise,
                              button_hour_clicked, button_minut_clicked, reset_funk_not_for_uniqe,
                              message_text_handler_for_month, on_photo_sent_for_month, button_zapusk_clicked_for_month)
from postgres_functions import return_lan


class MONAT_MAHNUNG(StatesGroup):
    general = State()
    taily = State()
    napominalka_start = State()
    nach_napom = State()
    hour = State()
    minuten = State()
    get_content = State()
    choose_type = State()

async def get_monat_mahnungen_first_window(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    lan = await return_lan(event_from_user.id)
    getter_data = {'choose_type': choose_type[lan], 'month':month[lan], 'week':week[lan], 'day':day[lan]}
    return getter_data

async def get_30_days(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    lan = await return_lan(event_from_user.id)
    getter_data = {'text_for_day_choose': text_for_day_choose[lan], 'approve_choise':approve_choise_lexicon[lan]}
    return getter_data

async def choosing_data_for_monat_getter(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    lan = await return_lan(event_from_user.id)
    getter_data = {'text_for_2_wind': choose_hours[lan]}
    return getter_data

async def form_mahnung_for_monat_getter(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    lan = await return_lan(event_from_user.id)
    getter_data = {'text_for_3_wind': choose_minuts[lan],  'form_grafik_mahnungen':form_grafik[lan]}
    return getter_data

async def get_titel_for_monat(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    lan = await return_lan(event_from_user.id)
    getter_data = {'data_mahnung': set_titel[lan]}
    return getter_data

async def zapusk_napom(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    lan = await return_lan(event_from_user.id)
    getter_data = {'text_for_napominalka': zapusk_button[lan], 'remind_me':'▶️'}
    return getter_data

async def mahnung_for_monat_accepted(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    lan = await return_lan(event_from_user.id)
    getter_data = {'accepted': accepted_uniq[lan], 'return_to_basic':return_to_basic[lan]}
    return getter_data

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
        Cancel(Const('◀️'),
               id='monat_cancel'),
        Button(text=Format('{approve_choise}'),
               id='approve_choise_button',
               on_click=approve_choise)),
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
            Button(text=Const('05'), id='button_5', on_click=button_hour_clicked), ),
        Row(
            Button(text=Const('06'), id='button_6', on_click=button_hour_clicked),
            Button(text=Const('07'), id='button_7', on_click=button_hour_clicked),
            Button(text=Const('08'), id='button_8', on_click=button_hour_clicked),
            Button(text=Const('09'), id='button_9', on_click=button_hour_clicked),
            Button(text=Const('10'), id='button_10', on_click=button_hour_clicked),
            Button(text=Const('11'), id='button_11', on_click=button_hour_clicked), ),
        Row(
            Button(text=Const('12'), id='button_12', on_click=button_hour_clicked),
            Button(text=Const('13'), id='button_13', on_click=button_hour_clicked),
            Button(text=Const('14'), id='button_14', on_click=button_hour_clicked),
            Button(text=Const('15'), id='button_15', on_click=button_hour_clicked),
            Button(text=Const('16'), id='button_16', on_click=button_hour_clicked),
            Button(text=Const('17'), id='button_17', on_click=button_hour_clicked), ),
        Row(
            Button(text=Const('18'), id='button_18', on_click=button_hour_clicked),
            Button(text=Const('19'), id='button_19', on_click=button_hour_clicked),
            Button(text=Const('20'), id='button_20', on_click=button_hour_clicked),
            Button(text=Const('21'), id='button_21', on_click=button_hour_clicked),
            Button(text=Const('22'), id='button_22', on_click=button_hour_clicked),
            Button(text=Const('23'), id='button_23', on_click=button_hour_clicked)
        ),
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
        Row(
            Button(text=Format('{form_grafik_mahnungen}'), id='zapusk', on_click=button_zapusk_clicked_for_month),
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
        state=MONAT_MAHNUNG.get_content,
        getter=get_titel_for_monat
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






