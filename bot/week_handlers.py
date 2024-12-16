from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import DialogManager
from aiogram_dialog import Dialog, Window
import operator
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Row,  Column, Cancel
from aiogram_dialog.widgets.kbd import Button, ManagedMultiselect, Multiselect
from aiogram_dialog.api.entities.modes import ShowMode, StartMode
from bot_instans import dp, bot_storage_key,  ZAPUSK
from lexicon import *
from aiogram_dialog.widgets.input import  MessageInput
from dialog_functions import week_day_bearbeiten
from scheduler_functions import week_sched
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ContentType
from input_handlers import message_not_foto_handler
from postgres_functions import return_tz, return_lan


class WEEK_MAHNUNG(StatesGroup):
    choose_weekdays = State()
    choose_hour = State()
    choose_min = State()
    sent_mahnung_data = State()
    run_scheduler = State()
    week_return_to_basic = State()

async def get_weekdays(dialog_manager: DialogManager, event_from_user: User, *args, **kwargs):
    lan = await return_lan(event_from_user.id)
    monday = {'ru':'Понедельник', 'en':'Monday'}
    tuesday = {'ru':'Вторник', 'en':'Tuesday'}
    wensday = {'ru':'Среда', 'en':'Wednesday'}
    thursday = {'ru':'Четверг', 'en':'Thursday'}
    friday = {'ru':'Пятница', 'en':'Friday'}
    saturday = {'ru':'Суббота', 'en':'Saturday'}
    sunday = {'ru':'Воскресенье', 'en':'Sunday'}
    day_of_week = [
        (f"{monday[lan]}", '0'),
        (f"{tuesday[lan]}", '1'),
        (f"{wensday[lan]}", '2'),
        (f"{thursday[lan]}", '3'),
        (f"{friday[lan]}", '4'),
        (f"{saturday[lan]}", '5'),
        (f"{sunday[lan]}", '6'),
    ]
    return {"wd": day_of_week, 'choose_week_day':choose_weekday[lan], 'approve':approve_choise_lexicon[lan]}

async def category_filled(callback: CallbackQuery, checkbox: ManagedMultiselect, dialog_manager: DialogManager, *args,
                          **kwargs):
    '''Функция формирует список с днями недели'''
    choose = checkbox.get_checked()
    # print('choose = ', choose)  # choose =  ['mon']
    dialog_manager.dialog_data['week_days'] = choose


async def on_confirm_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, *args, **kwargs):
    lan = await return_lan(callback.from_user.id)
    dialog_manager.dialog_data['lan'] = lan # Завожу язык в манаджер
    select_at_least_one ={ 'ru':"Выберите хотя бы один день", 'en':'Select please at least one',
                           'fa': 'لطفاً حداقل یکی را انتخاب کنید', 'ar':'يرجى تحديد واحد على الأقل',
                           'de': 'Bitte wählen Sie mindestens eines aus', 'uk': 'Виберіть, будь ласка, принаймні один',
                           'tr': 'Lütfen en az birini seçin'}
    selected_days = dialog_manager.dialog_data.get('week_days', [])
    if selected_days:
        await dialog_manager.next()  # Переход к следующему окну
    else:
        await callback.message.answer(select_at_least_one[lan], show_alert=True)

async def button_hour_for_week_clicked(callback: CallbackQuery, widget: Button,
                             dialog_manager: DialogManager, *args, **kwargs):
    uhr_dict = {'button_00': '00', 'button_1': '01', 'button_2': '02', 'button_3': '03',
                'button_4': '04', 'button_5': '05', 'button_6': '06', 'button_7': '07',
                'button_8': '08', 'button_9': '09', 'button_10': '10', 'button_11': '11',
                'button_12': '12', 'button_13': '13', 'button_14': '14', 'button_15': '15',
                'button_16': '16', 'button_17': '17', 'button_18': '18', 'button_19': '19',
                'button_20': '20', 'button_21': '21', 'button_22': '22', 'button_23': '23',
                }
    hour_mahnung = uhr_dict[callback.data]
    dialog_manager.dialog_data['hours'] = hour_mahnung
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    await dialog_manager.next()

async def week_choosing_hour_getter(
                             dialog_manager: DialogManager, event_from_user: User,*args, **kwargs):
    lan = await return_lan(event_from_user.id)
    text_for_week_2_window = choose_hours
    getter_data = {'text_for_week_wind': text_for_week_2_window[lan], 'remind_me': zapusk_button[lan]}
    return getter_data


async def week_get_minuts( dialog_manager: DialogManager,event_from_user: User, *args, **kwargs):
    lan = await return_lan(event_from_user.id)
    text_for_week_3_window = vibor_minut
    getter_data = {'text_for_3_week_wind': text_for_week_3_window[lan], 'form_grafik_week_mahnungen':form_grafik[lan]}
    return getter_data

async def week_button_minut_clicked(callback: CallbackQuery, widget: Button,
                                    dialog_manager: DialogManager, *args, **kwargs):
        min_dict = {'button_00': '00', 'button_05': '05', 'button_10': '10', 'button_15': '15',
                    'button_20': '20', 'button_25': '25', 'button_30': '30', 'button_35': '35',
                    'button_40': '40', 'button_45': '45', 'button_50': '50', 'button_55': '55'
                    }
        dialog_manager.dialog_data['minuts'] = min_dict[callback.data]
        lan = await return_lan(callback.from_user.id)
        await callback.message.answer(text=knopka_nazata[lan])

async def button_zapusk_clicked_for_week(callback: CallbackQuery, widget: Button,
                                    dialog_manager: DialogManager, *args, **kwargs):
    lan = await return_lan(callback.from_user.id)
    dialog_manager.dialog_data['tz'] = await return_tz(callback.from_user.id)
    text_for_week_3 = vibor_minut
    if 'minuts' in dialog_manager.dialog_data:
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await dialog_manager.next()
    else:
        await callback.message.answer(text_for_week_3[lan])
        dialog_manager.show_mode = ShowMode.SEND

async def message_text_handler_for_week(message: Message, widget: MessageInput,
                                        dialog_manager: DialogManager, *args, **kwargs) -> None:
    user_id = str(message.from_user.id)
    lan = await return_lan(message.from_user.id)
    dialog_manager.dialog_data['titel'] = message.text
    titel = message.text
    days_list = dialog_manager.dialog_data['week_days']
    print('days = ', days_list)
    chas = dialog_manager.dialog_data['hours']
    minuts = dialog_manager.dialog_data['minuts']
    day_digit = week_days = ''
    digit_arr = []
    for day in days_list:
        week_days += day + ','
        day_digit += day
        digit_arr.append(int(day))
    dialog_manager.dialog_data['week_days'] = week_days[:-1]
    new_days = week_day_bearbeiten(digit_arr)
    real_time_key = day_digit + chas + minuts  # 121050 - составная часть ключа id scheduler
    print('real_time_key = ', real_time_key)
    real_time = f'{new_days}, {chas}:{minuts}'  # 'Mon, Tue, 17:15'
    print('real_time_key = ', real_time_key)
    dialog_manager.dialog_data['real_time'] = real_time
    dialog_manager.dialog_data['key'] = real_time_key

    pseudo_class = {'titel': titel, 'foto_id': '', 'za_chas': None, 'za_sutki': None,
                    'selector': 'W', 'real_time': real_time, 'job_id': real_time_key}
    bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
    b_u_dict = bot_dict[user_id]  # получаю словарь юзера
    if real_time_key not in b_u_dict:
        bot_dict[user_id][real_time_key] = pseudo_class  # Записываю в словарь бота ЭК манунг
        await dp.storage.update_data(key=bot_storage_key, data=bot_dict)  # Обновляю словарь бота
        await message.answer(text=gut[lan])
        dialog_manager.show_mode = ShowMode.SEND
        await message.delete()
        await dialog_manager.next()
    else:
        await message.answer(error_same_time[lan])
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await dialog_manager.done()


async def on_photo_sent_for_week(message: Message, widget:
                                MessageInput, dialog_manager: DialogManager, *args, **kwargs):
    user_id = str(message.from_user.id)
    print('176 on_photo_sent works week_handlers')
    foto_id = message.photo[-1].file_id  # Берем последнее фото (наибольшего размера)
    lan = await return_lan(message.from_user.id)
    days_list = dialog_manager.dialog_data['week_days']
    dialog_manager.dialog_data['foto_id'] = foto_id
    dialog_manager.dialog_data['titel'] = ''
    chas = dialog_manager.dialog_data['hours']
    minuts = dialog_manager.dialog_data['minuts']

    day_digit = week_days = ''
    digit_arr = []
    for day in days_list:
        week_days += day + ','
        day_digit += day
        digit_arr.append(int(day))
    dialog_manager.dialog_data['week_days'] = week_days[:-1]

    new_days = week_day_bearbeiten(digit_arr)
    real_time_key = day_digit + chas + minuts  # 121050 - составная часть ключа id scheduler
    # print('real_time_key = ', real_time_key)
    dialog_manager.dialog_data['key'] = real_time_key
    real_time = f'{new_days}, {chas}:{minuts}'  # 'Mon, Tue, 17:15'

    dialog_manager.dialog_data['real_time'] = real_time
    pseudo_class = {'titel': '', 'foto_id': foto_id, 'za_chas': None, 'za_sutki': None,
                    'selector': 'W', 'real_time': real_time, 'job_id': real_time_key}
    bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
    b_u_dict = bot_dict[user_id]  # получаю словарь юзера
    if real_time_key not in b_u_dict:
        bot_dict[user_id][real_time_key] = pseudo_class  # Записываю в словарь бота ЭК манунг
        await dp.storage.update_data(key=bot_storage_key, data=bot_dict)  # Обновляю словарь бота
        await message.answer(text=gut[lan])
        dialog_manager.show_mode = ShowMode.SEND
        await message.delete()
        await dialog_manager.next()
    else:
        await message.answer(error_same_time[lan])
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await dialog_manager.done()

async def week_get_for_input_data(dialog_manager: DialogManager,
                                  event_from_user: User, *args, **kwargs):
    lan = await return_lan(event_from_user.id)
    getter_data = {'week_data_mahnung': set_titel[lan]}
    return getter_data

async def pre_week_sched(callback: CallbackQuery, widget: Button,
                        dialog_manager: DialogManager):
    print('\n\nWe are into pre_sched\n\n')
    dialog_dict = dialog_manager.dialog_data
    user_id = callback.from_user.id
    week_sched(user_id, dialog_dict)  # Запуск планировщика
    await dialog_manager.next()
    dialog_manager.show_mode = ShowMode.SEND


async def week_get_runner(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    lan = await return_lan(event_from_user.id)
    getter_data = {'text_for_week_sched': text_for_week[lan], 'week_remind_me':'▶️'}
    return getter_data



async def week_reset_funk_not_for_uniqe(callback: CallbackQuery, widget:Button,
                     dialog_manager: DialogManager, *args, **kwargs):
    print('reset funk week not_for_uniqe works')
    dialog_manager.dialog_data.clear() # Очищаю словарь
    await dialog_manager.start(state=ZAPUSK.add_show, mode=StartMode.RESET_STACK)

async def week_return_getter(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    lan = await return_lan(event_from_user.id)
    getter_data = {'week_accepted': accepted_uniq[lan], 'week_return_to_basic':return_to_basic[lan]}
    return getter_data


week_mahnung_dialog = Dialog(
    Window(  # Окно отправляющее клаву c днями недели
        Format('{choose_week_day}'),
        Column(
            Multiselect(
                checked_text=Format('[✔️] {item[0]}'),
                unchecked_text=Format('[  ] {item[0]}'),
                id='multi_topics',
                item_id_getter=operator.itemgetter(1),
                items="wd",
                min_selected=1,
                max_selected=6,
                on_state_changed=category_filled
            )),
        Row(
            Cancel(Const('◀️'),
                    id='week_cancel'),
            Button(Format("{approve}"), id="confirm_button", on_click=on_confirm_clicked)
        ),
        state=WEEK_MAHNUNG.choose_weekdays,
        getter=get_weekdays
    ),

    Window(
        Format('{text_for_week_wind}'),
        Row(
            Button(text=Const('00'), id='button_00', on_click=button_hour_for_week_clicked),
            Button(text=Const('01'), id='button_1', on_click=button_hour_for_week_clicked),
            Button(text=Const('02'), id='button_2', on_click=button_hour_for_week_clicked),
            Button(text=Const('03'), id='button_3', on_click=button_hour_for_week_clicked),
            Button(text=Const('04'), id='button_4', on_click=button_hour_for_week_clicked),
            Button(text=Const('05'), id='button_5', on_click=button_hour_for_week_clicked), ),
        Row(
            Button(text=Const('06'), id='button_6', on_click=button_hour_for_week_clicked),
            Button(text=Const('07'), id='button_7', on_click=button_hour_for_week_clicked),
            Button(text=Const('08'), id='button_8', on_click=button_hour_for_week_clicked),
            Button(text=Const('09'), id='button_9', on_click=button_hour_for_week_clicked),
            Button(text=Const('10'), id='button_10', on_click=button_hour_for_week_clicked),
            Button(text=Const('11'), id='button_11', on_click=button_hour_for_week_clicked), ),
        Row(
            Button(text=Const('12'), id='button_12', on_click=button_hour_for_week_clicked),
            Button(text=Const('13'), id='button_13', on_click=button_hour_for_week_clicked),
            Button(text=Const('14'), id='button_14', on_click=button_hour_for_week_clicked),
            Button(text=Const('15'), id='button_15', on_click=button_hour_for_week_clicked),
            Button(text=Const('16'), id='button_16', on_click=button_hour_for_week_clicked),
            Button(text=Const('17'), id='button_17', on_click=button_hour_for_week_clicked), ),
        Row(
            Button(text=Const('18'), id='button_18', on_click=button_hour_for_week_clicked),
            Button(text=Const('19'), id='button_19', on_click=button_hour_for_week_clicked),
            Button(text=Const('20'), id='button_20', on_click=button_hour_for_week_clicked),
            Button(text=Const('21'), id='button_21', on_click=button_hour_for_week_clicked),
            Button(text=Const('22'), id='button_22', on_click=button_hour_for_week_clicked),
            Button(text=Const('23'), id='button_23', on_click=button_hour_for_week_clicked)
        ),
        state=WEEK_MAHNUNG.choose_hour,
        getter=week_choosing_hour_getter
    ),

    Window(  # Окно формирует два задания для планировщика
        Format('{text_for_3_week_wind}'),
        Row(
            Button(text=Const('00'), id='button_00', on_click=week_button_minut_clicked),
            Button(text=Const('05'), id='button_05', on_click=week_button_minut_clicked),
            Button(text=Const('10'), id='button_10', on_click=week_button_minut_clicked),),
        Row(
            Button(text=Const('15'), id='button_15', on_click=week_button_minut_clicked),
            Button(text=Const('20'), id='button_20', on_click=week_button_minut_clicked),
            Button(text=Const('25'), id='button_25', on_click=week_button_minut_clicked), ),
        Row(
            Button(text=Const('30'), id='button_30', on_click=week_button_minut_clicked),
            Button(text=Const('35'), id='button_35', on_click=week_button_minut_clicked),
            Button(text=Const('40'), id='button_40', on_click=week_button_minut_clicked), ),
        Row(
            Button(text=Const('45'), id='button_45', on_click=week_button_minut_clicked),
            Button(text=Const('50'), id='button_50', on_click=week_button_minut_clicked),
            Button(text=Const('55'), id='button_55', on_click=week_button_minut_clicked), ),
        Row(
            Button(text=Format('{form_grafik_week_mahnungen}'), id='week_zapusk', on_click=button_zapusk_clicked_for_week),
        ),
        state=WEEK_MAHNUNG.choose_min,
        getter=week_get_minuts
    ),

    Window(  # Окно принимающее содержание напоминания и формирующее ЭК Mahnung
        Format(text='{week_data_mahnung}'),
        MessageInput(
            func=message_text_handler_for_week,
            content_types=ContentType.TEXT,
        ),
        MessageInput(
            func=on_photo_sent_for_week,
            content_types=ContentType.PHOTO,
        ),
        MessageInput(
            func=message_not_foto_handler,
            content_types=ContentType.ANY,
        ),
        state=WEEK_MAHNUNG.sent_mahnung_data,
        getter=week_get_for_input_data # Из input_getter
    ),

    Window(  # Окно запускающее шедулер
        Format('{text_for_week_sched}'),
        Button(text=Format('{week_remind_me}'),
               id='pre_week_sched_button',
               on_click=pre_week_sched),
        state=WEEK_MAHNUNG.run_scheduler,
        getter=week_get_runner
    ),

    Window(  # окно возвращаюшее в Корневое окно
        Format(text='{week_accepted}'),
        Button(text=Format(text='{week_return_to_basic}'),
               id='week_see_stelle_button',
               on_click=week_reset_funk_not_for_uniqe),
        state=WEEK_MAHNUNG.week_return_to_basic,
        getter=week_return_getter
    ),

)

