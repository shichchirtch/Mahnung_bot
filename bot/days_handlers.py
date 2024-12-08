from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import DialogManager
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Row
from aiogram_dialog.widgets.kbd import Button
from aiogram_dialog.api.entities.modes import ShowMode, StartMode
from bot_instans import dp, bot_storage_key,  ZAPUSK
from lexicon import *
from aiogram_dialog.widgets.input import  MessageInput
from scheduler_functions import day_sched
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ContentType
from input_handlers import message_not_foto_handler
from postgres_functions import return_tz, return_lan

class DAY_MAHNUNG(StatesGroup):
    first = State()
    choose_time_during_day = State()
    run_day_scheduler = State()
    day_sent_mahnung_data = State()
    day_return_to_basic = State()

async def on_confirm_hours_in_days_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, *args, **kwargs):
    lan = await return_lan(callback.from_user.id)
    select_at_least_one ={ 'ru':"Выберите хотя бы один час", 'en':'Select please at least one'}
    selected_days = dialog_manager.dialog_data.get('hours', '')
    if selected_days:
        await dialog_manager.next()  # Переход к следующему окну
    else:
        await callback.message.answer(select_at_least_one[lan], show_alert=True)


async def button_hour_for_day_clicked(callback: CallbackQuery, widget: Button,
                             dialog_manager: DialogManager, *args, **kwargs):
    lan = await return_lan(callback.from_user.id)
    dialog_manager.dialog_data['lan'] = lan
    uhr_dict = {'button_00': '00', 'button_1': '01', 'button_2': '02', 'button_3': '03',
                'button_4': '04', 'button_5': '05', 'button_6': '06', 'button_7': '07',
                'button_8': '08', 'button_9': '09', 'button_10': '10', 'button_11': '11',
                'button_12': '12', 'button_13': '13', 'button_14': '14', 'button_15': '15',
                'button_16': '16', 'button_17': '17', 'button_18': '18', 'button_19': '19',
                'button_20': '20', 'button_21': '21', 'button_22': '22', 'button_23': '23',
                }
    hour_mahnung = uhr_dict[callback.data]
    temp_hours = dialog_manager.dialog_data.get('hours', '')
    if temp_hours:
        if hour_mahnung not in temp_hours:  # Если 2 раза нажимается одна и та же кнопка
            new_hours = temp_hours + ','+hour_mahnung
        else:
            new_hours = temp_hours
    else:
        new_hours = hour_mahnung
    print('59 new_hours = ', new_hours)
    dialog_manager.dialog_data['hours'] = new_hours
    await callback.message.answer(text=f'{for_days_arbeit_stunde[lan]} {new_hours}')
    # dialog_manager.show_mode = ShowMode.SEND

async def days_choosing_hour_getter(
                             dialog_manager: DialogManager, event_from_user: User, *args, **kwargs):
    lan = await return_lan(event_from_user.id)
    text_for_day_1_window = {'ru':'Выберите час/часы', 'en':'Choose an Hour'}
    getter_data = {'go_to_minuts_in_days': go_to_minuts_in_days[lan], 'select_hour': text_for_day_1_window[lan]}
    return getter_data


async def day_get_minuts( dialog_manager: DialogManager, event_from_user: User, *args, **kwargs):
    lan = await return_lan(event_from_user.id)
    text_for_days_2_window = {'ru':'Выберите минуты', 'en':'Choose minuts'}
    getter_data = {'text_for_2_day_wind': text_for_days_2_window[lan], 'form_grafik_dayly_mahnungen': form_grafik[lan]}
    return getter_data



async def day_button_minut_clicked(callback: CallbackQuery, widget: Button,
                                    dialog_manager: DialogManager, *args, **kwargs):
        min_dict = {'button_00': '00', 'button_05': '05', 'button_10': '10', 'button_15': '15',
                    'button_20': '20', 'button_25': '25', 'button_30': '30', 'button_35': '35',
                    'button_40': '40', 'button_45': '45', 'button_50': '50', 'button_55': '55'
                    }
        dialog_manager.dialog_data['minuts'] = min_dict[callback.data]
        lan = await return_lan(callback.from_user.id)
        await callback.message.answer(text=knopka_nazata[lan])

async def button_zapusk_clicked_for_day(callback: CallbackQuery, widget: Button,
                                    dialog_manager: DialogManager, *args, **kwargs):
    lan = await return_lan(callback.from_user.id)
    dialog_manager.dialog_data['tz']=await return_tz(callback.from_user.id)
    text_for_day_2 = {'ru': 'Выберите минуты', 'en': 'Choose an minutes', 'tr': 'Bir dakika seçin',
                      'uk': 'Виберіть хвилини', 'de': 'Wählen Sie eine Minute',
                      'fa': 'یک دقیقه انتخاب کنید', 'ar': 'اختر دقيقة' }
    if 'minuts' in dialog_manager.dialog_data:
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await dialog_manager.next()
    else:
        await callback.message.answer(text_for_day_2[lan])
        dialog_manager.show_mode = ShowMode.SEND

async def message_text_handler_for_days(message: Message, widget: MessageInput,
                                        dialog_manager: DialogManager, *args, **kwargs) -> None:
    user_id = str(message.from_user.id)
    lan = await return_lan(message.from_user.id)
    dialog_manager.dialog_data['titel'] = message.text
    titel = message.text
    chas = dialog_manager.dialog_data['hours']
    # print('chas  =', chas)
    minuts = dialog_manager.dialog_data['minuts']
    str_folge = right_folge = ''
    digit_arr = []
    if len(chas)>2:
        # print('mehr 2 titel')
        for stunde in chas.split(','):
            digit_arr.append(int(stunde))
        sort_arr = sorted(digit_arr)
        for int_stunde in sort_arr:
            right_folge+=str(int_stunde)+','
            str_folge+=str(int_stunde)
        chas = right_folge[:-1]
    else:
        str_folge = chas

    dialog_manager.dialog_data['hours'] = chas
    real_time_key = str_folge + minuts  # 121050 - составная часть ключа id scheduler
    print('real_time_key = ', real_time_key)
    real_time = f'{daily[lan]} {str_folge}:{minuts}'  # '8, 20, 17:15'
    print('real_time = ', real_time)
    dialog_manager.dialog_data['real_time'] = real_time
    dialog_manager.dialog_data['key'] = real_time_key
    pseudo_class = {'titel': titel, 'foto_id': '', 'za_chas': None, 'za_sutki': None,
                    'selector': 'D', 'real_time': real_time, 'job_id': real_time_key}
    bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
    b_u_dict = bot_dict[user_id]
    if real_time_key not in b_u_dict:
        bot_dict[user_id][real_time_key] = pseudo_class  # Записываю в словарь бота ЭК манунг
        await dp.storage.update_data(key=bot_storage_key, data=bot_dict)  # Обновляю словарь бота
        await message.answer(text=gut[lan])
    else:
        await message.answer('error 🤷')
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    await dialog_manager.next()


async def on_photo_sent_for_day(message: Message, widget:
                                MessageInput, dialog_manager: DialogManager, *args, **kwargs):
    user_id = str(message.from_user.id)
    print('161 on_photo_sent works day_handlers')
    foto_id = message.photo[-1].file_id  # Берем последнее фото (наибольшего размера)
    lan = await return_lan(message.from_user.id)
    dialog_manager.dialog_data['foto_id'] = foto_id
    dialog_manager.dialog_data['titel'] = ''
    chas = dialog_manager.dialog_data['hours']
    minuts = dialog_manager.dialog_data['minuts']
    str_folge = right_folge = ''
    digit_arr = []
    if len(chas) > 1:
        # print('mehr 1')
        for stunde in chas.split(','):
            digit_arr.append(int(stunde))
        sort_arr = sorted(digit_arr)
        for int_stunde in sort_arr:
            right_folge += str(int_stunde) + ','
            str_folge += str(int_stunde)
        chas = right_folge[:-1]

    dialog_manager.dialog_data['hours'] = chas
    real_time_key = chas + minuts  # 121050 - составная часть ключа id scheduler

    real_time = f'{daily[lan]} {chas}:{minuts}'  # 'Dayly 17:15'
    dialog_manager.dialog_data['real_time'] = real_time
    dialog_manager.dialog_data['key'] = real_time_key

    pseudo_class = {'titel': '', 'foto_id': foto_id, 'za_chas': None, 'za_sutki': None,
                    'selector': 'D', 'real_time': real_time, 'job_id': real_time_key}
    bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
    b_u_dict = bot_dict[user_id]
    if real_time_key not in b_u_dict:
        bot_dict[user_id][real_time_key] = pseudo_class  # Записываю в словарь бота ЭК манунг
        await dp.storage.update_data(key=bot_storage_key, data=bot_dict)  # Обновляю словарь бота
        await message.answer(text=gut[lan])
    else:
        await message.answer('error 🤷')
    await message.delete()
    await dialog_manager.next()

async def day_get_for_input_data(dialog_manager: DialogManager,
                                  event_from_user: User, *args, **kwargs):
    lan  = await return_lan(event_from_user.id)
    getter_data = {'day_data_mahnung': set_titel[lan]}
    return getter_data

async def pre_day_sched(callback: CallbackQuery, widget: Button,
                        dialog_manager: DialogManager):
    print('\n\nWe are into pre_sched\n\n')
    dialog_dict = dialog_manager.dialog_data
    user_id = callback.from_user.id
    day_sched(user_id, dialog_dict) # Запуск планировщика
    await dialog_manager.next()
    dialog_manager.show_mode = ShowMode.SEND

async def day_get_runner(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    lan = await return_lan(event_from_user.id)
    getter_data = {'text_for_day_sched': text_for_day[lan], 'day_remind_me':'▶️'}
    return getter_data



async def day_reset_funk_not_for_uniqe(callback: CallbackQuery, widget:Button,
                     dialog_manager: DialogManager, *args, **kwargs):
    print('reset funk day not_for_uniqe works')
    dialog_manager.dialog_data.clear() # Очищаю словарь
    await dialog_manager.start(state=ZAPUSK.add_show, mode=StartMode.RESET_STACK)

async def day_return_getter(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    lan = await return_lan(event_from_user.id)
    getter_data = {'day_accepted': accepted_uniq[lan], 'day_return_to_basic':return_to_basic[lan]}
    return getter_data

day_mahnung_dialog = Dialog(
    Window(  # Окно отправляющее клаву из часов
        Format('{select_hour}'),
        Row(
            Button(text=Const('00'), id='button_00', on_click=button_hour_for_day_clicked),
            Button(text=Const('01'), id='button_1', on_click=button_hour_for_day_clicked),
            Button(text=Const('02'), id='button_2', on_click=button_hour_for_day_clicked),
            Button(text=Const('03'), id='button_3', on_click=button_hour_for_day_clicked),
            Button(text=Const('04'), id='button_4', on_click=button_hour_for_day_clicked),
            Button(text=Const('05'), id='button_5', on_click=button_hour_for_day_clicked), ),
        Row(
            Button(text=Const('06'), id='button_6', on_click=button_hour_for_day_clicked),
            Button(text=Const('07'), id='button_7', on_click=button_hour_for_day_clicked),
            Button(text=Const('08'), id='button_8', on_click=button_hour_for_day_clicked),
            Button(text=Const('09'), id='button_9', on_click=button_hour_for_day_clicked),
            Button(text=Const('10'), id='button_10', on_click=button_hour_for_day_clicked),
            Button(text=Const('11'), id='button_11', on_click=button_hour_for_day_clicked), ),
        Row(
            Button(text=Const('12'), id='button_12', on_click=button_hour_for_day_clicked),
            Button(text=Const('13'), id='button_13', on_click=button_hour_for_day_clicked),
            Button(text=Const('14'), id='button_14', on_click=button_hour_for_day_clicked),
            Button(text=Const('15'), id='button_15', on_click=button_hour_for_day_clicked),
            Button(text=Const('16'), id='button_16', on_click=button_hour_for_day_clicked),
            Button(text=Const('17'), id='button_17', on_click=button_hour_for_day_clicked), ),
        Row(
            Button(text=Const('18'), id='button_18', on_click=button_hour_for_day_clicked),
            Button(text=Const('19'), id='button_19', on_click=button_hour_for_day_clicked),
            Button(text=Const('20'), id='button_20', on_click=button_hour_for_day_clicked),
            Button(text=Const('21'), id='button_21', on_click=button_hour_for_day_clicked),
            Button(text=Const('22'), id='button_22', on_click=button_hour_for_day_clicked),
            Button(text=Const('23'), id='button_23', on_click=button_hour_for_day_clicked)
        ),
        Button(text=Format('{go_to_minuts_in_days}'), id='choose_minuts', on_click=on_confirm_hours_in_days_clicked),
        state=DAY_MAHNUNG.first,
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
        Row(
            Button(text=Format('{form_grafik_dayly_mahnungen}'), id='day_zapusk', on_click=button_zapusk_clicked_for_day),
        ),
        state=DAY_MAHNUNG.choose_time_during_day,
        getter=day_get_minuts
    ),

    Window(  # Окно принимающее содержание напоминания и формирующее ЭК Mahnung
        Format(text='{day_data_mahnung}'),
        MessageInput(
            func=message_text_handler_for_days,
            content_types=ContentType.TEXT,
        ),
        MessageInput(
            func=on_photo_sent_for_day,
            content_types=ContentType.PHOTO,
        ),
        MessageInput(
            func=message_not_foto_handler,
            content_types=ContentType.ANY,
        ),
        state=DAY_MAHNUNG.day_sent_mahnung_data,
        getter=day_get_for_input_data # Из input_getter
    ),

    Window(  # Окно запускающее шедулер
        Format('{text_for_day_sched}'),
        Button(text=Format('{day_remind_me}'),
               id='pre_day_sched_button',
               on_click=pre_day_sched),
        state=DAY_MAHNUNG.run_day_scheduler,
        getter=day_get_runner
    ),

    Window(  # окно возвращаюшее в Корневое окно
        Format(text='{day_accepted}'),
        Button(text=Format(text='{day_return_to_basic}'),
               id='day_see_stelle_button',
               on_click=day_reset_funk_not_for_uniqe),
        state=DAY_MAHNUNG.day_return_to_basic,
        getter=day_return_getter
    ),
)