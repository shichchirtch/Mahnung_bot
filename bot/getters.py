from aiogram.types import User
from aiogram_dialog import DialogManager
from lexicon import *
import datetime
from postgres_functions import return_lan, insert_lan, insert_timezone



async def get_set_or_show(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    # print('get_lang works')
    lan = await return_lan(event_from_user.id)
    if not lan:
        await insert_lan(event_from_user.id, 'ru')
        await insert_timezone(event_from_user.id, 'Europe/Moscow')
        lan = 'ru'
    returned_data = show_or_set[lan]
    set_r = new_mahnung[lan]
    see_r = see_reminder_list[lan]
    return {'knopka': returned_data, 'set_r':set_r, 'see_r':see_r}

async def get_spam(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    spam = [('🤢','1'), ('😃','2')]
    lan = await return_lan(event_from_user.id)
    sp = spam_vopros[lan]
    return {"spam_data": spam, 'lan':sp}

async def get_type(dialog_manager: DialogManager, event_from_user: User,**kwargs):
    lan = await return_lan(event_from_user.id)
    return {'type':get_m_type[lan], 'reg':regular_mahnung[lan], 'uniq':unique_mahnung[lan]}



async def  select_data(dialog_manager: DialogManager, event_from_user: User,**kwargs):
    lan = await return_lan(event_from_user.id)
    return {'select_data':selected_data[lan]}


async def choosing_data_getter(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    lan = await return_lan(event_from_user.id)
    if dialog_manager.dialog_data['choosing_data']:
        getter_data = {'text_for_2_wind': choose_hours[lan], 'choosing_data':True}
    else:
        getter_data = {'text_for_2_wind': car_time[lan], 'choosing_data':False}
    return getter_data


async def form_mahnung_getter(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    lan = await return_lan(event_from_user.id)
    if dialog_manager.dialog_data['choosing_data']:
        getter_data = {'text_for_3_wind': choose_minuts[lan], 'choosing_data':True }
    else:
        getter_data = {'text_for_3_wind': car_time[lan], 'choosing_data':False}
    return getter_data


async def mahnung_accepted(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    lan = await return_lan(event_from_user.id)
    getter_data = {'accepted': accepted_uniq[lan], 'return_to_basic':return_to_basic[lan]}
    return getter_data


async def get_titel(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    lan = await return_lan(event_from_user.id)
    getter_data = {'data_mahnung': set_titel[lan], 'choosing_data':True}
    return getter_data

async def get_timezone_info(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    lan = await return_lan(event_from_user.id)
    current_time = datetime.datetime.now()
    bot_time = current_time.strftime("%H:%M")
    getter_data = {'bot_time':f'<b>{bot_time_now[lan]} {bot_time}</b>',
                   'gleich':us_tz_gleich[lan], 'plus_1':us_tz_plus_1[lan], 'plus_2':us_tz_plus_2[lan], 'plus_3':us_tz_plus_3[lan],
                   'plus_4':us_tz_plus_4[lan], 'plus_5':us_tz_plus_5[lan], 'plus_6':us_tz_plus_6[lan],
                   'plus_7': us_tz_plus_7[lan],
                   'plus_8': us_tz_plus_8[lan],
                   'plus_9': us_tz_plus_9[lan],
                   'plus_10': us_tz_plus_10[lan],
                   'plus_11': us_tz_plus_11[lan],
                   'plus_12': us_tz_plus_12[lan],
                   }
    return getter_data




