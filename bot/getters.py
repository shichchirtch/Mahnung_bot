from aiogram.types import User
from aiogram_dialog import DialogManager
from lexicon import *
import datetime



async def get_languages(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    state = dialog_manager.middleware_data["state"]
    us_dict = await state.get_data()
    lan = us_dict['lan']
    returned_data = show_or_set[lan]
    set_r = new_mahnung[lan]
    see_r = see_reminder_list[lan]
    return {'knopka': returned_data, 'set_r':set_r, 'see_r':see_r}

async def get_spam(dialog_manager: DialogManager, **kwargs):
    # manager: DialogManager = kwargs.get("manager")
    spam = [('🤢','1'), ('😃','2')]
    lan = dialog_manager.dialog_data['lan']
    sp = spam_vopros[lan]
    return {"spam_data": spam, 'lan':sp}

async def get_type(dialog_manager: DialogManager, **kwargs):
    state = dialog_manager.middleware_data["state"]
    us_dict = await state.get_data()
    lan = us_dict['lan']
    return {'type':get_m_type[lan], 'reg':regular_mahnung[lan], 'uniq':unique_mahnung[lan]}

async def  select_data(dialog_manager: DialogManager, **kwargs):
    state = dialog_manager.middleware_data["state"]
    us_dict = await state.get_data()
    lan = us_dict['lan']
    return {'select_data':selected_data[lan]}


async def choosing_data_getter(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    # print('dialog_manager.dialog_data = ', dialog_manager.dialog_data['choosing_data'])
    state = dialog_manager.middleware_data["state"]
    us_dict = await state.get_data()
    lan = us_dict['lan']
    if dialog_manager.dialog_data['choosing_data']:
        getter_data = {'text_for_2_wind': choose_hours[lan], 'choosing_data':True
                       }
    else:
        getter_data = {'text_for_2_wind': car_time[lan], 'choosing_data':False}
    return getter_data


async def form_mahnung_getter(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    state = dialog_manager.middleware_data["state"]
    us_dict = await state.get_data()
    lan = us_dict['lan']
    if dialog_manager.dialog_data['choosing_data']:
        getter_data = {'text_for_3_wind': choose_minuts[lan], 'choosing_data':True, 'form_grafik_mahnungen':form_grafik[lan]
                       }
    else:
        getter_data = {'text_for_3_wind': car_time[lan], 'choosing_data':False}
    return getter_data


async def choosing_minut_getter(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    state = dialog_manager.middleware_data["state"]
    us_dict = await state.get_data()
    lan = us_dict['lan']
    if dialog_manager.dialog_data['choosing_data']:
        getter_data = {'text_for_4_wind': zapuskaem_scheduler[lan], 'choosing_data':True, 'remind_me':remind_me[lan]
                       }
    else:
        getter_data = {'text_for_4_wind': car_time[lan], 'choosing_data':False}
    return getter_data


async def mahnung_accepted(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    state = dialog_manager.middleware_data["state"]
    us_dict = await state.get_data()
    lan = us_dict['lan']
    getter_data = {'accepted': accepted_uniq[lan], 'return_to_basic':return_to_basic[lan]
                   }
    return getter_data


async def get_titel(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    state = dialog_manager.middleware_data["state"]
    us_dict = await state.get_data()
    lan = us_dict['lan']
    getter_data = {'data_mahnung': set_titel[lan], 'choosing_data':True}
    return getter_data

async def get_timezone_info(dialog_manager: DialogManager, event_from_user: User, **kwargs):
    state = dialog_manager.middleware_data["state"]
    us_dict = await state.get_data()
    lan = us_dict['lan']
    current_time = datetime.datetime.now()
    bot_time = current_time.strftime("%H:%M")
    getter_data = {'bot_time':f'<b>{bot_time_now[lan]} {bot_time}</b>',
                   'minus_3':us_tz_minus_3[lan], 'minus_2':us_tz_minus_2[lan], 'minus_1':us_tz_minus_1[lan],
                   'gleich':us_tz_gleich[lan], 'plus_1':us_tz_plus_1[lan], 'plus_2':us_tz_plus_2[lan], 'plus_3':us_tz_plus_3[lan]}
    return getter_data




