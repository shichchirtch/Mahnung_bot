from aiogram.types import CallbackQuery, Message, User
from aiogram_dialog import DialogManager
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Row
from aiogram_dialog.widgets.kbd import Button, Cancel, Next
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

async def accept_foto_for_day(message: Message, widget: MessageInput, dialog_manager: DialogManager):
    foto_id = message.photo[-1].file_id
    dialog_manager.dialog_data['titel'] = ''
    dialog_manager.dialog_data['foto_id'] = foto_id
    dialog_manager.show_mode = ShowMode.SEND
    await dialog_manager.next()

async def on_confirm_hours_in_days_clicked(callback: CallbackQuery, button: Button, dialog_manager: DialogManager, *args, **kwargs):
    lan = await return_lan(callback.from_user.id)
    select_at_least_one ={ 'ru':"Выберите хотя бы один час", 'en':'Select please at least one',
                           'de':'Wählen Sie bitte mindestens eine Stunde', 'tr':'Lütfen en az birini seçin', 'uk':'Будь ласка, виберіть принаймні одну годину',
                           'ar':'الرجاء تحديد واحد على الأقل',
                           'fa':'لطفا حداقل یکی را انتخاب کنید'}
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
            # print('new_hour = ', new_hours)
        else:
            new_hours = temp_hours
    else:
        new_hours = hour_mahnung
    # print('59 new_hours = ', new_hours)
    dialog_manager.dialog_data['hours'] = new_hours
    dialog_manager.dialog_data['capture'] = ''
    await callback.message.answer(text=f'{for_days_arbeit_stunde[lan]} <b>{new_hours}</b>')


async def days_choosing_hour_getter(
                             dialog_manager: DialogManager, event_from_user: User, *args, **kwargs):
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
        min_dict = {'button_00': '00', 'button_05': '05', 'button_10': '10', 'button_15': '15',
                    'button_20': '20', 'button_25': '25', 'button_30': '30', 'button_35': '35',
                    'button_40': '40', 'button_45': '45', 'button_50': '50', 'button_55': '55'
                    }
        dialog_manager.dialog_data['minuts'] = min_dict[callback.data]
        lan = await return_lan(callback.from_user.id)
        strocka = f'{real_min_selekted[lan]}  <b>{min_dict[callback.data]}</b>\n\n{knopka_nazata[lan]}'
        await callback.message.answer(text=strocka)

async def button_zapusk_clicked_for_day(callback: CallbackQuery, widget: Button,
                                    dialog_manager: DialogManager, *args, **kwargs):
    lan = await return_lan(callback.from_user.id)
    dialog_manager.dialog_data['tz']=await return_tz(callback.from_user.id)
    dialog_manager.dialog_data['capture'] = ''  # Устанавлию в  dialog data ключ capture
    text_for_day_2 = {'ru': 'Выберите минуты', 'en': 'Choose an minutes', 'tr': 'Bir dakika seçin',
                      'uk': 'Виберіть хвилини', 'de': 'Wählen Sie eine Minute',
                      'fa': 'یک دقیقه انتخاب کنید', 'ar': 'اختر دقيقة' }
    if 'minuts' in dialog_manager.dialog_data:
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await dialog_manager.next()
    else:
        await callback.message.answer(text_for_day_2[lan])
        dialog_manager.show_mode = ShowMode.EDIT

async def message_text_handler_for_days(message: Message, widget: MessageInput,
                                        dialog_manager: DialogManager, *args, **kwargs) -> None:
    user_id = str(message.from_user.id)
    lan = await return_lan(message.from_user.id)
    titel = message.text
    if len(titel) > 4000:
        titel = titel[:4000]
    dialog_manager.dialog_data['titel'] = titel
    chas = dialog_manager.dialog_data['hours']
    # print('chas  =', chas)
    minuts = dialog_manager.dialog_data['minuts']
    str_folge = right_folge = ''
    digit_arr = []
    if len(chas)>2: # 01
        # print('mehr 2 titel')
        for stunde in chas.split(','):
            digit_arr.append(int(stunde))
        sort_arr = sorted(digit_arr)
        for int_stunde in sort_arr:
            right_folge+=str(int_stunde)+','
            str_folge+=str(int_stunde)
        chas = right_folge[:-1]
        # print('\n\nchas = ', chas)
    else:
        str_folge = chas
        # print('### srt folge = ', str_folge)

    dialog_manager.dialog_data['hours'] = chas
    real_time_key = str_folge + minuts  # 121050 - составная часть ключа id scheduler
    # print('real_time_key = ', real_time_key)
    real_time = f'{daily[lan]} {chas} : {minuts}'  # '8, 20, 17:15'
    # print('real_time = ', real_time)
    dialog_manager.dialog_data['real_time'] = real_time
    dialog_manager.dialog_data['key'] = real_time_key
    pseudo_class = {'titel': titel, 'foto_id': '', 'za_chas': None, 'za_sutki': None,
                    'selector': 'D', 'real_time': real_time, 'capture':'','job_id': real_time_key}
    bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
    b_u_dict = bot_dict[user_id]['reg']  # получаю словарь юзера
    if real_time_key not in b_u_dict:  # Если такого времени еще не забухено
        b_u_dict[real_time_key] = pseudo_class  # Записываю в словарь бота ЭК манунг
        await dp.storage.update_data(key=bot_storage_key, data=bot_dict)  # Обновляю словарь бота
        await message.answer(text=gut[lan])
        dialog_manager.show_mode = ShowMode.SEND
        await message.delete()
        await dialog_manager.switch_to(DAY_MAHNUNG.run_day_scheduler)
    else:
        await message.answer(error_same_time[lan])
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await dialog_manager.done()


async def form_mahnung_ohne_capture_day(cb: CallbackQuery, widget:
                                Button, dialog_manager: DialogManager, *args, **kwargs):
    user_id = str(cb.from_user.id)
    lan = await return_lan(cb.from_user.id)
    foto_id = dialog_manager.dialog_data['foto_id']
    dialog_manager.dialog_data['titel'] = ''
    chas = dialog_manager.dialog_data['hours']
    minuts = dialog_manager.dialog_data['minuts']
    str_folge = right_folge = ''
    digit_arr = []
    if len(chas) > 2:  # 01
        # print('mehr 2 titel')
        for stunde in chas.split(','):
            digit_arr.append(int(stunde))
        sort_arr = sorted(digit_arr)
        for int_stunde in sort_arr:
            right_folge += str(int_stunde) + ','
            str_folge += str(int_stunde)
        chas = right_folge[:-1]
    else:
        str_folge = chas

    dialog_manager.dialog_data['hours'] = chas
    real_time_key = str_folge + minuts  # 121050 - составная часть ключа id scheduler

    real_time = f'{daily[lan]} {chas} : {minuts}'  # 'Dayly 17:15'
    dialog_manager.dialog_data['real_time'] = real_time
    dialog_manager.dialog_data['key'] = real_time_key

    pseudo_class = {'titel': '', 'foto_id': foto_id, 'za_chas': None, 'za_sutki': None,
                    'selector': 'D', 'real_time': real_time, 'capture':'','job_id': real_time_key}
    bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
    b_u_dict = bot_dict[user_id]['reg']  # получаю словарь юзера
    if real_time_key not in b_u_dict:
        b_u_dict[real_time_key] = pseudo_class  # Записываю в словарь бота ЭК манунг
        await dp.storage.update_data(key=bot_storage_key, data=bot_dict)  # Обновляю словарь бота
        await cb.message.answer(text=gut[lan])
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await cb.message.delete()
        await dialog_manager.switch_to(DAY_MAHNUNG.run_day_scheduler)
    else:
        await cb.message.answer(error_same_time[lan])
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await dialog_manager.done()

async def set_capture_day(message: Message, widget:
                                MessageInput, dialog_manager: DialogManager, *args, **kwargs):
    user_id = str(message.from_user.id)
    lan = await return_lan(message.from_user.id)
    foto_id = dialog_manager.dialog_data['foto_id']
    dialog_manager.dialog_data['titel'] = ''
    chas = dialog_manager.dialog_data['hours']
    minuts = dialog_manager.dialog_data['minuts']
    capture = message.text
    if len(capture)>800:
        capture = capture[:800]
    dialog_manager.dialog_data['capture'] = capture
    str_folge = right_folge = ''
    digit_arr = []
    if len(chas) > 2:  # 01
        # print('mehr 2 titel')
        for stunde in chas.split(','):
            digit_arr.append(int(stunde))
        sort_arr = sorted(digit_arr)
        for int_stunde in sort_arr:
            right_folge += str(int_stunde) + ','
            str_folge += str(int_stunde)
        chas = right_folge[:-1]
    else:
        str_folge = chas

    dialog_manager.dialog_data['hours'] = chas
    real_time_key = str_folge + minuts  # 121050 - составная часть ключа id scheduler

    real_time = f'{daily[lan]} {chas} : {minuts}'  # 'Dayly 17:15'
    dialog_manager.dialog_data['real_time'] = real_time
    dialog_manager.dialog_data['key'] = real_time_key

    pseudo_class = {'titel': '', 'foto_id': foto_id, 'za_chas': None, 'za_sutki': None,
                    'selector': 'D', 'real_time': real_time, 'capture':message.text,'job_id': real_time_key}
    bot_dict = await dp.storage.get_data(key=bot_storage_key)  # Получаю словарь бота
    b_u_dict = bot_dict[user_id]['reg']  # получаю словарь юзера
    if real_time_key not in b_u_dict:
        b_u_dict[real_time_key] = pseudo_class  # Записываю в словарь бота ЭК манунг
        await dp.storage.update_data(key=bot_storage_key, data=bot_dict)  # Обновляю словарь бота
        await message.answer(text=gut[lan])
        dialog_manager.show_mode = ShowMode.SEND
        await message.delete()
        await dialog_manager.next()
    else:
        await message.answer(error_same_time[lan])
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await dialog_manager.done()

async def day_get_for_input_data(dialog_manager: DialogManager,
                                  event_from_user: User, *args, **kwargs):
    lan  = await return_lan(event_from_user.id)
    getter_data = {'day_data_mahnung': set_titel[lan]}
    return getter_data

async def pre_day_sched(callback: CallbackQuery, widget: Button,
                        dialog_manager: DialogManager):
    # print('\n\nWe are into pre_sched\n\n')
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

async def message_not_text_handler_in_capture_day(message: Message, widget: MessageInput,
        dialog_manager: DialogManager) -> None:
    dialog_manager.show_mode = ShowMode.NO_UPDATE
    lan = await return_lan(message.from_user.id)
    await message.answer(not_text_capture_send[lan])

async def return_to_hours(cb: CallbackQuery, widget: Button, dialog_manager: DialogManager):
    del dialog_manager.dialog_data['hours']
    dialog_manager.dialog_data['minuts'] = ''
    dialog_manager.show_mode = ShowMode.EDIT
    await dialog_manager.back()

#####################################################################################################

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
        Row(
        Cancel(Const('◀️'),
               id='day_cancel'),
        Button(text=Format('{go_to_minuts_in_days}'), id='choose_minuts', on_click=on_confirm_hours_in_days_clicked)),
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
        Row(Button(Const('◀️'),id='back_to_tage_week',on_click=return_to_hours),
            Button(text=Const('▶️'), id='day_zapusk', on_click=button_zapusk_clicked_for_day),
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
            func=accept_foto_for_day,
            content_types=ContentType.PHOTO,
        ),
        MessageInput(
            func=message_not_foto_handler,
            content_types=ContentType.ANY,
        ),
        Cancel(Const('◀️'),
               id='Cancel_for_uniq_day'),
        state=DAY_MAHNUNG.day_sent_mahnung_data,
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
                   on_click=form_mahnung_ohne_capture_day)),

        state=DAY_MAHNUNG.ask_capture,
        getter=getter_for_capture_day
    ),

    Window(  # Окно принимающее capture
        Format(text='{data_capture}'),  # Отправьте capture
        MessageInput(
            func=set_capture_day,
            content_types=ContentType.TEXT,
        ),
        MessageInput(
            func=message_not_text_handler_in_capture_day,
            content_types=ContentType.ANY,
        ),
        Cancel(Const('◀️'),
               id='Cancel_for_uniq_day'),
        state=DAY_MAHNUNG.accept_capture,
        getter=get_enter_capture_day
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